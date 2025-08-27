import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='pharmacy.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        # Users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            store_id INTEGER,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Stores table (for whitelabel/multi-store)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT,
            logo_path TEXT,
            gst_number TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Medicines table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            manufacturer TEXT,
            barcode TEXT UNIQUE,
            price REAL NOT NULL,
            cost_price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            expiry_date DATE,
            prescription_required BOOLEAN DEFAULT 0,
            store_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (store_id) REFERENCES stores(id)
        )
        ''')
        
        # Customers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Suppliers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            gst_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Sales table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            store_id INTEGER,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'Completed',
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (store_id) REFERENCES stores(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Sale Items table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            medicine_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            discount REAL DEFAULT 0,
            FOREIGN KEY (sale_id) REFERENCES sales(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
        ''')
        
        # Purchases table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            supplier_id INTEGER,
            store_id INTEGER,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (store_id) REFERENCES stores(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Purchase Items table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER,
            medicine_id INTEGER,
            quantity INTEGER NOT NULL,
            cost_price REAL NOT NULL,
            expiry_date DATE,
            batch_number TEXT,
            FOREIGN KEY (purchase_id) REFERENCES purchases(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
        ''')
        
        # Prescriptions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            doctor_name TEXT,
            diagnosis TEXT,
            prescription_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        ''')
        
        # Prescription Items table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescription_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER,
            medicine_id INTEGER,
            dosage TEXT,
            duration TEXT,
            instructions TEXT,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
        ''')
        
        # Audit Log table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            table_name TEXT,
            record_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create default store and admin user if they don't exist
        self.cursor.execute("SELECT * FROM stores")
        if self.cursor.fetchone() is None:
            self.cursor.execute('''
            INSERT INTO stores (name, address, phone, email)
            VALUES (?, ?, ?, ?)
            ''', ("Main Pharmacy", "123 Health St, Medical City", "555-1234", "info@pharmacy.com"))
            
        self.cursor.execute("SELECT * FROM users WHERE role='admin'")
        if self.cursor.fetchone() is None:
            from hashlib import sha256
            default_password = sha256("admin123".encode()).hexdigest()
            self.cursor.execute('''
            INSERT INTO users (username, password, role, name, email, store_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ("admin", default_password, "admin", "System Administrator", "admin@pharmacy.com", 1))
            
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def execute_update(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def backup_database(self, backup_path=None):
        if not backup_path:
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_conn = sqlite3.connect(backup_path)
        self.conn.backup(backup_conn)
        backup_conn.close()
        return backup_path
    
    def restore_database(self, backup_path):
        if os.path.exists(backup_path):
            # Close current connection
            self.close()
            
            # Replace current database with backup
            if os.path.exists(self.db_name):
                os.remove(self.db_name)
            os.rename(backup_path, self.db_name)
            
            # Reconnect
            self.connect()
            return True
        return False