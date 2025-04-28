# Taxi Booking System with Admin Panel, Ride History, Driver Assignment, and Enhanced UI + Create Account Feature

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import webbrowser
from datetime import datetime

# ----------- DATABASE SETUP -----------
conn = sqlite3.connect('taxi_system.db')
c = conn.cursor()

# User Table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

# Booking Table
c.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    name TEXT,
    phone TEXT,
    email TEXT,
    pickup TEXT,
    "drop" TEXT,
    fare REAL,
    timestamp TEXT,
    driver TEXT
)
''')

# Driver Table
c.execute('''
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    vehicle TEXT,
    status TEXT
)
''')

# Admin credentials (hardcoded for simplicity)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

conn.commit()

# ----------- UTILITY FUNCTIONS -----------
def calculate_distance_km(pickup, drop):
    if pickup.strip().lower() == drop.strip().lower():
        return 0
    return round(abs(len(pickup) - len(drop)) * 2 + 5, 2)

def calculate_fare(distance):
    return round(50 + distance * 10, 2)

def open_map(pickup, drop):
    pickup = pickup.replace(' ', '+')
    drop = drop.replace(' ', '+')
    url = f"https://www.google.com/maps/dir/{pickup}/{drop}"
    webbrowser.open(url)

def assign_driver():
    c.execute("SELECT * FROM drivers WHERE status='Available'")
    driver = c.fetchone()
    if driver:
        c.execute("UPDATE drivers SET status='Busy' WHERE id=?", (driver[0],))
        conn.commit()
        return driver[1]  # Return driver's name
    return "No Driver Available"

# ----------- MAIN APP -----------
root = tk.Tk()
root.title("Taxi Booking System")
root.geometry("500x600")

notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# ----------- USER TAB -----------
user_tab = ttk.Frame(notebook)
notebook.add(user_tab, text="User")

login_frame = ttk.LabelFrame(user_tab, text="Login")
login_frame.pack(pady=10, padx=10, fill="x")

username_entry = ttk.Entry(login_frame)
password_entry = ttk.Entry(login_frame, show='*')

tt_label = lambda frame, text: ttk.Label(frame, text=text).pack()
tt_label(login_frame, "Username")
username_entry.pack()
tt_label(login_frame, "Password")
password_entry.pack()

user_data = {}

booking_frame = ttk.LabelFrame(user_tab, text="Book a Taxi")
ride_result = ttk.Label(booking_frame, text="")

def user_login():
    user = username_entry.get()
    pwd = password_entry.get()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    if c.fetchone():
        messagebox.showinfo("Login", "Login Successful")
        user_data['username'] = user
        booking_frame.pack(padx=10, pady=10, fill="x")
        show_history()
    else:
        messagebox.showerror("Error", "Invalid Credentials")

def show_history():
    history_text.delete("1.0", tk.END)
    c.execute("SELECT pickup, \"drop\", fare, timestamp, driver FROM bookings WHERE username=?", (user_data['username'],))
    for row in c.fetchall():
        history_text.insert(tk.END, f"From: {row[0]}, To: {row[1]}, Fare: ₹{row[2]}, Time: {row[3]}, Driver: {row[4]}\n")

def create_account():
    user = username_entry.get()
    pwd = password_entry.get()
    if not user or not pwd:
        messagebox.showerror("Error", "Please enter both username and password")
        return
    c.execute("SELECT * FROM users WHERE username=?", (user,))
    if c.fetchone():
        messagebox.showerror("Error", "Username already exists")
    else:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))
        conn.commit()
        messagebox.showinfo("Success", "Account created. Please login.")

tt_button = lambda frame, text, command: ttk.Button(frame, text=text, command=command).pack(pady=5)
tt_button(login_frame, "Login", user_login)
tt_button(login_frame, "Create Account", create_account)

tt_label(booking_frame, "Name")
name_entry = ttk.Entry(booking_frame)
name_entry.pack()
tt_label(booking_frame, "Phone")
phone_entry = ttk.Entry(booking_frame)
phone_entry.pack()
tt_label(booking_frame, "Email")
email_entry = ttk.Entry(booking_frame)
email_entry.pack()
tt_label(booking_frame, "Pickup")
pickup_entry = ttk.Entry(booking_frame)
pickup_entry.pack()
tt_label(booking_frame, "Drop")
drop_entry = ttk.Entry(booking_frame)
drop_entry.pack()

fare_info_label = ttk.Label(booking_frame, text="")
fare_info_label.pack()

def show_fare():
    pickup = pickup_entry.get()
    drop = drop_entry.get()
    if not pickup or not drop:
        messagebox.showerror("Error", "Please enter pickup and drop")
        return
    distance = calculate_distance_km(pickup, drop)
    fare = calculate_fare(distance)
    fare_info_label.config(text=f"Distance: {distance} km | Fare: ₹{fare}")

def book_ride():
    pickup = pickup_entry.get()
    drop = drop_entry.get()
    if not pickup or not drop:
        messagebox.showerror("Error", "Please enter pickup and drop")
        return
    distance = calculate_distance_km(pickup, drop)
    fare = calculate_fare(distance)
    driver = assign_driver()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO bookings (username, name, phone, email, pickup, \"drop\", fare, timestamp, driver) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (user_data['username'], name_entry.get(), phone_entry.get(), email_entry.get(), pickup, drop, fare, ts, driver))
    conn.commit()
    ride_result.config(text=f"Ride Booked! Fare: ₹{fare}\nDriver: {driver}")
    show_history()
    open_map(pickup, drop)

tt_button(booking_frame, "Show Distance & Fare", show_fare)
tt_button(booking_frame, "Book Taxi", book_ride)
ride_result.pack()

history_frame = ttk.LabelFrame(user_tab, text="Ride History")
history_frame.pack(padx=10, pady=10, fill="both", expand=True)
history_text = tk.Text(history_frame, height=10)
history_text.pack(fill="both", expand=True)

# ----------- ADMIN TAB -----------
admin_tab = ttk.Frame(notebook)
notebook.add(admin_tab, text="Admin")

admin_username_entry = ttk.Entry(admin_tab)
admin_password_entry = ttk.Entry(admin_tab, show='*')

tt_label(admin_tab, "Admin Username")
admin_username_entry.pack()
tt_label(admin_tab, "Admin Password")
admin_password_entry.pack()

admin_data_frame = ttk.Frame(admin_tab)

bookings_tree = ttk.Treeview(admin_data_frame, columns=("user", "pickup", "drop", "fare", "driver"), show='headings')
for col in ("user", "pickup", "drop", "fare", "driver"):
    bookings_tree.heading(col, text=col.capitalize())
    bookings_tree.column(col, width=80)
bookings_tree.pack(fill="both", expand=True)

def load_bookings():
    for i in bookings_tree.get_children():
        bookings_tree.delete(i)
    c.execute("SELECT username, pickup, \"drop\", fare, driver FROM bookings")
    for row in c.fetchall():
        bookings_tree.insert("", tk.END, values=row)

def admin_login():
    if admin_username_entry.get() == ADMIN_USERNAME and admin_password_entry.get() == ADMIN_PASSWORD:
        messagebox.showinfo("Admin", "Welcome Admin!")
        admin_data_frame.pack(pady=10, fill="both", expand=True)
        load_bookings()
    else:
        messagebox.showerror("Error", "Invalid admin credentials")

tt_button(admin_tab, "Login as Admin", admin_login)

root.mainloop()