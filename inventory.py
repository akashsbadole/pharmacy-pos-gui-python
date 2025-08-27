# inventory.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime, date

class Inventory:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db

        # Main frame
        self.inventory_frame = ttk.Frame(parent, padding=12)
        self.inventory_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            self.inventory_frame,
            text="💊 Inventory Management",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 12))

        # Search & filter frame
        search_frame = ttk.Frame(self.inventory_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_inventory)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=(2, 6))
        self.category_var = tk.StringVar()
        self.category_var.trace_add('write', self.filter_inventory)
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, width=20)
        self.category_combo.pack(side=tk.LEFT)

        # Load categories
        try:
            categories = self.db.execute_query(
                "SELECT DISTINCT category FROM medicines WHERE store_id = ? AND category IS NOT NULL",
                (self.user['store_id'],)
            )
            self.category_combo['values'] = [c[0] for c in categories]
        except Exception:
            self.category_combo['values'] = []

        # Buttons row
        buttons_frame = ttk.Frame(self.inventory_frame)
        buttons_frame.pack(fill=tk.X, pady=(6, 10))

        btn_specs = [
            ("➕ Add", self.add_medicine),
            ("✏️ Edit", self.edit_medicine),
            ("🗑️ Delete", self.delete_medicine),
            ("📥 Import CSV", self.import_csv),
            ("📤 Export CSV", self.export_csv)
        ]
        for txt, cmd in btn_specs:
            ttk.Button(buttons_frame, text=txt, command=cmd).pack(side=tk.LEFT, padx=4)

        # Table frame
        table_frame = ttk.Frame(self.inventory_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Name", "Category", "Manufacturer", "Price", "Cost", "Stock", "Expiry", "Barcode")
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)

        # Column configuration
        col_widths = {
            "ID": 50, "Name": 220, "Category": 120, "Manufacturer": 140,
            "Price": 80, "Cost": 80, "Stock": 70, "Expiry": 100, "Barcode": 130
        }
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=col_widths.get(col, 100), anchor=tk.CENTER)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=vsb.set)
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Load data initially
        self.load_inventory()

        # Bind double-click to edit
        self.inventory_tree.bind("<Double-1>", self.on_double_click)

    # -------------------------
    # Utility / Normalization
    # -------------------------
    def normalize_date(self, value):
        """Return expiry date as YYYY-MM-DD string. Accepts None, date, datetime, or string."""
        if not value and value != 0:
            return ""
        # If it's already a date object
        if isinstance(value, date) and not isinstance(value, str):
            try:
                return value.strftime("%Y-%m-%d")
            except Exception:
                return str(value)
        # If it's a string, try to validate format; if invalid, return raw string
        if isinstance(value, str):
            # If looks like ISO date already, return as-is
            try:
                # Accept either YYYY-MM-DD or other common formats convert to YYYY-MM-DD
                parsed = None
                if len(value) >= 10:
                    try:
                        parsed = datetime.strptime(value[:10], "%Y-%m-%d").date()
                    except Exception:
                        # Try other common separators
                        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                            try:
                                parsed = datetime.strptime(value[:10], fmt).date()
                                break
                            except Exception:
                                parsed = None
                if parsed:
                    return parsed.strftime("%Y-%m-%d")
            except Exception:
                pass
            return value
        # Fallback
        try:
            return str(value)
        except Exception:
            return ""

    def safe_float(self, val):
        try:
            return float(val) if val is not None else 0.0
        except Exception:
            return 0.0

    def safe_int(self, val):
        try:
            return int(val) if val is not None else 0
        except Exception:
            return 0

    def parse_bool_flexible(self, v):
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        return s in ("1", "true", "t", "yes", "y", "on")

    # -------------------------
    # Load / Filter / UI
    # -------------------------
    def load_inventory(self):
        # Clear items
        for it in self.inventory_tree.get_children():
            self.inventory_tree.delete(it)

        try:
            medicines = self.db.execute_query('''
                SELECT id, name, category, manufacturer, price, cost_price, stock_quantity, expiry_date, barcode
                FROM medicines
                WHERE store_id = ?
                ORDER BY name
            ''', (self.user['store_id'],))
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to load inventory: {e}")
            medicines = []

        for med in medicines:
            # med tuple indices aligned with SELECT
            med_id = med[0]
            name = med[1] or ""
            category = med[2] or ""
            manufacturer = med[3] or ""
            price = self.safe_float(med[4])
            cost_price = self.safe_float(med[5])
            stock = med[6] if med[6] is not None else 0
            expiry_str = self.normalize_date(med[7])
            barcode = med[8] or ""

            self.inventory_tree.insert("", tk.END, values=(
                med_id, name, category, manufacturer,
                f"${price:.2f}", f"${cost_price:.2f}", stock, expiry_str, barcode
            ))

    def filter_inventory(self, *args):
        search_term = (self.search_var.get() or "").strip().lower()
        category = (self.category_var.get() or "").strip()

        for it in self.inventory_tree.get_children():
            self.inventory_tree.delete(it)

        query = '''
            SELECT id, name, category, manufacturer, price, cost_price, stock_quantity, expiry_date, barcode
            FROM medicines
            WHERE store_id = ?
        '''
        params = [self.user['store_id']]

        if search_term:
            query += " AND (LOWER(name) LIKE ? OR LOWER(barcode) LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY name"

        try:
            medicines = self.db.execute_query(query, params)
        except Exception as e:
            messagebox.showerror("DB Error", f"Filter failed: {e}")
            medicines = []

        for med in medicines:
            expiry_str = self.normalize_date(med[7])
            price = self.safe_float(med[4])
            cost_price = self.safe_float(med[5])
            self.inventory_tree.insert("", tk.END, values=(
                med[0], med[1] or "", med[2] or "", med[3] or "",
                f"${price:.2f}", f"${cost_price:.2f}", med[6] or 0, expiry_str, med[8] or ""
            ))

    def on_double_click(self, event):
        self.edit_medicine()

    # -------------------------
    # Add Medicine
    # -------------------------
    def add_medicine(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Medicine")
        dialog.geometry("520x520")
        dialog.resizable(False, False)

        heading = ttk.Label(dialog, text="Medicine Details", font=('Arial', 12, 'bold'))
        heading.grid(row=0, column=0, columnspan=2, pady=(10, 8))

        labels = [
            ("Name:", 1), ("Description:", 2), ("Category:", 3), ("Manufacturer:", 4),
            ("Barcode:", 5), ("Price ($):", 6), ("Cost Price ($):", 7), ("Stock Quantity:", 8),
            ("Expiry Date (YYYY-MM-DD):", 9)
        ]
        vars = {}

        for text, r in labels:
            ttk.Label(dialog, text=text).grid(row=r, column=0, sticky=tk.W, padx=12, pady=6)
            v = tk.StringVar()
            vars[text] = v
            ttk.Entry(dialog, textvariable=v, width=40).grid(row=r, column=1, padx=8, pady=6)

        prescription_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Prescription Required", variable=prescription_var).grid(
            row=10, column=0, columnspan=2, pady=6
        )

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=11, column=0, columnspan=2, pady=12)

        def save_medicine():
            # Basic validation & parsing
            name = vars["Name:"].get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Medicine name is required")
                return

            description = vars["Description:"].get().strip()
            category = vars["Category:"].get().strip()
            manufacturer = vars["Manufacturer:"].get().strip()
            barcode = vars["Barcode:"].get().strip()

            try:
                price = self.safe_float(vars["Price ($):"].get().strip() or 0.0)
                cost = self.safe_float(vars["Cost Price ($):"].get().strip() or 0.0)
                stock = self.safe_int(vars["Stock Quantity:"].get().strip() or 0)
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid numeric input: {e}")
                return

            expiry_date = None
            expiry_input = vars["Expiry Date (YYYY-MM-DD):"].get().strip()
            if expiry_input:
                try:
                    expiry_date = datetime.strptime(expiry_input, "%Y-%m-%d").date()
                except ValueError:
                    # Let user know but don't block insert (you may want to block instead)
                    messagebox.showerror("Validation Error", "Invalid expiry date format. Use YYYY-MM-DD")
                    return

            pres_req = prescription_var.get()

            try:
                result = self.db.execute_update('''
                    INSERT INTO medicines (name, description, category, manufacturer, barcode, price, cost_price, 
                                           stock_quantity, expiry_date, prescription_required, store_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name, description, category, manufacturer, barcode,
                    price, cost, stock, expiry_date, pres_req, self.user['store_id']
                ))
                # Try to get last inserted id if db returns it
                medicine_id = None
                try:
                    # Some db wrappers return lastrowid from execute_update
                    medicine_id = result if isinstance(result, int) else None
                except Exception:
                    medicine_id = None

                # Fallback: we try a DB-specific last-row query if available
                if not medicine_id:
                    try:
                        # For SQLite, last insert id can be retrieved using SELECT last_insert_rowid()
                        last = self.db.execute_query("SELECT last_insert_rowid()", ())
                        if last and isinstance(last, (list, tuple)) and len(last) > 0:
                            medicine_id = last[0][0]
                    except Exception:
                        medicine_id = None

                # Audit log (safe)
                try:
                    self.db.execute_update(
                        "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                        (self.user['id'], "CREATE", "medicines", medicine_id)
                    )
                except Exception:
                    pass

                messagebox.showinfo("Success", "Medicine added successfully")
                dialog.destroy()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to add medicine: {e}")

        ttk.Button(button_frame, text="Save", command=save_medicine).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=6)

    # -------------------------
    # Edit Medicine
    # -------------------------
    def edit_medicine(self):
        sel = self.inventory_tree.selection()
        if not sel:
            messagebox.showinfo("Selection Required", "Please select a medicine to edit")
            return

        item = self.inventory_tree.item(sel[0])
        medicine_id = item['values'][0]

        try:
            meds = self.db.execute_query('''
                SELECT id, name, description, category, manufacturer, barcode, price, cost_price, 
                       stock_quantity, expiry_date, prescription_required
                FROM medicines
                WHERE id = ?
            ''', (medicine_id,))
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to read medicine: {e}")
            return

        if not meds:
            messagebox.showerror("Not Found", "Medicine not found in DB")
            return

        med = meds[0]

        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Medicine")
        dialog.geometry("520x520")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Medicine Details", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(10, 8))

        fields = [
            ("Name:", med[1]), ("Description:", med[2] or ""), ("Category:", med[3] or ""),
            ("Manufacturer:", med[4] or ""), ("Barcode:", med[5] or ""),
            ("Price ($):", str(med[6] if med[6] is not None else 0.0)),
            ("Cost Price ($):", str(med[7] if med[7] is not None else 0.0)),
            ("Stock Quantity:", str(med[8] if med[8] is not None else 0)),
            ("Expiry Date (YYYY-MM-DD):", self.normalize_date(med[9] if len(med) > 9 else med[9]))
        ]
        vars = {}
        for idx, (label_txt, value) in enumerate(fields, start=1):
            ttk.Label(dialog, text=label_txt).grid(row=idx, column=0, sticky=tk.W, padx=12, pady=6)
            v = tk.StringVar(value=value)
            vars[label_txt] = v
            ttk.Entry(dialog, textvariable=v, width=40).grid(row=idx, column=1, padx=8, pady=6)

        prescription_var = tk.BooleanVar(value=bool(med[10] if len(med) > 10 else False))
        ttk.Checkbutton(dialog, text="Prescription Required", variable=prescription_var).grid(row=10, column=0, columnspan=2, pady=6)

        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=11, column=0, columnspan=2, pady=12)

        def update_medicine():
            name = vars["Name:"].get().strip()
            if not name:
                messagebox.showerror("Validation Error", "Medicine name is required")
                return

            description = vars["Description:"].get().strip()
            category = vars["Category:"].get().strip()
            manufacturer = vars["Manufacturer:"].get().strip()
            barcode = vars["Barcode:"].get().strip()

            try:
                price = self.safe_float(vars["Price ($):"].get().strip() or 0.0)
                cost = self.safe_float(vars["Cost Price ($):"].get().strip() or 0.0)
                stock = self.safe_int(vars["Stock Quantity:"].get().strip() or 0)
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid numeric input: {e}")
                return

            expiry_date = None
            expiry_input = vars["Expiry Date (YYYY-MM-DD):"].get().strip()
            if expiry_input:
                try:
                    expiry_date = datetime.strptime(expiry_input, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Validation Error", "Invalid expiry date format. Use YYYY-MM-DD")
                    return

            pres_req = prescription_var.get()

            try:
                self.db.execute_update('''
                    UPDATE medicines SET 
                        name = ?, description = ?, category = ?, manufacturer = ?, barcode = ?, 
                        price = ?, cost_price = ?, stock_quantity = ?, expiry_date = ?, 
                        prescription_required = ?
                    WHERE id = ?
                ''', (
                    name, description, category, manufacturer, barcode,
                    price, cost, stock, expiry_date, pres_req, medicine_id
                ))
                # Audit
                try:
                    self.db.execute_update(
                        "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                        (self.user['id'], "UPDATE", "medicines", medicine_id)
                    )
                except Exception:
                    pass

                messagebox.showinfo("Success", "Medicine updated successfully")
                dialog.destroy()
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to update medicine: {e}")

        ttk.Button(button_frame, text="Update", command=update_medicine).pack(side=tk.LEFT, padx=6)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=6)

    # -------------------------
    # Delete Medicine
    # -------------------------
    def delete_medicine(self):
        sel = self.inventory_tree.selection()
        if not sel:
            messagebox.showinfo("Selection Required", "Please select a medicine to delete")
            return

        item = self.inventory_tree.item(sel[0])
        medicine_id = item['values'][0]
        medicine_name = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {medicine_name}? This action cannot be undone."
        )
        if not confirm:
            return

        try:
            self.db.execute_update("DELETE FROM medicines WHERE id = ?", (medicine_id,))
            try:
                self.db.execute_update(
                    "INSERT INTO audit_log (user_id, action, table_name, record_id) VALUES (?, ?, ?, ?)",
                    (self.user['id'], "DELETE", "medicines", medicine_id)
                )
            except Exception:
                pass
            messagebox.showinfo("Success", "Medicine deleted successfully")
            self.load_inventory()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to delete medicine: {e}")

    # -------------------------
    # CSV Import / Export
    # -------------------------
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Import CSV File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)  # could be None if empty
                imported = 0
                skipped = 0
                rownum = 1 if header is None else 2

                for row in reader:
                    try:
                        if not row or len(row) == 0:
                            skipped += 1
                            rownum += 1
                            continue

                        # Expected order (flexible): Name, Description, Category, Manufacturer, Barcode,
                        # Price, Cost Price, Stock Quantity, Expiry Date, Prescription Required
                        name = row[0].strip() if len(row) > 0 else ""
                        if not name:
                            skipped += 1
                            rownum += 1
                            continue

                        description = row[1].strip() if len(row) > 1 else ""
                        category = row[2].strip() if len(row) > 2 else ""
                        manufacturer = row[3].strip() if len(row) > 3 else ""
                        barcode = row[4].strip() if len(row) > 4 else ""

                        price = self.safe_float(row[5]) if len(row) > 5 else 0.0
                        cost_price = self.safe_float(row[6]) if len(row) > 6 else 0.0
                        stock_quantity = self.safe_int(row[7]) if len(row) > 7 else 0

                        expiry_date = None
                        if len(row) > 8 and row[8].strip():
                            expiry_raw = row[8].strip()
                            try:
                                expiry_date = datetime.strptime(expiry_raw, "%Y-%m-%d").date()
                            except ValueError:
                                # don't fail entire import for bad date; log and skip only date
                                print(f"Row {rownum}: Invalid expiry date format: {expiry_raw}")
                                expiry_date = None

                        prescription_required = False
                        if len(row) > 9:
                            prescription_required = self.parse_bool_flexible(row[9])

                        # Insert
                        try:
                            res = self.db.execute_update('''
                                INSERT INTO medicines 
                                (name, description, category, manufacturer, barcode, 
                                 price, cost_price, stock_quantity, expiry_date, 
                                 prescription_required, store_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                name, description, category, manufacturer, barcode,
                                price, cost_price, stock_quantity, expiry_date,
                                prescription_required, self.user['store_id']
                            ))
                            imported += 1
                        except Exception as e:
                            print(f"Row {rownum}: DB insert error: {e}")
                            skipped += 1

                        rownum += 1
                    except Exception as e:
                        print(f"Row {rownum}: Unexpected error: {e}")
                        skipped += 1
                        rownum += 1

                messagebox.showinfo("Import Complete", f"Imported {imported} rows, skipped {skipped} rows.")
                self.load_inventory()
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing CSV file: {e}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Export CSV File", defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "Name", "Description", "Category", "Manufacturer", "Barcode",
                    "Price", "Cost Price", "Stock Quantity", "Expiry Date",
                    "Prescription Required"
                ])

                try:
                    medicines = self.db.execute_query('''
                        SELECT name, description, category, manufacturer, barcode, price, cost_price,
                               stock_quantity, expiry_date, prescription_required
                        FROM medicines
                        WHERE store_id = ?
                    ''', (self.user['store_id'],))
                except Exception as e:
                    messagebox.showerror("DB Error", f"Failed to read medicines for export: {e}")
                    return

                for med in medicines:
                    expiry_str = self.normalize_date(med[8])
                    writer.writerow([
                        med[0] or "", med[1] or "", med[2] or "", med[3] or "",
                        med[4] or "", med[5] if med[5] is not None else 0.0,
                        med[6] if med[6] is not None else 0.0,
                        med[7] if med[7] is not None else 0,
                        expiry_str, med[9] if len(med) > 9 else False
                    ])

                messagebox.showinfo("Export Complete", "Medicines exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting CSV file: {e}")
