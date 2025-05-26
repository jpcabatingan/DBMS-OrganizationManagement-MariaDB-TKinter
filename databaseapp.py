import mysql.connector
from mysql.connector import errorcode
from tkinter import *
from tkinter import ttk, messagebox # Import messagebox for pop-ups
from tkinter import simpledialog # For input dialogs

# --- Database Configuration ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'admin',
    'password': 'admin',
    'database': 'welove127'
}

# --- Database Connection and Cursor (Global for easier GUI access) ---
cnx = None
cursor = None

def connect_db():
    global cnx, cursor
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("Successfully connected to the database!")
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Error", "Error: Access denied. Check your user name or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Database Error", "Error: Database does not exist. Please create it or check the name.")
        else:
            messagebox.showerror("Database Error", f"An unexpected error occurred: {err}")
        return False

def close_db():
    global cnx, cursor
    if cursor:
        cursor.close()
    if cnx and cnx.is_connected():
        cnx.close()
    print("Database connection closed.")

# --- GUI Functions ---

def add_member_gui():
    """Opens a dialog to get member details and adds to the database."""
    if not cnx or not cnx.is_connected():
        messagebox.showwarning("Connection Error", "Not connected to the database. Please try connecting first.")
        return

    # Use simpledialog for quick input, or build a more complex Toplevel window for many inputs
    student_no = simpledialog.askstring("Add Member", "Enter Student Number:")
    if not student_no: return # User cancelled

    first_name = simpledialog.askstring("Add Member", "Enter First Name:")
    if not first_name: return

    middle_name = simpledialog.askstring("Add Member", "Enter Middle Name (Optional):")
    # For optional fields, an empty string is fine

    last_name = simpledialog.askstring("Add Member", "Enter Last Name:")
    if not last_name: return

    degree_program = simpledialog.askstring("Add Member", "Enter Degree Program:")
    if not degree_program: return

    gender = simpledialog.askstring("Add Member", "Enter Gender:")
    if not gender: return

    batch_str = simpledialog.askstring("Add Member", "Enter Batch (Year, e.g., 2025):")
    if not batch_str: return
    try:
        batch = int(batch_str)
    except ValueError:
        messagebox.showerror("Input Error", "Batch must be an integer.")
        return

    # Execute the INSERT query
    query = """
    INSERT INTO member (student_no, first_name, middle_name, last_name, degree_program, gender, batch)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    values = (student_no, first_name, middle_name, last_name, degree_program, gender, batch)

    try:
        cursor.execute(query, values)
        cnx.commit() # Commit changes to the database
        messagebox.showinfo("Success", f"Member {first_name} {last_name} (ID: {student_no}) added successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding member: {err}")

def view_members_gui():
    """Fetches all members and displays them in a new window."""
    if not cnx or not cnx.is_connected():
        messagebox.showwarning("Connection Error", "Not connected to the database. Please try connecting first.")
        return

    view_window = Toplevel(root)
    view_window.title("View Members")
    view_window.geometry("800x400")

    # Create a Treeview widget for tabular data
    tree = ttk.Treeview(view_window)
    tree.pack(fill=BOTH, expand=True)

    # Define columns
    columns = ("Student No", "First Name", "Middle Name", "Last Name", "Degree Program", "Gender", "Batch")
    tree["columns"] = columns
    tree.heading("#0", text="ID (internal)", anchor=W) # Hidden column for Treeview's internal ID
    for col in columns:
        tree.heading(col, text=col, anchor=W)
        tree.column(col, width=100, anchor=W)

    # Add scrollbars
    vsb = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(view_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")


    query = "SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member ORDER BY last_name, first_name;"
    try:
        cursor.execute(query)
        rows = cursor.fetchall() # Fetch all results

        # Clear existing data in treeview
        for i in tree.get_children():
            tree.delete(i)

        # Insert fetched data into the treeview
        if rows:
            for row in rows:
                tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("No Data", "No members found in the database.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error viewing members: {err}")

# --- Main GUI Setup ---

root = Tk()
root.title("CMSC 127 - Member Management")
root.geometry("600x400")

# --- Menu Bar ---
menubar = Menu(root)
root.config(menu=menubar)

# Database Menu
db_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Database", menu=db_menu)
db_menu.add_command(label="Connect", command=connect_db)
db_menu.add_command(label="Disconnect", command=close_db)
db_menu.add_separator()
db_menu.add_command(label="Exit", command=root.quit)

# Members Menu
members_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Members", menu=members_menu)
members_menu.add_command(label="Add New Member", command=add_member_gui)
members_menu.add_command(label="View All Members", command=view_members_gui)

# --- Initial Connection Attempt ---
# You can connect automatically on startup, or via the menu
# connect_db() # Uncomment this if you want to auto-connect on app start

# --- Main Loop ---
# This ensures the database connection is closed when the GUI window is closed
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        close_db()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing) # Handle window close button
root.mainloop()

# The final finally block in your original script is now less relevant
# because the GUI handles closing, but it wouldn't hurt.
# For a GUI app, `on_closing` is the primary way to manage app exit.