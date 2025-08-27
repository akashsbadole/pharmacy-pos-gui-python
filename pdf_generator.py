from fpdf import FPDF
import os
from datetime import datetime
import tempfile

def generate_invoice(sale, sale_items):
    """
    Generate a PDF invoice for a sale
    
    Args:
        sale: Sale record tuple
        sale_items: List of sale item tuples
        
    Returns:
        str: Path to the generated PDF file
    """
    # Extract sale data
    sale_id = sale[0]
    invoice_number = sale[1]
    customer_name = sale[2] or "Walk-in Customer"
    customer_address = sale[3] or ""
    customer_phone = sale[4] or ""
    total_amount = sale[5]
    discount_amount = sale[6]
    tax_amount = sale[7]
    payment_method = sale[8]
    sale_date = sale[9]
    staff_name = sale[10]
    store_name = sale[11]
    store_address = sale[12] or ""
    store_phone = sale[13] or ""
    store_email = sale[14] or ""
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add store header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, store_name, 0, 1, 'C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, store_address, 0, 1, 'C')
    pdf.cell(0, 5, f"Phone: {store_phone}", 0, 1, 'C')
    pdf.cell(0, 5, f"Email: {store_email}", 0, 1, 'C')
    
    # Add line
    pdf.line(10, 40, 200, 40)
    
    # Add invoice title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 15, "INVOICE", 0, 1, 'C')
    
    # Add invoice details
    pdf.set_font("Arial", size=10)
    pdf.cell(100, 8, f"Invoice #: {invoice_number}", 0, 0)
    pdf.cell(100, 8, f"Date: {sale_date.strftime('%Y-%m-%d')}", 0, 1)
    
    # Add customer details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Bill To:", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, customer_name, 0, 1)
    pdf.cell(0, 6, customer_address, 0, 1)
    pdf.cell(0, 6, f"Phone: {customer_phone}", 0, 1)
    
    # Add line
    pdf.line(10, 90, 200, 90)
    
    # Add table headers
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 10, "Medicine", 1, 0)
    pdf.cell(30, 10, "Qty", 1, 0, 'C')
    pdf.cell(40, 10, "Price", 1, 0, 'R')
    pdf.cell(40, 10, "Total", 1, 1, 'R')
    
    # Add sale items
    pdf.set_font("Arial", size=10)
    for item in sale_items:
        name = item[0]
        quantity = item[1]
        price = item[2]
        total = item[3]
        
        pdf.cell(80, 10, name, 1, 0)
        pdf.cell(30, 10, str(quantity), 1, 0, 'C')
        pdf.cell(40, 10, f"${price:.2f}", 1, 0, 'R')
        pdf.cell(40, 10, f"${total:.2f}", 1, 1, 'R')
    
    # Add summary
    subtotal = sum(item[3] for item in sale_items)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(150, 10, "", 0, 0)
    pdf.cell(40, 10, f"Subtotal: ${subtotal:.2f}", 0, 1, 'R')
    
    pdf.cell(150, 10, "", 0, 0)
    pdf.cell(40, 10, f"Discount: ${discount_amount:.2f}", 0, 1, 'R')
    
    pdf.cell(150, 10, "", 0, 0)
    pdf.cell(40, 10, f"Tax: ${tax_amount:.2f}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(150, 10, "", 0, 0)
    pdf.cell(40, 10, f"Total: ${total_amount:.2f}", 0, 1, 'R')
    
    # Add payment info
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Payment Method: {payment_method}", 0, 1)
    pdf.cell(0, 10, f"Served by: {staff_name}", 0, 1)
    
    # Add footer
    pdf.line(10, 250, 200, 250)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')
    
    # Save PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"{invoice_number}.pdf")
    pdf.output(pdf_path)
    
    return pdf_path