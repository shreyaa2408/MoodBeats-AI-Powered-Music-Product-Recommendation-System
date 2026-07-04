import sqlite3
import re
from flask import Blueprint, current_app, render_template, request, redirect, session, url_for
import os
from flask import request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from flask import flash, get_flashed_messages
from .emotion_detect import detect_emotion




main = Blueprint('main', __name__)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# ✅ Helper function to get consistent DB connection
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../moodbeats.db")
    return sqlite3.connect(db_path, check_same_thread=False)

# ------------------------
# Home Page
# ------------------------
@main.route('/')
def index():
    return render_template('index.html')



# Show login form
@main.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Handle login form submit
@main.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Admin login
    if username == 'admin' and password == 'admin123':
        session['username'] = 'admin'
        session['role'] = 'admin'
        return redirect(url_for('main.admin_dashboard'))


     # User login
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = user[1]  # ✅ Store actual username
        session['user_id'] = user[0]
        session['role'] = 'user'
        return redirect(url_for('main.user_home'))
    
    
    else:
         flash("❌ Invalid credentials. Please try again.")
         return redirect(url_for('main.login_page'))
    



    

#LOGOUT    
@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))







# ------------------------
# Admin Dashboard
# ------------------------
@main.route('/admin')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('main.login_page'))
    return render_template('admin_dashboard.html')


# ------------------------
# User Dashboard
# ------------------------
@main.route('/user')
def user_home():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('main.login_page'))
    return render_template('user_home.html')


# ------------------------
# Sign Up Page (GET)
# ------------------------
@main.route('/signup')
def signup_page():
    return render_template('signup.html')

@main.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    phone = request.form.get('phone').strip()
    dob = request.form.get('dob').strip()

    # Backend validations
    if not username or not password or not phone or not dob:
        flash("❌ All fields are required.", "danger")
        return redirect(url_for('main.signup_page'))

    if not phone.isdigit() or len(phone) != 10:
        flash("❌ Phone number must be 10 digits.", "danger")
        return redirect(url_for('main.signup_page'))

    import re
    strong_password = re.compile(r'^(?=.*[0-9])(?=.*[!@#$%^&*]).{6,}$')
    if not strong_password.match(password):
        flash("❌ Password must include a number and a symbol.", "danger")
        return redirect(url_for('main.signup_page'))

    # Insert into DB
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, phone, dob) VALUES (?, ?, ?, ?)",
                  (username, password, phone, dob))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("❌ Username already exists. Please try another username.", "danger")
        return redirect(url_for('main.signup_page'))
    finally:
        conn.close()

    flash("✅ Signed up successfully!", "success")
    return redirect(url_for('main.login_page'))


# ------------------------
# Mood-based Product Display
# ------------------------
@main.route('/products/<mood>')
def show_products(mood):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, price, image FROM products WHERE mood = ?", (mood,))
    products = c.fetchall()
    conn.close()

    return render_template('products.html', products=products, mood=mood)




# # ------------------------
# # Add to Cart
# # ------------------------
@main.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return "Unauthorized", 401

    user_id = session['user_id']
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    existing = c.fetchone()

    if existing:
        c.execute("UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (existing[0],))
        message = "Item quantity updated"
    else:
        c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))
        message = "Item added to cart"

    conn.commit()
    conn.close()

    # For AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return message, 200
    else:
        flash(message)
        return redirect(url_for('main.view_cart'))




# ------------------------
# View Cart
@main.route("/cart")
def view_cart():
    username = session.get("username")
    if not username:
        return redirect(url_for('main.login'))

    conn = get_db_connection()
    c = conn.cursor()

    # Join cart and users and products tables
    c.execute("""
        SELECT p.name, p.price, c.quantity, (p.price * c.quantity) AS subtotal, p.image, p.id
        FROM cart c
        JOIN users u ON c.user_id = u.id
        JOIN products p ON c.product_id = p.id
        WHERE u.username = ?
    """, (username,))

    cart_items = c.fetchall()
    total = sum(item[3] for item in cart_items)
    conn.close()

    return render_template("cart.html", cart_items=cart_items, total=total)




# View all products & add product form
@main.route('/admin/products', methods=['GET'])
def manage_products():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('manage_products.html', products=products)



# Handle product deletion
@main.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.manage_products'))




#MANAGE USERS
@main.route('/admin/users/manage', methods=['GET'])
def manage_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, phone, dob FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('manage_users.html', users=users)

@main.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('main.manage_users'))


