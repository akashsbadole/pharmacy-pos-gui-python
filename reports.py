import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pdf_generator

class Reports:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create reports frame
        self.reports_frame = ttk.Frame(parent, padding=20)
        self.reports_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.reports_frame, text="Reports Generation", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for report types
        notebook = ttk.Notebook(self.reports_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Sales Reports tab
        sales_tab = ttk.Frame(notebook, padding=10)
        notebook.add(sales_tab, text="Sales Reports")
        
        # Inventory Reports tab
        inventory_tab = ttk.Frame(notebook, padding=10)
        notebook.add(inventory_tab, text="Inventory Reports")
        
        # Financial Reports tab
        financial_tab = ttk.Frame(notebook, padding=10)
        notebook.add(financial_tab, text="Financial Reports")
        
        # Setup Sales Reports tab
        self.setup_sales_reports_tab(sales_tab)
        
        # Setup Inventory Reports tab
        self.setup_inventory_reports_tab(inventory_tab)
        
        # Setup Financial Reports tab
        self.setup_financial_reports_tab(financial_tab)
    
    def setup_sales_reports_tab(self, parent):
        # Report selection
        ttk.Label(parent, text="Select Report Type:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        report_types = [
            "Daily Sales Report",
            "Weekly Sales Report",
            "Monthly Sales Report",
            "Sales by Medicine",
            "Sales by Customer",
            "Sales by Staff"
        ]
        
        self.sales_report_var = tk.StringVar(value=report_types[0])
        for report_type in report_types:
            ttk.Radiobutton(parent, text=report_type, variable=self.sales_report_var, 
                           value=report_type).pack(anchor=tk.W, padx=20, pady=2)
        
        # Date range
        date_frame = ttk.LabelFrame(parent, text="Date Range", padding=10)
        date_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.sales_from_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        from_entry = ttk.Entry(date_frame, textvariable=self.sales_from_var, width=15)
        from_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.sales_to_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        to_entry = ttk.Entry(date_frame, textvariable=self.sales_to_var, width=15)
        to_entry.grid(row=0, column=3, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = ttk.Button(button_frame, text="Generate Report", command=self.generate_sales_report)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="Export to CSV", command=self.export_sales_report)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        pdf_btn = ttk.Button(button_frame, text="Export to PDF", command=self.export_sales_pdf)
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.sales_results_frame = ttk.Frame(parent)
        self.sales_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder
        ttk.Label(self.sales_results_frame, text="Generate a report to see results here").pack(pady=20)
    
    def setup_inventory_reports_tab(self, parent):
        # Report selection
        ttk.Label(parent, text="Select Report Type:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        report_types = [
            "Current Stock",
            "Low Stock Items",
            "Expiring Soon",
            "Stock Movement",
            "Inventory Valuation"
        ]
        
        self.inventory_report_var = tk.StringVar(value=report_types[0])
        for report_type in report_types:
            ttk.Radiobutton(parent, text=report_type, variable=self.inventory_report_var, 
                           value=report_type).pack(anchor=tk.W, padx=20, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = ttk.Button(button_frame, text="Generate Report", command=self.generate_inventory_report)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="Export to CSV", command=self.export_inventory_report)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        pdf_btn = ttk.Button(button_frame, text="Export to PDF", command=self.export_inventory_pdf)
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.inventory_results_frame = ttk.Frame(parent)
        self.inventory_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder
        ttk.Label(self.inventory_results_frame, text="Generate a report to see results here").pack(pady=20)
    
    def setup_financial_reports_tab(self, parent):
        # Report selection
        ttk.Label(parent, text="Select Report Type:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        report_types = [
            "Revenue Report",
            "Profit Analysis",
            "Tax Report",
            "Payment Method Analysis"
        ]
        
        self.financial_report_var = tk.StringVar(value=report_types[0])
        for report_type in report_types:
            ttk.Radiobutton(parent, text=report_type, variable=self.financial_report_var, 
                           value=report_type).pack(anchor=tk.W, padx=20, pady=2)
        
        # Date range
        date_frame = ttk.LabelFrame(parent, text="Date Range", padding=10)
        date_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ttk.Label(date_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.financial_from_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        from_entry = ttk.Entry(date_frame, textvariable=self.financial_from_var, width=15)
        from_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(date_frame, text="To:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.financial_to_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        to_entry = ttk.Entry(date_frame, textvariable=self.financial_to_var, width=15)
        to_entry.grid(row=0, column=3, pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        generate_btn = ttk.Button(button_frame, text="Generate Report", command=self.generate_financial_report)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="Export to CSV", command=self.export_financial_report)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        pdf_btn = ttk.Button(button_frame, text="Export to PDF", command=self.export_financial_pdf)
        pdf_btn.pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.financial_results_frame = ttk.Frame(parent)
        self.financial_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder
        ttk.Label(self.financial_results_frame, text="Generate a report to see results here").pack(pady=20)
    
    def generate_sales_report(self):
        # Clear previous results
        for widget in self.sales_results_frame.winfo_children():
            widget.destroy()
        
        report_type = self.sales_report_var.get()
        from_date = self.sales_from_var.get()
        to_date = self.sales_to_var.get()
        
        try:
            # Validate dates
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format")
            return
        
        # Generate report based on type
        if report_type == "Daily Sales Report":
            self.generate_daily_sales_report(from_date, to_date)
        elif report_type == "Weekly Sales Report":
            self.generate_weekly_sales_report(from_date, to_date)
        elif report_type == "Monthly Sales Report":
            self.generate_monthly_sales_report(from_date, to_date)
        elif report_type == "Sales by Medicine":
            self.generate_sales_by_medicine_report(from_date, to_date)
        elif report_type == "Sales by Customer":
            self.generate_sales_by_customer_report(from_date, to_date)
        elif report_type == "Sales by Staff":
            self.generate_sales_by_staff_report(from_date, to_date)
    
    def generate_daily_sales_report(self, from_date, to_date):
        # Get daily sales data
        sales_data = self.db.execute_query('''
        SELECT DATE(sale_date) as date, COUNT(*) as transactions, SUM(total_amount) as total
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY DATE(sale_date)
        ORDER BY date
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Date", "Transactions", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0].strftime('%Y-%m-%d'),
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart
        self.create_sales_chart(sales_data, "Daily Sales Report")
    
    def generate_weekly_sales_report(self, from_date, to_date):
        # Get weekly sales data
        sales_data = self.db.execute_query('''
        SELECT strftime('%Y-%W', sale_date) as week, COUNT(*) as transactions, SUM(total_amount) as total
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY strftime('%Y-%W', sale_date)
        ORDER BY week
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Week", "Transactions", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart
        self.create_sales_chart(sales_data, "Weekly Sales Report")
    
    def generate_monthly_sales_report(self, from_date, to_date):
        # Get monthly sales data
        sales_data = self.db.execute_query('''
        SELECT strftime('%Y-%m', sale_date) as month, COUNT(*) as transactions, SUM(total_amount) as total
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY strftime('%Y-%m', sale_date)
        ORDER BY month
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Month", "Transactions", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart
        self.create_sales_chart(sales_data, "Monthly Sales Report")
    
    def generate_sales_by_medicine_report(self, from_date, to_date):
        # Get sales by medicine data
        sales_data = self.db.execute_query('''
        SELECT m.name, SUM(si.quantity) as quantity, SUM(si.quantity * si.price) as total
        FROM sales s
        JOIN sale_items si ON s.id = si.sale_id
        JOIN medicines m ON si.medicine_id = m.id
        WHERE s.store_id = ? AND DATE(s.sale_date) BETWEEN ? AND ?
        GROUP BY m.id
        ORDER BY total DESC
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Medicine", "Quantity Sold", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart (top 10 medicines)
        top_medicines = sales_data[:10]
        self.create_medicine_sales_chart(top_medicines, "Top 10 Medicines by Sales")
    
    def generate_sales_by_customer_report(self, from_date, to_date):
        # Get sales by customer data
        sales_data = self.db.execute_query('''
        SELECT c.name, COUNT(s.id) as transactions, SUM(s.total_amount) as total
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.store_id = ? AND DATE(s.sale_date) BETWEEN ? AND ?
        GROUP BY c.id
        ORDER BY total DESC
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Customer", "Transactions", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0] or "Walk-in",
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart (top 10 customers)
        top_customers = sales_data[:10]
        self.create_customer_sales_chart(top_customers, "Top 10 Customers by Sales")
    
    def generate_sales_by_staff_report(self, from_date, to_date):
        # Get sales by staff data
        sales_data = self.db.execute_query('''
        SELECT u.name, COUNT(s.id) as transactions, SUM(s.total_amount) as total
        FROM sales s
        JOIN users u ON s.user_id = u.id
        WHERE s.store_id = ? AND DATE(s.sale_date) BETWEEN ? AND ?
        GROUP BY u.id
        ORDER BY total DESC
        ''', (self.user['store_id'], from_date, to_date))
        
        if not sales_data:
            ttk.Label(self.sales_results_frame, text="No sales data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Staff", "Transactions", "Total Sales")
        tree = ttk.Treeview(self.sales_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.sales_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in sales_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create chart
        self.create_staff_sales_chart(sales_data, "Sales by Staff")
    
    def generate_inventory_report(self):
        # Clear previous results
        for widget in self.inventory_results_frame.winfo_children():
            widget.destroy()
        
        report_type = self.inventory_report_var.get()
        
        # Generate report based on type
        if report_type == "Current Stock":
            self.generate_current_stock_report()
        elif report_type == "Low Stock Items":
            self.generate_low_stock_report()
        elif report_type == "Expiring Soon":
            self.generate_expiring_soon_report()
        elif report_type == "Stock Movement":
            self.generate_stock_movement_report()
        elif report_type == "Inventory Valuation":
            self.generate_inventory_valuation_report()
    
    def generate_current_stock_report(self):
        # Get current stock data
        stock_data = self.db.execute_query('''
        SELECT id, name, category, stock_quantity, price, cost_price
        FROM medicines
        WHERE store_id = ?
        ORDER BY name
        ''', (self.user['store_id'],))
        
        if not stock_data:
            ttk.Label(self.inventory_results_frame, text="No inventory data found").pack(pady=20)
            return
        
        # Create table
        columns = ("ID", "Name", "Category", "Stock", "Price", "Cost", "Value")
        tree = ttk.Treeview(self.inventory_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        total_value = 0
        for row in stock_data:
            value = row[3] * row[5]  # stock * cost_price
            total_value += value
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                row[2] or "",
                row[3],
                f"${row[4]:.2f}",
                f"${row[5]:.2f}",
                f"${value:.2f}"
            ))
        
        # Display total value
        ttk.Label(self.inventory_results_frame, text=f"Total Inventory Value: ${total_value:.2f}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
    
    def generate_low_stock_report(self):
        # Get low stock data (less than 10 units)
        stock_data = self.db.execute_query('''
        SELECT id, name, category, stock_quantity, price
        FROM medicines
        WHERE store_id = ? AND stock_quantity < 10
        ORDER BY stock_quantity
        ''', (self.user['store_id'],))
        
        if not stock_data:
            ttk.Label(self.inventory_results_frame, text="No low stock items found").pack(pady=20)
            return
        
        # Create table
        columns = ("ID", "Name", "Category", "Stock", "Price")
        tree = ttk.Treeview(self.inventory_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in stock_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                row[2] or "",
                row[3],
                f"${row[4]:.2f}"
            ))
    
    def generate_expiring_soon_report(self):
        # Get medicines expiring within next 90 days
        stock_data = self.db.execute_query('''
        SELECT id, name, category, stock_quantity, expiry_date
        FROM medicines
        WHERE store_id = ? AND expiry_date BETWEEN DATE('now') AND DATE('now', '+90 days')
        ORDER BY expiry_date
        ''', (self.user['store_id'],))
        
        if not stock_data:
            ttk.Label(self.inventory_results_frame, text="No medicines expiring soon found").pack(pady=20)
            return
        
        # Create table
        columns = ("ID", "Name", "Category", "Stock", "Expiry Date")
        tree = ttk.Treeview(self.inventory_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in stock_data:
            expiry_str = row[4].strftime('%Y-%m-%d') if row[4] else ""
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                row[2] or "",
                row[3],
                expiry_str
            ))
    
    def generate_stock_movement_report(self):
        # Get stock movement data (purchases - sales)
        # This is a simplified version - in a real system, you would track each stock movement
        movement_data = self.db.execute_query('''
        SELECT m.id, m.name, m.category, m.stock_quantity,
               (SELECT SUM(pi.quantity) FROM purchase_items pi JOIN purchases p ON pi.purchase_id = p.id 
                WHERE pi.medicine_id = m.id AND p.store_id = ?) as purchased,
               (SELECT SUM(si.quantity) FROM sale_items si JOIN sales s ON si.sale_id = s.id 
                WHERE si.medicine_id = m.id AND s.store_id = ?) as sold
        FROM medicines m
        WHERE m.store_id = ?
        ORDER BY m.name
        ''', (self.user['store_id'], self.user['store_id'], self.user['store_id']))
        
        if not movement_data:
            ttk.Label(self.inventory_results_frame, text="No stock movement data found").pack(pady=20)
            return
        
        # Create table
        columns = ("ID", "Name", "Category", "Current Stock", "Purchased", "Sold", "Net Movement")
        tree = ttk.Treeview(self.inventory_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in movement_data:
            purchased = row[4] or 0
            sold = row[5] or 0
            net_movement = purchased - sold
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                row[2] or "",
                row[3],
                purchased,
                sold,
                net_movement
            ))
    
    def generate_inventory_valuation_report(self):
        # Get inventory valuation data by category
        valuation_data = self.db.execute_query('''
        SELECT category, SUM(stock_quantity * cost_price) as total_value
        FROM medicines
        WHERE store_id = ? AND category IS NOT NULL
        GROUP BY category
        ORDER BY total_value DESC
        ''', (self.user['store_id'],))
        
        if not valuation_data:
            ttk.Label(self.inventory_results_frame, text="No inventory valuation data found").pack(pady=20)
            return
        
        # Create table
        columns = ("Category", "Total Value")
        tree = ttk.Treeview(self.inventory_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        total_value = 0
        for row in valuation_data:
            total_value += row[1]
            tree.insert("", tk.END, values=(
                row[0],
                f"${row[1]:.2f}"
            ))
        
        # Display total value
        ttk.Label(self.inventory_results_frame, text=f"Total Inventory Value: ${total_value:.2f}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create pie chart
        self.create_valuation_pie_chart(valuation_data, "Inventory Valuation by Category")
    
    def generate_financial_report(self):
        # Clear previous results
        for widget in self.financial_results_frame.winfo_children():
            widget.destroy()
        
        report_type = self.financial_report_var.get()
        from_date = self.financial_from_var.get()
        to_date = self.financial_to_var.get()
        
        try:
            # Validate dates
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format")
            return
        
        # Generate report based on type
        if report_type == "Revenue Report":
            self.generate_revenue_report(from_date, to_date)
        elif report_type == "Profit Analysis":
            self.generate_profit_analysis_report(from_date, to_date)
        elif report_type == "Tax Report":
            self.generate_tax_report(from_date, to_date)
        elif report_type == "Payment Method Analysis":
            self.generate_payment_method_report(from_date, to_date)
    
    def generate_revenue_report(self, from_date, to_date):
        # Get revenue data
        revenue_data = self.db.execute_query('''
        SELECT DATE(sale_date) as date, SUM(total_amount) as revenue
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY DATE(sale_date)
        ORDER BY date
        ''', (self.user['store_id'], from_date, to_date))
        
        if not revenue_data:
            ttk.Label(self.financial_results_frame, text="No revenue data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Date", "Revenue")
        tree = ttk.Treeview(self.financial_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.financial_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        total_revenue = 0
        for row in revenue_data:
            total_revenue += row[1]
            tree.insert("", tk.END, values=(
                row[0].strftime('%Y-%m-%d'),
                f"${row[1]:.2f}"
            ))
        
        # Display total revenue
        ttk.Label(self.financial_results_frame, text=f"Total Revenue: ${total_revenue:.2f}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create chart
        self.create_revenue_chart(revenue_data, "Revenue Report")
    
    def generate_profit_analysis_report(self, from_date, to_date):
        # Get profit analysis data
        profit_data = self.db.execute_query('''
        SELECT m.name, 
               SUM(si.quantity * si.price) as revenue,
               SUM(si.quantity * m.cost_price) as cost,
               SUM(si.quantity * (si.price - m.cost_price)) as profit
        FROM sales s
        JOIN sale_items si ON s.id = si.sale_id
        JOIN medicines m ON si.medicine_id = m.id
        WHERE s.store_id = ? AND DATE(s.sale_date) BETWEEN ? AND ?
        GROUP BY m.id
        ORDER BY profit DESC
        ''', (self.user['store_id'], from_date, to_date))
        
        if not profit_data:
            ttk.Label(self.financial_results_frame, text="No profit data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Medicine", "Revenue", "Cost", "Profit", "Margin %")
        tree = ttk.Treeview(self.financial_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.financial_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        total_revenue = 0
        total_cost = 0
        total_profit = 0
        
        for row in profit_data:
            revenue = row[1]
            cost = row[2]
            profit = row[3]
            margin = (profit / revenue * 100) if revenue > 0 else 0
            
            total_revenue += revenue
            total_cost += cost
            total_profit += profit
            
            tree.insert("", tk.END, values=(
                row[0],
                f"${revenue:.2f}",
                f"${cost:.2f}",
                f"${profit:.2f}",
                f"{margin:.1f}%"
            ))
        
        # Display totals
        total_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        summary_frame = ttk.Frame(self.financial_results_frame)
        summary_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(summary_frame, text=f"Total Revenue: ${total_revenue:.2f}", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(summary_frame, text=f"Total Cost: ${total_cost:.2f}", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(summary_frame, text=f"Total Profit: ${total_profit:.2f}", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(summary_frame, text=f"Overall Margin: {total_margin:.1f}%", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Create chart (top 10 medicines by profit)
        top_medicines = profit_data[:10]
        self.create_profit_chart(top_medicines, "Top 10 Medicines by Profit")
    
    def generate_tax_report(self, from_date, to_date):
        # Get tax data
        tax_data = self.db.execute_query('''
        SELECT DATE(sale_date) as date, SUM(tax_amount) as tax
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY DATE(sale_date)
        ORDER BY date
        ''', (self.user['store_id'], from_date, to_date))
        
        if not tax_data:
            ttk.Label(self.financial_results_frame, text="No tax data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Date", "Tax Amount")
        tree = ttk.Treeview(self.financial_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.financial_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        total_tax = 0
        for row in tax_data:
            total_tax += row[1]
            tree.insert("", tk.END, values=(
                row[0].strftime('%Y-%m-%d'),
                f"${row[1]:.2f}"
            ))
        
        # Display total tax
        ttk.Label(self.financial_results_frame, text=f"Total Tax: ${total_tax:.2f}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create chart
        self.create_tax_chart(tax_data, "Tax Report")
    
    def generate_payment_method_report(self, from_date, to_date):
        # Get payment method data
        payment_data = self.db.execute_query('''
        SELECT payment_method, COUNT(*) as transactions, SUM(total_amount) as total
        FROM sales
        WHERE store_id = ? AND DATE(sale_date) BETWEEN ? AND ?
        GROUP BY payment_method
        ORDER BY total DESC
        ''', (self.user['store_id'], from_date, to_date))
        
        if not payment_data:
            ttk.Label(self.financial_results_frame, text="No payment method data found for the selected period").pack(pady=20)
            return
        
        # Create table
        columns = ("Payment Method", "Transactions", "Total Amount")
        tree = ttk.Treeview(self.financial_results_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.financial_results_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data
        for row in payment_data:
            tree.insert("", tk.END, values=(
                row[0],
                row[1],
                f"${row[2]:.2f}"
            ))
        
        # Create pie chart
        self.create_payment_pie_chart(payment_data, "Payment Method Distribution")
    
    # Chart creation functions
    def create_sales_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = [row[0] for row in data]
        totals = [row[2] for row in data]
        
        ax.bar(dates, totals)
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Sales ($)')
        ax.tick_params(axis='x', rotation=45)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.sales_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_medicine_sales_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        medicines = [row[0] for row in data]
        totals = [row[2] for row in data]
        
        ax.barh(medicines, totals)
        ax.set_title(title)
        ax.set_xlabel('Total Sales ($)')
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.sales_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_customer_sales_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        customers = [row[0] for row in data]
        totals = [row[2] for row in data]
        
        ax.barh(customers, totals)
        ax.set_title(title)
        ax.set_xlabel('Total Sales ($)')
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.sales_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_staff_sales_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        staff = [row[0] for row in data]
        totals = [row[2] for row in data]
        
        ax.bar(staff, totals)
        ax.set_title(title)
        ax.set_xlabel('Staff')
        ax.set_ylabel('Total Sales ($)')
        ax.tick_params(axis='x', rotation=45)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.sales_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_valuation_pie_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        categories = [row[0] for row in data]
        values = [row[1] for row in data]
        
        ax.pie(values, labels=categories, autopct='%1.1f%%')
        ax.set_title(title)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.inventory_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_revenue_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = [row[0] for row in data]
        revenues = [row[1] for row in data]
        
        ax.plot(dates, revenues, marker='o')
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Revenue ($)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.financial_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_profit_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        medicines = [row[0] for row in data]
        profits = [row[3] for row in data]
        
        ax.barh(medicines, profits)
        ax.set_title(title)
        ax.set_xlabel('Profit ($)')
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.financial_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_tax_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = [row[0] for row in data]
        taxes = [row[1] for row in data]
        
        ax.bar(dates, taxes)
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Tax Amount ($)')
        ax.tick_params(axis='x', rotation=45)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.financial_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_payment_pie_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(8, 6))
        
        methods = [row[0] for row in data]
        totals = [row[2] for row in data]
        
        ax.pie(totals, labels=methods, autopct='%1.1f%%')
        ax.set_title(title)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.financial_results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Export functions
    def export_sales_report(self):
        # Placeholder for export functionality
        messagebox.showinfo("Export", "Sales report export functionality would be implemented here")
    
    def export_sales_pdf(self):
        # Placeholder for PDF export functionality
        messagebox.showinfo("Export", "Sales report PDF export functionality would be implemented here")
    
    def export_inventory_report(self):
        # Placeholder for export functionality
        messagebox.showinfo("Export", "Inventory report export functionality would be implemented here")
    
    def export_inventory_pdf(self):
        # Placeholder for PDF export functionality
        messagebox.showinfo("Export", "Inventory report PDF export functionality would be implemented here")
    
    def export_financial_report(self):
        # Placeholder for export functionality
        messagebox.showinfo("Export", "Financial report export functionality would be implemented here")
    
    def export_financial_pdf(self):
        # Placeholder for PDF export functionality
        messagebox.showinfo("Export", "Financial report PDF export functionality would be implemented here")