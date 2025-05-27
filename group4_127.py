import mysql.connector
from mysql.connector import errorcode
from tkinter import *
from tkinter import ttk, messagebox, Toplevel
from tkinter.font import BOLD
import datetime
from passlib.hash import pbkdf2_sha256 
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
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

# --- Global Authentication Variables ---
CURRENT_USER_TYPE = None # 'member' or 'organization' or None
CURRENT_USER_ID = None   # student_no for member, org_id for organization
CURRENT_ORG_NAME = None # To store the organization name after organization login

# --- Database Connection Functions ---
# Modified connect_db: No longer shows "Already connected" message
def connect_db():
    global cnx, cursor
    if cnx and cnx.is_connected():
        return True # Already connected

    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor(buffered=True) # Use buffered cursor for multiple queries
        print("Successfully connected to the database!")
        # messagebox.showinfo("Connection Success", "Successfully connected to the database!") # Removed for silent connect
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Error", "Access denied. Check your user name or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Database Error", f"Database '{DB_CONFIG['database']}' does not exist.")
        else:
            messagebox.showerror("Database Error", str(err))
        return False

# Modified disconnect_db: No longer shows "No active connection" message
def disconnect_db():
    global cnx, cursor
    if cnx and cnx.is_connected():
        cursor.close()
        cnx.close()
        # messagebox.showinfo("Connection Status", "Disconnected from the database.") # Removed for silent disconnect
        print("Disconnected from the database.")
    # else: # Removed for silent disconnect
        # messagebox.showinfo("Connection Status", "No active database connection to close.")


