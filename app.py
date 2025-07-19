from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
DATA_FILE = 'inventory.json'

# Load or initialize inventory
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        inventory = json.load(f)
else:
    inventory = []

# Auto-increment ID
next_id = max([item['id'] for item in inventory], default=0) + 1

# Save to file
def save_to_file():
    with open(DATA_FILE, 'w') as f:
        json.dump(inventory, f, indent=4)

# Serve HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

# API endpoints
@app.route('/api/items', methods=['POST'])
def add_item():
    global next_id
    data = request.get_json()
    if not data or 'name' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing 'name' or 'quantity'"}), 400
    item = {'id': next_id, 'name': data['name'], 'quantity': data['quantity']}
    inventory.append(item)
    next_id += 1
    save_to_file()
    return jsonify(item), 201

@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(inventory)

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    for item in inventory:
        if item['id'] == item_id:
            return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    for item in inventory:
        if item['id'] == item_id:
            item['name'] = data.get('name', item['name'])
            item['quantity'] = data.get('quantity', item['quantity'])
            save_to_file()
            return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global inventory
    inventory = [item for item in inventory if item['id'] != item_id]
    save_to_file()
    return jsonify({'message': 'Item deleted successfully'})

@app.route('/api/items/all', methods=['DELETE'])
def delete_all_items():
    global inventory
    inventory = []
    save_to_file()
    return jsonify({'message': 'All items deleted.'})

@app.route('/api/items/search')
def search_item():
    name_query = request.args.get('name', '').lower()
    results = [item for item in inventory if name_query in item['name'].lower()]
    return jsonify(results)

@app.route('/api/download', methods=['GET'])
def download_inventory():
    return send_file(DATA_FILE, as_attachment=True)

@app.route('/api/items/total', methods=['GET'])
def get_total_quantity():
    total = sum(item['quantity'] for item in inventory)
    return jsonify({'total_quantity': total})

if __name__ == '__main__':
    app.run(debug=True)
