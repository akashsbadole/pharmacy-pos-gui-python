import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import uuid
from datetime import datetime
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sys
import subprocess

# --------- DATABASE MOCKUP CLASS ---------
class Database:
    def __init__(self, db_file='pos.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY, name TEXT, phone TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS medicines(id INTEGER PRIMARY KEY, name TEXT, price REAL, stock_quantity INTEGER, store_id INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY, invoice_number TEXT, customer_id INTEGER, store_id INTEGER, user_id INTEGER, total_amount REAL, discount_amount REAL, tax_amount REAL, payment_method TEXT, sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS sale_items(id INTEGER PRIMARY KEY, sale_id INTEGER, medicine_id INTEGER, quantity INTEGER, price REAL, discount REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS stores(id INTEGER PRIMARY KEY, name TEXT, address TEXT, phone TEXT, email TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT, table_name TEXT, record_id INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def execute_query(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        return c.fetchall()

    def execute_update(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        self.conn.commit()
        return c.lastrowid

# --------- PDF GENERATOR FUNCTION ---------
def generate_invoice(sale, sale_items):
    invoice_file = f"Invoice_{sale[1]}.pdf"
    c = canvas.Canvas(invoice_file, pagesize=A4)
    width, height = A4

    # Store Info
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, f"{sale[11]}")  # Store Name
    c.setFont("Helvetica", 10)
    c.drawString(50, height-70, f"{sale[12]}")  # Store Address
    c.drawString(50, height-85, f"Phone: {sale[13]} | Email: {sale[14]}")

    # Invoice Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, height-50, f"INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(400, height-70, f"Invoice #: {sale[1]}")
    c.drawString(400, height-85, f"Date: {sale[9]}")

    # Customer Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height-120, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height-135, f"{sale[2] or 'Walk-in'}")
    c.drawString(50, height-150, f"Phone: {sale[3] or ''}")

    # Table Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height-180, "Item")
    c.drawString(250, height-180, "Qty")
    c.drawString(300, height-180, "Price")
    c.drawString(400, height-180, "Total")
    y = height - 200
    c.setFont("Helvetica", 10)
    for item in sale_items:
        c.drawString(50, y, f"{item[0]}")
        c.drawString(250, y, str(item[1]))
        c.drawString(300, y, f"${item[2]:.2f}")
        c.drawString(400, y, f"${item[3]:.2f}")
        y -= 20

    # Summary
    y -= 10
    c.drawString(300, y, f"Subtotal: ${sum([i[3] for i in sale_items]):.2f}")
    y -= 15
    c.drawString(300, y, f"Discount: ${sale[6]:.2f}")
    y -= 15
    c.drawString(300, y, f"Tax: ${sale[7]:.2f}")
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, y, f"Total: ${sale[5]:.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for your purchase!")
    c.save()
    return invoice_file

