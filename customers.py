import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class Customers:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create customers frame
        self.customers_frame = ttk.Frame(parent, padding=20)
        self.customers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.customers_frame, text="Customer Management", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Search section
        search_frame = ttk.Frame(self.customers_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_customers)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        buttons_frame = ttk.Frame(self.customers_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Add Customer", command=self.add_customer)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(buttons_frame, text="Edit Customer", command=self.edit_customer)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(buttons_frame, text="Delete Customer", command=self.delete_customer)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = ttk.Button(buttons_frame, text="Import CSV", command=self.import_csv)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(buttons_frame, text="Export CSV", command=self.export_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Customers table
        table_frame = ttk.Frame(self.customers_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for customers
        columns = ("ID", "Name", "Phone", "Email", "Address", "Loyalty Points")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load customers data
        self.load_customers()
        
        # Bind double-click event
        self.customers_tree.bind("<Double-1>", self.on_double_click)
    
    def load_customers(self):
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Get customers data
        customers = self.db.execute_query('''
        SELECT id, name, phone, email, address, loyalty_points
        FROM customers
        ORDER BY name
        ''')
        
        for customer in customers:
            self.customers_tree.insert("", tk.END, values=(
                customer[0],  # ID
                customer[1],  # Name
                customer[2] or "",  # Phone
                customer[3] or "",  # Email
                customer[4] or "",  # Address
                customer[5]  # Loyalty Points
            ))
    
    def filter_customers(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Get filtered customers data
        query = '''
        SELECT id, name, phone, email, address, loyalty_points
        FROM customers
        '''
        params = []
        
        if search_term:
            query += " WHERE (LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(email) LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY name"
        
        customers = self.db.execute_query(query, params)
        
        for customer in customers:
            self.customers_tree.insert("", tk.END, values=(
                customer[0],  # ID
                customer[1],  # Name
                customer[2] or "",  # Phone
                customer[3] or "",  # Email
                customer[4] or "",  # Address
                customer[5]  # Loyalty Points
            ))
    
    def on_double_click(self, event):
        self.edit_customer()
    
    def add_customer(self):
        # Create add customer dialog
        add_dialog = tk.Toplevel(self.parent)
        add_dialog.title("Add Customer")
        add_dialog.geometry("500x400")
        add_dialog.resizable(False, False)
        
        # Customer form
        ttk.Label(add_dialog, text="Customer Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(add_dialog, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(add_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(add_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(add_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Address:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        address_var = tk.StringVar()
        address_entry = ttk.Entry(add_dialog, textvariable=address_var, width=30)
        address_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Loyalty Points:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        loyalty_var = tk.StringVar(value="0")
        loyalty_entry = ttk.Entry(add_dialog, textvariable=loyalty_var, width=30)
        loyalty_entry.grid(row=5, column=1, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(add_dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        def save_customer():
            try:
                # Validate inputs
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Customer name is required")
                    return
                
                loyalty_points = int(loyalty_var.get()) if loyalty_var.get() else 0
                
                # Insert customer
                customer_id = self.db.execute_update('''
                INSERT INTO customers (name, phone, email, address, loyalty_points)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    name_var.get(),
                    phone_var.get(),
                    email_var.get(),
                    address_var.get(),
                    loyalty_points
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "CREATE", "customers", customer_id)
                )
                
                messagebox.showinfo("Success", "Customer added successfully")
                add_dialog.destroy()
                self.load_customers()
                
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_customer)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def edit_customer(self):
        # Get selected customer
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a customer to edit")
            return
        
        item = self.customers_tree.item(selected[0])
        customer_id = item['values'][0]
        
        # Get customer details
        customer = self.db.execute_query('''
        SELECT id, name, phone, email, address, loyalty_points
        FROM customers
        WHERE id = ?
        ''', (customer_id,))
        
        if not customer:
            messagebox.showerror("Error", "Customer not found")
            return
        
        customer = customer[0]
        
        # Create edit customer dialog
        edit_dialog = tk.Toplevel(self.parent)
        edit_dialog.title("Edit Customer")
        edit_dialog.geometry("500x400")
        edit_dialog.resizable(False, False)
        
        # Customer form
        ttk.Label(edit_dialog, text="Customer Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(edit_dialog, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar(value=customer[1])
        name_entry = ttk.Entry(edit_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar(value=customer[2] or "")
        phone_entry = ttk.Entry(edit_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar(value=customer[3] or "")
        email_entry = ttk.Entry(edit_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Address:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        address_var = tk.StringVar(value=customer[4] or "")
        address_entry = ttk.Entry(edit_dialog, textvariable=address_var, width=30)
        address_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Loyalty Points:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        loyalty_var = tk.StringVar(value=str(customer[5]))
        loyalty_entry = ttk.Entry(edit_dialog, textvariable=loyalty_var, width=30)
        loyalty_entry.grid(row=5, column=1, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(edit_dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        def update_customer():
            try:
                # Validate inputs
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Customer name is required")
                    return
                
                loyalty_points = int(loyalty_var.get()) if loyalty_var.get() else 0
                
                # Update customer
                self.db.execute_update('''
                UPDATE customers SET 
                    name = ?, phone = ?, email = ?, address = ?, loyalty_points = ?
                WHERE id = ?
                ''', (
                    name_var.get(),
                    phone_var.get(),
                    email_var.get(),
                    address_var.get(),
                    loyalty_points,
                    customer_id
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "UPDATE", "customers", customer_id)
                )
                
                messagebox.showinfo("Success", "Customer updated successfully")
                edit_dialog.destroy()
                self.load_customers()
                
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        update_btn = ttk.Button(button_frame, text="Update", command=update_customer)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_customer(self):
        # Get selected customer
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a customer to delete")
            return
        
        item = self.customers_tree.item(selected[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Check if customer has sales
        sales = self.db.execute_query("SELECT COUNT(*) FROM sales WHERE customer_id = ?", (customer_id,))
        if sales[0][0] > 0:
            messagebox.showerror("Cannot Delete", f"Cannot delete customer {customer_name} because they have sales records")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {customer_name}? This action cannot be undone."
        )
        
        if confirm:
            # Delete customer
            self.db.execute_update("DELETE FROM customers WHERE id = ?", (customer_id,))
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.user['id'], "DELETE", "customers", customer_id)
            )
            
            messagebox.showinfo("Success", "Customer deleted successfully")
            self.load_customers()
    
    def import_csv(self):
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Import CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    
                    # Skip header if exists
                    header = next(reader, None)
                    
                    count = 0
                    for row in reader:
                        if len(row) < 1:  # Minimum required fields
                            continue
                        
                        try:
                            # Extract data from row
                            name = row[0]
                            phone = row[1] if len(row) > 1 else ""
                            email = row[2] if len(row) > 2 else ""
                            address = row[3] if len(row) > 3 else ""
                            loyalty_points = int(row[4]) if len(row) > 4 and row[4] else 0
                            
                            # Insert customer
                            self.db.execute_update('''
                            INSERT INTO customers (name, phone, email, address, loyalty_points)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (name, phone, email, address, loyalty_points))
                            
                            count += 1
                        except Exception as e:
                            print(f"Error importing row: {e}")
                    
                    messagebox.showinfo("Import Complete", f"Successfully imported {count} customers")
                    self.load_customers()
                    
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing CSV file: {str(e)}")
    
    def export_csv(self):
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Export CSV File",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        "Name", "Phone", "Email", "Address", "Loyalty Points"
                    ])
                    
                    # Get customers data
                    customers = self.db.execute_query('''
                    SELECT name, phone, email, address, loyalty_points
                    FROM customers
                    ORDER BY name
                    ''')
                    
                    # Write data
                    for customer in customers:
                        writer.writerow([
                            customer[0],  # Name
                            customer[1] or "",  # Phone
                            customer[2] or "",  # Email
                            customer[3] or "",  # Address
                            customer[4]  # Loyalty Points
                        ])
                    
                    messagebox.showinfo("Export Complete", "Customers exported successfully")
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting CSV file: {str(e)}")