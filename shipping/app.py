# shipping/app.py
from flask import Flask, request, jsonify, abort
from models import init_db, Shipping
import requests

app = Flask(__name__)
init_db()

ORDER_URL = "http://127.0.0.1:5002"  # Order service URL

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')

@app.route('/shipping/<order_id>', methods=['GET'])
def get_shipping(order_id):
    s = Shipping.get_by_order_id(order_id)
    if not s:
        return jsonify({}), 404
    return jsonify(s.as_dict())

@app.route('/shipping/process', methods=['POST'])
def process_shipping():
    data = request.get_json()
    if not data or 'order_id' not in data:
        abort(400, "order_id required")
    
    order_id = data['order_id']
    # Check if shipping already exists
    if Shipping.get_by_order_id(order_id):
        return jsonify({"message":"Shipping already created"}), 400
    
    # Get order details
    resp = requests.get(f"{ORDER_URL}/orders/{order_id}")
    order = resp.json()
    if not order:
        return jsonify({"error":"Order not found"}), 404
    
    # Create shipping
    shipping = Shipping.create(order_id, order['items'])
    return jsonify(shipping.as_dict()), 201

import threading

def consume_orders():
    import pika
    import json
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='order_queue')

    def callback(ch, method, properties, body):
        order = json.loads(body)
        print(f"New order received: {order}")
        # Here you can create shipping entry in DB
        # For demo, just printing
    channel.basic_consume(queue='order_queue', on_message_callback=callback, auto_ack=True)
    print("Waiting for orders...")
    channel.start_consuming()

# Run consumer in a separate thread
threading.Thread(target=consume_orders, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)