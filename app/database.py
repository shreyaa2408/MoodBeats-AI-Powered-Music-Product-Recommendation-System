import sqlite3
import os

def init_db():
    # Path to DB
    db_path = os.path.join(os.path.dirname(__file__), "../moodbeats.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL
    )''')

    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        image TEXT,
        mood TEXT
    )''')

    # Create cart table
    c.execute('''CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')

    # Create orders table
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    # Create order items table
    c.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        image_filename TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )''')

    # Insert default products if none exist
        # Insert default products if none exist
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        image_dir = os.path.join(os.path.dirname(__file__), "static/images")

        products = [
            ("Headphones", 999, "headphones.jpg", "happy"),
            ("Scented Candle", 499, "candle.jpg", "calm"),
            ("Soothing Tea Pack", 399, "tea.jpg", "calm"),
            ("Relaxing Bath Bombs", 599, "bathbomb.jpg", "calm"),
            ("Coffee Mug", 299, "sadvibesmug.jpg", "sad"),
        ]

        valid_products = []
        for name, price, image, mood in products:
            image_path = os.path.join(image_dir, image)
            if os.path.exists(image_path):
                valid_products.append((name, price, image, mood))
            else:
                print(f"⚠️ Skipped missing image: {image}")

        if valid_products:
            c.executemany("INSERT INTO products (name, price, image, mood) VALUES (?, ?, ?, ?)", valid_products)
            print("✅ Inserted products with available images.")
        else:
            print("❌ No product images found. Nothing inserted.")

      
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

# Run the function if script is run directly
if __name__ == "__main__":
    init_db()
