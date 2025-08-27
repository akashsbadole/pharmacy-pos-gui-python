import tkinter as tk
from auth import AuthSystem

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pharmacy Management System")
    root.geometry("400x300")
    root.resizable(False, False)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    app = AuthSystem(root)
    root.mainloop()