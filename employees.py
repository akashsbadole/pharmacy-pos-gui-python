import tkinter as tk
from tkinter import ttk, messagebox
from hashlib import sha256
import csv
from datetime import datetime

class Employees:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Check if user has admin privileges
        if self.user['role'] != 'admin':
            error_frame = ttk.Frame(parent, padding=20)
            error_frame.pack(fill=tk.BOTH, expand=True)
            
            error_label = ttk.Label(error_frame, text="Access Denied: Admin privileges required", 
                                   font=('Arial', 16, 'bold'), foreground="red")
            error_label.pack(pady=20)
            
            return
        
        # Create employees frame
        self.employees_frame = ttk.Frame(parent, padding=20)
        self.employees_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.employees_frame, text="Employee Management", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Search section
        search_frame = ttk.Frame(self.employees_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_employees)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Role:").pack(side=tk.LEFT, padx=5)
        self.role_var = tk.StringVar()
        self.role_var.trace('w', self.filter_employees)
        role_combo = ttk.Combobox(search_frame, textvariable=self.role_var, width=15)
        role_combo.pack(side=tk.LEFT, padx=5)
        role_combo['values'] = ["All", "admin", "pharmacist", "cashier"]
        
        # Buttons
        buttons_frame = ttk.Frame(self.employees_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Add Employee", command=self.add_employee)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(buttons_frame, text="Edit Employee", command=self.edit_employee)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(buttons_frame, text="Delete Employee", command=self.delete_employee)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(buttons_frame, text="Reset Password", command=self.reset_password)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Employees table
        table_frame = ttk.Frame(self.employees_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for employees
        columns = ("ID", "Username", "Name", "Role", "Email", "Phone", "Store", "Active")
        self.employees_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.employees_tree.heading(col, text=col)
            self.employees_tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        self.employees_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load employees data
        self.load_employees()
        
        # Bind double-click event
        self.employees_tree.bind("<Double-1>", self.on_double_click)
    
    def load_employees(self):
        # Clear existing items
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Get employees data
        employees = self.db.execute_query('''
        SELECT u.id, u.username, u.name, u.role, u.email, u.phone, s.name, u.active
        FROM users u
        LEFT JOIN stores s ON u.store_id = s.id
        ORDER BY u.name
        ''')
        
        for employee in employees:
            self.employees_tree.insert("", tk.END, values=(
                employee[0],  # ID
                employee[1],  # Username
                employee[2],  # Name
                employee[3],  # Role
                employee[4] or "",  # Email
                employee[5] or "",  # Phone
                employee[6] or "",  # Store
                "Yes" if employee[7] else "No"  # Active
            ))
    
    def filter_employees(self, *args):
        search_term = self.search_var.get().lower()
        role = self.role_var.get()
        
        # Clear existing items
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        # Build query
        query = '''
        SELECT u.id, u.username, u.name, u.role, u.email, u.phone, s.name, u.active
        FROM users u
        LEFT JOIN stores s ON u.store_id = s.id
        '''
        params = []
        
        conditions = []
        
        if search_term:
            conditions.append("(LOWER(u.username) LIKE ? OR LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ?)")
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        if role and role != "All":
            conditions.append("u.role = ?")
            params.append(role)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY u.name"
        
        # Get filtered employees data
        employees = self.db.execute_query(query, params)
        
        for employee in employees:
            self.employees_tree.insert("", tk.END, values=(
                employee[0],  # ID
                employee[1],  # Username
                employee[2],  # Name
                employee[3],  # Role
                employee[4] or "",  # Email
                employee[5] or "",  # Phone
                employee[6] or "",  # Store
                "Yes" if employee[7] else "No"  # Active
            ))
    
    def on_double_click(self, event):
        self.edit_employee()
    
    def add_employee(self):
        # Create add employee dialog
        add_dialog = tk.Toplevel(self.parent)
        add_dialog.title("Add Employee")
        add_dialog.geometry("500x500")
        add_dialog.resizable(False, False)
        
        # Employee form
        ttk.Label(add_dialog, text="Employee Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(add_dialog, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(add_dialog, textvariable=username_var, width=30)
        username_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(add_dialog, textvariable=password_var, width=30, show="*")
        password_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Name:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(add_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Role:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(add_dialog, textvariable=role_var, width=28)
        role_combo.grid(row=4, column=1, pady=5, padx=10)
        role_combo['values'] = ["admin", "pharmacist", "cashier"]
        
        ttk.Label(add_dialog, text="Email:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(add_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Phone:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(add_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=6, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Store:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=10)
        store_var = tk.StringVar()
        store_combo = ttk.Combobox(add_dialog, textvariable=store_var, width=28)
        store_combo.grid(row=7, column=1, pady=5, padx=10)
        
        # Get stores
        stores = self.db.execute_query("SELECT id, name FROM stores")
        store_combo['values'] = [f"{s[0]} - {s[1]}" for s in stores]
        
        active_var = tk.BooleanVar(value=True)
        active_check = ttk.Checkbutton(add_dialog, text="Active", variable=active_var)
        active_check.grid(row=8, column=0, columnspan=2, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(add_dialog)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        def save_employee():
            try:
                # Validate inputs
                if not username_var.get():
                    messagebox.showerror("Validation Error", "Username is required")
                    return
                
                if not password_var.get():
                    messagebox.showerror("Validation Error", "Password is required")
                    return
                
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Employee name is required")
                    return
                
                if not role_var.get():
                    messagebox.showerror("Validation Error", "Role is required")
                    return
                
                # Check if username already exists
                existing = self.db.execute_query("SELECT COUNT(*) FROM users WHERE username = ?", (username_var.get(),))
                if existing[0][0] > 0:
                    messagebox.showerror("Validation Error", "Username already exists")
                    return
                
                # Get store ID
                store_id = None
                if store_var.get():
                    try:
                        store_id = int(store_var.get().split(' - ')[0])
                    except ValueError:
                        pass
                
                # Hash the password
                hashed_password = sha256(password_var.get().encode()).hexdigest()
                
                # Insert employee
                employee_id = self.db.execute_update('''
                INSERT INTO users (username, password, role, name, email, phone, store_id, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    username_var.get(),
                    hashed_password,
                    role_var.get(),
                    name_var.get(),
                    email_var.get(),
                    phone_var.get(),
                    store_id,
                    active_var.get()
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "CREATE", "users", employee_id)
                )
                
                messagebox.showinfo("Success", "Employee added successfully")
                add_dialog.destroy()
                self.load_employees()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        save_btn = ttk.Button(button_frame, text="Save", command=save_employee)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def edit_employee(self):
        # Get selected employee
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an employee to edit")
            return
        
        item = self.employees_tree.item(selected[0])
        employee_id = item['values'][0]
        
        # Get employee details
        employee = self.db.execute_query('''
        SELECT id, username, name, role, email, phone, store_id, active
        FROM users
        WHERE id = ?
        ''', (employee_id,))
        
        if not employee:
            messagebox.showerror("Error", "Employee not found")
            return
        
        employee = employee[0]
        
        # Create edit employee dialog
        edit_dialog = tk.Toplevel(self.parent)
        edit_dialog.title("Edit Employee")
        edit_dialog.geometry("500x500")
        edit_dialog.resizable(False, False)
        
        # Employee form
        ttk.Label(edit_dialog, text="Employee Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(edit_dialog, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        username_var = tk.StringVar(value=employee[1])
        username_entry = ttk.Entry(edit_dialog, textvariable=username_var, width=30)
        username_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Name:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        name_var = tk.StringVar(value=employee[2])
        name_entry = ttk.Entry(edit_dialog, textvariable=name_var, width=30)
        name_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Role:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        role_var = tk.StringVar(value=employee[3])
        role_combo = ttk.Combobox(edit_dialog, textvariable=role_var, width=28)
        role_combo.grid(row=3, column=1, pady=5, padx=10)
        role_combo['values'] = ["admin", "pharmacist", "cashier"]
        
        ttk.Label(edit_dialog, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        email_var = tk.StringVar(value=employee[4] or "")
        email_entry = ttk.Entry(edit_dialog, textvariable=email_var, width=30)
        email_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Phone:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        phone_var = tk.StringVar(value=employee[5] or "")
        phone_entry = ttk.Entry(edit_dialog, textvariable=phone_var, width=30)
        phone_entry.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Store:").grid(row=6, column=0, sticky=tk.W, pady=5, padx=10)
        store_var = tk.StringVar()
        store_combo = ttk.Combobox(edit_dialog, textvariable=store_var, width=28)
        store_combo.grid(row=6, column=1, pady=5, padx=10)
        
        # Get stores
        stores = self.db.execute_query("SELECT id, name FROM stores")
        store_values = [f"{s[0]} - {s[1]}" for s in stores]
        store_combo['values'] = store_values
        
        # Set current store
        if employee[6]:
            for store in stores:
                if store[0] == employee[6]:
                    store_var.set(f"{store[0]} - {store[1]}")
                    break
        
        active_var = tk.BooleanVar(value=bool(employee[7]))
        active_check = ttk.Checkbutton(edit_dialog, text="Active", variable=active_var)
        active_check.grid(row=7, column=0, columnspan=2, pady=5, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(edit_dialog)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        def update_employee():
            try:
                # Validate inputs
                if not username_var.get():
                    messagebox.showerror("Validation Error", "Username is required")
                    return
                
                if not name_var.get():
                    messagebox.showerror("Validation Error", "Employee name is required")
                    return
                
                if not role_var.get():
                    messagebox.showerror("Validation Error", "Role is required")
                    return
                
                # Get store ID
                store_id = None
                if store_var.get():
                    try:
                        store_id = int(store_var.get().split(' - ')[0])
                    except ValueError:
                        pass
                
                # Update employee
                self.db.execute_update('''
                UPDATE users SET 
                    username = ?, name = ?, role = ?, email = ?, phone = ?, store_id = ?, active = ?
                WHERE id = ?
                ''', (
                    username_var.get(),
                    name_var.get(),
                    role_var.get(),
                    email_var.get(),
                    phone_var.get(),
                    store_id,
                    active_var.get(),
                    employee_id
                ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "UPDATE", "users", employee_id)
                )
                
                messagebox.showinfo("Success", "Employee updated successfully")
                edit_dialog.destroy()
                self.load_employees()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        update_btn = ttk.Button(button_frame, text="Update", command=update_employee)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_employee(self):
        # Get selected employee
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an employee to delete")
            return
        
        item = self.employees_tree.item(selected[0])
        employee_id = item['values'][0]
        employee_name = item['values'][2]
        
        # Prevent deleting the current user
        if employee_id == self.user['id']:
            messagebox.showerror("Cannot Delete", "You cannot delete your own account")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {employee_name}? This action cannot be undone."
        )
        
        if confirm:
            # Delete employee
            self.db.execute_update("DELETE FROM users WHERE id = ?", (employee_id,))
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.user['id'], "DELETE", "users", employee_id)
            )
            
            messagebox.showinfo("Success", "Employee deleted successfully")
            self.load_employees()
    
    def reset_password(self):
        # Get selected employee
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select an employee to reset password")
            return
        
        item = self.employees_tree.item(selected[0])
        employee_id = item['values'][0]
        employee_name = item['values'][2]
        
        # Create reset password dialog
        reset_dialog = tk.Toplevel(self.parent)
        reset_dialog.title("Reset Password")
        reset_dialog.geometry("400x200")
        reset_dialog.resizable(False, False)
        
        ttk.Label(reset_dialog, text=f"Reset password for {employee_name}", font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Label(reset_dialog, text="New Password:").pack(pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(reset_dialog, textvariable=password_var, width=30, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(reset_dialog, text="Confirm Password:").pack(pady=5)
        confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(reset_dialog, textvariable=confirm_var, width=30, show="*")
        confirm_entry.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(reset_dialog)
        button_frame.pack(pady=10)
        
        def reset_password():
            if not password_var.get():
                messagebox.showerror("Validation Error", "Password is required")
                return
            
            if password_var.get() != confirm_var.get():
                messagebox.showerror("Validation Error", "Passwords do not match")
                return
            
            # Hash the password
            hashed_password = sha256(password_var.get().encode()).hexdigest()
            
            # Update password
            self.db.execute_update('''
            UPDATE users SET password = ?
            WHERE id = ?
            ''', (hashed_password, employee_id))
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id, new_values) VALUES (?, ?, ?, ?, ?)",
                (self.user['id'], "RESET_PASSWORD", "users", employee_id, "Password reset")
            )
            
            messagebox.showinfo("Success", "Password reset successfully")
            reset_dialog.destroy()
        
        reset_btn = ttk.Button(button_frame, text="Reset Password", command=reset_password)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=reset_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)