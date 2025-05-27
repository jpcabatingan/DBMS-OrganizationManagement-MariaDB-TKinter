# shared_variables.py

import mysql.connector
from tkinter import messagebox
from tkinter.font import BOLD
import tkinter as tk # Ensure tk is imported for BasePage

# Database configuration - Replace with your actual database credentials
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'admin',
    'password': 'admin',
    'database': 'welove127'
}

cnx = None
cursor = None

def connect_db():
    global cnx, cursor
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor(dictionary=True) # dictionary=True for column names as keys
        print("Successfully connected to the database!")
        return True
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database: {err}")
        return False

def disconnect_db():
    global cnx, cursor
    if cursor:
        cursor.close()
    if cnx:
        cnx.close()
        print("Database connection closed.")

def execute_query(query, params=None):
    global cnx, cursor
    try:
        cursor.execute(query, params)
        cnx.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        messagebox.showerror("Database Error", f"Error executing query: {err}")
        if cnx:
            cnx.rollback() # Rollback changes on error
        return -1 # Indicate an error

def fetch_one(query, params=None):
    global cursor
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error fetching one row: {err}")
        messagebox.showerror("Database Error", f"Error fetching data: {err}")
        return None

def fetch_all(query, params=None):
    global cursor
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching all rows: {err}")
        messagebox.showerror("Database Error", f"Error fetching data: {err}")
        return None

class BasePage(tk.Frame):
    def __init__(self, master, app_instance, title_text=""):
        super().__init__(master, bg="#f0f0f0")
        self.app = app_instance # app_instance is now the App class instance

        # Instead of self.pack(), let the master (App) manage BasePage with grid
        # self.pack(fill="both", expand=True) # <--- REMOVE THIS LINE

        # Configure BasePage to be gridded by its parent (the App instance)
        # This allows App's show_page to put BasePage in grid correctly.
        # But crucially, we'll use grid within BasePage itself from now on.
        self.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.grid_rowconfigure(1, weight=1) # Row for content_frame
        self.grid_columnconfigure(0, weight=1) # Column for content_frame

        # The back button will be in its own row at the top
        self.back_button = tk.Button(self, text="Back to Menu", command=self.go_back,
                                     bg="#888888", fg="white", font=("Arial", 10, BOLD), relief="flat", padx=10, pady=5)
        # Place back_button using grid directly on BasePage
        self.back_button.grid(row=0, column=0, sticky=tk.NW, padx=20, pady=10)


        self.content_frame = tk.Frame(self, bg="#f0f0f0")
        # Place content_frame using grid on BasePage
        self.content_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=20, pady=20)
        
        # Now, children of content_frame can use grid (or pack, independently)
        self.content_frame.grid_columnconfigure(0, weight=1) # This is fine here

    def go_back(self):
        # Now access current user type from the app_instance
        if self.app.current_user_type == 'organization' and self.app.current_org_name:
            self.app.show_organization_menu()
        elif self.app.current_user_type == 'member': 
            self.app.show_member_menu()
        elif self.app.current_user_type == 'admin':
            # Assuming you have an admin menu method in App
            # self.app.show_admin_menu() 
            messagebox.showinfo("Coming Soon", "Admin menu is not yet implemented.") # Placeholder
        else:
            self.app.show_auth_page() # Default to auth page if no specific menu is applicable