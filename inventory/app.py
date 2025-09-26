# inventory/app.py
from flask import Flask, request, jsonify, abort
from models import init_db, Product

app = Flask(__name__)
init_db()  # create tables if not exist

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')


@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data or 'sku' not in data or 'name' not in data or 'quantity' not in data:
        abort(400, 'sku, name and quantity required')
    sku = data['sku']
    if Product.get_by_sku(sku):
        abort(409, 'Product already exists')
    product = Product.create(
        sku,
        data['name'],
        int(data['quantity']),
        float(data.get('price', 0.0))
    )
    return jsonify(product.as_dict()), 201


@app.route('/products/<sku>', methods=['PUT'])
def update_product(sku):
    data = request.get_json() or {}
    product = Product.get_by_sku(sku)
    if not product:
        abort(404)
    if 'quantity' in data:
        product.quantity = int(data['quantity'])
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = float(data['price'])
    product.save()
    return jsonify(product.as_dict())


@app.route('/products/<sku>', methods=['GET'])
def get_product(sku):
    product = Product.get_by_sku(sku)
    if not product:
        return jsonify({}), 404
    return jsonify(product.as_dict())


@app.route('/inventory/check', methods=['POST'])
def check_inventory():
    """Expect: {"items":[{"sku":"A","qty":2}, ...] }"""
    data = request.get_json()
    items = data.get('items', [])
    result = []
    for it in items:
        sku = it['sku']
        qty = int(it['qty'])
        product = Product.get_by_sku(sku)
        available = product.quantity if product else 0
        result.append({
            'sku': sku,
            'requested': qty,
            'available': available,
            'ok': available >= qty
        })
    ok = all(r['ok'] for r in result)
    return jsonify({'ok': ok, 'details': result})


@app.route('/inventory/deduct', methods=['POST'])
def deduct_inventory():
    """
    Deduct quantities after a successful order.
    Expect: {"items":[{"sku":"A101","qty":2}, ...]}
    """
    data = request.get_json()
    if not data or 'items' not in data:
        abort(400, 'items required')

    updated_items = []
    for it in data['items']:
        sku = it['sku']
        qty = int(it['qty'])
        product = Product.get_by_sku(sku)
        if not product:
            return jsonify({"error": f"Product {sku} not found"}), 404
        if product.quantity < qty:
            return jsonify({"error": f"Not enough stock for {sku}"}), 400
        product.quantity -= qty
        product.save()
        updated_items.append({"sku": sku, "new_quantity": product.quantity})

    return jsonify({"ok": True, "updated": updated_items})

from flask_swagger_ui import get_swaggerui_blueprint
import os

# Make sure your openapi.yaml is inside inventory/ directory
@app.route('/openapi.yaml')
def serve_openapi():
    return app.send_static_file('openapi.yaml')

# Setup Swagger UI
SWAGGER_URL = '/docs'
API_URL = '/openapi.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Inventory Service"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)