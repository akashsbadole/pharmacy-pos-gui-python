import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
import uuid

class Purchases:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create purchases frame
        self.purchases_frame = ttk.Frame(parent, padding=20)
        self.purchases_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.purchases_frame, text="Purchase Management", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.purchases_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # New Purchase tab
        new_purchase_tab = ttk.Frame(notebook, padding=10)
        notebook.add(new_purchase_tab, text="New Purchase")
        
        # Purchase History tab
        history_tab = ttk.Frame(notebook, padding=10)
        notebook.add(history_tab, text="Purchase History")
        
        # Setup New Purchase tab
        self.setup_new_purchase_tab(new_purchase_tab)
        
        # Setup Purchase History tab
        self.setup_history_tab(history_tab)
    
    def setup_new_purchase_tab(self, parent):
        # Supplier section
        supplier_frame = ttk.LabelFrame(parent, text="Supplier Information", padding=10)
        supplier_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(supplier_frame, text="Supplier:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(supplier_frame, textvariable=self.supplier_var, width=30)
        self.supplier_combo.grid(row=0, column=1, pady=5, padx=5)
        
        # Get suppliers
        suppliers = self.db.execute_query("SELECT id, name FROM suppliers")
        self.supplier_combo['values'] = [f"{s[0]} - {s[1]}" for s in suppliers]
        
        ttk.Label(supplier_frame, text="Invoice Date:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(supplier_frame, textvariable=self.date_var, width=30)
        date_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(supplier_frame, text="Invoice Number:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.invoice_var = tk.StringVar()
        invoice_entry = ttk.Entry(supplier_frame, textvariable=self.invoice_var, width=30)
        invoice_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Medicine section
        medicine_frame = ttk.LabelFrame(parent, text="Medicine Selection", padding=10)
        medicine_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(medicine_frame, text="Medicine:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(medicine_frame, textvariable=self.medicine_var, width=30)
        self.medicine_combo.grid(row=0, column=1, pady=5, padx=5)
        
        # Get medicines
        medicines = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id = ?", (self.user['store_id'],))
        self.medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        ttk.Label(medicine_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(medicine_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(medicine_frame, text="Cost Price ($):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.cost_var = tk.StringVar()
        self.cost_entry = ttk.Entry(medicine_frame, textvariable=self.cost_var, width=10)
        self.cost_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(medicine_frame, text="Expiry Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.expiry_var = tk.StringVar()
        self.expiry_entry = ttk.Entry(medicine_frame, textvariable=self.expiry_var, width=15)
        self.expiry_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(medicine_frame, text="Batch Number:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.batch_var = tk.StringVar()
        self.batch_entry = ttk.Entry(medicine_frame, textvariable=self.batch_var, width=15)
        self.batch_entry.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        add_btn = ttk.Button(medicine_frame, text="Add to Purchase", command=self.add_medicine_to_purchase)
        add_btn.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Purchase items table
        items_frame = ttk.LabelFrame(parent, text="Purchase Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for purchase items
        columns = ("ID", "Name", "Cost", "Quantity", "Total", "Expiry", "Batch")
        self.purchase_items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        for col in columns:
            self.purchase_items_tree.heading(col, text=col)
            self.purchase_items_tree.column(col, width=70)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.purchase_items_tree.yview)
        self.purchase_items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchase_items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Payment section
        payment_frame = ttk.LabelFrame(parent, text="Purchase Details", padding=10)
        payment_frame.pack(fill=tk.X, pady=10)
        
        # Summary
        summary_frame = ttk.Frame(payment_frame)
        summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.subtotal_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        
        ttk.Label(summary_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Label(summary_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky=tk.E, pady=5, padx=5)
        
        ttk.Label(summary_frame, text="Total:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Label(summary_frame, textvariable=self.total_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.E, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        complete_btn = ttk.Button(button_frame, text="Complete Purchase", command=self.complete_purchase)
        complete_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel Purchase", command=self.cancel_purchase)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Initialize purchase data
        self.purchase_items = []
        self.subtotal = 0.0
        self.total = 0.0
    
    def setup_history_tab(self, parent):
        # Search and filter section
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_purchase_history)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Date From:").pack(side=tk.LEFT, padx=5)
        self.date_from_var = tk.StringVar()
        date_from_entry = ttk.Entry(search_frame, textvariable=self.date_from_var, width=10)
        date_from_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.date_to_var = tk.StringVar()
        date_to_entry = ttk.Entry(search_frame, textvariable=self.date_to_var, width=10)
        date_to_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        view_btn = ttk.Button(buttons_frame, text="View Details", command=self.view_purchase_details)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(buttons_frame, text="Export to CSV", command=self.export_purchases_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Purchase history table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for purchase history
        columns = ("ID", "Invoice #", "Supplier", "Amount", "Date", "Staff")
        self.purchase_history_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.purchase_history_tree.heading(col, text=col)
            self.purchase_history_tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.purchase_history_tree.yview)
        self.purchase_history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchase_history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load purchase history
        self.load_purchase_history()
        
        # Bind double-click event
        self.purchase_history_tree.bind("<Double-1>", self.on_purchase_double_click)
    
    def load_purchase_history(self):
        # Clear existing items
        for item in self.purchase_history_tree.get_children():
            self.purchase_history_tree.delete(item)
        
        # Get purchase data
        purchases = self.db.execute_query('''
        SELECT p.id, p.invoice_number, s.name, p.total_amount, p.purchase_date, u.name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.store_id = ?
        ORDER BY p.purchase_date DESC
        LIMIT 100
        ''', (self.user['store_id'],))
        
        for purchase in purchases:
            self.purchase_history_tree.insert("", tk.END, values=(
                purchase[0],  # ID
                purchase[1],  # Invoice #
                purchase[2] or "Unknown",  # Supplier
                f"${purchase[3]:.2f}",  # Amount
                purchase[4].strftime('%Y-%m-%d'),  # Date
                purchase[5]  # Staff
            ))
    
    def filter_purchase_history(self, *args):
        search_term = self.search_var.get().lower()
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()
        
        # Clear existing items
        for item in self.purchase_history_tree.get_children():
            self.purchase_history_tree.delete(item)
        
        # Build query
        query = '''
        SELECT p.id, p.invoice_number, s.name, p.total_amount, p.purchase_date, u.name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.store_id = ?
        '''
        params = [self.user['store_id']]
        
        if search_term:
            query += " AND (LOWER(p.invoice_number) LIKE ? OR LOWER(s.name) LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if date_from:
            query += " AND DATE(p.purchase_date) >= DATE(?)"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(p.purchase_date) <= DATE(?)"
            params.append(date_to)
        
        query += " ORDER BY p.purchase_date DESC"
        
        # Get filtered purchase data
        purchases = self.db.execute_query(query, params)
        
        for purchase in purchases:
            self.purchase_history_tree.insert("", tk.END, values=(
                purchase[0],  # ID
                purchase[1],  # Invoice #
                purchase[2] or "Unknown",  # Supplier
                f"${purchase[3]:.2f}",  # Amount
                purchase[4].strftime('%Y-%m-%d'),  # Date
                purchase[5]  # Staff
            ))
    
    def on_purchase_double_click(self, event):
        self.view_purchase_details()
    
    def view_purchase_details(self):
        # Get selected purchase
        selected = self.purchase_history_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a purchase to view")
            return
        
        item = self.purchase_history_tree.item(selected[0])
        purchase_id = item['values'][0]
        
        # Get purchase details
        purchase = self.db.execute_query('''
        SELECT p.id, p.invoice_number, s.name, s.phone, p.total_amount, p.purchase_date, u.name
        FROM purchases p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
        ''', (purchase_id,))
        
        if not purchase:
            messagebox.showerror("Error", "Purchase not found")
            return
        
        purchase = purchase[0]
        
        # Get purchase items
        purchase_items = self.db.execute_query('''
        SELECT m.name, pi.quantity, pi.cost_price, (pi.quantity * pi.cost_price) as total, 
               pi.expiry_date, pi.batch_number
        FROM purchase_items pi
        JOIN medicines m ON pi.medicine_id = m.id
        WHERE pi.purchase_id = ?
        ''', (purchase_id,))
        
        # Create purchase details dialog
        details_dialog = tk.Toplevel(self.parent)
        details_dialog.title(f"Purchase Details - {purchase[1]}")
        details_dialog.geometry("700x500")
        
        # Purchase information
        info_frame = ttk.LabelFrame(details_dialog, text="Purchase Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(info_frame, text=f"Invoice #: {purchase[1]}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Date: {purchase[5].strftime('%Y-%m-%d')}").grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Supplier: {purchase[2] or 'Unknown'}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Phone: {purchase[3] or ''}").grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Staff: {purchase[6]}").grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Purchase items
        items_frame = ttk.LabelFrame(details_dialog, text="Purchase Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Create treeview for purchase items
        columns = ("Name", "Quantity", "Cost", "Total", "Expiry", "Batch")
        items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_tree.yview)
        items_tree.configure(yscrollcommand=scrollbar.set)
        
        items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add items
        subtotal = 0.0
        for item in purchase_items:
            expiry_str = item[4].strftime('%Y-%m-%d') if item[4] else ""
            items_tree.insert("", tk.END, values=(
                item[0],  # Name
                item[1],  # Quantity
                f"${item[2]:.2f}",  # Cost
                f"${item[3]:.2f}",  # Total
                expiry_str,  # Expiry
                item[5] or ""  # Batch
            ))
            subtotal += item[3]
        
        # Summary
        summary_frame = ttk.LabelFrame(details_dialog, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(summary_frame, text=f"Subtotal: ${subtotal:.2f}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(summary_frame, text=f"Total: ${purchase[4]:.2f}", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(details_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        close_btn = ttk.Button(button_frame, text="Close", command=details_dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)
    
    def export_purchases_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Export Purchases CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        "Invoice #", "Supplier", "Date", "Total", "Staff"
                    ])
                    
                    # Get purchases data
                    purchases = self.db.execute_query('''
                    SELECT p.invoice_number, s.name, p.purchase_date, p.total_amount, u.name
                    FROM purchases p
                    LEFT JOIN suppliers s ON p.supplier_id = s.id
                    LEFT JOIN users u ON p.user_id = u.id
                    WHERE p.store_id = ?
                    ORDER BY p.purchase_date DESC
                    ''', (self.user['store_id'],))
                    
                    # Write data
                    for purchase in purchases:
                        writer.writerow([
                            purchase[0],  # Invoice #
                            purchase[1] or "Unknown",  # Supplier
                            purchase[2].strftime('%Y-%m-%d'),  # Date
                            purchase[3],  # Total
                            purchase[4]  # Staff
                        ])
                    
                    messagebox.showinfo("Export Complete", "Purchases data exported successfully")
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting purchases data: {str(e)}")
    
    def add_medicine_to_purchase(self):
        # Get selected medicine
        medicine_text = self.medicine_var.get()
        if not medicine_text:
            messagebox.showinfo("Selection Required", "Please select a medicine")
            return
        
        try:
            medicine_id = int(medicine_text.split(' - ')[0])
            quantity = int(self.quantity_var.get())
            
            if quantity <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0")
                return
            
            # Get medicine details
            medicine = self.db.execute_query('''
            SELECT id, name, cost_price
            FROM medicines
            WHERE id = ? AND store_id = ?
            ''', (medicine_id, self.user['store_id']))
            
            if not medicine:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            medicine = medicine[0]
            
            # Get cost price
            cost_price = self.cost_var.get()
            if cost_price:
                try:
                    cost_price = float(cost_price)
                except ValueError:
                    messagebox.showerror("Invalid Cost", "Please enter a valid cost price")
                    return
            else:
                cost_price = medicine[2]
            
            # Get expiry date
            expiry_date = None
            if self.expiry_var.get():
                try:
                    expiry_date = datetime.strptime(self.expiry_var.get(), '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Invalid Expiry Date", "Invalid expiry date format. Use YYYY-MM-DD")
                    return
            
            # Add to purchase items
            self.purchase_items.append({
                'id': medicine[0],
                'name': medicine[1],
                'cost_price': cost_price,
                'quantity': quantity,
                'expiry_date': expiry_date,
                'batch_number': self.batch_var.get()
            })
            
            # Update purchase items tree
            expiry_str = expiry_date.strftime('%Y-%m-%d') if expiry_date else ""
            self.purchase_items_tree.insert("", tk.END, values=(
                medicine[0],  # ID
                medicine[1],  # Name
                f"${cost_price:.2f}",  # Cost
                quantity,  # Quantity
                f"${cost_price * quantity:.2f}",  # Total
                expiry_str,  # Expiry
                self.batch_var.get()  # Batch
            ))
            
            # Update totals
            self.update_totals()
            
            # Reset medicine selection
            self.medicine_var.set("")
            self.quantity_var.set("1")
            self.cost_var.set("")
            self.expiry_var.set("")
            self.batch_var.set("")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid quantity")
    
    def update_totals(self):
        # Calculate subtotal
        self.subtotal = sum(item['cost_price'] * item['quantity'] for item in self.purchase_items)
        self.total = self.subtotal
        
        # Update display
        self.subtotal_var.set(f"${self.subtotal:.2f}")
        self.total_var.set(f"${self.total:.2f}")
    
    def complete_purchase(self):
        if not self.purchase_items:
            messagebox.showinfo("No Items", "Please add at least one medicine to the purchase")
            return
        
        # Get supplier
        supplier_id = None
        supplier_text = self.supplier_var.get()
        if supplier_text:
            try:
                supplier_id = int(supplier_text.split(' - ')[0])
            except ValueError:
                pass
        
        # Generate invoice number
        if not self.invoice_var.get():
            self.invoice_var.set(f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        
        # Get purchase date
        try:
            purchase_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Invalid date format. Use YYYY-MM-DD")
            return
        
        try:
            # Start transaction
            self.db.conn.execute("BEGIN TRANSACTION")
            
            # Insert purchase record
            purchase_id = self.db.execute_update('''
            INSERT INTO purchases (invoice_number, supplier_id, store_id, user_id, total_amount, purchase_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.invoice_var.get(),
                supplier_id,
                self.user['store_id'],
                self.user['id'],
                self.total,
                purchase_date
            ))
            
            # Insert purchase items and update stock
            for item in self.purchase_items:
                # Insert purchase item
                self.db.execute_update('''
                INSERT INTO purchase_items (purchase_id, medicine_id, quantity, cost_price, expiry_date, batch_number)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    purchase_id,
                    item['id'],
                    item['quantity'],
                    item['cost_price'],
                    item['expiry_date'],
                    item['batch_number']
                ))
                
                # Update stock
                self.db.execute_update('''
                UPDATE medicines
                SET stock_quantity = stock_quantity + ?, cost_price = ?
                WHERE id = ?
                ''', (item['quantity'], item['cost_price'], item['id']))
            
            # Commit transaction
            self.db.conn.commit()
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.user['id'], "CREATE", "purchases", purchase_id)
            )
            
            messagebox.showinfo("Purchase Completed", "Purchase completed successfully")
            
            # Reset purchase form
            self.cancel_purchase()
            
            # Refresh purchase history
            self.load_purchase_history()
            
        except Exception as e:
            # Rollback transaction
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to complete purchase: {str(e)}")
    
    def cancel_purchase(self):
        # Reset purchase form
        self.purchase_items = []
        self.subtotal = 0.0
        self.total = 0.0
        
        # Clear purchase items tree
        for item in self.purchase_items_tree.get_children():
            self.purchase_items_tree.delete(item)
        
        # Reset form fields
        self.supplier_var.set("")
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.invoice_var.set("")
        self.medicine_var.set("")
        self.quantity_var.set("1")
        self.cost_var.set("")
        self.expiry_var.set("")
        self.batch_var.set("")
        
        # Update totals display
        self.subtotal_var.set("$0.00")
        self.total_var.set("$0.00")