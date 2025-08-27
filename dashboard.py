import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk

class Dashboard:
    def __init__(self, root, user, db):
        self.root = root
        self.user = user
        self.db = db
        self.root.title(f"Pharmacy Management System - {user['name']} ({user['role']})")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.main_content = ttk.Frame(self.main_container)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Welcome, {user['name']} | Role: {user['role']}")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Show home screen
        self.show_home()
    
    def create_sidebar(self):
        # Sidebar frame
        sidebar = ttk.Frame(self.main_container, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Store logo/name
        store = self.db.execute_query("SELECT name, logo_path FROM stores WHERE id = ?", (self.user['store_id'],))
        if store:
            store_name = store[0][0]
            logo_path = store[0][1]
            
            store_frame = ttk.Frame(sidebar, padding=10)
            store_frame.pack(fill=tk.X, pady=10)
            
            if logo_path and os.path.exists(logo_path):
                try:
                    logo_img = Image.open(logo_path)
                    logo_img = logo_img.resize((100, 100), Image.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_img)
                    logo_label = ttk.Label(store_frame, image=logo_photo)
                    logo_label.image = logo_photo  # Keep a reference
                    logo_label.pack()
                except Exception as e:
                    print(f"Error loading logo: {e}")
            
            store_label = ttk.Label(store_frame, text=store_name, font=('Arial', 12, 'bold'))
            store_label.pack(pady=5)
        
        # Navigation buttons
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        nav_buttons = [
            ("Home", self.show_home),
            ("Inventory", self.show_inventory),
            ("Sales", self.show_sales),
            ("Purchases", self.show_purchases),
            ("Customers", self.show_customers),
            ("Suppliers", self.show_suppliers),
            ("Prescriptions", self.show_prescriptions),
            ("Reports", self.show_reports),
        ]
        
        # Add admin-only buttons
        if self.user['role'] == 'admin':
            nav_buttons.extend([
                ("Employees", self.show_employees),
                ("Settings", self.show_settings),
            ])
        
        for text, command in nav_buttons:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill=tk.X, pady=2, padx=10)
        
        # Advanced features section
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(sidebar, text="Advanced Features", font=('Arial', 10, 'bold')).pack(pady=5)
        
        adv_buttons = [
            ("AI Insights", self.show_ai_insights),
            ("n8n Workflows", self.show_n8n_workflows),
            ("Backup/Restore", self.show_backup_restore),
        ]
        
        for text, command in adv_buttons:
            btn = ttk.Button(sidebar, text=text, command=command)
            btn.pack(fill=tk.X, pady=2, padx=10)
        
        # Logout button
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        logout_btn = ttk.Button(sidebar, text="Logout", command=self.logout)
        logout_btn.pack(fill=tk.X, pady=10, padx=10)
    
    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_home(self):
        self.clear_main_content()
        
        # Home screen
        home_frame = ttk.Frame(self.main_content, padding=20)
        home_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(home_frame, text="Dashboard", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Summary cards
        cards_frame = ttk.Frame(home_frame)
        cards_frame.pack(fill=tk.X, pady=10)
        
        # Get summary data
        total_medicines = self.db.execute_query("SELECT COUNT(*) FROM medicines WHERE store_id = ?", (self.user['store_id'],))[0][0]
        low_stock = self.db.execute_query("SELECT COUNT(*) FROM medicines WHERE store_id = ? AND stock_quantity < 10", (self.user['store_id'],))[0][0]
        today_sales = self.db.execute_query("SELECT COUNT(*) FROM sales WHERE store_id = ? AND DATE(sale_date) = DATE('now')", (self.user['store_id'],))[0][0]
        expiring_soon = self.db.execute_query("SELECT COUNT(*) FROM medicines WHERE store_id = ? AND expiry_date <= DATE('now', '+30 days')", (self.user['store_id'],))[0][0]
        
        # Create cards
        cards = [
            ("Total Medicines", total_medicines, "blue"),
            ("Low Stock Items", low_stock, "red"),
            ("Today's Sales", today_sales, "green"),
            ("Expiring Soon", expiring_soon, "orange")
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card_frame = ttk.LabelFrame(cards_frame, text=title, padding=10)
            card_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            value_label = ttk.Label(card_frame, text=str(value), font=('Arial', 24, 'bold'))
            value_label.pack()
        
        # Configure grid weights
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Recent sales table
        recent_frame = ttk.LabelFrame(home_frame, text="Recent Sales", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for recent sales
        columns = ("Invoice #", "Customer", "Amount", "Date", "Staff")
        tree = ttk.Treeview(recent_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get recent sales data
        recent_sales = self.db.execute_query('''
        SELECT s.invoice_number, c.name, s.total_amount, s.sale_date, u.name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.store_id = ?
        ORDER BY s.sale_date DESC
        LIMIT 10
        ''', (self.user['store_id'],))
        
        for sale in recent_sales:
            tree.insert("", tk.END, values=(
                sale[0],  # Invoice #
                sale[1] or "Walk-in",  # Customer
                f"${sale[2]:.2f}",  # Amount
                sale[3].split()[0],  # Date (only date part)
                sale[4]  # Staff
            ))
    
    def show_inventory(self):
        self.clear_main_content()
        
        # Import inventory module
        import inventory
        inventory.Inventory(self.main_content, self.user, self.db)
    
    def show_sales(self):
        self.clear_main_content()
        
        # Import sales module
        import sales
        sales.Sales(self.main_content, self.user, self.db)
    
    def show_purchases(self):
        self.clear_main_content()
        
        # Import purchases module
        import purchases
        purchases.Purchases(self.main_content, self.user, self.db)
    
    def show_customers(self):
        self.clear_main_content()
        
        # Import customers module
        import customers
        customers.Customers(self.main_content, self.user, self.db)
    
    def show_suppliers(self):
        self.clear_main_content()
        
        # Import suppliers module
        import suppliers
        suppliers.Suppliers(self.main_content, self.user, self.db)
    
    def show_employees(self):
        self.clear_main_content()
        
        # Import employees module
        import employees
        employees.Employees(self.main_content, self.user, self.db)
    
    def show_prescriptions(self):
        self.clear_main_content()
        
        # Import prescriptions module
        import prescriptions
        prescriptions.Prescriptions(self.main_content, self.user, self.db)
    
    def show_reports(self):
        self.clear_main_content()
        
        # Import reports module
        import reports
        reports.Reports(self.main_content, self.user, self.db)
    
    def show_ai_insights(self):
        self.clear_main_content()
        
        # Import AI integration module
        import ai_integration
        ai_integration.AIIntegration(self.main_content, self.user, self.db)
    
    def show_n8n_workflows(self):
        self.clear_main_content()
        
        # Import n8n integration module
        import n8n_integration
        n8n_integration.N8NIntegration(self.main_content, self.user, self.db)
    
    def show_backup_restore(self):
        self.clear_main_content()
        
        # Create backup/restore frame
        backup_frame = ttk.Frame(self.main_content, padding=20)
        backup_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(backup_frame, text="Backup & Restore", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Backup section
        backup_section = ttk.LabelFrame(backup_frame, text="Backup Database", padding=10)
        backup_section.pack(fill=tk.X, pady=10, padx=20)
        
        backup_info = ttk.Label(backup_section, text="Create a backup of your pharmacy database")
        backup_info.pack(pady=5)
        
        backup_btn = ttk.Button(backup_section, text="Create Backup Now", command=self.create_backup)
        backup_btn.pack(pady=5)
        
        # Restore section
        restore_section = ttk.LabelFrame(backup_frame, text="Restore Database", padding=10)
        restore_section.pack(fill=tk.X, pady=10, padx=20)
        
        restore_info = ttk.Label(restore_section, text="Restore your pharmacy database from a backup file")
        restore_info.pack(pady=5)
        
        restore_btn = ttk.Button(restore_section, text="Restore from Backup", command=self.restore_backup)
        restore_btn.pack(pady=5)
        
        # Recent backups
        backups_section = ttk.LabelFrame(backup_frame, text="Recent Backups", padding=10)
        backups_section.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # Create treeview for backups
        columns = ("File Name", "Date", "Size")
        tree = ttk.Treeview(backups_section, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(backups_section, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # List backup files
        self.update_backup_list(tree)
    
    def update_backup_list(self, tree):
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Get backup files
        import glob
        backup_files = glob.glob("backup_*.db")
        
        for file in backup_files:
            try:
                file_size = os.path.getsize(file) / 1024  # KB
                tree.insert("", tk.END, values=(
                    file,
                    datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S'),
                    f"{file_size:.2f} KB"
                ))
            except:
                pass
    
    def create_backup(self):
        try:
            backup_path = self.db.backup_database()
            messagebox.showinfo("Backup Successful", f"Database backup created at: {backup_path}")
            self.status_var.set(f"Backup created: {backup_path}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Error creating backup: {str(e)}")
    
    def restore_backup(self):
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
        )
        
        if file_path:
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore the database? This will replace all current data."
            )
            
            if confirm:
                try:
                    if self.db.restore_database(file_path):
                        messagebox.showinfo("Restore Successful", "Database restored successfully")
                        self.status_var.set("Database restored successfully")
                    else:
                        messagebox.showerror("Restore Failed", "Failed to restore database")
                except Exception as e:
                    messagebox.showerror("Restore Failed", f"Error restoring database: {str(e)}")
    
    def show_settings(self):
        self.clear_main_content()
        
        # Create settings frame
        settings_frame = ttk.Frame(self.main_content, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(settings_frame, text="System Settings", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Store settings tab
        store_tab = ttk.Frame(notebook, padding=10)
        notebook.add(store_tab, text="Store Settings")
        
        # Get current store data
        store = self.db.execute_query("SELECT * FROM stores WHERE id = ?", (self.user['store_id'],))[0]
        
        # Store form
        ttk.Label(store_tab, text="Store Name:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        store_name_var = tk.StringVar(value=store[1])
        store_name_entry = ttk.Entry(store_tab, textvariable=store_name_var, width=30)
        store_name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(store_tab, text="Address:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        store_address_var = tk.StringVar(value=store[2])
        store_address_entry = ttk.Entry(store_tab, textvariable=store_address_var, width=30)
        store_address_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(store_tab, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        store_phone_var = tk.StringVar(value=store[3])
        store_phone_entry = ttk.Entry(store_tab, textvariable=store_phone_var, width=30)
        store_phone_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(store_tab, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        store_email_var = tk.StringVar(value=store[4])
        store_email_entry = ttk.Entry(store_tab, textvariable=store_email_var, width=30)
        store_email_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(store_tab, text="GST Number:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        store_gst_var = tk.StringVar(value=store[6])
        store_gst_entry = ttk.Entry(store_tab, textvariable=store_gst_var, width=30)
        store_gst_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Logo upload
        ttk.Label(store_tab, text="Logo:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        logo_path_var = tk.StringVar(value=store[5])
        logo_path_entry = ttk.Entry(store_tab, textvariable=logo_path_var, width=30)
        logo_path_entry.grid(row=5, column=1, pady=5, padx=5)
        
        def browse_logo():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select Logo Image",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")]
            )
            if file_path:
                logo_path_var.set(file_path)
        
        browse_btn = ttk.Button(store_tab, text="Browse", command=browse_logo)
        browse_btn.grid(row=5, column=2, pady=5, padx=5)
        
        # Save button
        def save_store_settings():
            self.db.execute_update('''
            UPDATE stores SET 
                name = ?, address = ?, phone = ?, email = ?, 
                logo_path = ?, gst_number = ?
            WHERE id = ?
            ''', (
                store_name_var.get(),
                store_address_var.get(),
                store_phone_var.get(),
                store_email_var.get(),
                logo_path_var.get(),
                store_gst_var.get(),
                self.user['store_id']
            ))
            
            messagebox.showinfo("Settings Saved", "Store settings have been updated successfully")
            self.status_var.set("Store settings updated")
        
        save_btn = ttk.Button(store_tab, text="Save Settings", command=save_store_settings)
        save_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # AI Settings tab
        ai_tab = ttk.Frame(notebook, padding=10)
        notebook.add(ai_tab, text="AI Settings")
        
        ttk.Label(ai_tab, text="AI Integration Settings", font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(ai_tab, text="Configure AI features for stock prediction and alternative suggestions").pack(pady=5)
        
        # Placeholder for AI settings
        ai_info = ttk.Frame(ai_tab, padding=10)
        ai_info.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(ai_info, text="AI settings will be available in a future update.").pack(pady=20)
        
        # n8n Settings tab
        n8n_tab = ttk.Frame(notebook, padding=10)
        notebook.add(n8n_tab, text="n8n Settings")
        
        ttk.Label(n8n_tab, text="n8n Workflow Integration", font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(n8n_tab, text="Configure n8n workflow automation settings").pack(pady=5)
        
        # Placeholder for n8n settings
        n8n_info = ttk.Frame(n8n_tab, padding=10)
        n8n_info.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(n8n_info, text="n8n settings will be available in a future update.").pack(pady=20)
    
    def logout(self):
        from auth import AuthSystem
        AuthSystem.logout(self)