# --------- SALES CLASS ---------
class Sales:
    def __init__(self, parent, user, db):
        self.parent = parent
        self.user = user
        self.db = db
        self.sale_items = []
        self.subtotal = self.discount = self.tax = self.total = 0.0

        self.sales_frame = ttk.Frame(parent, padding=10)
        self.sales_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.sales_frame, text="POS - Sales & Billing", font=('Arial', 16, 'bold')).pack(pady=5)

        notebook = ttk.Notebook(self.sales_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.new_sale_tab = ttk.Frame(notebook, padding=5)
        self.history_tab = ttk.Frame(notebook, padding=5)
        notebook.add(self.new_sale_tab, text="New Sale")
        notebook.add(self.history_tab, text="Sales History")

        self.setup_new_sale_tab()
        self.setup_history_tab()

    # ---- NEW SALE ----
    def setup_new_sale_tab(self):
        # Customer
        customer_frame = ttk.LabelFrame(self.new_sale_tab, text="Customer")
        customer_frame.pack(fill=tk.X, pady=5)
        ttk.Label(customer_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=2)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=25)
        self.customer_combo.grid(row=0, column=1, padx=5)
        customers = self.db.execute_query("SELECT id, name FROM customers")
        self.customer_combo['values'] = [f"{c[0]} - {c[1]}" for c in customers]

        # Medicine
        medicine_frame = ttk.LabelFrame(self.new_sale_tab, text="Medicine")
        medicine_frame.pack(fill=tk.X, pady=5)
        ttk.Label(medicine_frame, text="Medicine:").grid(row=0, column=0, padx=5, pady=2)
        self.medicine_var = tk.StringVar()
        self.medicine_combo = ttk.Combobox(medicine_frame, textvariable=self.medicine_var, width=25)
        self.medicine_combo.grid(row=0, column=1, padx=5)
        meds = self.db.execute_query("SELECT id, name FROM medicines WHERE store_id=? AND stock_quantity>0",(self.user['store_id'],))
        self.medicine_combo['values'] = [f"{m[0]} - {m[1]}" for m in meds]

        ttk.Label(medicine_frame, text="Qty:").grid(row=0, column=2, padx=5)
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(medicine_frame, textvariable=self.qty_var, width=5).grid(row=0, column=3, padx=5)
        ttk.Button(medicine_frame, text="Add", command=self.add_item).grid(row=0, column=4, padx=5)

        # Sale Items Table
        self.tree = ttk.Treeview(self.new_sale_tab, columns=("ID","Name","Price","Qty","Total"), show="headings")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Payment & Totals
        payment_frame = ttk.Frame(self.new_sale_tab)
        payment_frame.pack(fill=tk.X)
        self.sub_var = tk.StringVar(value="$0.00")
        self.discount_var = tk.StringVar(value="$0.00")
        self.tax_var = tk.StringVar(value="$0.00")
        self.total_var = tk.StringVar(value="$0.00")
        ttk.Label(payment_frame, text="Subtotal").grid(row=0, column=0, padx=5)
        ttk.Label(payment_frame, textvariable=self.sub_var).grid(row=0, column=1, padx=5)
        ttk.Label(payment_frame, text="Discount").grid(row=1, column=0, padx=5)
        ttk.Entry(payment_frame, textvariable=self.discount_var, width=8).grid(row=1, column=1, padx=5)
        ttk.Label(payment_frame, text="Tax").grid(row=2, column=0, padx=5)
        ttk.Label(payment_frame, textvariable=self.tax_var).grid(row=2, column=1, padx=5)
        ttk.Label(payment_frame, text="Total").grid(row=3, column=0, padx=5)
        ttk.Label(payment_frame, textvariable=self.total_var).grid(row=3, column=1, padx=5)

        ttk.Label(payment_frame, text="Payment Method").grid(row=0, column=2, padx=5)
        self.pay_var = tk.StringVar(value="Cash")
        ttk.Combobox(payment_frame, textvariable=self.pay_var, values=["Cash","Card","Insurance","Credit"], width=10).grid(row=0, column=3, padx=5)
        ttk.Button(payment_frame, text="Complete Sale", command=self.complete_sale).grid(row=0, column=4, padx=5)
        ttk.Button(payment_frame, text="Cancel", command=self.cancel_sale).grid(row=1, column=4, padx=5)

    def add_item(self):
        med_text = self.medicine_var.get()
        if not med_text:
            messagebox.showerror("Error","Select medicine")
            return
        try:
            med_id = int(med_text.split(' - ')[0])
            qty = int(self.qty_var.get())
        except:
            messagebox.showerror("Error","Invalid quantity")
            return
        med = self.db.execute_query("SELECT id,name,price,stock_quantity FROM medicines WHERE id=?",(med_id,))
        if not med: return
        med = med[0]
        if qty>med[3]: messagebox.showerror("Error","Not enough stock"); return
        self.sale_items.append({'id':med[0],'name':med[1],'price':med[2],'qty':qty})
        self.tree.insert("", tk.END, values=(med[0],med[1],f"${med[2]:.2f}",qty,f"${med[2]*qty:.2f}"))
        self.update_totals()
        self.medicine_var.set(""); self.qty_var.set("1")

    def update_totals(self):
        self.subtotal = sum([i['price']*i['qty'] for i in self.sale_items])
        try: self.discount=float(self.discount_var.get().replace('$',''))
        except: self.discount=0.0
        self.tax=(self.subtotal-self.discount)*0.1
        self.total=self.subtotal-self.discount+self.tax
        self.sub_var.set(f"${self.subtotal:.2f}"); self.tax_var.set(f"${self.tax:.2f}"); self.total_var.set(f"${self.total:.2f}")

    def cancel_sale(self):
        self.sale_items=[]; self.subtotal=self.discount=self.tax=self.total=0.0
        for i in self.tree.get_children(): self.tree.delete(i)
        self.customer_var.set(""); self.medicine_var.set(""); self.qty_var.set("1")
        self.discount_var.set("$0.00"); self.pay_var.set("Cash")
        self.update_totals()

    def complete_sale(self):
        if not self.sale_items: messagebox.showerror("Error","No items"); return
        cust_id=None
        if self.customer_var.get():
            try: cust_id=int(self.customer_var.get().split(' - ')[0])
            except: pass
        invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        try:
            self.db.conn.execute("BEGIN TRANSACTION")
            sale_id=self.db.execute_update('''INSERT INTO sales(invoice_number,customer_id,store_id,user_id,total_amount,discount_amount,tax_amount,payment_method) VALUES(?,?,?,?,?,?,?,?)''',
                                           (invoice_number,cust_id,self.user['store_id'],self.user['id'],self.total,self.discount,self.tax,self.pay_var.get()))
            for item in self.sale_items:
                self.db.execute_update('''INSERT INTO sale_items(sale_id,medicine_id,quantity,price,discount) VALUES(?,?,?,?,?)''',
                                       (sale_id,item['id'],item['qty'],item['price'],0))
                self.db.execute_update('''UPDATE medicines SET stock_quantity=stock_quantity-? WHERE id=?''',(item['qty'],item['id']))
            self.db.conn.commit()

            # 
            
            sale=self.db.execute_query('''
                SELECT s.id, s.invoice_number, 
                    COALESCE(c.name, 'Walk-in'), COALESCE(c.phone, ''), 
                    s.total_amount, s.discount_amount, s.tax_amount, s.payment_method, 
                    s.sale_date, COALESCE(u.name, 'Admin'),
                    COALESCE(st.name, 'Store'), COALESCE(st.address, ''), COALESCE(st.phone,''), COALESCE(st.email,'')
                FROM sales s 
                LEFT JOIN customers c ON s.customer_id=c.id 
                LEFT JOIN users u ON s.user_id=u.id 
                LEFT JOIN stores st ON s.store_id=st.id 
                WHERE s.id=?
            ''',(sale_id,))
            if not sale:
                messagebox.showerror("Error","Sale not found"); return
            sale=sale[0]


            # 

            items=self.db.execute_query('''SELECT m.name,si.quantity,si.price,(si.quantity*si.price) FROM sale_items si JOIN medicines m ON si.medicine_id=m.id WHERE si.sale_id=?''',(sale_id,))
            invoice=generate_invoice(sale,items)
            if os.name=='nt': os.startfile(invoice)
            else: subprocess.call(['open',invoice] if sys.platform=='darwin' else ['xdg-open',invoice])
            messagebox.showinfo("Sale Completed",f"Invoice: {invoice}")
            self.cancel_sale()
        except Exception as e:
            self.db.conn.rollback(); messagebox.showerror("Error",str(e))

    # ---- SALES HISTORY ----
    def setup_history_tab(self):
        frame=ttk.Frame(self.history_tab)
        frame.pack(fill=tk.X)
        ttk.Label(frame,text="Search:").pack(side=tk.LEFT,padx=5)
        self.search_var=tk.StringVar(); self.search_var.trace('w',self.filter_history)
        ttk.Entry(frame,textvariable=self.search_var,width=20).pack(side=tk.LEFT,padx=5)
        ttk.Button(frame,text="Export CSV",command=self.export_csv).pack(side=tk.RIGHT,padx=5)
        self.history_tree=ttk.Treeview(self.history_tab,columns=("ID","Invoice","Customer","Amount","Date","Staff"),show="headings")
        for col in self.history_tree['columns']: self.history_tree.heading(col,text=col); self.history_tree.column(col,width=80)
        self.history_tree.pack(fill=tk.BOTH,expand=True)
        self.load_history()

    def load_history(self):
        for i in self.history_tree.get_children(): self.history_tree.delete(i)
        sales=self.db.execute_query('''SELECT s.id,s.invoice_number,c.name,s.total_amount,s.sale_date,u.name FROM sales s LEFT JOIN customers c ON s.customer_id=c.id LEFT JOIN users u ON s.user_id=u.id ORDER BY s.sale_date DESC''')
        for s in sales: self.history_tree.insert("",tk.END,values=s)

    def filter_history(self,*args):
        query=self.search_var.get().lower()
        for i in self.history_tree.get_children(): self.history_tree.delete(i)
        sales=self.db.execute_query('''SELECT s.id,s.invoice_number,c.name,s.total_amount,s.sale_date,u.name FROM sales s LEFT JOIN customers c ON s.customer_id=c.id LEFT JOIN users u ON s.user_id=u.id ORDER BY s.sale_date DESC''')
        for s in sales:
            if query in str(s).lower(): self.history_tree.insert("",tk.END,values=s)

    def export_csv(self):
        if not self.history_tree.get_children(): messagebox.showerror("Error","No data"); return
        file=f"sales_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        with open(file,'w',newline='') as f:
            writer=csv.writer(f)
            writer.writerow([self.history_tree.heading(c)['text'] for c in self.history_tree['columns']])
            for row in self.history_tree.get_children(): writer.writerow(self.history_tree.item(row)['values'])
        messagebox.showinfo("Exported",f"CSV saved as {file}")

# --------- RUN APP ---------
if __name__=="__main__":
    db=Database()
    # Mock user
    user={'id':1,'name':'Admin','store_id':1}
    # Add dummy store
    if not db.execute_query("SELECT * FROM stores WHERE id=1"): db.execute_update("INSERT INTO stores(id,name,address,phone,email) VALUES(?,?,?,?,?)",(1,"My Pharmacy","123 Main St","9999999999","store@email.com"))
    root=tk.Tk()
    root.title("POS System")
    root.geometry("900x600")
    Sales(root,user,db)
    root.mainloop()
