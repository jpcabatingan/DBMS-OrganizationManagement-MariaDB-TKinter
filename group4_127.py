import mysql.connector
from mysql.connector import errorcode
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.font import BOLD

# --- Database Configuration ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'admin',
    'password': 'admin',
    'database': 'welove127'
}

# --- Global Database Connection Variables ---
cnx = None
cursor = None

# --- Database Connection Functions ---
def connect_db():
    global cnx, cursor
    if cnx and cnx.is_connected():
        messagebox.showinfo("Database Status", "Already connected to the database.")
        return True
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("Successfully connected to the database!")
        messagebox.showinfo("Connection Success", "Successfully connected to the database!")
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Error", "Access denied. Check your user name or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Database Error", f"Database '{DB_CONFIG['database']}' does not exist. Please create it or check the name.")
        else:
            messagebox.showerror("Database Error", f"An unexpected error occurred: {err}")
        return False

def close_db():
    global cnx, cursor
    if cursor:
        cursor.close()
        cursor = None # Set to None after closing
    if cnx and cnx.is_connected():
        cnx.close()
        cnx = None # Set to None after closing
        messagebox.showinfo("Connection Closed", "Database connection closed.")
        print("Database connection closed.")
    else:
        messagebox.showwarning("Database Status", "No active database connection to close.")

# --- Frame Management ---
current_content_frame = None

def show_content_frame(frame_class):
    """Destroys current content frame and shows a new one."""
    global current_content_frame
    if current_content_frame is not None:
        current_content_frame.destroy()

    current_content_frame = frame_class(content_area_frame) # Pack into the content_area_frame
    current_content_frame.pack(fill="both", expand=True)

    # Automatically connect if a data-related frame is loaded and not connected
    # HomePage does not require a DB connection.
    if frame_class != HomePage and (not cnx or not cnx.is_connected()):
        connect_db()

# --- GUI Content Frames ---

class HomePage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg="#f0f0f0") # Light grey background
        Label(self, text="Welcome to the Member Management System!",
              font=("Arial", 28, BOLD), bg="#f0f0f0", fg="#333").pack(pady=80)
        Label(self, text="Use the navigation buttons above to access different sections.",
              font=("Arial", 14), bg="#f0f0f0", fg="#555").pack(pady=10)
        Label(self, text="Remember to 'Connect to DB' from the 'Database' menu.",
              font=("Arial", 12), bg="#f0f0f0", fg="#888").pack(pady=50)


class MembersHomePage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg="#f0f0f0")
        Label(self, text="Members Management", font=("Arial", 24, BOLD), bg="#f0f0f0").pack(pady=30)

        Button(self, text="Add New Member", font=("Arial", 14), width=20,
               command=lambda: show_content_frame(AddMemberPage),
               bg="#4CAF50", fg="white", activebackground="#45a049").pack(pady=10)
        Button(self, text="View All Members", font=("Arial", 14), width=20,
               command=lambda: show_content_frame(ViewMembersPage),
               bg="#2196F3", fg="white", activebackground="#1976D2").pack(pady=10)

