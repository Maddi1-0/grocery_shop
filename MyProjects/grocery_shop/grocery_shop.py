from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
import json
import sqlite3
import datetime
import os

# Database Setup
conn = sqlite3.connect("grocery.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
conn.commit()

# Main Window
root = tk.Tk()
root.title("Grocery Shop Management")
root.geometry("900x500")
root.configure(bg="#f8f9fa")

# Product Data
products = [
    {"name": "Apples", "price": 3},
    {"name": "Bananas", "price": 2},
    {"name": "Tomatoes", "price": 4},
    {"name": "Potatoes", "price": 1}
]

cart = []

# Functions
def add_to_cart(product):
    cart.append(product)
    update_cart_display()

def update_cart_display():
    cart_listbox.delete(0, tk.END)
    total_price = sum(item['price'] for item in cart)
    for item in cart:
        cart_listbox.insert(tk.END, f"{item['name']} - £{item['price']}")
    total_label.config(text=f"Total: £{total_price}")

def checkout():
    if not cart:
        messagebox.showwarning("Cart Empty", "Please add items to the cart!")
        return
    total_price = sum(item['price'] for item in cart)
    items = "\n".join(f"{item['name']} - £{item['price']}" for item in cart)
    messagebox.showinfo("Bill", f"Items:\n{items}\n\nTotal: £{total_price}")

def open_admin_panel():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel")
    admin_window.geometry("400x300")

    ttk.Label(admin_window, text="Product Name:").pack(pady=5)
    name_entry = ttk.Entry(admin_window)
    name_entry.pack(pady=5)

    ttk.Label(admin_window, text="Price:").pack(pady=5)
    price_entry = ttk.Entry(admin_window)
    price_entry.pack(pady=5)

    def add_product():
        name = name_entry.get()
        price = price_entry.get()
        if name and price:
            cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, float(price)))
            conn.commit()
            messagebox.showinfo("Success", "Product added!")
            admin_window.destroy()

    ttk.Button(admin_window, text="Add Product", command=add_product).pack(pady=10)

# Search Function
def search_products():
    query = search_var.get().lower()
    product_listbox.delete(0, tk.END)
    for product in products:
        if query in product["name"].lower():
            product_listbox.insert(tk.END, f"{product['name']} - £{product['price']}")


def generate_receipt():
    if not cart:
        messagebox.showwarning("Cart Empty", "Please add items to the cart!")
        return

    customer_name = simpledialog.askstring("Customer Name", "Enter customer name:")
    if not customer_name:
        return  # If the user cancels, don't proceed

    receipt_folder = "Receipts"
    if not os.path.exists(receipt_folder):
        os.makedirs(receipt_folder)

    receipt_filename = f"{receipt_folder}/{customer_name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    
    pdf = canvas.Canvas(receipt_filename, pagesize=letter)
    pdf.setTitle("Grocery Shop Receipt")

    pdf.drawString(100, 750, f"Grocery Shop Receipt - {customer_name}")
    pdf.drawString(100, 730, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(100, 710, "--------------------------------------")

    y_position = 690
    total_price = 0

    for item in cart:
        pdf.drawString(100, y_position, f"{item['name']} - £{item['price']}")
        total_price += item['price']
        y_position -= 20

    pdf.drawString(100, y_position, "--------------------------------------")
    pdf.drawString(100, y_position - 20, f"Total: £{total_price}")

    pdf.save()
    messagebox.showinfo("Receipt Generated", f"Receipt saved as {receipt_filename}")

# Function to Load Products from Database
def load_products():
    cursor.execute("SELECT name, price FROM products")
    return cursor.fetchall()

def show_sales_summary():
    summary_window = tk.Toplevel(root)
    summary_window.title("Sales Summary")
    summary_window.geometry("300x200")

    cursor.execute("SELECT COUNT(*), SUM(price) FROM products")
    total_products, total_sales = cursor.fetchone()

    ttk.Label(summary_window, text=f"Total Products: {total_products}").pack(pady=10)
    ttk.Label(summary_window, text=f"Total Sales: £{total_sales:.2f}").pack(pady=10)


# Add Default Products If Empty
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO products (name, price) VALUES (?, ?)", [
        ("Apples", 3),
        ("Bananas", 2),
        ("Tomatoes", 4),
        ("Potatoes", 1)
    ])
    conn.commit()

# Load Products
products = [{"name": row[0], "price": row[1]} for row in load_products()]

# Frames
product_frame = tk.Frame(root, bg="white", relief=tk.RIDGE, bd=2)
product_frame.pack(side=tk.LEFT, padx=10, pady=10, fill="y")

cart_frame = tk.Frame(root, bg="white", relief=tk.RIDGE, bd=2)
cart_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill="y")

# Product Section
ttk.Label(product_frame, text="Products", font=("Arial", 14, "bold")).pack(pady=5)

for product in products:
    btn = ttk.Button(product_frame, text=f"{product['name']} - £{product['price']}",
                     command=lambda p=product: add_to_cart(p))
    btn.pack(pady=5)

# Cart Section
ttk.Label(cart_frame, text="Shopping Cart", font=("Arial", 14, "bold")).pack(pady=5)
cart_listbox = tk.Listbox(cart_frame, width=40, height=10)
cart_listbox.pack()
total_label = ttk.Label(cart_frame, text="Total: £0", font=("Arial", 12, "bold"))
total_label.pack()
checkout_button = ttk.Button(cart_frame, text="Checkout", command=generate_receipt)
checkout_button.pack(pady=5)


# Search Bar UI
search_var = tk.StringVar()
search_entry = tk.Entry(product_frame, textvariable=search_var, font=("Arial", 12), width=20)
search_entry.pack(pady=5)
search_button = tk.Button(product_frame, text="Search", command=search_products, bg="orange", fg="white", font=("Arial", 10))
search_button.pack(pady=5)

# Product Listbox
product_listbox = tk.Listbox(product_frame, width=30, height=10)
product_listbox.pack()

# Load Initial Products
for product in products:
    product_listbox.insert(tk.END, f"{product['name']} - £{product['price']}")


admin_button = ttk.Button(root, text="Admin Panel", command=open_admin_panel)
admin_button.pack(pady=5)

summary_button = ttk.Button(root, text="View Sales Summary", command=show_sales_summary)
summary_button.pack(pady=5)


style = ttk.Style()
style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
style.configure("TLabel", font=("Arial", 12))
style.configure("TFrame", background="#f4f4f4")  # Light gray background

root.mainloop()
