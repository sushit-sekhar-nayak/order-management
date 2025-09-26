# order/app.py
from flask import Flask, request, jsonify, abort
from models import init_db, Order
import requests
import uuid
import pika
import json
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
init_db()

INVENTORY_URL = "http://127.0.0.1:5001"  # Inventory service URL

# ---------- Health check ----------
@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')

# ---------- Place an order ----------
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    if not data or 'items' not in data:
        abort(400, 'items required')

    # 1️⃣ Check inventory
    resp = requests.post(f"{INVENTORY_URL}/inventory/check", json={"items": data['items']})
    inv_result = resp.json()
    if not inv_result['ok']:
        return jsonify({"error": "Some items are out of stock", "details": inv_result['details']}), 400

    # 2️⃣ Calculate total
    total = 0.0
    for it in data['items']:
        sku = it['sku']
        qty = it['qty']
        prod_resp = requests.get(f"{INVENTORY_URL}/products/{sku}")
        prod = prod_resp.json()
        total += prod['price'] * qty

    # 3️⃣ Create order in DB
    order_id = str(uuid.uuid4())
    order = Order.create(order_id, data['items'], total)

    # 4️⃣ Deduct inventory quantities via Inventory Service
    try:
        requests.post(f"{INVENTORY_URL}/inventory/deduct", json={"items": data['items']})
    except Exception as e:
        print(f"Failed to deduct inventory: {e}")

    # 5️⃣ Publish order to RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='order_queue')

        order_message = {
            "order_id": order_id,
            "items": data['items'],
            "total_amount": total
        }
        channel.basic_publish(
            exchange='',
            routing_key='order_queue',
            body=json.dumps(order_message)
        )
        connection.close()
        print(f"Order {order_id} sent to shipping queue")
    except Exception as e:
        print(f"Failed to publish order to RabbitMQ: {e}")

    return jsonify(order.as_dict()), 201

# ---------- Get order by ID ----------
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    o = Order.get_by_order_id(order_id)
    if not o:
        return jsonify({}), 404
    return jsonify(o.as_dict())

# ---------- Swagger UI ----------
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/docs'                 # URL for Swagger UI
API_URL = '/static/openapi.yaml'      # Path to OpenAPI spec
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Order Service"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ---------- Run server ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)