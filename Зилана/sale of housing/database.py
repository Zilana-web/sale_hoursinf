import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("real_estate.db")
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Таблица пользователей
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'user')) DEFAULT 'user'
            )
            """)

            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                price REAL NOT NULL,
                image TEXT NOT NULL DEFAULT '',
                isAvailable INTEGER NOT NULL DEFAULT 1
            )
            """)

            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                purchase_date datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (property_id) REFERENCES properties (id)
            )
            """)
    def seed_data(self):
        with self.conn:
            self.conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "admin"))
            self.conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user", "password", "user"))
            self.conn.execute("INSERT INTO properties (address, price, image) VALUES (?, ?, ?)", ("123 Main St", 100000, "image1.jpg"))
            self.conn.execute("INSERT INTO properties (address, price, image) VALUES (?, ?, ?)", ("456 Elm St", 200000, "image2.jpg"))
            self.conn.execute("INSERT INTO properties (address, price, image) VALUES (?, ?, ?)", ("789 Oak St", 300000, "image3.jpg"))
    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    def register_user(self, username, password, role="user"):
        try:
            with self.conn:
                self.conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_purchase_history(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT p.address, p.price, p.image, pr.purchase_date
        FROM purchases pr
        INNER JOIN properties p ON pr.property_id = p.id
        WHERE pr.user_id = ?
        """, (user_id,))
        return cursor.fetchall()
