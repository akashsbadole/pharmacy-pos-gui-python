import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime, timedelta
import hashlib
import re
import random
import string

class Utils:
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_invoice_number():
        """Generate a unique invoice number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"INV-{timestamp}-{random_str}"
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        # Remove all non-digit characters
        phone_clean = re.sub(r'[^\d]', '', phone)
        return len(phone_clean) >= 10
    
    @staticmethod
    def format_currency(amount):
        """Format amount as currency"""
        return f"${amount:.2f}"
    
    @staticmethod
    def format_date(date_obj, format_str="%Y-%m-%d"):
        """Format date object as string"""
        if date_obj:
            return date_obj.strftime(format_str)
        return ""
    
    @staticmethod
    def parse_date(date_str, format_str="%Y-%m-%d"):
        """Parse string to date object"""
        if date_str:
            return datetime.strptime(date_str, format_str).date()
        return None
    
    @staticmethod
    def get_current_date():
        """Get current date"""
        return datetime.now().date()
    
    @staticmethod
    def get_current_datetime():
        """Get current datetime"""
        return datetime.now()
    
    @staticmethod
    def add_days(date, days):
        """Add days to a date"""
        return date + timedelta(days=days)
    
    @staticmethod
    def days_between(date1, date2):
        """Calculate days between two dates"""
        return (date2 - date1).days
    
    @staticmethod
    def is_weekend(date):
        """Check if date is a weekend"""
        return date.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    @staticmethod
    def create_directory_if_not_exists(directory):
        """Create directory if it doesn't exist"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def file_exists(file_path):
        """Check if file exists"""
        return os.path.exists(file_path)
    
    @staticmethod
    def get_file_size(file_path):
        """Get file size in bytes"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_filename_extension(file_path):
        """Get file extension from file path"""
        return os.path.splitext(file_path)[1].lower()
    
    @staticmethod
    def is_valid_image_file(file_path):
        """Check if file is a valid image"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        extension = Utils.get_filename_extension(file_path)
        return extension in valid_extensions
    
    @staticmethod
    def is_valid_csv_file(file_path):
        """Check if file is a valid CSV"""
        return Utils.get_filename_extension(file_path) == '.csv'
    
    @staticmethod
    def is_valid_pdf_file(file_path):
        """Check if file is a valid PDF"""
        return Utils.get_filename_extension(file_path) == '.pdf'
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename by removing invalid characters"""
        # Remove invalid characters
        sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        return sanitized
    
    @staticmethod
    def generate_random_string(length=10):
        """Generate random string of specified length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_number(length=6):
        """Generate random number of specified length"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def truncate_string(text, max_length=30):
        """Truncate string to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def clean_string(text):
        """Clean string by removing extra spaces and special characters"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters (keep alphanumeric and spaces)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text
    
    @staticmethod
    def capitalize_words(text):
        """Capitalize each word in a string"""
        return ' '.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def show_info_dialog(parent, title, message):
        """Show information dialog"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error_dialog(parent, title, message):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning_dialog(parent, title, message):
        """Show warning dialog"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_yes_no_dialog(parent, title, message):
        """Show yes/no dialog and return True if yes is selected"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def show_input_dialog(parent, title, message, initial_value=""):
        """Show input dialog and return the entered value"""
        return tk.simpledialog.askstring(title, message, initialvalue=initial_value)
    
    @staticmethod
    def center_window(window):
        """Center window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def set_window_icon(window, icon_path):
        """Set window icon"""
        if os.path.exists(icon_path):
            window.iconbitmap(icon_path)
    
    @staticmethod
    def create_tooltip(widget, text):
        """Create tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    @staticmethod
    def set_widget_state(widget, state):
        """Set state of widget and its children"""
        widget.configure(state=state)
        try:
            for child in widget.winfo_children():
                Utils.set_widget_state(child, state)
        except:
            pass
    
    @staticmethod
    def clear_treeview(treeview):
        """Clear all items from treeview"""
        for item in treeview.get_children():
            treeview.delete(item)
    
    @staticmethod
    def get_treeview_selection(treeview, column=0):
        """Get selected value from treeview"""
        selected = treeview.selection()
        if selected:
            item = treeview.item(selected[0])
            return item['values'][column]
        return None
    
    @staticmethod
    def add_treeview_item(treeview, values):
        """Add item to treeview and return item ID"""
        return treeview.insert("", tk.END, values=values)
    
    @staticmethod
    def update_treeview_item(treeview, item, values):
        """Update treeview item with new values"""
        treeview.item(item, values=values)
    
    @staticmethod
    def delete_treeview_item(treeview, item):
        """Delete item from treeview"""
        treeview.delete(item)
    
    @staticmethod
    def create_combobox_with_search(parent, values, textvariable=None, width=20):
        """Create combobox with search functionality"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        # Search entry
        search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Combobox
        combo_var = textvariable or tk.StringVar()
        combobox = ttk.Combobox(frame, textvariable=combo_var, values=values, width=width)
        combobox.pack(side=tk.RIGHT, padx=5)
        
        # Filter function
        def filter_combobox(*args):
            search_term = search_var.get().lower()
            filtered_values = [v for v in values if search_term in v.lower()]
            combobox['values'] = filtered_values
        
        search_var.trace('w', filter_combobox)
        
        return frame, combobox, search_var
    
    @staticmethod
    def create_progress_bar(parent, maximum=100):
        """Create progress bar with label"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=maximum)
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        label = ttk.Label(frame, text="0%")
        label.pack(side=tk.RIGHT, padx=5)
        
        def update_progress(value):
            progress_var.set(value)
            percentage = int((value / maximum) * 100)
            label.config(text=f"{percentage}%")
        
        return frame, progress_var, update_progress
    
    @staticmethod
    def create_notebook_with_tabs(parent, tabs):
        """Create notebook with tabs"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        tab_frames = {}
        for tab_name in tabs:
            tab_frame = ttk.Frame(notebook, padding=10)
            notebook.add(tab_frame, text=tab_name)
            tab_frames[tab_name] = tab_frame
        
        return notebook, tab_frames
    
    @staticmethod
    def create_label_entry_frame(parent, label_text, entry_width=20):
        """Create frame with label and entry"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        label = ttk.Label(frame, text=label_text, width=15)
        label.pack(side=tk.LEFT, padx=5)
        
        entry_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=entry_var, width=entry_width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        return frame, label, entry, entry_var
    
    @staticmethod
    def create_button_frame(parent, buttons):
        """Create frame with buttons"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)
        
        button_widgets = []
        for button_text, command in buttons:
            button = ttk.Button(frame, text=button_text, command=command)
            button.pack(side=tk.LEFT, padx=5)
            button_widgets.append(button)
        
        return frame, button_widgets
    
    @staticmethod
    def create_treeview_with_scrollbar(parent, columns, height=10):
        """Create treeview with scrollbar"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        treeview = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        
        for col in columns:
            treeview.heading(col, text=col)
            treeview.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=treeview.yview)
        treeview.configure(yscrollcommand=scrollbar.set)
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame, treeview, scrollbar
    
    @staticmethod
    def log_action(db, user_id, action, table_name=None, record_id=None, old_values=None, new_values=None):
        """Log user action to audit log"""
        try:
            db.execute_update('''
            INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, action, table_name, record_id, old_values, new_values))
        except Exception as e:
            print(f"Error logging action: {e}")
    
    @staticmethod
    def backup_database(db, backup_path=None):
        """Backup database to specified path"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        
        try:
            backup_conn = sqlite3.connect(backup_path)
            db.conn.backup(backup_conn)
            backup_conn.close()
            return backup_path
        except Exception as e:
            print(f"Error backing up database: {e}")
            return None
    
    @staticmethod
    def restore_database(db, backup_path):
        """Restore database from backup file"""
        if os.path.exists(backup_path):
            try:
                # Close current connection
                db.close()
                
                # Replace current database with backup
                if os.path.exists(db.db_name):
                    os.remove(db.db_name)
                os.rename(backup_path, db.db_name)
                
                # Reconnect
                db.connect()
                return True
            except Exception as e:
                print(f"Error restoring database: {e}")
                return False
        return False
    
    @staticmethod
    def send_email(to_email, subject, message, smtp_server, smtp_port, username, password):
        """Send email using SMTP"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = username
            msg['To'] = to_email
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_sms(phone_number, message, api_key, api_url):
        """Send SMS using API"""
        try:
            import requests
            
            params = {
                'api_key': api_key,
                'to': phone_number,
                'message': message
            }
            
            response = requests.post(api_url, params=params)
            
            if response.status_code == 200:
                return True
            else:
                print(f"SMS API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    @staticmethod
    def generate_barcode(text, barcode_type="CODE128"):
        """Generate barcode image"""
        try:
            import barcode
            from barcode.writer import ImageWriter
            
            # Get barcode class
            barcode_class = barcode.get_barcode_class(barcode_type)
            
            # Generate barcode
            barcode_image = barcode_class(text, writer=ImageWriter())
            
            # Save to temporary file
            temp_dir = os.path.join(os.path.dirname(__file__), "temp")
            Utils.create_directory_if_not_exists(temp_dir)
            
            filename = os.path.join(temp_dir, f"{Utils.generate_random_string()}.png")
            barcode_image.save(filename)
            
            return filename
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
    
    @staticmethod
    def scan_barcode(image_path):
        """Scan barcode from image"""
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            
            image = Image.open(image_path)
            barcodes = decode(image)
            
            if barcodes:
                return barcodes[0].data.decode('utf-8')
            return None
        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None
    
    @staticmethod
    def text_to_speech(text, language='en'):
        """Convert text to speech"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Set voice based on language
            voices = engine.getProperty('voices')
            for voice in voices:
                if language in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(text)
            engine.runAndWait()
            
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return False