#VIEW USERS 
@main.route('/admin/users', methods=['GET'])
def view_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, phone, dob FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('view_users.html', users=users)





@main.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        mood = request.form['mood']
        image_file = request.files['image']  # file from the form

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)

            # ✅ Build image save path: app/static/images/filename.jpg
            image_folder = os.path.join(current_app.root_path, 'static', 'images')
            os.makedirs(image_folder, exist_ok=True)  # ensure the folder exists

            image_path = os.path.join(image_folder, filename)
            image_file.save(image_path)

            # ✅ Save product to DB
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO products (name, price, image, mood)
                VALUES (?, ?, ?, ?)
            ''', (name, price, filename, mood))
            conn.commit()
            conn.close()

            flash('✅ Product added successfully!')
            return redirect(url_for('main.manage_products'))
        else:
            flash('❌ Invalid image format. Please upload JPG, JPEG, or PNG.')
            return redirect(url_for('main.add_product'))

    return render_template('add_product.html')
    



@main.route("/cart/update/<int:product_id>/<string:action>", methods=["POST"])
def update_quantity(product_id, action):
    username = session.get("username")
    conn = get_db_connection()
    c = conn.cursor()

    # Get the user_id using username
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    if not user:
        conn.close()
        return "User not found"

    user_id = user[0]

    # Check if the item exists
    c.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    row = c.fetchone()

    if not row:
        conn.close()
        return "Item not found in cart"

    current_qty = row[0]

    if action == 'increase':
        c.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    elif action == 'decrease' and current_qty > 1:
        c.execute("UPDATE cart SET quantity = quantity - 1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    elif action == 'decrease' and current_qty == 1:
        # Optional: remove item from cart if quantity goes to 0
        c.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))

    conn.commit()
    conn.close()
    return redirect(url_for('main.view_cart'))


# Remove from cart
@main.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    username = session.get("username")
    if not username:
        return redirect(url_for('main.login'))

    conn = get_db_connection()
    c = conn.cursor()

    # Get user_id from username
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    if user:
        user_id = user[0]
        c.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        conn.commit()

    conn.close()
    return redirect(url_for('main.view_cart'))




@main.route("/checkout")
def checkout():
    if "username" not in session:
        return redirect(url_for("main.login"))

    username = session.get("username")
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return redirect(url_for("main.login"))

    user_id = user[0]

    # Get cart items
    c.execute("""
        SELECT p.name, c.quantity, p.price, p.image
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user_id,))
    cart_items = c.fetchall()

    if not cart_items:
        conn.close()
        return redirect(url_for("main.view_cart"))

    total = sum(item[1] * item[2] for item in cart_items)

    # Insert into orders table
    c.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
    order_id = c.lastrowid

    # Insert into order_items
    for name, quantity, price, image in cart_items:
        c.execute(
            "INSERT INTO order_items (order_id, product_name, quantity, price, image_filename) VALUES (?, ?, ?, ?, ?)",
            (order_id, name, quantity, price, image)
        )

    # Clear the user's cart
    c.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return render_template("checkout.html")




@main.route("/my-orders")
def my_orders():
    if "username" not in session:
        return redirect(url_for("main.login"))

    username = session["username"]
    conn = get_db_connection()
    c = conn.cursor()

    # Get user_id
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "User not found."

    user_id = user[0]

    # Get all orders of the user
    c.execute("SELECT id, total, timestamp FROM orders WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    orders = c.fetchall()

    order_data = []
    for order in orders:
        order_id, total, timestamp = order

        c.execute("""
            SELECT product_name, quantity, price, image_filename
            FROM order_items
            WHERE order_id = ?
        """, (order_id,))
        items_raw = c.fetchall()

        # Convert tuple to dictionary for each item
        items = []
        for item in items_raw:
            items.append({
                "product_name": item[0],
                "quantity": item[1],
                "price": item[2],
                "image_filename": item[3]
            })

        order_data.append({
            "id": order_id,
            "total": total,
            "timestamp": timestamp,
            "items": items
        })

    conn.close()
    return render_template("my_orders.html", orders=order_data)




@main.route('/start-detection')
def emotion_detect_route():
    from .emotion_detect import detect_emotion
    mood = detect_emotion()
    print("Detected mood:", mood)
    return redirect(url_for('main.recommend_by_emotion', mood=mood))




@main.route('/recommend/<mood>')
def recommend_by_emotion(mood):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE mood=?", (mood,))
    products = c.fetchall()
    conn.close()
    return render_template("recommended_products.html", products=products, mood=mood)













