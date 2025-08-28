import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import uuid
from datetime import datetime
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sys
import subprocess

# --------- DATABASE CLASS ---------
class Database:
    def __init__(self, db_file='pos.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
    
    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS customers(
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    phone TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS medicines(
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    price REAL, 
                    stock_quantity INTEGER, 
                    store_id INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sales(
                    id INTEGER PRIMARY KEY, 
                    invoice_number TEXT, 
                    customer_id INTEGER, 
                    store_id INTEGER, 
                    user_id INTEGER, 
                    total_amount REAL, 
                    discount_amount REAL, 
                    tax_amount REAL, 
                    payment_method TEXT, 
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sale_items(
                    id INTEGER PRIMARY KEY, 
                    sale_id INTEGER, 
                    medicine_id INTEGER, 
                    quantity INTEGER, 
                    price REAL, 
                    discount REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY, 
                    name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS stores(
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    address TEXT, 
                    phone TEXT, 
                    email TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log(
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, 
                    action TEXT, 
                    table_name TEXT, 
                    record_id INTEGER, 
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()
    
    def execute_query(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    
    def execute_update(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        self.conn.commit()
        return c.lastrowid

# --------- PDF GENERATOR FUNCTION ---------
def generate_invoice(sale, sale_items):
    invoice_file = f"Invoice_{sale[1]}.pdf"
    c = canvas.Canvas(invoice_file, pagesize=A4)
    width, height = A4
    
    # Store Info
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, f"{sale[11]}")  # Store Name
    c.setFont("Helvetica", 10)
    c.drawString(50, height-70, f"{sale[12]}")  # Store Address
    c.drawString(50, height-85, f"Phone: {sale[13]} | Email: {sale[14]}")
    
    # Invoice Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, height-50, f"INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(400, height-70, f"Invoice #: {sale[1]}")
    c.drawString(400, height-85, f"Date: {sale[9]}")
    
    # Customer Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height-120, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height-135, f"{sale[2] or 'Walk-in'}")
    c.drawString(50, height-150, f"Phone: {sale[3] or ''}")
    
    # Table Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height-180, "Item")
    c.drawString(250, height-180, "Qty")
    c.drawString(300, height-180, "Price")
    c.drawString(400, height-180, "Total")
    
    y = height - 200
    c.setFont("Helvetica", 10)
    for item in sale_items:
        c.drawString(50, y, f"{item[0]}")
        c.drawString(250, y, str(item[1]))
        c.drawString(300, y, f"${item[2]:.2f}")
        c.drawString(400, y, f"${item[3]:.2f}")
        y -= 20
    
    # Summary
    y -= 10
    c.drawString(300, y, f"Subtotal: ${sum([i[3] for i in sale_items]):.2f}")
    y -= 15
    c.drawString(300, y, f"Discount: ${sale[6]:.2f}")
    y -= 15
    c.drawString(300, y, f"Tax: ${sale[7]:.2f}")
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, f"Total: ${sale[5]:.2f}")
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for your purchase!")
    c.save()
    return invoice_file

# --------- SALES CLASS ---------
class Sales:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.sale_items = []
        self.subtotal = self.discount = self.tax = self.total = 0.0
        self.sales_frame = ttk.Frame(parent, padding=10)
        self.sales_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.sales_frame, text="Pharmacy POS System", font=('Arial', 16, 'bold')).pack(pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.sales_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.new_sale_tab = ttk.Frame(notebook, padding=5)
        self.history_tab = ttk.Frame(notebook, padding=5)
        notebook.add(self.new_sale_tab, text="New Sale")
        notebook.add(self.history_tab, text="Sales History")
        
        # Setup tabs
        self.setup_new_sale_tab()
        self.setup_history_tab()
        
        # Add sample data if needed
        self.add_sample_data()
    
    def add_sample_data(self):
        # Add sample customers if none exist
        if not self.db.execute_query("SELECT * FROM customers"):
            self.db.execute_update("INSERT INTO customers (name, phone) VALUES (?, ?)", 
                                 ("John Doe", "555-1234"))
            self.db.execute_update("INSERT INTO customers (name, phone) VALUES (?, ?)", 
                                 ("Jane Smith", "555-5678"))
        
        # Add sample medicines if none exist
        if not self.db.execute_query("SELECT * FROM medicines"):
            self.db.execute_update("INSERT INTO medicines (name, price, stock_quantity, store_id) VALUES (?, ?, ?, ?)", 
                                 ("Paracetamol", 5.99, 100, self.user['store_id']))
            self.db.execute_update("INSERT INTO medicines (name, price, stock_quantity, store_id) VALUES (?, ?, ?, ?)", 
                                 ("Ibuprofen", 7.49, 50, self.user['store_id']))
            self.db.execute_update("INSERT INTO medicines (name, price, stock_quantity, store_id) VALUES (?, ?, ?, ?)", 
                                 ("Amoxicillin", 12.99, 30, self.user['store_id']))
    
    # ---- NEW SALE TAB ----
    def setup_new_sale_tab(self):
        # Customer Selection Frame
        customer_frame = ttk.LabelFrame(self.new_sale_tab, text="Customer Information")
        customer_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(customer_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=25)
        self.customer_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Refresh customer list
        self.refresh_customer_list()
        
        # Medicine Selection Frame
        medicine_frame = ttk.LabelFrame(self.new_sale_tab, text="Medicine Selection")
        medicine_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(medicine_frame, text="Medicine:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(medicine_frame, textvariable=self.medicine_var, width=25)
        self.medicine_combo.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Refresh medicine list
        self.refresh_medicine_list()
        
        ttk.Label(medicine_frame, text="Qty:").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(medicine_frame, textvariable=self.qty_var, width=5).grid(row=0, column=3, padx=5, sticky=tk.W)
        
        ttk.Button(medicine_frame, text="Add to Sale", command=self.add_item).grid(row=0, column=4, padx=5, pady=2)
        
        # Sale Items Table
        items_frame = ttk.LabelFrame(self.new_sale_tab, text="Sale Items")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(items_frame, columns=("ID", "Name", "Price", "Qty", "Total"), show="headings")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Payment and Totals Frame
        payment_frame = ttk.LabelFrame(self.new_sale_tab, text="Payment & Totals")
        payment_frame.pack(fill=tk.X, pady=5)
        
        # Totals
        self.sub_var = tk.StringVar(value="$0.00")
        self.discount_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        
        ttk.Label(payment_frame, text="Subtotal:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(payment_frame, textvariable=self.sub_var).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(payment_frame, text="Discount:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        discount_entry = ttk.Entry(payment_frame, textvariable=self.discount_var, width=8)
        discount_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        discount_entry.bind("<KeyRelease>", lambda e: self.update_totals())
        
        ttk.Label(payment_frame, text="Tax:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(payment_frame, textvariable=self.tax_var).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(payment_frame, text="Total:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Label(payment_frame, textvariable=self.total_var, font=('Arial', 10, 'bold')).grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Payment Method
        ttk.Label(payment_frame, text="Payment Method:").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.pay_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.pay_var, 
                                   values=["Cash", "Card", "Insurance", "Credit"], width=10)
        payment_combo.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(payment_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Complete Sale", command=self.complete_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel Sale", command=self.cancel_sale).pack(side=tk.LEFT, padx=5)
    
    def refresh_customer_list(self):
        customers = self.db.execute_query("SELECT id, name FROM customers")
        self.customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in customers]
    
    def refresh_medicine_list(self):
        meds = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id=? AND stock_quantity>0", 
                                   (self.user['store_id'],))
        self.medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in meds]
    
    def add_item(self):
        med_text = self.medicine_var.get()
        if not med_text:
            messagebox.showerror("Error", "Please select a medicine")
            return
        
        try:
            med_id = int(med_text.split(' - ')[0])
            qty = int(self.qty_var.get())
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid medicine selection or quantity")
            return
        
        med = self.db.execute_query("SELECT id, name, price, stock_quantity FROM medicines WHERE id=?", (med_id,))
        if not med:
            messagebox.showerror("Error", "Medicine not found")
            return
        
        med = med[0]
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0")
            return
        
        if qty > med[3]:
            messagebox.showerror("Error", f"Not enough stock. Available: {med[3]}")
            return
        
        # Add item to sale
        self.sale_items.append({
            'id': med[0],
            'name': med[1],
            'price': med[2],
            'qty': qty
        })
        
        # Add to treeview
        self.tree.insert("", tk.END, values=(
            med[0],
            med[1],
            f"${med[2]:.2f}",
            qty,
            f"${med[2] * qty:.2f}"
        ))
        
        # Update totals
        self.update_totals()
        
        # Reset medicine selection
        self.medicine_var.set("")
        self.qty_var.set("1")
    
    def update_totals(self):
        self.subtotal = sum([item['price'] * item['qty'] for item in self.sale_items])
        
        try:
            self.discount = float(self.discount_var.get().replace('$', ''))
        except ValueError:
            self.discount = 0.0
        
        self.tax = (self.subtotal - self.discount) * 0.1  # 10% tax
        self.total = self.subtotal - self.discount + self.tax
        
        # Update display
        self.sub_var.set(f"${self.subtotal:.2f}")
        self.tax_var.set(f"${self.tax:.2f}")
        self.total_var.set(f"${self.total:.2f}")
    
    def cancel_sale(self):
        if self.sale_items and messagebox.askyesno("Confirm", "Cancel this sale?"):
            self.sale_items = []
            self.subtotal = self.discount = self.tax = self.total = 0.0
            
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Reset form
            self.customer_var.set("")
            self.medicine_var.set("")
            self.qty_var.set("1")
            self.discount_var.set("$0.00")
            self.pay_var.set("Cash")
            self.update_totals()
    
    def complete_sale(self):
        if not self.sale_items:
            messagebox.showerror("Error", "No items in sale")
            return
        
        # Get customer ID
        cust_id = None
        if self.customer_var.get():
            try:
                cust_id = int(self.customer_var.get().split(' - ')[0])
            except (ValueError, IndexError):
                pass
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        try:
            # Begin transaction
            self.db.conn.execute("BEGIN TRANSACTION")
            
            # Insert sale record
            sale_id = self.db.execute_update(
                '''INSERT INTO sales(
                    invoice_number, customer_id, store_id, user_id, 
                    total_amount, discount_amount, tax_amount, payment_method) 
                VALUES(?,?,?,?,?,?,?,?)''',
                (invoice_number, cust_id, self.user['store_id'], self.user['id'], 
                 self.total, self.discount, self.tax, self.pay_var.get())
            )
            
            # Insert sale items and update stock
            for item in self.sale_items:
                # Insert sale item
                self.db.execute_update(
                    '''INSERT INTO sale_items(
                        sale_id, medicine_id, quantity, price, discount) 
                    VALUES(?,?,?,?,?)''',
                    (sale_id, item['id'], item['qty'], item['price'], 0)
                )
                
                # Update medicine stock
                self.db.execute_update(
                    '''UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?''',
                    (item['qty'], item['id'])
                )
            
            # Commit transaction
            self.db.conn.commit()
            
            # Generate and open invoice
            sale = self.db.execute_query('''
                SELECT s.id, s.invoice_number, 
                    COALESCE(c.name, 'Walk-in'), COALESCE(c.phone, ''), 
                    s.total_amount, s.discount_amount, s.tax_amount, s.payment_method, 
                    s.sale_date, COALESCE(u.name, 'Admin'),
                    COALESCE(st.name, 'Store'), COALESCE(st.address, ''), COALESCE(st.phone,''), COALESCE(st.email,'')
                FROM sales s 
                LEFT JOIN customers c ON s.customer_id = c.id 
                LEFT JOIN users u ON s.user_id = u.id 
                LEFT JOIN stores st ON s.store_id = st.id 
                WHERE s.id = ?
            ''', (sale_id,))
            
            if not sale:
                messagebox.showerror("Error", "Sale not found after creation")
                return
            
            sale = sale[0]
            
            # Get sale items
            items = self.db.execute_query('''
                SELECT m.name, si.quantity, si.price, (si.quantity * si.price) 
                FROM sale_items si 
                JOIN medicines m ON si.medicine_id = m.id 
                WHERE si.sale_id = ?
            ''', (sale_id,))
            
            # Generate PDF invoice
            invoice_file = generate_invoice(sale, items)
            
            # Open invoice based on OS
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(invoice_file)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', invoice_file])
                else:  # Linux
                    subprocess.call(['xdg-open', invoice_file])
            except Exception as e:
                messagebox.showwarning("Warning", f"Invoice created but couldn't open: {str(e)}")
            
            # Show success message
            messagebox.showinfo("Sale Completed", f"Sale completed successfully!\nInvoice: {invoice_file}")
            
            # Reset sale
            self.cancel_sale()
            
            # Refresh medicine list to show updated stock
            self.refresh_medicine_list()
            
        except Exception as e:
            # Rollback transaction on error
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
    
    # ---- SALES HISTORY TAB ----
    def setup_history_tab(self):
        # Search and export frame
        search_frame = ttk.Frame(self.history_tab)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_history)
        ttk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        
        # Sales history treeview
        history_frame = ttk.LabelFrame(self.history_tab, text="Sales History")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_tree = ttk.Treeview(history_frame, columns=("ID", "Invoice", "Customer", "Amount", "Date", "Staff"), show="headings")
        for col in self.history_tree['columns']:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        # Add scrollbar
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=history_scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load sales history
        self.load_history()
    
    def load_history(self):
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get sales data
        sales = self.db.execute_query('''
            SELECT s.id, s.invoice_number, c.name, s.total_amount, s.sale_date, u.name 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id 
            LEFT JOIN users u ON s.user_id = u.id 
            ORDER BY s.sale_date DESC
        ''')
        
        # Add to treeview
        for sale in sales:
            self.history_tree.insert("", tk.END, values=sale)
    
    def filter_history(self, *args):
        # Get search term
        query = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get all sales
        sales = self.db.execute_query('''
            SELECT s.id, s.invoice_number, c.name, s.total_amount, s.sale_date, u.name 
            FROM sales s 
            LEFT JOIN customers c ON s.customer_id = c.id 
            LEFT JOIN users u ON s.user_id = u.id 
            ORDER BY s.sale_date DESC
        ''')
        
        # Filter and add matching sales
        for sale in sales:
            if query in str(sale).lower():
                self.history_tree.insert("", tk.END, values=sale)
    
    def export_csv(self):
        if not self.history_tree.get_children():
            messagebox.showerror("Error", "No sales data to export")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers
                headers = [self.history_tree.heading(col)['text'] for col in self.history_tree['columns']]
                writer.writerow(headers)
                
                # Write data
                for item in self.history_tree.get_children():
                    writer.writerow(self.history_tree.item(item)['values'])
            
            messagebox.showinfo("Export Successful", f"Sales data exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data:\n{str(e)}")

# --------- MAIN APPLICATION ---------
if __name__ == "__main__":
    # Initialize database
    db = Database()
    
    # Mock user
    user = {'id': 1, 'name': 'Admin', 'store_id': 1}
    
    # Add dummy store if not exists
    if not db.execute_query("SELECT * FROM stores WHERE id=1"):
        db.execute_update(
            "INSERT INTO stores(id, name, address, phone, email) VALUES(?,?,?,?,?)", 
            (1, "My Pharmacy", "123 Main St", "999-999-9999", "contact@mypharmacy.com")
        )
    
    # Create main window
    root = tk.Tk()
    root.title("Pharmacy POS System")
    root.geometry("900x600")
    root.minsize(800, 500)
    
    # Create sales interface
    app = Sales(root, user, db)
    
    # Start application
    root.mainloop()