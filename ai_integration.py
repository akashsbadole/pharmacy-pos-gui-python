# ai_integration.py

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class AIIntegration:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create AI frame
        self.ai_frame = ttk.Frame(parent, padding=20)
        self.ai_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.ai_frame, text="AI Integration", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.ai_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Stock Prediction tab
        prediction_tab = ttk.Frame(notebook, padding=10)
        notebook.add(prediction_tab, text="Stock Prediction")
        
        # Alternative Suggestions tab
        alternatives_tab = ttk.Frame(notebook, padding=10)
        notebook.add(alternatives_tab, text="Alternative Suggestions")
        
        # Setup Stock Prediction tab
        self.setup_prediction_tab(prediction_tab)
        
        # Setup Alternative Suggestions tab
        self.setup_alternatives_tab(alternatives_tab)
    
    def setup_prediction_tab(self, parent):
        # Description
        desc_label = ttk.Label(parent, text="Predict future stock requirements based on historical sales data", font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(controls_frame, text="Medicine:").pack(side=tk.LEFT, padx=5)
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(controls_frame, textvariable=self.medicine_var, width=30)
        self.medicine_combo.pack(side=tk.LEFT, padx=5)
        
        # Get medicines
        medicines = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id = ?", (self.user['store_id'],))
        self.medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        predict_btn = ttk.Button(controls_frame, text="Predict Stock", command=self.predict_stock)
        predict_btn.pack(side=tk.LEFT, padx=10)
        
        # Results frame
        self.results_frame = ttk.Frame(parent)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder for results
        self.placeholder_label = ttk.Label(self.results_frame, text="Select a medicine and click 'Predict Stock' to see predictions")
        self.placeholder_label.pack(pady=20)
    
    def setup_alternatives_tab(self, parent):
        # Description
        desc_label = ttk.Label(parent, text="Find alternative medicines based on active ingredients and therapeutic effects", font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(controls_frame, text="Medicine:").pack(side=tk.LEFT, padx=5)
        self.alt_medicine_var = tk.StringVar()
        self.alt_medicine_combo = ttk.Combobox(controls_frame, textvariable=self.alt_medicine_var, width=30)
        self.alt_medicine_combo.pack(side=tk.LEFT, padx=5)
        
        # Get medicines
        medicines = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id = ?", (self.user['store_id'],))
        self.alt_medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        find_btn = ttk.Button(controls_frame, text="Find Alternatives", command=self.find_alternatives)
        find_btn.pack(side=tk.LEFT, padx=10)
        
        # Results frame
        self.alt_results_frame = ttk.Frame(parent)
        self.alt_results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Placeholder for results
        self.alt_placeholder_label = ttk.Label(self.alt_results_frame, text="Select a medicine and click 'Find Alternatives' to see similar medicines")
        self.alt_placeholder_label.pack(pady=20)
    
    def predict_stock(self):
        # Get selected medicine
        medicine_text = self.medicine_var.get()
        if not medicine_text:
            messagebox.showinfo("Selection Required", "Please select a medicine")
            return
        
        try:
            medicine_id = int(medicine_text.split(' - ')[0])
            
            # Get medicine details
            medicine = self.db.execute_query('''
            SELECT id, name
            FROM medicines
            WHERE id = ? AND store_id = ?
            ''', (medicine_id, self.user['store_id']))
            
            if not medicine:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            medicine = medicine[0]
            
            # Get sales data for this medicine
            sales_data = self.db.execute_query('''
            SELECT DATE(sale_date) as sale_date, SUM(si.quantity) as quantity
            FROM sales s
            JOIN sale_items si ON s.id = si.sale_id
            WHERE si.medicine_id = ? AND s.store_id = ?
            GROUP BY DATE(sale_date)
            ORDER BY sale_date
            ''', (medicine_id, self.user['store_id']))
            
            if not sales_data:
                messagebox.showinfo("No Data", f"No sales data found for {medicine[1]}")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(sales_data, columns=['sale_date', 'quantity'])
            df['sale_date'] = pd.to_datetime(df['sale_date'])
            df['day_of_week'] = df['sale_date'].dt.dayofweek
            df['month'] = df['sale_date'].dt.month
            df['day_of_month'] = df['sale_date'].dt.day
            
            # Prepare features and target
            X = df[['day_of_week', 'month', 'day_of_month']]
            y = df['quantity']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Make predictions for next 30 days
            future_dates = pd.date_range(start=df['sale_date'].max() + pd.Timedelta(days=1), periods=30)
            future_df = pd.DataFrame({
                'sale_date': future_dates,
                'day_of_week': future_dates.dayofweek,
                'month': future_dates.month,
                'day_of_month': future_dates.day
            })
            
            future_X = future_df[['day_of_week', 'month', 'day_of_month']]
            future_df['predicted_quantity'] = model.predict(future_X)
            
            # Round predictions to integers
            future_df['predicted_quantity'] = future_df['predicted_quantity'].round().astype(int)
            
            # Clear previous results
            for widget in self.results_frame.winfo_children():
                widget.destroy()
            
            # Create results frame
            results_title = ttk.Label(self.results_frame, text=f"Stock Prediction for {medicine[1]}", font=('Arial', 14, 'bold'))
            results_title.pack(pady=10)
            
            # Create table for predictions
            columns = ("Date", "Predicted Quantity")
            tree = ttk.Treeview(self.results_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Add predictions to table
            for _, row in future_df.iterrows():
                tree.insert("", tk.END, values=(
                    row['sale_date'].strftime('%Y-%m-%d'),
                    row['predicted_quantity']
                ))
            
            # Create plot
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Plot historical data
            ax.plot(df['sale_date'], df['quantity'], label='Historical Sales', marker='o')
            
            # Plot predictions
            ax.plot(future_df['sale_date'], future_df['predicted_quantity'], label='Predicted Sales', marker='x', linestyle='--')
            
            ax.set_title(f'Stock Prediction for {medicine[1]}')
            ax.set_xlabel('Date')
            ax.set_ylabel('Quantity')
            ax.legend()
            ax.grid(True)
            
            # Embed plot in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.results_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Prediction Error", f"Error making prediction: {str(e)}")
    
    def find_alternatives(self):
        # Get selected medicine
        medicine_text = self.alt_medicine_var.get()
        if not medicine_text:
            messagebox.showinfo("Selection Required", "Please select a medicine")
            return
        
        try:
            medicine_id = int(medicine_text.split(' - ')[0])
            
            # Get medicine details
            medicine = self.db.execute_query('''
            SELECT id, name, category, description
            FROM medicines
            WHERE id = ? AND store_id = ?
            ''', (medicine_id, self.user['store_id']))
            
            if not medicine:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            medicine = medicine[0]
            
            # Find similar medicines (same category, different ID)
            alternatives = self.db.execute_query('''
            SELECT id, name, category, description, price, stock_quantity
            FROM medicines
            WHERE category = ? AND id != ? AND store_id = ? AND stock_quantity > 0
            ORDER BY name
            ''', (medicine[2], medicine_id, self.user['store_id']))
            
            # Clear previous results
            for widget in self.alt_results_frame.winfo_children():
                widget.destroy()
            
            # Create results frame
            results_title = ttk.Label(self.alt_results_frame, text=f"Alternatives for {medicine[1]}", font=('Arial', 14, 'bold'))
            results_title.pack(pady=10)
            
            if not alternatives:
                no_results = ttk.Label(self.alt_results_frame, text="No alternatives found")
                no_results.pack(pady=20)
                return
            
            # Create table for alternatives
            columns = ("ID", "Name", "Category", "Price", "Stock")
            tree = ttk.Treeview(self.alt_results_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.alt_results_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Add alternatives to table
            for alt in alternatives:
                tree.insert("", tk.END, values=(
                    alt[0],  # ID
                    alt[1],  # Name
                    alt[2] or "",  # Category
                    f"${alt[4]:.2f}",  # Price
                    alt[5]  # Stock
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error finding alternatives: {str(e)}")