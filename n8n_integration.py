import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class N8NIntegration:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create n8n frame
        self.n8n_frame = ttk.Frame(parent, padding=20)
        self.n8n_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.n8n_frame, text="n8n Workflow Integration", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Description
        desc_label = ttk.Label(self.n8n_frame, text="Connect to n8n for workflow automation", font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(self.n8n_frame, text="n8n Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(config_frame, text="n8n URL:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.n8n_url_var = tk.StringVar(value="http://localhost:5678")
        n8n_url_entry = ttk.Entry(config_frame, textvariable=self.n8n_url_var, width=40)
        n8n_url_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(config_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, width=40, show="*")
        api_key_entry.grid(row=1, column=1, pady=5, padx=5)
        
        test_btn = ttk.Button(config_frame, text="Test Connection", command=self.test_connection)
        test_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Workflows frame
        workflows_frame = ttk.LabelFrame(self.n8n_frame, text="Available Workflows", padding=10)
        workflows_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for workflows
        columns = ("ID", "Name", "Active", "Last Executed")
        self.workflows_tree = ttk.Treeview(workflows_frame, columns=columns, show="headings")
        
        for col in columns:
            self.workflows_tree.heading(col, text=col)
            self.workflows_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(workflows_frame, orient=tk.VERTICAL, command=self.workflows_tree.yview)
        self.workflows_tree.configure(yscrollcommand=scrollbar.set)
        
        self.workflows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons_frame = ttk.Frame(self.n8n_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        refresh_btn = ttk.Button(buttons_frame, text="Refresh Workflows", command=self.load_workflows)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        execute_btn = ttk.Button(buttons_frame, text="Execute Workflow", command=self.execute_workflow)
        execute_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.n8n_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load workflows
        self.load_workflows()
    
    def test_connection(self):
        url = f"{self.n8n_url_var.get()}/rest/workflows"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.api_key_var.get():
            headers["Authorization"] = f"Bearer {self.api_key_var.get()}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.status_var.set("Connection successful")
                messagebox.showinfo("Connection Test", "Successfully connected to n8n")
            else:
                self.status_var.set(f"Connection failed: {response.status_code}")
                messagebox.showerror("Connection Test", f"Failed to connect to n8n: {response.status_code}")
        except Exception as e:
            self.status_var.set(f"Connection error: {str(e)}")
            messagebox.showerror("Connection Test", f"Error connecting to n8n: {str(e)}")
    
    def load_workflows(self):
        url = f"{self.n8n_url_var.get()}/rest/workflows"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.api_key_var.get():
            headers["Authorization"] = f"Bearer {self.api_key_var.get()}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                workflows = response.json()['data']
                
                # Clear existing items
                for item in self.workflows_tree.get_children():
                    self.workflows_tree.delete(item)
                
                # Add workflows to tree
                for workflow in workflows:
                    self.workflows_tree.insert("", tk.END, values=(
                        workflow['id'],
                        workflow['name'],
                        "Yes" if workflow['active'] else "No",
                        workflow.get('lastExecution', {}).get('startedAt', 'Never')
                    ))
                
                self.status_var.set(f"Loaded {len(workflows)} workflows")
            else:
                self.status_var.set(f"Failed to load workflows: {response.status_code}")
                messagebox.showerror("Error", f"Failed to load workflows: {response.status_code}")
        except Exception as e:
            self.status_var.set(f"Error loading workflows: {str(e)}")
            messagebox.showerror("Error", f"Error loading workflows: {str(e)}")
    
    def execute_workflow(self):
        # Get selected workflow
        selected = self.workflows_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a workflow to execute")
            return
        
        item = self.workflows_tree.item(selected[0])
        workflow_id = item['values'][0]
        workflow_name = item['values'][1]
        
        # Confirm execution
        confirm = messagebox.askyesno(
            "Confirm Execution",
            f"Are you sure you want to execute the workflow '{workflow_name}'?"
        )
        
        if confirm:
            url = f"{self.n8n_url_var.get()}/rest/workflows/{workflow_id}/run"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            if self.api_key_var.get():
                headers["Authorization"] = f"Bearer {self.api_key_var.get()}"
            
            try:
                response = requests.post(url, headers=headers)
                
                if response.status_code == 200:
                    execution_data = response.json()
                    execution_id = execution_data.get('data', {}).get('executionId', '')
                    
                    self.status_var.set(f"Workflow '{workflow_name}' executed successfully")
                    messagebox.showinfo("Execution Successful", f"Workflow '{workflow_name}' executed successfully\nExecution ID: {execution_id}")
                else:
                    self.status_var.set(f"Execution failed: {response.status_code}")
                    messagebox.showerror("Execution Failed", f"Failed to execute workflow: {response.status_code}")
            except Exception as e:
                self.status_var.set(f"Execution error: {str(e)}")
                messagebox.showerror("Execution Error", f"Error executing workflow: {str(e)}")
    
    def send_sale_data_to_n8n(self, sale_id):
        """
        Send sale data to n8n webhook
        
        Args:
            sale_id (int): ID of the sale to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get sale details
        sale = self.db.execute_query('''
        SELECT s.id, s.invoice_number, c.name, c.phone, s.total_amount, s.discount_amount, 
               s.tax_amount, s.payment_method, s.sale_date, u.name, st.name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN stores st ON s.store_id = st.id
        WHERE s.id = ?
        ''', (sale_id,))
        
        if not sale:
            return False
        
        sale = sale[0]
        
        # Get sale items
        sale_items = self.db.execute_query('''
        SELECT m.name, si.quantity, si.price, (si.quantity * si.price) as total
        FROM sale_items si
        JOIN medicines m ON si.medicine_id = m.id
        WHERE si.sale_id = ?
        ''', (sale_id,))
        
        # Prepare data
        data = {
            'sale_id': sale[0],
            'invoice_number': sale[1],
            'customer_name': sale[2] or "Walk-in",
            'customer_phone': sale[3] or "",
            'total_amount': sale[4],
            'discount_amount': sale[5],
            'tax_amount': sale[6],
            'payment_method': sale[7],
            'sale_date': sale[8].strftime('%Y-%m-%d %H:%M:%S'),
            'staff_name': sale[9],
            'store_name': sale[10],
            'items': [
                {
                    'name': item[0],
                    'quantity': item[1],
                    'price': item[2],
                    'total': item[3]
                } for item in sale_items
            ]
        }
        
        # Send to n8n
        url = f"{self.n8n_url_var.get()}/webhook/sale-data"
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key_var.get():
            headers["Authorization"] = f"Bearer {self.api_key_var.get()}"
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Failed to send sale data to n8n: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending sale data to n8n: {str(e)}")
            return False