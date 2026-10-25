# app.py - BargainHub Backend Server v2.0
# Full REST API with real functionality!

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create Flask app
app = Flask(__name__)
CORS(app)

# ==========================================
# TEMPORARY IN-MEMORY DATABASE
# (We'll connect to real database in next phase)
# ==========================================

users = []  # Store registered users
products = [
    {'id': 1, 'name': 'Wireless Earbuds Pro', 'price': 3999, 'originalPrice': 9999, 'discount': 60, 'category': 'electronics', 'stock': 150, 'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400', 'description': 'Premium sound with ANC'},
    {'id': 2, 'name': 'Smart Watch Ultra', 'price': 4999, 'originalPrice': 12999, 'discount': 62, 'category': 'electronics', 'stock': 80, 'image': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400', 'description': 'Health tracking watch'},
    {'id': 3, 'name': 'Premium Running Shoes', 'price': 2299, 'originalPrice': 5499, 'discount': 58, 'category': 'fashion', 'stock': 200, 'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400', 'description': 'Lightweight and breathable'},
    {'id': 4, 'name': 'iPhone 15 Pro Max', 'price': 129999, 'originalPrice': 149999, 'discount': 13, 'category': 'mobile', 'stock': 45, 'image': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400', 'description': 'Titanium build, A17 Pro chip'},
    {'id': 5, 'name': 'Denim Jacket Classic', 'price': 1799, 'originalPrice': 3999, 'discount': 55, 'category': 'fashion', 'stock': 100, 'image': 'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=400', 'description': '100% premium cotton'}
]
orders = []

# Auto-increment IDs
next_user_id = 1
next_product_id = 6  # Start after existing products
next_order_id = 1

# ==========================================
# HOMEPAGE ROUTE
# ==========================================

@app.route('/')
def home():
    """Welcome endpoint - shows all available APIs"""
    return jsonify({
        'message': 'Welcome to BargainHub Backend API! 🎉',
        'version': '2.0.0',
        'endpoints': {
            'auth': {
                'register': 'POST /api/register',
                'login': 'POST /api/login'
            },
            'products': {
                'get_all': 'GET /api/products',
                'get_one': 'GET /api/products/<id>',
                'create': 'POST /api/products',
                'update': 'PUT /api/products/<id>',
                'delete': 'DELETE /api/products/<id>'
            },
            'orders': {
                'get_all': 'GET /api/orders',
                'create': 'POST /api/orders'
            }
        }
    })

# ==========================================
# AUTHENTICATION APIs
# ==========================================

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user
    Expects JSON: { "name": "...", "email": "...", "phone": "...", "password": "..." }
    """
    global next_user_id
    
    # Get JSON data from request
    data = request.get_json()
    
    # Validation - check required fields
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Check if email already exists
    for user in users:
        if user['email'] == data['email']:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Hash the password (NEVER store plain text passwords!)
    hashed_password = generate_password_hash(data['password'])
    
    # Create new user
    new_user = {
        'id': next_user_id,
        'name': data['name'],
        'email': data['email'],
        'phone': data.get('phone', ''),
        'password': hashed_password,  # stored hashed
        'created_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    users.append(new_user)
    next_user_id += 1
    
    # Return success (don't send password back!)
    return jsonify({
        'success': True,
        'message': 'Registration successful!',
        'user': {
            'id': new_user['id'],
            'name': new_user['name'],
            'email': new_user['email'],
            'phone': new_user['phone']
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login user
    Expects JSON: { "email": "...", "password": "..." }
    """
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    # Find user by email
    user = next((u for u in users if u['email'] == data['email']), None)
    
    if not user:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    
    # Check password
    if not check_password_hash(user['password'], data['password']):
        return jsonify({'success': False, 'message': 'Incorrect password'}), 401
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users (for merchant/admin)"""
    # Return users WITHOUT passwords!
    safe_users = [
        {'id': u['id'], 'name': u['name'], 'email': u['email'], 
         'phone': u['phone'], 'created_at': u['created_at'], 'status': u['status']}
        for u in users
    ]
    return jsonify({'users': safe_users, 'total': len(safe_users)})

# ==========================================
# PRODUCTS APIs
# ==========================================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products, with optional category filter"""
    category = request.args.get('category')  # ?category=electronics
    
    if category:
        filtered = [p for p in products if p['category'] == category]
        return jsonify({'products': filtered, 'total': len(filtered)})
    
    return jsonify({'products': products, 'total': len(products)})

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    return jsonify(product)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add new product (merchant)"""
    global next_product_id
    
    data = request.get_json()
    
    if not data.get('name') or not data.get('price'):
        return jsonify({'success': False, 'message': 'Name and price required'}), 400
    
    new_product = {
        'id': next_product_id,
        'name': data['name'],
        'price': data['price'],
        'originalPrice': data.get('originalPrice', data['price']),
        'discount': data.get('discount', 0),
        'category': data.get('category', 'general'),
        'stock': data.get('stock', 0),
        'image': data.get('image', ''),
        'description': data.get('description', '')
    }
    
    products.append(new_product)
    next_product_id += 1
    
    return jsonify({'success': True, 'message': 'Product added!', 'product': new_product}), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product (merchant)"""
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    data = request.get_json()
    
    # Update only the fields provided
    product.update(data)
    
    return jsonify({'success': True, 'message': 'Product updated!', 'product': product})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product (merchant)"""
    global products
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    products = [p for p in products if p['id'] != product_id]
    
    return jsonify({'success': True, 'message': 'Product deleted!'})

# ==========================================
# ORDERS APIs
# ==========================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    return jsonify({'orders': orders, 'total': len(orders)})

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Place new order"""
    global next_order_id
    
    data = request.get_json()
    
    if not data.get('items') or not data.get('total'):
        return jsonify({'success': False, 'message': 'Items and total required'}), 400
    
    new_order = {
        'id': next_order_id,
        'user_id': data.get('user_id'),
        'user_email': data.get('user_email', ''),
        'items': data['items'],
        'total': data['total'],
        'address': data.get('address', {}),
        'payment_method': data.get('payment_method', 'COD'),
        'status': 'Confirmed',
        'created_at': datetime.now().isoformat()
    }
    
    orders.append(new_order)
    next_order_id += 1
    
    return jsonify({'success': True, 'message': 'Order placed!', 'order': new_order}), 201

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 BargainHub Backend API v2.0')
    print('📡 Server: http://localhost:5000')
    print('📚 API Docs: http://localhost:5000/')
    print('🛑 Press CTRL+C to stop')
    print('=' * 60)
    app.run(debug=True, port=5000)