class AddMemberPage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(padx=20, pady=20, bg="#e0e0e0")

        Label(self, text="Add New Member", font=("Arial", 20, BOLD), bg="#e0e0e0").grid(row=0, column=0, columnspan=2, pady=20)

        self.entries = {}
        fields = [
            ("Student Number:", "student_no"),
            ("First Name:", "first_name"),
            ("Middle Name:", "middle_name"),
            ("Last Name:", "last_name"),
            ("Degree Program:", "degree_program"),
            ("Gender:", "gender"),
            ("Batch (Year):", "batch")
        ]

        for i, (label_text, field_name) in enumerate(fields):
            Label(self, text=label_text, font=("Arial", 10), bg="#e0e0e0", anchor="w").grid(row=i+1, column=0, sticky="ew", pady=5, padx=5)
            entry = Entry(self, width=40, font=("Arial", 10))
            entry.grid(row=i+1, column=1, sticky="ew", pady=5, padx=5)
            self.entries[field_name] = entry

        submit_btn = Button(self, text="Add Member", command=self.submit_member, font=("Arial", 12, BOLD), bg="#4CAF50", fg="white", activebackground="#45a049")
        submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20, padx=5, sticky="ew")

        back_btn = Button(self, text="<- Back to Members", command=lambda: show_content_frame(MembersHomePage), font=("Arial", 10), bg="#6c757d", fg="white", activebackground="#5a6268")
        back_btn.grid(row=len(fields)+2, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

    def submit_member(self):
        if not cnx or not cnx.is_connected():
            messagebox.showwarning("Connection Error", "Not connected to the database. Please connect first.")
            return

        data = {field: entry.get().strip() for field, entry in self.entries.items()}

        required_fields = ["student_no", "first_name", "last_name", "degree_program", "gender", "batch"]
        for field in required_fields:
            if not data[field]:
                messagebox.showerror("Input Error", f"'{field.replace('_', ' ').title()}' is required.")
                return

        try:
            data['batch'] = int(data['batch'])
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be a valid year (integer).")
            return

        query = """
        INSERT INTO member (student_no, first_name, middle_name, last_name, degree_program, gender, batch)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            data['student_no'],
            data['first_name'],
            data['middle_name'] if data['middle_name'] else None,
            data['last_name'],
            data['degree_program'],
            data['gender'],
            data['batch']
        )

        try:
            cursor.execute(query, values)
            cnx.commit()
            messagebox.showinfo("Success", f"Member {data['first_name']} {data['last_name']} added successfully!")
            for entry in self.entries.values():
                entry.delete(0, END)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding member: {err}")


class ViewMembersPage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(padx=10, pady=10, bg="#e0e0e0")

        Label(self, text="All Members", font=("Arial", 20, BOLD), bg="#e0e0e0").pack(pady=10)

        tree_frame = Frame(self, bg="#e0e0e0")
        tree_frame.pack(fill=BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        columns = ("student_no", "first_name", "middle_name", "last_name", "degree_program", "gender", "batch")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title(), anchor=W)
            self.tree.column(col, width=100, anchor=W)

        self.tree.column("student_no", width=120)
        self.tree.column("first_name", width=120)
        self.tree.column("middle_name", width=100)
        self.tree.column("last_name", width=120)
        self.tree.column("degree_program", width=150)
        self.tree.column("gender", width=80)
        self.tree.column("batch", width=70)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self.load_members()

        back_btn = Button(self, text="<- Back to Members", command=lambda: show_content_frame(MembersHomePage), font=("Arial", 10), bg="#6c757d", fg="white", activebackground="#5a6268")
        back_btn.pack(pady=10)

    def load_members(self):
        if not cnx or not cnx.is_connected():
            messagebox.showwarning("Connection Error", "Not connected to the database. Please connect first.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        query = "SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member ORDER BY last_name, first_name;"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Data", "No members found in the database.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error viewing members: {err}")

# --- Placeholder Content Frames ---
class OrganizationsHomePage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg="#f0f0f0")
        Label(self, text="Organizations Management (Coming Soon)", font=("Arial", 20, BOLD), bg="#f0f0f0").pack(pady=30)
        Button(self, text="Add New Organization", font=("Arial", 14), width=20,
               command=lambda: messagebox.showinfo("Org", "Add Organization Form goes here!"),
               bg="#4CAF50", fg="white", activebackground="#45a049").pack(pady=10)
        Button(self, text="View All Organizations", font=("Arial", 14), width=20,
               command=lambda: messagebox.showinfo("Org", "View Organizations Table goes here!"),
               bg="#2196F3", fg="white", activebackground="#1976D2").pack(pady=10)

class FeesHomePage(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg="#f0f0f0")
        Label(self, text="Fees Management (Coming Soon)", font=("Arial", 20, BOLD), bg="#f0f0f0").pack(pady=30)
        Button(self, text="View Unpaid Fees", font=("Arial", 14), width=20,
               command=lambda: messagebox.showinfo("Fees", "Functionality to view unpaid fees goes here!"),
               bg="#ff9800", fg="white", activebackground="#f57c00").pack(pady=10)
        Button(self, text="Record Payment", font=("Arial", 14), width=20,
               command=lambda: messagebox.showinfo("Fees", "Functionality to record payments goes here!"),
               bg="#607d8b", fg="white", activebackground="#455a64").pack(pady=10)

# --- Main GUI Setup ---

root = Tk()
root.title("CMSC 127 - Member Management System")
root.geometry("800x600")
root.minsize(700, 500)

# --- Top Navigation Bar ---
top_nav_frame = Frame(root, bg="#333", relief=RAISED, bd=2) # Dark grey background for nav bar
top_nav_frame.pack(side="top", fill="x")

# Navigation buttons
btn_font = ("Arial", 12, BOLD)
btn_padx = 15
btn_pady = 10

Button(top_nav_frame, text="Home", font=btn_font, fg="white", bg="#333", activebackground="#555",
       command=lambda: show_content_frame(HomePage)).pack(side="left", padx=btn_padx, pady=btn_pady)
Button(top_nav_frame, text="Members", font=btn_font, fg="white", bg="#333", activebackground="#555",
       command=lambda: show_content_frame(MembersHomePage)).pack(side="left", padx=btn_padx, pady=btn_pady)
Button(top_nav_frame, text="Organizations", font=btn_font, fg="white", bg="#333", activebackground="#555",
       command=lambda: show_content_frame(OrganizationsHomePage)).pack(side="left", padx=btn_padx, pady=btn_pady)
Button(top_nav_frame, text="Fees", font=btn_font, fg="white", bg="#333", activebackground="#555",
       command=lambda: show_content_frame(FeesHomePage)).pack(side="left", padx=btn_padx, pady=btn_pady)


# --- Content Area Frame ---
# This frame will hold the dynamically loaded content pages
content_area_frame = Frame(root, bg="#f0f0f0")
content_area_frame.pack(side="top", fill="both", expand=True)

# --- Menu Bar (for Database and Exit) ---
menubar = Menu(root)
root.config(menu=menubar)

db_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Database", menu=db_menu)
db_menu.add_command(label="Connect to DB", command=connect_db)
db_menu.add_command(label="Disconnect from DB", command=close_db)
db_menu.add_separator()
db_menu.add_command(label="Exit", command=root.quit)

# --- Initial Content Display ---
show_content_frame(HomePage) # Start with the Home Page by default

# --- Handle Window Closing ---
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        close_db() # Ensure DB connection is closed
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing) # Bind the function to the window's close button

# --- Run the GUI ---
root.mainloop()