import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class Prescriptions:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        
        # Create prescriptions frame
        self.prescriptions_frame = ttk.Frame(parent, padding=20)
        self.prescriptions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.prescriptions_frame, text="Prescription Management", font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.prescriptions_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Prescriptions tab
        prescriptions_tab = ttk.Frame(notebook, padding=10)
        notebook.add(prescriptions_tab, text="Prescriptions")
        
        # Refill Reminders tab
        reminders_tab = ttk.Frame(notebook, padding=10)
        notebook.add(reminders_tab, text="Refill Reminders")
        
        # Setup Prescriptions tab
        self.setup_prescriptions_tab(prescriptions_tab)
        
        # Setup Refill Reminders tab
        self.setup_reminders_tab(reminders_tab)
    
    def setup_prescriptions_tab(self, parent):
        # Search section
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_prescriptions)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Add Prescription", command=self.add_prescription)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = ttk.Button(buttons_frame, text="Edit Prescription", command=self.edit_prescription)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(buttons_frame, text="Delete Prescription", command=self.delete_prescription)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        view_btn = ttk.Button(buttons_frame, text="View Details", command=self.view_prescription)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # Prescriptions table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for prescriptions
        columns = ("ID", "Customer", "Doctor", "Date", "Notes")
        self.prescriptions_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.prescriptions_tree.heading(col, text=col)
            self.prescriptions_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.prescriptions_tree.yview)
        self.prescriptions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.prescriptions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load prescriptions data
        self.load_prescriptions()
        
        # Bind double-click event
        self.prescriptions_tree.bind("<Double-1>", self.on_double_click)
    
    def setup_reminders_tab(self, parent):
        # Description
        desc_label = ttk.Label(parent, text="Prescriptions that need refilling soon", font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Reminders table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for reminders
        columns = ("ID", "Customer", "Medicine", "Days Left", "Last Refill")
        self.reminders_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.reminders_tree.heading(col, text=col)
            self.reminders_tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.reminders_tree.yview)
        self.reminders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reminders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load reminders data
        self.load_reminders()
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        notify_btn = ttk.Button(buttons_frame, text="Send Reminder", command=self.send_reminder)
        notify_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(buttons_frame, text="Refresh", command=self.load_reminders)
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def load_prescriptions(self):
        # Clear existing items
        for item in self.prescriptions_tree.get_children():
            self.prescriptions_tree.delete(item)
        
        # Get prescriptions data
        prescriptions = self.db.execute_query('''
        SELECT p.id, c.name, p.doctor_name, p.prescription_date, p.notes
        FROM prescriptions p
        LEFT JOIN customers c ON p.customer_id = c.id
        ORDER BY p.prescription_date DESC
        ''')
        
        for prescription in prescriptions:
            date_str = prescription[3].strftime('%Y-%m-%d') if prescription[3] else ""
            self.prescriptions_tree.insert("", tk.END, values=(
                prescription[0],  # ID
                prescription[1] or "Unknown",  # Customer
                prescription[2] or "",  # Doctor
                date_str,  # Date
                prescription[4] or ""  # Notes
            ))
    
    def filter_prescriptions(self, *args):
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.prescriptions_tree.get_children():
            self.prescriptions_tree.delete(item)
        
        # Get filtered prescriptions data
        query = '''
        SELECT p.id, c.name, p.doctor_name, p.prescription_date, p.notes
        FROM prescriptions p
        LEFT JOIN customers c ON p.customer_id = c.id
        '''
        params = []
        
        if search_term:
            query += " WHERE (LOWER(c.name) LIKE ? OR LOWER(p.doctor_name) LIKE ? OR LOWER(p.notes) LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY p.prescription_date DESC"
        
        prescriptions = self.db.execute_query(query, params)
        
        for prescription in prescriptions:
            date_str = prescription[3].strftime('%Y-%m-%d') if prescription[3] else ""
            self.prescriptions_tree.insert("", tk.END, values=(
                prescription[0],  # ID
                prescription[1] or "Unknown",  # Customer
                prescription[2] or "",  # Doctor
                date_str,  # Date
                prescription[4] or ""  # Notes
            ))
    
    def on_double_click(self, event):
        self.view_prescription()
    
    def add_prescription(self):
        # Create add prescription dialog
        add_dialog = tk.Toplevel(self.parent)
        add_dialog.title("Add Prescription")
        add_dialog.geometry("600x500")
        add_dialog.resizable(False, False)
        
        # Prescription form
        ttk.Label(add_dialog, text="Prescription Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(add_dialog, text="Customer:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(add_dialog, textvariable=customer_var, width=40)
        customer_combo.grid(row=1, column=1, pady=5, padx=10)
        
        # Get customers
        customers = self.db.execute_query("SELECT id, name FROM customers")
        customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in customers]
        
        ttk.Label(add_dialog, text="Doctor Name:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        doctor_var = tk.StringVar()
        doctor_entry = ttk.Entry(add_dialog, textvariable=doctor_var, width=40)
        doctor_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Diagnosis:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        diagnosis_var = tk.StringVar()
        diagnosis_entry = ttk.Entry(add_dialog, textvariable=diagnosis_var, width=40)
        diagnosis_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Prescription Date:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(add_dialog, textvariable=date_var, width=40)
        date_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Notes:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(add_dialog, textvariable=notes_var, width=40)
        notes_entry.grid(row=5, column=1, pady=5, padx=10)
        
        # Medicines section
        ttk.Label(add_dialog, text="Medicines", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Medicine form
        ttk.Label(add_dialog, text="Medicine:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=10)
        medicine_var = tk.StringVar()
        medicine_combo = ttk.Combobox(add_dialog, textvariable=medicine_var, width=40)
        medicine_combo.grid(row=7, column=1, pady=5, padx=10)
        
        # Get medicines
        medicines = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id = ?", (self.user['store_id'],))
        medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        ttk.Label(add_dialog, text="Dosage:").grid(row=8, column=0, sticky=tk.W, pady=5, padx=10)
        dosage_var = tk.StringVar()
        dosage_entry = ttk.Entry(add_dialog, textvariable=dosage_var, width=40)
        dosage_entry.grid(row=8, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Duration:").grid(row=9, column=0, sticky=tk.W, pady=5, padx=10)
        duration_var = tk.StringVar()
        duration_entry = ttk.Entry(add_dialog, textvariable=duration_var, width=40)
        duration_entry.grid(row=9, column=1, pady=5, padx=10)
        
        ttk.Label(add_dialog, text="Instructions:").grid(row=10, column=0, sticky=tk.W, pady=5, padx=10)
        instructions_var = tk.StringVar()
        instructions_entry = ttk.Entry(add_dialog, textvariable=instructions_var, width=40)
        instructions_entry.grid(row=10, column=1, pady=5, padx=10)
        
        # Add medicine button
        add_medicine_btn = ttk.Button(add_dialog, text="Add Medicine", command=lambda: self.add_medicine_to_list(
            medicine_var, dosage_var, duration_var, instructions_var, medicines_list
        ))
        add_medicine_btn.grid(row=11, column=0, columnspan=2, pady=5)
        
        # Medicines list
        ttk.Label(add_dialog, text="Medicines in Prescription", font=('Arial', 10, 'bold')).grid(row=12, column=0, columnspan=2, pady=5)
        
        medicines_list_frame = ttk.Frame(add_dialog)
        medicines_list_frame.grid(row=13, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        # Create treeview for medicines list
        columns = ("ID", "Name", "Dosage", "Duration", "Instructions")
        medicines_list = ttk.Treeview(medicines_list_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            medicines_list.heading(col, text=col)
            medicines_list.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(medicines_list_frame, orient=tk.VERTICAL, command=medicines_list.yview)
        medicines_list.configure(yscrollcommand=scrollbar.set)
        
        medicines_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(add_dialog)
        button_frame.grid(row=14, column=0, columnspan=2, pady=10)
        
        def save_prescription():
            try:
                # Validate inputs
                if not customer_var.get():
                    messagebox.showerror("Validation Error", "Customer is required")
                    return
                
                # Get customer ID
                try:
                    customer_id = int(customer_var.get().split(' - ')[0])
                except ValueError:
                    messagebox.showerror("Validation Error", "Invalid customer selection")
                    return
                
                # Get prescription date
                try:
                    prescription_date = datetime.strptime(date_var.get(), '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Validation Error", "Invalid date format. Use YYYY-MM-DD")
                    return
                
                # Insert prescription
                prescription_id = self.db.execute_update('''
                INSERT INTO prescriptions (customer_id, doctor_name, diagnosis, prescription_date, notes)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    customer_id,
                    doctor_var.get(),
                    diagnosis_var.get(),
                    prescription_date,
                    notes_var.get()
                ))
                
                # Add medicines to prescription
                for item in medicines_list.get_children():
                    values = medicines_list.item(item)['values']
                    medicine_id = values[0]
                    dosage = values[2]
                    duration = values[3]
                    instructions = values[4]
                    
                    self.db.execute_update('''
                    INSERT INTO prescription_items (prescription_id, medicine_id, dosage, duration, instructions)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        prescription_id,
                        medicine_id,
                        dosage,
                        duration,
                        instructions
                    ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "CREATE", "prescriptions", prescription_id)
                )
                
                messagebox.showinfo("Success", "Prescription added successfully")
                add_dialog.destroy()
                self.load_prescriptions()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        save_btn = ttk.Button(button_frame, text="Save Prescription", command=save_prescription)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def add_medicine_to_list(self, medicine_var, dosage_var, duration_var, instructions_var, medicines_list):
        medicine_text = medicine_var.get()
        if not medicine_text:
            messagebox.showinfo("Selection Required", "Please select a medicine")
            return
        
        try:
            medicine_id = int(medicine_text.split(' - ')[0])
            medicine_name = medicine_text.split(' - ')[1]
            
            dosage = dosage_var.get()
            duration = duration_var.get()
            instructions = instructions_var.get()
            
            # Add to list
            medicines_list.insert("", tk.END, values=(
                medicine_id,
                medicine_name,
                dosage,
                duration,
                instructions
            ))
            
            # Clear form
            medicine_var.set("")
            dosage_var.set("")
            duration_var.set("")
            instructions_var.set("")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please select a valid medicine")
    
    def edit_prescription(self):
        # Get selected prescription
        selected = self.prescriptions_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a prescription to edit")
            return
        
        item = self.prescriptions_tree.item(selected[0])
        prescription_id = item['values'][0]
        
        # Get prescription details
        prescription = self.db.execute_query('''
        SELECT p.id, p.customer_id, c.name, p.doctor_name, p.diagnosis, p.prescription_date, p.notes
        FROM prescriptions p
        LEFT JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
        ''', (prescription_id,))
        
        if not prescription:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        prescription = prescription[0]
        
        # Get prescription items
        prescription_items = self.db.execute_query('''
        SELECT pi.id, m.id, m.name, pi.dosage, pi.duration, pi.instructions
        FROM prescription_items pi
        JOIN medicines m ON pi.medicine_id = m.id
        WHERE pi.prescription_id = ?
        ''', (prescription_id,))
        
        # Create edit prescription dialog
        edit_dialog = tk.Toplevel(self.parent)
        edit_dialog.title("Edit Prescription")
        edit_dialog.geometry("600x500")
        edit_dialog.resizable(False, False)
        
        # Prescription form
        ttk.Label(edit_dialog, text="Prescription Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(edit_dialog, text="Customer:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        customer_var = tk.StringVar(value=f"{prescription[1]} - {prescription[2]}")
        customer_combo = ttk.Combobox(edit_dialog, textvariable=customer_var, width=40)
        customer_combo.grid(row=1, column=1, pady=5, padx=10)
        
        # Get customers
        customers = self.db.execute_query("SELECT id, name FROM customers")
        customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in customers]
        
        ttk.Label(edit_dialog, text="Doctor Name:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=10)
        doctor_var = tk.StringVar(value=prescription[3] or "")
        doctor_entry = ttk.Entry(edit_dialog, textvariable=doctor_var, width=40)
        doctor_entry.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Diagnosis:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=10)
        diagnosis_var = tk.StringVar(value=prescription[4] or "")
        diagnosis_entry = ttk.Entry(edit_dialog, textvariable=diagnosis_var, width=40)
        diagnosis_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Prescription Date:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=10)
        date_var = tk.StringVar(value=prescription[5].strftime('%Y-%m-%d') if prescription[5] else "")
        date_entry = ttk.Entry(edit_dialog, textvariable=date_var, width=40)
        date_entry.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Notes:").grid(row=5, column=0, sticky=tk.W, pady=5, padx=10)
        notes_var = tk.StringVar(value=prescription[6] or "")
        notes_entry = ttk.Entry(edit_dialog, textvariable=notes_var, width=40)
        notes_entry.grid(row=5, column=1, pady=5, padx=10)
        
        # Medicines section
        ttk.Label(edit_dialog, text="Medicines", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Medicine form
        ttk.Label(edit_dialog, text="Medicine:").grid(row=7, column=0, sticky=tk.W, pady=5, padx=10)
        medicine_var = tk.StringVar()
        medicine_combo = ttk.Combobox(edit_dialog, textvariable=medicine_var, width=40)
        medicine_combo.grid(row=7, column=1, pady=5, padx=10)
        
        # Get medicines
        medicines = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id = ?", (self.user['store_id'],))
        medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
        
        ttk.Label(edit_dialog, text="Dosage:").grid(row=8, column=0, sticky=tk.W, pady=5, padx=10)
        dosage_var = tk.StringVar()
        dosage_entry = ttk.Entry(edit_dialog, textvariable=dosage_var, width=40)
        dosage_entry.grid(row=8, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Duration:").grid(row=9, column=0, sticky=tk.W, pady=5, padx=10)
        duration_var = tk.StringVar()
        duration_entry = ttk.Entry(edit_dialog, textvariable=duration_var, width=40)
        duration_entry.grid(row=9, column=1, pady=5, padx=10)
        
        ttk.Label(edit_dialog, text="Instructions:").grid(row=10, column=0, sticky=tk.W, pady=5, padx=10)
        instructions_var = tk.StringVar()
        instructions_entry = ttk.Entry(edit_dialog, textvariable=instructions_var, width=40)
        instructions_entry.grid(row=10, column=1, pady=5, padx=10)
        
        # Add medicine button
        add_medicine_btn = ttk.Button(edit_dialog, text="Add Medicine", command=lambda: self.add_medicine_to_list(
            medicine_var, dosage_var, duration_var, instructions_var, medicines_list
        ))
        add_medicine_btn.grid(row=11, column=0, columnspan=2, pady=5)
        
        # Medicines list
        ttk.Label(edit_dialog, text="Medicines in Prescription", font=('Arial', 10, 'bold')).grid(row=12, column=0, columnspan=2, pady=5)
        
        medicines_list_frame = ttk.Frame(edit_dialog)
        medicines_list_frame.grid(row=13, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        # Create treeview for medicines list
        columns = ("ID", "Name", "Dosage", "Duration", "Instructions")
        medicines_list = ttk.Treeview(medicines_list_frame, columns=columns, show="headings", height=5)
        
        for col in columns:
            medicines_list.heading(col, text=col)
            medicines_list.column(col, width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(medicines_list_frame, orient=tk.VERTICAL, command=medicines_list.yview)
        medicines_list.configure(yscrollcommand=scrollbar.set)
        
        medicines_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add existing medicines
        for item in prescription_items:
            medicines_list.insert("", tk.END, values=(
                item[1],  # Medicine ID
                item[2],  # Medicine Name
                item[3],  # Dosage
                item[4],  # Duration
                item[5]   # Instructions
            ))
        
        # Buttons
        button_frame = ttk.Frame(edit_dialog)
        button_frame.grid(row=14, column=0, columnspan=2, pady=10)
        
        def update_prescription():
            try:
                # Validate inputs
                if not customer_var.get():
                    messagebox.showerror("Validation Error", "Customer is required")
                    return
                
                # Get customer ID
                try:
                    customer_id = int(customer_var.get().split(' - ')[0])
                except ValueError:
                    messagebox.showerror("Validation Error", "Invalid customer selection")
                    return
                
                # Get prescription date
                try:
                    prescription_date = datetime.strptime(date_var.get(), '%Y-%m-%d').date()
                except ValueError:
                    messagebox.showerror("Validation Error", "Invalid date format. Use YYYY-MM-DD")
                    return
                
                # Update prescription
                self.db.execute_update('''
                UPDATE prescriptions SET 
                    customer_id = ?, doctor_name = ?, diagnosis = ?, prescription_date = ?, notes = ?
                WHERE id = ?
                ''', (
                    customer_id,
                    doctor_var.get(),
                    diagnosis_var.get(),
                    prescription_date,
                    notes_var.get(),
                    prescription_id
                ))
                
                # Delete existing prescription items
                self.db.execute_update("DELETE FROM prescription_items WHERE prescription_id = ?", (prescription_id,))
                
                # Add medicines to prescription
                for item in medicines_list.get_children():
                    values = medicines_list.item(item)['values']
                    medicine_id = values[0]
                    dosage = values[2]
                    duration = values[3]
                    instructions = values[4]
                    
                    self.db.execute_update('''
                    INSERT INTO prescription_items (prescription_id, medicine_id, dosage, duration, instructions)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        prescription_id,
                        medicine_id,
                        dosage,
                        duration,
                        instructions
                    ))
                
                # Log the action
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "UPDATE", "prescriptions", prescription_id)
                )
                
                messagebox.showinfo("Success", "Prescription updated successfully")
                edit_dialog.destroy()
                self.load_prescriptions()
                
            except Exception as e:
                messagebox.showerror("Validation Error", f"Invalid input: {str(e)}")
        
        update_btn = ttk.Button(button_frame, text="Update Prescription", command=update_prescription)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def delete_prescription(self):
        # Get selected prescription
        selected = self.prescriptions_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a prescription to delete")
            return
        
        item = self.prescriptions_tree.item(selected[0])
        prescription_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the prescription for {customer_name}? This action cannot be undone."
        )
        
        if confirm:
            # Delete prescription items
            self.db.execute_update("DELETE FROM prescription_items WHERE prescription_id = ?", (prescription_id,))
            
            # Delete prescription
            self.db.execute_update("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
            
            # Log the action
            self.db.execute_update(
                "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                (self.user['id'], "DELETE", "prescriptions", prescription_id)
            )
            
            messagebox.showinfo("Success", "Prescription deleted successfully")
            self.load_prescriptions()
    
    def view_prescription(self):
        # Get selected prescription
        selected = self.prescriptions_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a prescription to view")
            return
        
        item = self.prescriptions_tree.item(selected[0])
        prescription_id = item['values'][0]
        
        # Get prescription details
        prescription = self.db.execute_query('''
        SELECT p.id, c.name, c.phone, c.email, p.doctor_name, p.diagnosis, p.prescription_date, p.notes
        FROM prescriptions p
        LEFT JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
        ''', (prescription_id,))
        
        if not prescription:
            messagebox.showerror("Error", "Prescription not found")
            return
        
        prescription = prescription[0]
        
        # Get prescription items
        prescription_items = self.db.execute_query('''
        SELECT m.name, pi.dosage, pi.duration, pi.instructions
        FROM prescription_items pi
        JOIN medicines m ON pi.medicine_id = m.id
        WHERE pi.prescription_id = ?
        ''', (prescription_id,))
        
        # Create view prescription dialog
        view_dialog = tk.Toplevel(self.parent)
        view_dialog.title(f"Prescription - {prescription[1]}")
        view_dialog.geometry("600x500")
        
        # Prescription information
        info_frame = ttk.LabelFrame(view_dialog, text="Prescription Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(info_frame, text=f"Customer: {prescription[1]}").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Phone: {prescription[2] or ''}").grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Email: {prescription[3] or ''}").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Doctor: {prescription[4] or ''}").grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Date: {prescription[6].strftime('%Y-%m-%d') if prescription[6] else ''}").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Diagnosis: {prescription[5] or ''}").grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"Notes: {prescription[7] or ''}").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Medicines
        medicines_frame = ttk.LabelFrame(view_dialog, text="Medicines", padding=10)
        medicines_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # Create treeview for medicines
        columns = ("Name", "Dosage", "Duration", "Instructions")
        medicines_tree = ttk.Treeview(medicines_frame, columns=columns, show="headings")
        
        for col in columns:
            medicines_tree.heading(col, text=col)
            medicines_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(medicines_frame, orient=tk.VERTICAL, command=medicines_tree.yview)
        medicines_tree.configure(yscrollcommand=scrollbar.set)
        
        medicines_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add medicines
        for item in prescription_items:
            medicines_tree.insert("", tk.END, values=(
                item[0],  # Name
                item[1],  # Dosage
                item[2],  # Duration
                item[3]   # Instructions
            ))
        
        # Buttons
        button_frame = ttk.Frame(view_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        close_btn = ttk.Button(button_frame, text="Close", command=view_dialog.destroy)
        close_btn.pack(side=tk.RIGHT, padx=10)
    
    def load_reminders(self):
        # Clear existing items
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        
        # Get prescriptions that need refilling soon
        # This is a simplified query - in a real system, you would track refill dates
        reminders = self.db.execute_query('''
        SELECT p.id, c.name, m.name, 7, p.prescription_date
        FROM prescriptions p
        JOIN customers c ON p.customer_id = c.id
        JOIN prescription_items pi ON p.id = pi.prescription_id
        JOIN medicines m ON pi.medicine_id = m.id
        WHERE p.prescription_date <= DATE('now', '-23 days')
        ORDER BY p.prescription_date
        LIMIT 20
        ''')
        
        for reminder in reminders:
            date_str = reminder[4].strftime('%Y-%m-%d') if reminder[4] else ""
            self.reminders_tree.insert("", tk.END, values=(
                reminder[0],  # ID
                reminder[1],  # Customer
                reminder[2],  # Medicine
                reminder[3],  # Days Left
                date_str  # Last Refill
            ))
    
    def send_reminder(self):
        # Get selected reminder
        selected = self.reminders_tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a prescription to send reminder")
            return
        
        item = self.reminders_tree.item(selected[0])
        prescription_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Get customer details
        customer = self.db.execute_query('''
        SELECT c.name, c.phone, c.email
        FROM prescriptions p
        JOIN customers c ON p.customer_id = c.id
        WHERE p.id = ?
        ''', (prescription_id,))
        
        if not customer:
            messagebox.showerror("Error", "Customer not found")
            return
        
        customer = customer[0]
        
        # Create send reminder dialog
        reminder_dialog = tk.Toplevel(self.parent)
        reminder_dialog.title("Send Reminder")
        reminder_dialog.geometry("500x300")
        reminder_dialog.resizable(False, False)
        
        ttk.Label(reminder_dialog, text=f"Send prescription refill reminder to {customer_name}", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Label(reminder_dialog, text=f"Phone: {customer[1] or ''}").pack(pady=5)
        ttk.Label(reminder_dialog, text=f"Email: {customer[2] or ''}").pack(pady=5)
        
        ttk.Label(reminder_dialog, text="Message:").pack(pady=5)
        message_text = tk.Text(reminder_dialog, width=50, height=5)
        message_text.pack(pady=5)
        message_text.insert(tk.END, f"Dear {customer_name},\n\nYour prescription is due for refill. Please visit our pharmacy to refill your medication.\n\nThank you,\n{self.user['store_name']}")
        
        # Buttons
        button_frame = ttk.Frame(reminder_dialog)
        button_frame.pack(pady=10)
        
        def send_sms():
            # Placeholder for SMS sending functionality
            messagebox.showinfo("SMS Sent", f"SMS reminder sent to {customer[1]}")
            reminder_dialog.destroy()
        
        def send_email():
            # Placeholder for email sending functionality
            messagebox.showinfo("Email Sent", f"Email reminder sent to {customer[2]}")
            reminder_dialog.destroy()
        
        sms_btn = ttk.Button(button_frame, text="Send SMS", command=send_sms)
        sms_btn.pack(side=tk.LEFT, padx=5)
        
        email_btn = ttk.Button(button_frame, text="Send Email", command=send_email)
        email_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=reminder_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)