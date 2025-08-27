import tkinter as tk
from tkinter import messagebox, ttk
from hashlib import sha256
from database import Database

class AuthSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.db = Database()
        self.current_user = None
        
        self.create_login_ui()
    
    def create_login_ui(self):
        # Frame for login form
        login_frame = ttk.Frame(self.root, padding="20")
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(login_frame, text="Pharmacy Management System", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Enter your credentials")
        status_bar = ttk.Label(login_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_var.set("Username and password are required")
            return
        
        # Hash the password
        hashed_password = sha256(password.encode()).hexdigest()
        
        # Check credentials
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND active = 1"
        users = self.db.execute_query(query, (username, hashed_password))
        
        if users:
            user = users[0]
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'name': user[4],
                'store_id': user[8]
            }
            self.status_var.set(f"Login successful. Welcome, {user[4]}!")
            
            # Log the login
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.current_user['id'], "LOGIN", "users", self.current_user['id'])
            )
            
            # Open dashboard
            self.root.destroy()
            import dashboard
            dashboard_root = tk.Tk()
            dashboard_app = dashboard.Dashboard(dashboard_root, self.current_user, self.db)
            dashboard_root.mainloop()
        else:
            self.status_var.set("Invalid username or password")
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def logout(self):
        # Log the logout
        if self.current_user:
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.current_user['id'], "LOGOUT", "users", self.current_user['id'])
            )
        
        self.current_user = None
        self.db.close()
        
        # Reopen login screen
        self.root.destroy()
        import main
        main_root = tk.Tk()
        main_app = AuthSystem(main_root)
        main_root.mainloop()