# --- AuthPage Class ---
# --- AuthPage Class ---
class AuthPage(ttk.Frame):
    def __init__(self, master, app_instance):
        super().__init__(master, padding="0")
        self.app = app_instance
        self.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Configure grid for the main AuthPage frame to have two columns
        self.grid_columnconfigure(0, weight=1) # Member panel column
        self.grid_columnconfigure(1, weight=1) # Organization panel column
        self.grid_rowconfigure(0, weight=1) # Single row

        # --- Member Panel (Left Side) ---
        member_panel = ttk.Frame(self, style='AuthPanel.TFrame', padding="30")
        member_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=0, pady=0)
        # We need 3 columns for the signup section to avoid overlap:
        # Col 0: Left Half of Fields (e.g., Student No, First Name)
        # Col 1: Right Half of Fields (e.g., Degree Program, Gender)
        # Col 2: The Signup Button
        member_panel.grid_columnconfigure(0, weight=1)
        member_panel.grid_columnconfigure(1, weight=1)
        member_panel.grid_columnconfigure(2, weight=0) # This column will hold the signup button

        # Member Login Section
        ttk.Label(member_panel, text="Member", font=("Arial", 24, BOLD), foreground='black').grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)) # Adjusted columnspan
        ttk.Label(member_panel, text="Enter your credentials below or sign up for a new account.", font=("Arial", 10), foreground='grey').grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 20)) # Adjusted columnspan

        ttk.Label(member_panel, text="Student no.", font=("Arial", 10, BOLD)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0)) # Adjusted columnspan
        self.member_student_no_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.member_student_no_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5)) # Spans 2 columns
        ttk.Label(member_panel, text="Format: 20XX-XXXXX", font=("Arial", 8), foreground='grey').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 20)) # Spans 2 columns

        # Login button should now be in column 2, aligning with the image
        ttk.Button(member_panel, text="Log-in", style='Login.TButton', command=self.member_login).grid(row=3, column=2, sticky=tk.E, padx=(5,0))


        # --- Separator Line for Member Section ---
        # Adjusted columnspan to span all 3 columns of member_panel
        ttk.Frame(member_panel, height=2, relief='sunken', style='Separator.TFrame').grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 20))


        # Member Sign-up Section (adjusted row numbers due to separator)
        # Student no. field
        ttk.Label(member_panel, text="Student no.", font=("Arial", 10, BOLD)).grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_student_no_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_student_no_entry.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(member_panel, text="Format: 20XX-XXXXX", font=("Arial", 8), foreground='grey').grid(row=8, column=0, sticky=tk.W, pady=(0, 10))

        # Degree Program field
        ttk.Label(member_panel, text="Degree Program", font=("Arial", 10, BOLD)).grid(row=6, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_degree_program_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_degree_program_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: BS Computer Science", font=("Arial", 8), foreground='grey').grid(row=8, column=1, sticky=tk.W, pady=(0, 10))

        # First Name field
        ttk.Label(member_panel, text="First Name", font=("Arial", 10, BOLD)).grid(row=9, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_first_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_first_name_entry.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))

        # Gender field
        ttk.Label(member_panel, text="Gender", font=("Arial", 10, BOLD)).grid(row=9, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_gender_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_gender_entry.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: F / M", font=("Arial", 8), foreground='grey').grid(row=11, column=1, sticky=tk.W, pady=(0, 10))

        # Middle Name field
        ttk.Label(member_panel, text="Middle Name", font=("Arial", 10, BOLD)).grid(row=12, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_middle_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_middle_name_entry.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(member_panel, text="Optional", font=("Arial", 8), foreground='grey').grid(row=14, column=0, sticky=tk.W, pady=(0, 10))

        # Batch field
        ttk.Label(member_panel, text="Batch", font=("Arial", 10, BOLD)).grid(row=12, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_batch_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_batch_entry.grid(row=13, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: 20XX", font=("Arial", 8), foreground='grey').grid(row=14, column=1, sticky=tk.W, pady=(0, 10))

        # Last Name field and Sign-up button - THIS IS THE CRUCIAL CHANGE
        ttk.Label(member_panel, text="Last Name", font=("Arial", 10, BOLD)).grid(row=15, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_last_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_last_name_entry.grid(row=16, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5)) # Span columns 0 and 1
        ttk.Button(member_panel, text="Sign-up", style='Login.TButton', command=self.member_signup).grid(row=16, column=2, sticky=tk.E, padx=(5,0)) # Button in column 2

        # --- Organization Panel (Right Side) ---
        org_panel = ttk.Frame(self, style='AuthPanel.TFrame', padding="30")
        org_panel.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=0, pady=0)
        # We need 2 columns for the signup section to avoid overlap for org signup:
        # Col 0: Entry field
        # Col 1: Button
        org_panel.grid_columnconfigure(0, weight=1)
        org_panel.grid_columnconfigure(1, weight=0) # This column will hold the signup button

        # Organization Login Section
        ttk.Label(org_panel, text="Organization", font=("Arial", 24, BOLD), foreground='black').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(org_panel, text="Enter your org ID below or register a new org.", font=("Arial", 10), foreground='grey').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        ttk.Label(org_panel, text="Organization ID", font=("Arial", 10, BOLD)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.org_id_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.org_id_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Button(org_panel, text="Log-in", style='Login.TButton', command=self.org_login).grid(row=3, column=1, sticky=tk.E, padx=(5,0))


        # --- Separator Line for Organization Section ---
        ttk.Frame(org_panel, height=2, relief='sunken', style='Separator.TFrame').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 20))


        # Organization Sign-up Section (adjusted row numbers due to separator)
        ttk.Label(org_panel, text="Organization ID", font=("Arial", 10, BOLD)).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.signup_org_id_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.signup_org_id_entry.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(org_panel, text="Format: XXXXX", font=("Arial", 8), foreground='grey').grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        ttk.Label(org_panel, text="Organization Name", font=("Arial", 10, BOLD)).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.signup_org_name_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.signup_org_name_entry.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5)) # Span 1 column
        ttk.Button(org_panel, text="Sign-up", style='Login.TButton', command=self.org_signup).grid(row=10, column=1, sticky=tk.E, padx=(5,0)) 

        # Configure org_panel columns weights after all widgets are placed
        org_panel.grid_columnconfigure(0, weight=1)
        org_panel.grid_columnconfigure(1, weight=0)


        # --- Styling ---
        style = ttk.Style(self)
        style.theme_use('clam')

        # Define custom colors
        LIGHT_GREY = "#E0E0E0"
        DARK_GREY = "#616161"
        PURPLE = "#673AB7"

        self.master.configure(bg=LIGHT_GREY)

        style.configure('TFrame', background=LIGHT_GREY)
        style.configure('AuthPanel.TFrame', background='white', borderwidth=0, relief='flat')

        # New style for the separator line
        style.configure('Separator.TFrame', background=DARK_GREY)


        style.configure('TLabel', background='white', foreground='black')
        style.configure('Login.TButton',
                        background=PURPLE,
                        foreground='white',
                        font=("Arial", 10, BOLD),
                        borderwidth=0,
                        focuscolor=PURPLE,
                        relief="flat")
        style.map('Login.TButton',
                  background=[('active', '#5E35B1'), ('pressed', '#4527A0')],
                  foreground=[('active', 'white'), ('pressed', 'white')])

        style.configure('TEntry',
                        fieldbackground=LIGHT_GREY,
                        foreground='black',
                        borderwidth=0,
                        padding=5)
        style.map('TEntry',
                  fieldbackground=[('focus', '#BBDEFB')])


    # --- Member Logic (No changes needed, already uses internal fields) ---
    def member_login(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID
        student_no = self.member_student_no_entry.get().strip()
        if not student_no:
            messagebox.showerror("Login Error", "Please enter a Student Number.")
            return

        try:
            cursor.execute("SELECT student_no, first_name FROM member WHERE student_no = %s", (student_no,))
            member_info = cursor.fetchone()
            if member_info:
                CURRENT_USER_TYPE = 'member'
                CURRENT_USER_ID = student_no
                messagebox.showinfo("Login Success", f"Welcome, {member_info[1]} (Member)!")
                self.app.show_member_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid Student Number. Please try again.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to login: {err}")

    def member_signup(self):
        student_no = self.signup_student_no_entry.get().strip()
        first_name = self.signup_first_name_entry.get().strip()
        middle_name = self.signup_middle_name_entry.get().strip()
        last_name = self.signup_last_name_entry.get().strip()
        degree_program = self.signup_degree_program_entry.get().strip()
        gender = self.signup_gender_entry.get().strip()
        batch = self.signup_batch_entry.get().strip()

        if not all([student_no, first_name, last_name, degree_program, gender, batch]):
            messagebox.showerror("Input Error", "Please fill in all required fields (Student No, First Name, Last Name, Degree Program, Gender, Batch).")
            return

        try:
            cursor.execute("SELECT student_no FROM member WHERE student_no = %s", (student_no,))
            if cursor.fetchone():
                messagebox.showerror("Signup Error", "Student Number already exists.")
                return

            insert_query = """
            INSERT INTO member (student_no, first_name, middle_name, last_name, degree_program, gender, batch)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (student_no, first_name, middle_name if middle_name else None, last_name, degree_program, gender, int(batch)))
            cnx.commit()
            messagebox.showinfo("Sign Up Success", "Member registered successfully!")
            self.signup_student_no_entry.delete(0, tk.END)
            self.signup_first_name_entry.delete(0, tk.END)
            self.signup_middle_name_entry.delete(0, tk.END)
            self.signup_last_name_entry.delete(0, tk.END)
            self.signup_degree_program_entry.delete(0, tk.END)
            self.signup_gender_entry.delete(0, tk.END)
            self.signup_batch_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to sign up: {err}")

    # --- Organization Logic (No changes needed, already uses internal fields) ---
    def org_login(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID, CURRENT_ORG_NAME
        org_id = self.org_id_entry.get().strip()

        if not org_id:
            messagebox.showerror("Login Error", "Please enter Org ID.")
            return

        try:
            cursor.execute("SELECT org_id, org_name FROM organization WHERE org_id = %s", (org_id,))
            org_info = cursor.fetchone()
            if org_info:
                CURRENT_USER_TYPE = 'organization'
                CURRENT_USER_ID = org_id
                CURRENT_ORG_NAME = org_info[1]
                messagebox.showinfo("Login Success", f"Welcome, {CURRENT_ORG_NAME} (Organization)!")
                self.app.show_organization_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid Org ID. Please try again.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to login: {err}")

    def org_signup(self):
        org_id = self.signup_org_id_entry.get().strip()
        org_name = self.signup_org_name_entry.get().strip()

        if not all([org_id, org_name]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            cursor.execute("SELECT org_id FROM organization WHERE org_id = %s OR org_name = %s", (org_id, org_name))
            if cursor.fetchone():
                messagebox.showerror("Signup Error", "Organization ID or Name already exists.")
                return

            insert_query = """
            INSERT INTO organization (org_id, org_name, no_of_members)
            VALUES (%s, %s, 0)
            """
            cursor.execute(insert_query, (org_id, org_name))
            cnx.commit()
            messagebox.showinfo("Sign Up Success", "Organization registered successfully!")
            self.signup_org_id_entry.delete(0, tk.END)
            self.signup_org_name_entry.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to sign up: {err}")

# --- Base Page Class ---
class BasePage(ttk.Frame):
    def __init__(self, master, app_instance, title):
        super().__init__(master, padding="20")
        self.app = app_instance
        self.title = title
        self.grid(row=0, column=0, sticky=(N, W, E, S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text=self.title, font=(None, 16, BOLD)).grid(row=0, column=0, columnspan=2, pady=10)
        self.back_button = ttk.Button(self, text="Back to Menu", command=self.go_back)
        self.back_button.grid(row=99, column=0, columnspan=2, pady=20) # A fixed position for back button

    def go_back(self):
        if CURRENT_USER_TYPE == 'member':
            self.app.show_member_menu()
        elif CURRENT_USER_TYPE == 'organization':
            self.app.show_organization_menu()
        else:
            self.app.show_auth_page()

# --- Member Pages ---
class MemberMenuPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Member Menu")
        self.create_member_menu_widgets()

    def create_member_menu_widgets(self):
        self.back_button.grid_forget() # Hide default back button

        row_idx = 1
        ttk.Button(self, text="View Personal Info", command=self.app.show_view_personal_info_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Edit Personal Info", command=self.app.show_edit_personal_info_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Registered Organizations", command=self.app.show_view_registered_orgs_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Unpaid Fees (All Organizations)", command=self.app.show_view_members_unpaid_fees_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Logout", command=self.app.logout).grid(row=row_idx + 1, column=0, sticky=W, pady=20)

class ViewPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "View Personal Information")
        self.display_info()

    def display_info(self):
        for widget in self.winfo_children():
            if widget not in [self.back_button, self.children['!label']]: # Keep title and back button
                widget.destroy()

        # No need to call connect_db here
        try:
            cursor.execute("SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member WHERE student_no = %s", (CURRENT_USER_ID,))
            member_info = cursor.fetchone()

            if member_info:
                labels = ["Student No:", "First Name:", "Middle Name:", "Last Name:", "Degree Program:", "Gender:", "Batch:"]
                for i, label_text in enumerate(labels):
                    ttk.Label(self, text=label_text, font=(None, 10, BOLD)).grid(row=i + 1, column=0, sticky=W, padx=5, pady=2)
                    ttk.Label(self, text=member_info[i]).grid(row=i + 1, column=1, sticky=W, padx=5, pady=2)
            else:
                ttk.Label(self, text="Member information not found.", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve personal info: {err}")
        # No finally block to disconnect_db, connection is persistent

class EditPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Edit Personal Information")
        self.create_edit_form()

    def create_edit_form(self):
        # No need to call connect_db here
        try:
            cursor.execute("SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member WHERE student_no = %s", (CURRENT_USER_ID,))
            member_info = cursor.fetchone()

            if member_info:
                self.entries = {}
                labels = ["Student No:", "First Name:", "Middle Name:", "Last Name:", "Degree Program:", "Gender:", "Batch:"]
                field_names = ["student_no", "first_name", "middle_name", "last_name", "degree_program", "gender", "batch"]

                for i, label_text in enumerate(labels):
                    ttk.Label(self, text=label_text).grid(row=i + 1, column=0, sticky=W, padx=5, pady=2)
                    entry = ttk.Entry(self)
                    entry.grid(row=i + 1, column=1, sticky=(W, E), padx=5, pady=2)
                    entry.insert(0, str(member_info[i]) if member_info[i] is not None else "")
                    self.entries[field_names[i]] = entry
                self.entries["student_no"].config(state='readonly') # Student number cannot be edited

                ttk.Button(self, text="Save Changes", command=self.save_changes).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)
            else:
                ttk.Label(self, text="Member information not found.", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load personal info for editing: {err}")
        # No finally block to disconnect_db, connection is persistent

    def save_changes(self):
        updated_data = {
            "first_name": self.entries["first_name"].get().strip(),
            "middle_name": self.entries["middle_name"].get().strip() or None, # Store empty string as NULL
            "last_name": self.entries["last_name"].get().strip(),
            "degree_program": self.entries["degree_program"].get().strip(),
            "gender": self.entries["gender"].get().strip(),
            "batch": self.entries["batch"].get().strip()
        }

        # Basic validation
        if not all([updated_data["first_name"], updated_data["last_name"], updated_data["degree_program"], updated_data["gender"], updated_data["batch"]]):
            messagebox.showerror("Input Error", "Please fill in all required fields (First Name, Last Name, Degree Program, Gender, Batch).")
            return
        try:
            updated_data["batch"] = int(updated_data["batch"])
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
            return

        # No need to call connect_db here
        try:
            update_query = """
            UPDATE member SET
                first_name = %s,
                middle_name = %s,
                last_name = %s,
                degree_program = %s,
                gender = %s,
                batch = %s
            WHERE student_no = %s
            """
            cursor.execute(update_query, (
                updated_data["first_name"],
                updated_data["middle_name"],
                updated_data["last_name"],
                updated_data["degree_program"],
                updated_data["gender"],
                updated_data["batch"],
                CURRENT_USER_ID
            ))
            cnx.commit()
            messagebox.showinfo("Success", "Personal information updated successfully!")
            self.app.show_view_personal_info_page() # Go back to view page to see changes
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update personal info: {err}")
        # No finally block to disconnect_db, connection is persistent

class ViewRegisteredOrgsPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Organizations You Are Registered In")
        self.create_treeview()
        self.load_data()

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Org Name", "Academic Year", "Semester", "Role", "Status", "Committee"), show="headings")
        self.tree.heading("Org Name", text="Organization Name")
        self.tree.heading("Academic Year", text="Academic Year")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Committee", text="Committee")

        # Adjust column widths
        self.tree.column("Org Name", width=150, anchor=W)
        self.tree.column("Academic Year", width=100, anchor=CENTER)
        self.tree.column("Semester", width=80, anchor=CENTER)
        self.tree.column("Role", width=100, anchor=W)
        self.tree.column("Status", width=80, anchor=CENTER)
        self.tree.column("Committee", width=120, anchor=W)

        self.tree.grid(row=1, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) # Allow both columns to expand

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_data(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        # No need to call connect_db here
        try:
            query = """
            SELECT
                s.org_name,
                s.academic_year,
                s.semester,
                s.role,
                s.status,
                s.committee
            FROM serves s
            WHERE s.student_no = %s
            ORDER BY s.academic_year DESC,
                     CASE s.semester
                         WHEN 'First' THEN 2
                         WHEN 'Second' THEN 1
                         ELSE 0 -- Handle unexpected values gracefully
                     END DESC;
            """
            cursor.execute(query, (CURRENT_USER_ID,))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                self.tree.insert("", "end", values=("No organizations found.", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve organizations: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewMembersUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Your Unpaid Fees")
        self.create_treeview()
        self.generate_report() # Automatically generate report on page load

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Org Name", "Receipt No", "Amount", "Payment Deadline", "Date Paid", "Payment Status"), show="headings")
        self.tree.heading("Org Name", text="Organization Name")
        self.tree.heading("Receipt No", text="Receipt Number")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Payment Deadline", text="Payment Deadline")
        self.tree.heading("Date Paid", text="Date Paid")
        self.tree.heading("Payment Status", text="Status")

        self.tree.column("Org Name", width=150, anchor=W)
        self.tree.column("Receipt No", width=100, anchor=CENTER)
        self.tree.column("Amount", width=100, anchor=E)
        self.tree.column("Payment Deadline", width=120, anchor=CENTER)
        self.tree.column("Date Paid", width=100, anchor=CENTER)
        self.tree.column("Payment Status", width=100, anchor=CENTER)

        self.tree.grid(row=1, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 3)
            query = """
            SELECT f.org_name, f.receipt_no, f.amount, f.payment_deadline, f.date_paid, f.payment_status
            FROM fee f
            WHERE f.student_no = %s
                AND (f.payment_status = "Unpaid" OR f.date_paid IS NULL)
            ORDER BY f.payment_deadline DESC;
            """
            cursor.execute(query, (CURRENT_USER_ID,))
            records = cursor.fetchall()

            if records:
                for record in records:
                    # Format date_paid if it's None to 'N/A'
                    formatted_record = list(record)
                    if formatted_record[4] is None:
                        formatted_record[4] = "N/A"
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=("No unpaid fees found.", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve unpaid fees: {err}")
        # No finally block to disconnect_db, connection is persistent


# --- Organization Pages ---
class OrganizationMenuPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Organization Menu - {CURRENT_ORG_NAME}")
        self.create_org_menu_widgets()

    def create_org_menu_widgets(self):
        self.back_button.grid_forget() # Hide default back button

        row_idx = 1
        ttk.Button(self, text="Add New Member", command=self.app.show_add_member_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Edit Membership Status", command=self.app.show_edit_membership_status_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Executive Committee Members", command=self.app.show_view_exec_committee_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Presidents by Academic Year", command=self.app.show_view_presidents_by_ay_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View All Late Payments", command=self.app.show_view_late_payments_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Active vs Inactive Members Percentage", command=self.app.show_view_active_inactive_percentage_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View All Alumni Members", command=self.app.show_view_alumni_members_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Total Unpaid and Paid Fees", command=self.app.show_view_total_paid_unpaid_fees_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Members with Highest Debt", command=self.app.show_view_highest_debt_members_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View All Members by Attributes", command=self.app.show_view_all_members_by_attributes_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Members with Unpaid Fees (Org POV)", command=self.app.show_view_org_unpaid_fees_page).grid(row=row_idx, column=0, sticky=W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Logout", command=self.app.logout).grid(row=row_idx + 1, column=0, sticky=W, pady=20)


class AddNewMemberPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Add New Member to {CURRENT_ORG_NAME}")
        self.create_add_member_form()

    def create_add_member_form(self):
        labels = ["Student No:", "Academic Year:", "Semester:", "Role:", "Status:", "Committee:"]
        self.entries = {}

        for i, text in enumerate(labels):
            ttk.Label(self, text=text).grid(row=i + 1, column=0, sticky=W, padx=5, pady=2)

            if text == "Semester:":
                self.semester_options = ["First", "Second"] # REMOVED "Midyear"
                self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
                self.semester_combobox.grid(row=i + 1, column=1, sticky=(W, E), padx=5, pady=2)
                self.semester_combobox.set("First")
                self.entries['semester'] = self.semester_combobox
            else:
                entry = ttk.Entry(self)
                entry.grid(row=i + 1, column=1, sticky=(W, E), padx=5, pady=2)
                self.entries[text.replace(":", "").replace(" ", "_").lower()] = entry

        self.role_options = ["Member", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer"]
        self.status_options = ["Active", "Inactive", "Dismissed", "Alumni"]
        self.committee_options = ["Executive", "Finance", "Logistics", "Publicity", "Internal Affairs", "External Affairs"]

        self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
        self.role_combobox.grid(row=4, column=1, sticky=(W, E), padx=5, pady=2)
        self.role_combobox.set("Member")
        self.entries['role'] = self.role_combobox

        self.status_combobox = ttk.Combobox(self, values=self.status_options, state="readonly")
        self.status_combobox.grid(row=5, column=1, sticky=(W, E), padx=5, pady=2)
        self.status_combobox.set("Active")
        self.entries['status'] = self.status_combobox

        self.committee_combobox = ttk.Combobox(self, values=self.committee_options, state="readonly")
        self.committee_combobox.grid(row=6, column=1, sticky=(W, E), padx=5, pady=2)
        self.committee_combobox.set("Executive")
        self.entries['committee'] = self.committee_combobox


        ttk.Button(self, text="Add Member", command=self.add_member).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def add_member(self):
        student_no = self.entries['student_no'].get().strip()
        academic_year = self.entries['academic_year'].get().strip()
        semester = self.entries['semester'].get().strip()
        role = self.entries['role'].get().strip()
        status = self.entries['status'].get().strip()
        committee = self.entries['committee'].get().strip()
        membership_fee = 250.00

        if not all([student_no, academic_year, semester, role, status, committee]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        try:
            cursor.execute("SELECT student_no FROM member WHERE student_no = %s", (student_no,))
            member_exists = cursor.fetchone()
            if not member_exists:
                messagebox.showerror("Error", f"Student No. {student_no} does not exist in the system. Please register the member first.")
                return

            cursor.execute("""
                SELECT student_no FROM serves
                WHERE student_no = %s AND org_name = %s AND academic_year = %s AND semester = %s
            """, (student_no, CURRENT_ORG_NAME, academic_year, semester))
            if cursor.fetchone():
                messagebox.showerror("Error", f"Member {student_no} is already registered in {CURRENT_ORG_NAME} for {academic_year} {semester}.")
                return

            insert_serves_query = """
            INSERT INTO serves (student_no, org_name, academic_year, semester, role, status, committee)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_serves_query, (student_no, CURRENT_ORG_NAME, academic_year, semester, role, status, committee))

            receipt_no = f"FEE-{student_no}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            payment_deadline = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')

            insert_fee_query = """
            INSERT INTO fee (receipt_no, amount, payment_deadline, student_no, org_name)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_fee_query, (receipt_no, membership_fee, payment_deadline, student_no, CURRENT_ORG_NAME))

            update_org_members_query = """
            UPDATE organization
            SET no_of_members = no_of_members + 1
            WHERE org_name = %s
            """
            cursor.execute(update_org_members_query, (CURRENT_ORG_NAME,))

            cnx.commit()
            messagebox.showinfo("Success", f"Member {student_no} added to {CURRENT_ORG_NAME} successfully!")
            self.app.show_organization_menu()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add member: {err}")

# ... (Remaining classes and App definition)

class EditMembershipStatusPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Edit Member Status for {CURRENT_ORG_NAME}")
        self.create_form()

    def create_form(self):
        # Input fields for filtering/selecting member
        ttk.Label(self, text="Student No:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.student_no_entry = ttk.Entry(self)
        self.student_no_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Academic Year:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=3, column=1, sticky=(W, E), padx=5, pady=2)
        self.semester_combobox.set("First") # Default value

        ttk.Button(self, text="Load Member Info", command=self.load_member_info).grid(row=4, column=0, columnspan=2, pady=10)

        # Labels/Comboboxes for displaying and editing current status
        self.status_frame = ttk.LabelFrame(self, text="Current Status Details", padding="10")
        self.status_frame.grid(row=5, column=0, columnspan=2, sticky=(N, W, E, S), pady=10)

        ttk.Label(self.status_frame, text="Current Role:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.current_role_label = ttk.Label(self.status_frame, text="")
        self.current_role_label.grid(row=0, column=1, sticky=W, padx=5, pady=2)

        ttk.Label(self.status_frame, text="Current Status:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.current_status_label = ttk.Label(self.status_frame, text="")
        self.current_status_label.grid(row=1, column=1, sticky=W, padx=5, pady=2)

        ttk.Label(self.status_frame, text="Current Committee:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.current_committee_label = ttk.Label(self.status_frame, text="")
        self.current_committee_label.grid(row=2, column=1, sticky=W, padx=5, pady=2)

        # New values for update
        ttk.Label(self.status_frame, text="New Role:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.role_options = ["Member", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer"]
        self.new_role_combobox = ttk.Combobox(self.status_frame, values=self.role_options, state="readonly")
        self.new_role_combobox.grid(row=3, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self.status_frame, text="New Status:").grid(row=4, column=0, sticky=W, padx=5, pady=2)
        self.status_options = ["Active", "Inactive", "Dismissed", "Alumni"]
        self.new_status_combobox = ttk.Combobox(self.status_frame, values=self.status_options, state="readonly")
        self.new_status_combobox.grid(row=4, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self.status_frame, text="New Committee:").grid(row=5, column=0, sticky=W, padx=5, pady=2)
        self.committee_options = ["Executive", "Finance", "Logistics", "Publicity", "Internal Affairs", "External Affairs"]
        self.new_committee_combobox = ttk.Combobox(self.status_frame, values=self.committee_options, state="readonly")
        self.new_committee_combobox.grid(row=5, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self.status_frame, text="Update Status", command=self.update_status).grid(row=6, column=0, columnspan=2, pady=10)

        # Initially hide status frame until member info is loaded
        self.status_frame.grid_remove()

    def load_member_info(self):
        student_no = self.student_no_entry.get().strip()
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip() # Get from combobox

        if not all([student_no, academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Student No, Academic Year, and Semester.")
            return

        try:
            query = """
            SELECT role, status, committee FROM serves
            WHERE student_no = %s AND org_name = %s AND academic_year = %s AND semester = %s
            """
            cursor.execute(query, (student_no, CURRENT_ORG_NAME, academic_year, semester))
            member_status_info = cursor.fetchone()

            if member_status_info:
                self.current_role_label.config(text=member_status_info[0])
                self.current_status_label.config(text=member_status_info[1])
                self.current_committee_label.config(text=member_status_info[2])

                self.new_role_combobox.set(member_status_info[0])
                self.new_status_combobox.set(member_status_info[1])
                self.new_committee_combobox.set(member_status_info[2])

                self.status_frame.grid() # Show the frame
            else:
                messagebox.showinfo("Not Found", f"Member {student_no} not found in {CURRENT_ORG_NAME} for {academic_year} {semester}.")
                self.status_frame.grid_remove() # Hide if not found
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load member status: {err}")

    def update_status(self):
        student_no = self.student_no_entry.get().strip()
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip() # Get from combobox
        new_role = self.new_role_combobox.get().strip()
        new_status = self.new_status_combobox.get().strip()
        new_committee = self.new_committee_combobox.get().strip()

        if not all([student_no, academic_year, semester, new_role, new_status, new_committee]):
            messagebox.showerror("Input Error", "Please select new values for Role, Status, and Committee.")
            return

        try:
            update_query = """
            UPDATE serves
            SET role = %s, status = %s, committee = %s
            WHERE student_no = %s AND org_name = %s AND academic_year = %s AND semester = %s
            """
            cursor.execute(update_query, (new_role, new_status, new_committee, student_no, CURRENT_ORG_NAME, academic_year, semester))
            cnx.commit()
            messagebox.showinfo("Success", "Membership status updated successfully!")
            self.load_member_info() # Reload to show updated status
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update membership status: {err}")

class ViewExecutiveCommitteePage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Executive Committee Members of {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        # Filter inputs
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1)) # Default to current/next year

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

        # Treeview for displaying results
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Middle Name", "Last Name", "Role", "Status", "Committee"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Committee", text="Committee")

        self.tree.column("Student No", width=100, anchor=CENTER)
        self.tree.column("First Name", width=100, anchor=W)
        self.tree.column("Middle Name", width=100, anchor=W)
        self.tree.column("Last Name", width=100, anchor=W)
        self.tree.column("Role", width=100, anchor=W)
        self.tree.column("Status", width=80, anchor=CENTER)
        self.tree.column("Committee", width=100, anchor=W)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()

        if not academic_year:
            messagebox.showerror("Input Error", "Please enter an Academic Year.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                s.role,
                s.status,
                s.committee
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.committee = "Executive"
            ORDER BY m.last_name, m.first_name;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                self.tree.insert("", "end", values=("No executive committee members found for this year.", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve executive committee members: {err}")

class ViewPresidentsByAYPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Presidents of {CURRENT_ORG_NAME} by Academic Year")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Role:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.role_options = ["President", "Executive President"] # Add other president roles if applicable
        self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
        self.role_combobox.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.role_combobox.set("President") # Default

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Academic Year", "Semester", "Student No", "First Name", "Last Name"), show="headings")
        self.tree.heading("Academic Year", text="Academic Year")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")

        self.tree.column("Academic Year", width=100, anchor=CENTER)
        self.tree.column("Semester", width=80, anchor=CENTER)
        self.tree.column("Student No", width=100, anchor=CENTER)
        self.tree.column("First Name", width=120, anchor=W)
        self.tree.column("Last Name", width=120, anchor=W)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        selected_role = self.role_combobox.get().strip()

        if not selected_role:
            messagebox.showerror("Input Error", "Please select a Role.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            query = """
            SELECT
                s.academic_year,
                s.semester,
                m.student_no,
                m.first_name,
                m.last_name
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.role = %s
            ORDER BY s.academic_year DESC,
                     CASE s.semester
                         WHEN 'First' THEN 2
                         WHEN 'Second' THEN 1
                         ELSE 0 -- Fallback for unexpected values
                     END DESC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, selected_role))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                messagebox.showinfo("No Data", f"No {selected_role} found for {CURRENT_ORG_NAME}.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve presidents: {err}")

class ViewLatePaymentsPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Late Payments for {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1))

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Student No", "Name", "Receipt No", "Amount", "Deadline", "Date Paid", "Status"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Receipt No", text="Receipt No")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Deadline", text="Payment Deadline")
        self.tree.heading("Date Paid", text="Date Paid")
        self.tree.heading("Status", text="Status")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("Name", width=150, anchor=W)
        self.tree.column("Receipt No", width=80, anchor=CENTER)
        self.tree.column("Amount", width=80, anchor=E)
        self.tree.column("Deadline", width=100, anchor=CENTER)
        self.tree.column("Date Paid", width=100, anchor=CENTER)
        self.tree.column("Status", width=80, anchor=CENTER)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please select Academic Year and Semester.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            query = """
            SELECT
                m.student_no,
                CONCAT(m.first_name, ' ', m.last_name),
                f.receipt_no,
                f.amount,
                f.payment_deadline,
                f.date_paid,
                f.payment_status
            FROM fee f
            JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
            JOIN member m ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
                AND (f.payment_status = 'Late' OR f.date_paid > f.payment_deadline)
            ORDER BY f.date_paid DESC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[5] is None: formatted_record[5] = "N/A" # date_paid
                    self.tree.insert("", "end", values=formatted_record)
            else:
                messagebox.showinfo("No Data", "No late payments found for the specified semester and academic year.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve late payments: {err}")

class ViewActiveInactivePercentagePage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Active vs Inactive Members Percentage for {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1))

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

        # Treeview for displaying results
        self.tree = ttk.Treeview(self, columns=("Status", "Count", "Percentage"), show="headings")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Count", text="Number of Members")
        self.tree.heading("Percentage", text="Percentage (%)")

        self.tree.column("Status", width=100, anchor=W)
        self.tree.column("Count", width=120, anchor=CENTER)
        self.tree.column("Percentage", width=100, anchor=E)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)


    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please select Academic Year and Semester.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            # Query to get total members for the given org, academic year, and semester
            cursor.execute("""
                SELECT COUNT(student_no)
                FROM serves
                WHERE org_name = %s AND academic_year = %s AND semester = %s
            """, (CURRENT_ORG_NAME, academic_year, semester))
            total_members = cursor.fetchone()[0]

            if total_members == 0:
                messagebox.showinfo("No Data", "No members found for the specified semester and academic year.")
                return

            # Query to get counts by status
            query_status_counts = """
            SELECT
                s.status,
                COUNT(s.student_no)
            FROM serves s
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
            GROUP BY s.status;
            """
            cursor.execute(query_status_counts, (CURRENT_ORG_NAME, academic_year, semester))
            status_counts = cursor.fetchall()

            for status, count in status_counts:
                percentage = (count / total_members) * 100
                self.tree.insert("", "end", values=(status, count, f"{percentage:.2f}%"))

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve active/inactive percentage: {err}")

class ViewAlumniMembersPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Alumni Members of {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year (as of):").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, str(datetime.datetime.now().year)) # Default to current year

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Last Name", "Batch", "Last Active AY", "Last Active Semester", "Role", "Committee"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Batch", text="Batch")
        self.tree.heading("Last Active AY", text="Last Active AY")
        self.tree.heading("Last Active Semester", text="Last Active Semester")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Committee", text="Committee")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("First Name", width=120, anchor=W)
        self.tree.column("Last Name", width=120, anchor=W)
        self.tree.column("Batch", width=60, anchor=CENTER)
        self.tree.column("Last Active AY", width=100, anchor=CENTER)
        self.tree.column("Last Active Semester", width=100, anchor=CENTER)
        self.tree.column("Role", width=100, anchor=W)
        self.tree.column("Committee", width=100, anchor=W)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        # The concept of "alumni as of a given date" is better handled by checking a status field
        # rather than comparing academic years with a "date" directly.
        # Assuming "Alumni" status in `serves` table is definitive for alumni.
        # If 'academic_year' comparison is critical, it implies a last active year *before* a given year.
        # Let's adjust the query to reflect the 'Alumni' status directly, as it's more robust.

        # If you still want to filter by academic year less than a given year:
        # academic_year_filter = self.academic_year_entry.get().strip()
        # if not academic_year_filter.isdigit():
        #     messagebox.showerror("Input Error", "Academic Year (as of) must be a year (e.g., 2024).")
        #     return
        # year_int = int(academic_year_filter)

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            # Query for alumni: members with status 'Alumni' in the given organization
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.last_name,
                m.batch,
                s.academic_year, -- The year they were marked alumni or last active
                s.semester,    -- The semester they were marked alumni or last active
                s.role,
                s.committee
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.status = 'Alumni'
            ORDER BY m.last_name, m.first_name;
            """
            cursor.execute(query, (CURRENT_ORG_NAME,)) # No academic_year_filter for this version
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                messagebox.showinfo("No Data", f"No alumni members found for {CURRENT_ORG_NAME}.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve alumni members: {err}")

class ViewTotalPaidUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Total Paid/Unpaid Fees for {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="As of Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.as_of_date_entry = ttk.Entry(self)
        self.as_of_date_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.as_of_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d')) # Default to today

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

        self.unpaid_label = ttk.Label(self, text="Total Unpaid Amount: PHP 0.00", font=(None, 12, BOLD), foreground="red")
        self.unpaid_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.paid_label = ttk.Label(self, text="Total Paid Amount: PHP 0.00", font=(None, 12, BOLD), foreground="green")
        self.paid_label.grid(row=4, column=0, columnspan=2, pady=5)

    def generate_report(self):
        as_of_date_str = self.as_of_date_entry.get().strip()

        if not as_of_date_str:
            messagebox.showerror("Input Error", "Please enter a date.")
            return

        try:
            # Validate date format
            datetime.datetime.strptime(as_of_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        try:
            # SQL query from your provided list (number 9), corrected for payment_status type
            query = """
            SELECT
                COALESCE(SUM(CASE WHEN f.payment_status = 'Unpaid' OR f.date_paid IS NULL THEN f.amount ELSE 0 END), 0) AS unpaid_amount,
                COALESCE(SUM(CASE WHEN f.payment_status = 'Paid' AND f.date_paid IS NOT NULL THEN f.amount ELSE 0 END), 0) AS paid_amount
            FROM fee f
            WHERE f.org_name = %s AND f.payment_deadline <= %s;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, as_of_date_str))
            result = cursor.fetchone()

            if result:
                unpaid_amount = result[0]
                paid_amount = result[1]
                self.unpaid_label.config(text=f"Total Unpaid Amount: PHP {unpaid_amount:,.2f}")
                self.paid_label.config(text=f"Total Paid Amount: PHP {paid_amount:,.2f}")
            else:
                self.unpaid_label.config(text="Total Unpaid Amount: PHP 0.00")
                self.paid_label.config(text="Total Paid Amount: PHP 0.00")
                messagebox.showinfo("No Data", "No fee records found for the specified organization as of this date.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve fee summary: {err}")

class ViewHighestDebtMembersPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Members with Highest Debt in {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1))

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self, text="Member with Highest Debt: N/A", font=(None, 12, BOLD), foreground="blue")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please select Academic Year and Semester.")
            return

        try:
            # SQL query from your provided list (number 10), joining to get member name
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.last_name,
                SUM(f.amount) AS total_debt
            FROM FEE f
            JOIN SERVES s
                ON f.student_no = s.student_no AND f.org_name = s.org_name
            JOIN member m
                ON s.student_no = m.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
                AND (f.payment_status = "Unpaid" OR f.date_paid IS NULL)
            GROUP BY m.student_no, m.first_name, m.last_name
            ORDER BY total_debt DESC
            LIMIT 1;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            result = cursor.fetchone()

            if result:
                student_no, first_name, last_name, total_debt = result
                self.result_label.config(text=f"Member with Highest Debt: {first_name} {last_name} ({student_no}) - PHP {total_debt:,.2f}")
            else:
                self.result_label.config(text="No unpaid debts found for the specified period.")
                messagebox.showinfo("No Data", "No unpaid debts found for the specified semester and academic year.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve highest debt member: {err}")

class ViewAllMembersByAttributesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"All Members of {CURRENT_ORG_NAME} by Attributes")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        # Filter options
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Role:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.role_options = ["", "Member", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer"] # Added empty for "all"
        self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
        self.role_combobox.grid(row=3, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Status:").grid(row=4, column=0, sticky=W, padx=5, pady=2)
        self.status_options = ["", "Active", "Inactive", "Dismissed", "Alumni"] # Added empty for "all"
        self.status_combobox = ttk.Combobox(self, values=self.status_options, state="readonly")
        self.status_combobox.grid(row=4, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Gender:").grid(row=5, column=0, sticky=W, padx=5, pady=2)
        self.gender_options = ["", "Male", "Female", "Other"] # Added empty for "all"
        self.gender_combobox = ttk.Combobox(self, values=self.gender_options, state="readonly")
        self.gender_combobox.grid(row=5, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Degree Program:").grid(row=6, column=0, sticky=W, padx=5, pady=2)
        self.degree_program_entry = ttk.Entry(self)
        self.degree_program_entry.grid(row=6, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Batch:").grid(row=7, column=0, sticky=W, padx=5, pady=2)
        self.batch_entry = ttk.Entry(self)
        self.batch_entry.grid(row=7, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Committee:").grid(row=8, column=0, sticky=W, padx=5, pady=2)
        self.committee_options = ["", "Executive", "Finance", "Logistics", "Publicity", "Internal Affairs", "External Affairs"] # Added empty for "all"
        self.committee_combobox = ttk.Combobox(self, values=self.committee_options, state="readonly")
        self.committee_combobox.grid(row=8, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=9, column=0, columnspan=2, pady=10)

        # Treeview for displaying results
        self.tree = ttk.Treeview(self, columns=("Student No", "Name", "Degree", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Degree", text="Degree Program")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Batch", text="Batch")
        self.tree.heading("Academic Year", text="Academic Year")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Committee", text="Committee")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("Name", width=150, anchor=W)
        self.tree.column("Degree", width=120, anchor=W)
        self.tree.column("Gender", width=60, anchor=CENTER)
        self.tree.column("Batch", width=60, anchor=CENTER)
        self.tree.column("Academic Year", width=100, anchor=CENTER)
        self.tree.column("Semester", width=80, anchor=CENTER)
        self.tree.column("Role", width=100, anchor=W)
        self.tree.column("Status", width=80, anchor=CENTER)
        self.tree.column("Committee", width=100, anchor=W)

        self.tree.grid(row=10, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=10, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()
        role = self.role_combobox.get().strip()
        status = self.status_combobox.get().strip()
        gender = self.gender_combobox.get().strip()
        degree_program = self.degree_program_entry.get().strip()
        batch = self.batch_entry.get().strip()
        committee = self.committee_combobox.get().strip()

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            # Base query (from problem 1, with added joins to get member details)
            query = """
            SELECT
                m.student_no,
                CONCAT(m.first_name, ' ', m.last_name),
                m.degree_program,
                m.gender,
                m.batch,
                s.academic_year,
                s.semester,
                s.role,
                s.status,
                s.committee
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
            """
            params = [CURRENT_ORG_NAME]

            # Add filters dynamically
            if academic_year:
                query += " AND s.academic_year = %s"
                params.append(academic_year)
            if semester:
                query += " AND s.semester = %s"
                params.append(semester)
            if role:
                query += " AND s.role = %s"
                params.append(role)
            if status:
                query += " AND s.status = %s"
                params.append(status)
            if gender:
                query += " AND m.gender = %s"
                params.append(gender)
            if degree_program:
                query += " AND m.degree_program LIKE %s" # Use LIKE for partial match
                params.append(f"%{degree_program}%")
            if batch:
                try:
                    batch_int = int(batch)
                    query += " AND m.batch = %s"
                    params.append(batch_int)
                except ValueError:
                    messagebox.showerror("Input Error", "Batch must be an integer.")
                    return
            if committee:
                query += " AND s.committee = %s"
                params.append(committee)

            query += " ORDER BY m.last_name, m.first_name, s.academic_year DESC, CASE s.semester WHEN 'First' THEN 2 WHEN 'Second' THEN 1 ELSE 0 END DESC;"

            cursor.execute(query, tuple(params))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                messagebox.showinfo("No Data", "No members found matching the selected criteria.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve members: {err}")

class ViewOrgUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Unpaid Fees for {CURRENT_ORG_NAME} (Org POV)")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1))

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second"] # REMOVED "Midyear"
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Student No", "Name", "Receipt No", "Amount", "Payment Deadline"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Receipt No", text="Receipt No")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Payment Deadline", text="Payment Deadline")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("Name", width=150, anchor=W)
        self.tree.column("Receipt No", width=100, anchor=CENTER)
        self.tree.column("Amount", width=100, anchor=E)
        self.tree.column("Payment Deadline", width=120, anchor=CENTER)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please select Academic Year and Semester.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            # SQL query from your provided list (number 2)
            query = """
            SELECT DISTINCT
                m.student_no,
                CONCAT(m.first_name, ' ', m.middle_name, ' ', m.last_name) AS full_name,
                f.receipt_no,
                f.amount,
                f.payment_deadline
            FROM member m
            JOIN fee f
                ON m.student_no = f.student_no
            JOIN serves s
                ON m.student_no = s.student_no AND s.org_name = f.org_name
            WHERE f.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
                AND (f.payment_status = "Unpaid" OR f.date_paid IS NULL)
            ORDER BY m.last_name, m.first_name, f.payment_deadline DESC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                messagebox.showinfo("No Data", "No members with unpaid fees found for the specified semester and academic year.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve unpaid fees: {err}")


# --- Main Application Class ---
# ... (Previous code remains the same until the App class definition)

# --- Main Application Class ---
class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("Organization Management System")
        self.geometry("1200x800")

        self.current_page = None
        self.pages = {}

        if connect_db():
            self.show_auth_page()
        else:
            messagebox.showerror("Initialization Error", "Failed to connect to the database. Exiting.")
            self.destroy()

    def show_page(self, page_class_name, *args): # Renamed for clarity: page_class_name
        if self.current_page:
            self.current_page.destroy()

        # Get the class itself from the pages dictionary
        page_class = self.pages.get(page_class_name)

        if page_class:
            # All pages expect master and app_instance.
            # master is 'self' (the Tk root window)
            # app_instance is 'self' (the App instance itself)
            self.current_page = page_class(self, self, *args) # Pass self twice: once as master, once as app_instance
            self.current_page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page class '{page_class_name}' not found.")

    def show_auth_page(self):
        self.pages['AuthPage'] = AuthPage # Store the class, not an instance
        self.show_page('AuthPage') # Pass the string name of the class

    def show_member_menu(self):
        self.pages['MemberMenuPage'] = MemberMenuPage
        self.show_page('MemberMenuPage')

    def show_view_personal_info_page(self):
        self.pages['ViewPersonalInfoPage'] = ViewPersonalInfoPage
        self.show_page('ViewPersonalInfoPage')

    def show_edit_personal_info_page(self):
        self.pages['EditPersonalInfoPage'] = EditPersonalInfoPage
        self.show_page('EditPersonalInfoPage')

    def show_view_registered_orgs_page(self):
        self.pages['ViewRegisteredOrgsPage'] = ViewRegisteredOrgsPage
        self.show_page('ViewRegisteredOrgsPage')

    def show_view_members_unpaid_fees_page(self):
        self.pages['ViewMembersUnpaidFeesPage'] = ViewMembersUnpaidFeesPage
        self.show_page('ViewMembersUnpaidFeesPage')

    def show_organization_menu(self):
        self.pages['OrganizationMenuPage'] = OrganizationMenuPage
        self.show_page('OrganizationMenuPage')

    def show_add_member_page(self):
        self.pages['AddNewMemberPage'] = AddNewMemberPage
        self.show_page('AddNewMemberPage')

    def show_edit_membership_status_page(self):
        self.pages['EditMembershipStatusPage'] = EditMembershipStatusPage
        self.show_page('EditMembershipStatusPage')

    def show_view_exec_committee_page(self):
        self.pages['ViewExecutiveCommitteePage'] = ViewExecutiveCommitteePage
        self.show_page('ViewExecutiveCommitteePage')

    def show_view_presidents_by_ay_page(self):
        self.pages['ViewPresidentsByAYPage'] = ViewPresidentsByAYPage
        self.show_page('ViewPresidentsByAYPage')

    def show_view_late_payments_page(self):
        self.pages['ViewLatePaymentsPage'] = ViewLatePaymentsPage
        self.show_page('ViewLatePaymentsPage')

    def show_view_active_inactive_percentage_page(self):
        self.pages['ViewActiveInactivePercentagePage'] = ViewActiveInactivePercentagePage
        self.show_page('ViewActiveInactivePercentagePage')

    def show_view_alumni_members_page(self):
        self.pages['ViewAlumniMembersPage'] = ViewAlumniMembersPage
        self.show_page('ViewAlumniMembersPage')

    def show_view_total_paid_unpaid_fees_page(self):
        self.pages['ViewTotalPaidUnpaidFeesPage'] = ViewTotalPaidUnpaidFeesPage
        self.show_page('ViewTotalPaidUnpaidFeesPage')

    def show_view_highest_debt_members_page(self):
        self.pages['ViewHighestDebtMembersPage'] = ViewHighestDebtMembersPage
        self.show_page('ViewHighestDebtMembersPage')

    def show_view_all_members_by_attributes_page(self):
        self.pages['ViewAllMembersByAttributesPage'] = ViewAllMembersByAttributesPage
        self.show_page('ViewAllMembersByAttributesPage')

    def show_view_org_unpaid_fees_page(self):
        self.pages['ViewOrgUnpaidFeesPage'] = ViewOrgUnpaidFeesPage
        self.show_page('ViewOrgUnpaidFeesPage')

    def logout(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID, CURRENT_ORG_NAME
        CURRENT_USER_TYPE = None
        CURRENT_USER_ID = None
        CURRENT_ORG_NAME = None
        messagebox.showinfo("Logout", "You have been logged out.")
        self.show_auth_page()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            disconnect_db()
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    