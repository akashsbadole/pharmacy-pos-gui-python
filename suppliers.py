import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class Suppliers:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create suppliers frame
        self.suppliers_frame = ttk.Frame(parent, padding=20)
        self.suppliers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.suppliers_frame, text="Supplier Management", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Search section
        search_frame = ttk.Frame(self.suppliers_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_suppliers)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        buttons_frame = ttk.Frame(self.suppliers_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Add Supplier", command=self.add_supplier)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(buttons_frame, text="Edit Supplier", command=self.edit_supplier)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(buttons_frame, text="Delete Supplier", command=self.delete_supplier)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        import_btn = ttk.Button(buttons_frame, text="Import CSV", command=self.import_csv)
        import_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(buttons_frame, text="Export CSV", command=self.export_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Suppliers table
        table_frame = ttk.Frame(self.suppliers_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for suppliers
        columns = ("ID", "Name", "Contact Person", "Phone", "Email", "GST Number")
        self.suppliers_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.suppliers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load suppliers data
        self.load_suppliers()
        
        # Bind double-click event
        self.suppliers_tree.bind("<Double-1>", self.on_double_click)
    
    def load_suppliers(self):
        # Clear existing items
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Get suppliers data
        suppliers = self.db.execute_query('''
        SELECT id, name, contact_person, phone, email, gst_number
        FROM suppliers
        ORDER BY name
        ''')
        
        for supplier in suppliers:
            self.suppliers_tree.insert("", tk.END, values=(
                supplier[0],  # ID
                supplier[1],  # Name
                supplier[2] or "",  # Contact Person
                supplier[3] or "",  # Phone
                supplier[4] or "",  # Email
                supplier[5] or ""  # GST Number
            ))
    
    def filter_suppliers(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Get filtered suppliers data
        query = '''
        SELECT id, name, contact_person, phone, email, gst_number
        FROM suppliers
        '''
        params = []
        
        if search_term:
            query += " WHERE (LOWER(name) LIKE ? OR LOWER(contact_person) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(email) LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY name"
        
        suppliers = self.db.execute_query(query, params)
        
        for supplier in suppliers:
            self.suppliers_tree.insert("", tk.END, values=(
                supplier[0],  # ID
                supplier[1],  # Name
                supplier[2] or "",  # Contact Person
                supplier[3] or "",  # Phone
                supplier[4] or "",  # Email
                supplier[5] or ""  # GST Number
            ))
    
    def on_double_click(self, event):
        self.edit_supplier()
    
    def add_supplier(self):
        # Create add supplier dialog
        add_dialog = tk.Toplevel(self.parent)
        add_dialog.title("Add Supplier")
        add_dialog.geometry("500x450")
        add_dialog.resizable(False, False)
        
        # Supplier form
        ttk.Label(add_dialog, text="Supplier Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(add_dialog, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(add_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Contact Person:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        contact_var = tk.StringVar()
        contact_entry = ttk.Entry(add_dialog, textvariable=contact_var, width=30)
        contact_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(add_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(add_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Address:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        address_var = tk.StringVar()
        address_entry = ttk.Entry(add_dialog, textvariable=address_var, width=30)
        address_entry.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="GST Number:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        gst_var = tk.StringVar()
        gst_entry = ttk.Entry(add_dialog, textvariable=gst_var, width=30)
        gst_entry.grid(row=6, column=1, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(add_dialog)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        def save_supplier():
            try:
                # Validate inputs
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Supplier name is required")
                    return
                
                # Insert supplier
                supplier_id = self.db.execute_update('''
                INSERT INTO suppliers (name, contact_person, phone, email, address, gst_number)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    name_var.get(),
                    contact_var.get(),
                    phone_var.get(),
                    email_var.get(),
                    address_var.get(),
                    gst_var.get()
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "CREATE", "suppliers", supplier_id)
                )
                
                messagebox.showinfo("Success", "Supplier added successfully")
                add_dialog.destroy()
                self.load_suppliers()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_supplier)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def edit_supplier(self):
        # Get selected supplier
        selected = self.suppliers_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a supplier to edit")
            return
        
        item = self.suppliers_tree.item(selected[0])
        supplier_id = item['values'][0]
        
        # Get supplier details
        supplier = self.db.execute_query('''
        SELECT id, name, contact_person, phone, email, address, gst_number
        FROM suppliers
        WHERE id = ?
        ''', (supplier_id,))
        
        if not supplier:
            messagebox.showerror("Error", "Supplier not found")
            return
        
        supplier = supplier[0]
        
        # Create edit supplier dialog
        edit_dialog = tk.Toplevel(self.parent)
        edit_dialog.title("Edit Supplier")
        edit_dialog.geometry("500x450")
        edit_dialog.resizable(False, False)
        
        # Supplier form
        ttk.Label(edit_dialog, text="Supplier Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(edit_dialog, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar(value=supplier[1])
        name_entry = ttk.Entry(edit_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Contact Person:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        contact_var = tk.StringVar(value=supplier[2] or "")
        contact_entry = ttk.Entry(edit_dialog, textvariable=contact_var, width=30)
        contact_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar(value=supplier[3] or "")
        phone_entry = ttk.Entry(edit_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar(value=supplier[4] or "")
        email_entry = ttk.Entry(edit_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Address:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        address_var = tk.StringVar(value=supplier[5] or "")
        address_entry = ttk.Entry(edit_dialog, textvariable=address_var, width=30)
        address_entry.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="GST Number:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        gst_var = tk.StringVar(value=supplier[6] or "")
        gst_entry = ttk.Entry(edit_dialog, textvariable=gst_var, width=30)
        gst_entry.grid(row=6, column=1, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(edit_dialog)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        def update_supplier():
            try:
                # Validate inputs
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Supplier name is required")
                    return
                
                # Update supplier
                self.db.execute_update('''
                UPDATE suppliers SET 
                    name = ?, contact_person = ?, phone = ?, email = ?, address = ?, gst_number = ?
                WHERE id = ?
                ''', (
                    name_var.get(),
                    contact_var.get(),
                    phone_var.get(),
                    email_var.get(),
                    address_var.get(),
                    gst_var.get(),
                    supplier_id
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "UPDATE", "suppliers", supplier_id)
                )
                
                messagebox.showinfo("Success", "Supplier updated successfully")
                edit_dialog.destroy()
                self.load_suppliers()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        update_btn = ttk.Button(button_frame, text="Update", command=update_supplier)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_supplier(self):
        # Get selected supplier
        selected = self.suppliers_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a supplier to delete")
            return
        
        item = self.suppliers_tree.item(selected[0])
        supplier_id = item['values'][0]
        supplier_name = item['values'][1]
        
        # Check if supplier has purchases
        purchases = self.db.execute_query("SELECT COUNT(*) FROM purchases WHERE supplier_id = ?", (supplier_id,))
        if purchases[0][0] > 0:
            messagebox.showerror("Cannot Delete", f"Cannot delete supplier {supplier_name} because they have purchase records")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {supplier_name}? This action cannot be undone."
        )
        
        if confirm:
            # Delete supplier
            self.db.execute_update("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.user['id'], "DELETE", "suppliers", supplier_id)
            )
            
            messagebox.showinfo("Success", "Supplier deleted successfully")
            self.load_suppliers()
    
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
                            contact_person = row[1] if len(row) > 1 else ""
                            phone = row[2] if len(row) > 2 else ""
                            email = row[3] if len(row) > 3 else ""
                            address = row[4] if len(row) > 4 else ""
                            gst_number = row[5] if len(row) > 5 else ""
                            
                            # Insert supplier
                            self.db.execute_update('''
                            INSERT INTO suppliers (name, contact_person, phone, email, address, gst_number)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ''', (name, contact_person, phone, email, address, gst_number))
                            
                            count += 1
                        except Exception as e:
                            print(f"Error importing row: {e}")
                    
                    messagebox.showinfo("Import Complete", f"Successfully imported {count} suppliers")
                    self.load_suppliers()
                    
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
                        "Name", "Contact Person", "Phone", "Email", "Address", "GST Number"
                    ])
                    
                    # Get suppliers data
                    suppliers = self.db.execute_query('''
                    SELECT name, contact_person, phone, email, address, gst_number
                    FROM suppliers
                    ORDER BY name
                    ''')
                    
                    # Write data
                    for supplier in suppliers:
                        writer.writerow([
                            supplier[0],  # Name
                            supplier[1] or "",  # Contact Person
                            supplier[2] or "",  # Phone
                            supplier[3] or "",  # Email
                            supplier[4] or "",  # Address
                            supplier[5] or ""  # GST Number
                        ])
                    
                    messagebox.showinfo("Export Complete", "Suppliers exported successfully")
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting CSV file: {str(e)}")