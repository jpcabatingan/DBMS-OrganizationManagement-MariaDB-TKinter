import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter.font import BOLD

import mysql.connector
from mysql.connector import errorcode

import datetime

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
def connect_db():
    global cnx, cursor
    if cnx and cnx.is_connected():
        return True

    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor(buffered=True)
        print("Successfully connected to the database!")
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Error", "Access denied. Check your user name or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Database Error", f"Database '{DB_CONFIG['database']}' does not exist.")
        else:
            messagebox.showerror("Database Error", str(err))
        return False

def disconnect_db():
    global cnx, cursor
    if cnx and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("Disconnected from the database.")


# --- AuthPage Class (No changes from previous update, included for context) ---
class AuthPage(ttk.Frame):
    def __init__(self, master, app_instance):
        super().__init__(master, padding="0")
        self.app = app_instance
        self.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Member Panel (Left Side) ---
        member_panel = ttk.Frame(self, style='AuthPanel.TFrame', padding="30")
        member_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=0, pady=0)
        member_panel.grid_columnconfigure(0, weight=1)
        member_panel.grid_columnconfigure(1, weight=1)
        member_panel.grid_columnconfigure(2, weight=0)

        ttk.Label(member_panel, text="Member", font=("Arial", 24, BOLD), foreground='black').grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        ttk.Label(member_panel, text="Enter your credentials below or sign up for a new account.", font=("Arial", 10), foreground='grey').grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))

        ttk.Label(member_panel, text="Student no.", font=("Arial", 10, BOLD)).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        self.member_student_no_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.member_student_no_entry.grid(row=3, column=0, columnspan=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: 20XX-XXXXX", font=("Arial", 8), foreground='grey').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        ttk.Button(member_panel, text="Log-in", style='Login.TButton', command=self.member_login).grid(row=3, column=1, sticky=tk.E, padx=(5,0))

        ttk.Frame(member_panel, height=2, relief='sunken', style='Separator.TFrame').grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 20))

        ttk.Label(member_panel, text="Student no.", font=("Arial", 10, BOLD)).grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_student_no_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_student_no_entry.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(member_panel, text="Format: 20XX-XXXXX", font=("Arial", 8), foreground='grey').grid(row=8, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Degree Program", font=("Arial", 10, BOLD)).grid(row=6, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_degree_program_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_degree_program_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: BS Computer Science", font=("Arial", 8), foreground='grey').grid(row=8, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="First Name", font=("Arial", 10, BOLD)).grid(row=9, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_first_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_first_name_entry.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))

        ttk.Label(member_panel, text="Gender", font=("Arial", 10, BOLD)).grid(row=9, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_gender_combobox = ttk.Combobox(member_panel, values=["F", "M"], state="readonly", font=("Arial", 12)) # Changed to Combobox
        self.signup_gender_combobox.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.signup_gender_combobox.set("F") # Default value
        ttk.Label(member_panel, text="Format: F / M", font=("Arial", 8), foreground='grey').grid(row=11, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Middle Name", font=("Arial", 10, BOLD)).grid(row=12, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_middle_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_middle_name_entry.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(member_panel, text="Optional", font=("Arial", 8), foreground='grey').grid(row=14, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Batch", font=("Arial", 10, BOLD)).grid(row=12, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_batch_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_batch_entry.grid(row=13, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: 20XX", font=("Arial", 8), foreground='grey').grid(row=14, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Last Name", font=("Arial", 10, BOLD)).grid(row=15, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_last_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_last_name_entry.grid(row=16, column=0, columnspan=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Button(member_panel, text="Sign-up", style='Login.TButton', command=self.member_signup).grid(row=16, column=1, sticky=tk.E, padx=(5,0))

        # --- Organization Panel (Right Side) ---
        
        org_panel = ttk.Frame(self, style='AuthPanel.TFrame', padding="30")
        org_panel.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=0, pady=0)
        org_panel.grid_columnconfigure(0, weight=1)
        org_panel.grid_columnconfigure(1, weight=0)

        ttk.Label(org_panel, text="Organization", font=("Arial", 24, BOLD), foreground='black').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(org_panel, text="Enter your org ID below or register a new org.", font=("Arial", 10), foreground='grey').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        ttk.Label(org_panel, text="Organization ID", font=("Arial", 10, BOLD)).grid(row=2, column=0, columnspan=1, sticky=tk.W, pady=(10, 0))
        self.org_id_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.org_id_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(org_panel, text="Format: XXXXX", font=("Arial", 8), foreground='grey').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        ttk.Button(org_panel, text="Log-in", style='Login.TButton', command=self.org_login).grid(row=3, column=1, sticky=tk.E, padx=(5,0))

        ttk.Frame(org_panel, height=2, relief='sunken', style='Separator.TFrame').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 20))

        # Modified Section for Organization Sign-up
        ttk.Label(org_panel, text="Organization Name", font=("Arial", 10, BOLD)).grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_org_name_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.signup_org_name_entry.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))

        ttk.Label(org_panel, text="Organization ID", font=("Arial", 10, BOLD)).grid(row=8, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_org_id_entry = ttk.Entry(org_panel, font=("Arial", 12))
        self.signup_org_id_entry.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(org_panel, text="Format: XXXXX", font=("Arial", 8), foreground='grey').grid(row=10, column=0, sticky=tk.W, pady=(0, 20)) 

        ttk.Button(org_panel, text="Sign-up", style='Login.TButton', command=self.org_signup).grid(row=9, column=1, sticky=tk.E, padx=(5,0))

        org_panel.grid_columnconfigure(0, weight=1)
        org_panel.grid_columnconfigure(1, weight=0)

        # --- Styling ---
        style = ttk.Style(self)
        style.theme_use('clam')

        LIGHT_GREY = "#E0E0E0"
        DARK_GREY = "#616161"
        BLUE = "#446EE2"

        self.master.configure(bg=LIGHT_GREY)

        style.configure('TFrame', background=LIGHT_GREY)
        style.configure('AuthPanel.TFrame', background='white', borderwidth=0, relief='flat')
        style.configure('Separator.TFrame', background=DARK_GREY)
        style.configure('TLabel', background='white', foreground='black')
        style.configure('Login.TButton',
                        background=BLUE,
                        foreground='white',
                        font=("Arial", 10, BOLD),
                        borderwidth=0,
                        focuscolor=BLUE,
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
        gender = self.signup_gender_combobox.get().strip() # Get value from combobox
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
            self.signup_gender_combobox.set("F") # Reset to default
            self.signup_batch_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to sign up: {err}")

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

# BasePage Class ----------------------------------------------------------------------------------
class BasePage(ttk.Frame):
    def __init__(self, master, app_instance, title):
        super().__init__(master, padding="20")
        self.app = app_instance
        self.title = title
        self.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text=self.title, font=(None, 16, BOLD)).grid(row=0, column=0, columnspan=2, pady=10)
        self.back_button = ttk.Button(self, text="Back to Menu", command=self.go_back)
        self.back_button.grid(row=99, column=0, columnspan=2, pady=20)

    def go_back(self):
        if CURRENT_USER_TYPE == 'member':
            self.app.show_member_menu()
        elif CURRENT_USER_TYPE == 'organization':
            self.app.show_organization_menu()
        else:
            self.app.show_auth_page()

# Member POV | Pages Class ----------------------------------------------------------------------------------
class MemberMenuPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Member Menu")
        self.create_member_menu_widgets()

    def create_member_menu_widgets(self):
        self.back_button.grid_forget()

        row_idx = 1
        ttk.Button(self, text="View Personal Info", command=self.app.show_view_personal_info_page).grid(row=row_idx, column=0, sticky=tk.W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Edit Personal Info", command=self.app.show_edit_personal_info_page).grid(row=row_idx, column=0, sticky=tk.W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Registered Organizations", command=self.app.show_view_registered_orgs_page).grid(row=row_idx, column=0, sticky=tk.W, pady=5)
        row_idx += 1
        ttk.Button(self, text="View Unpaid Fees (All Organizations)", command=self.app.show_view_members_unpaid_fees_page).grid(row=row_idx, column=0, sticky=tk.W, pady=5)
        row_idx += 1
        ttk.Button(self, text="Logout", command=self.app.logout).grid(row=row_idx + 1, column=0, sticky=tk.W, pady=20)

# Member POV | Personal Info Page Class ----------------------------------------------------------------------------------
class ViewPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "View Personal Information")
        self.display_info()

    def display_info(self):
        for widget in self.winfo_children():
            if widget not in [self.back_button, self.children['!label']]:
                widget.destroy()

        try:
            cursor.execute("SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member WHERE student_no = %s", (CURRENT_USER_ID,))
            member_info = cursor.fetchone()

            if member_info:
                labels = ["Student No:", "First Name:", "Middle Name:", "Last Name:", "Degree Program:", "Gender:", "Batch:"]
                for i, label_text in enumerate(labels):
                    ttk.Label(self, text=label_text, font=(None, 10, BOLD)).grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=2)
                    ttk.Label(self, text=member_info[i]).grid(row=i + 1, column=1, sticky=tk.W, padx=5, pady=2)
            else:
                ttk.Label(self, text="Member information not found.", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve personal info: {err}")

# Member POV | Edit Personal Info Class ----------------------------------------------------------------------------------
class EditPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Edit Personal Information")
        self.create_edit_form()

    def create_edit_form(self):
        try:
            cursor.execute("SELECT student_no, first_name, middle_name, last_name, degree_program, gender, batch FROM member WHERE student_no = %s", (CURRENT_USER_ID,))
            member_info = cursor.fetchone()

            if member_info:
                self.entries = {}
                labels = ["Student No:", "First Name:", "Middle Name:", "Last Name:", "Degree Program:", "Gender:", "Batch:"]
                field_names = ["student_no", "first_name", "middle_name", "last_name", "degree_program", "gender", "batch"]

                for i, label_text in enumerate(labels):
                    ttk.Label(self, text=label_text).grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=2)
                    if label_text == "Gender:":
                        entry = ttk.Combobox(self, values=["F", "M"], state="readonly")
                        entry.set(member_info[i] if member_info[i] is not None else "F") 
                    else:
                        entry = ttk.Entry(self)
                        entry.insert(0, str(member_info[i]) if member_info[i] is not None else "")
                    entry.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                    self.entries[field_names[i]] = entry

                self.entries["student_no"].config(state='readonly')

                ttk.Button(self, text="Save Changes", command=self.save_changes).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)
            else:
                ttk.Label(self, text="Member information not found.", foreground="red").grid(row=1, column=0, columnspan=2, pady=10)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load personal info for editing: {err}")

    def save_changes(self):
        updated_data = {
            "first_name": self.entries["first_name"].get().strip(),
            "middle_name": self.entries["middle_name"].get().strip() or None,
            "last_name": self.entries["last_name"].get().strip(),
            "degree_program": self.entries["degree_program"].get().strip(),
            "gender": self.entries["gender"].get().strip(),
            "batch": self.entries["batch"].get().strip()
        }

        if not all([updated_data["first_name"], updated_data["last_name"], updated_data["degree_program"], updated_data["gender"], updated_data["batch"]]):
            messagebox.showerror("Input Error", "Please fill in all required fields (First Name, Last Name, Degree Program, Gender, Batch).")
            return
        try:
            updated_data["batch"] = int(updated_data["batch"])
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
            return

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
            self.app.show_view_personal_info_page()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update personal info: {err}")

# Member POV | Orgs Page Class ----------------------------------------------------------------------------------
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

        self.tree.column("Org Name", width=150, anchor=tk.W)
        self.tree.column("Academic Year", width=100, anchor=tk.CENTER)
        self.tree.column("Semester", width=80, anchor=tk.CENTER)
        self.tree.column("Role", width=100, anchor=tk.W)
        self.tree.column("Status", width=80, anchor=tk.CENTER)
        self.tree.column("Committee", width=120, anchor=tk.W)

        self.tree.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

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
                         ELSE 0
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

# Member POV | Upaid Fees Class ----------------------------------------------------------------------------------
class ViewMembersUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Your Unpaid Fees")
        self.create_treeview()
        self.generate_report()

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Org Name", "Receipt No", "Amount", "Payment Deadline", "Date Paid", "Payment Status"), show="headings")
        self.tree.heading("Org Name", text="Organization Name")
        self.tree.heading("Receipt No", text="Receipt Number")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Payment Deadline", text="Payment Deadline")
        self.tree.heading("Date Paid", text="Date Paid")
        self.tree.heading("Payment Status", text="Status")

        self.tree.column("Org Name", width=150, anchor=tk.W)
        self.tree.column("Receipt No", width=100, anchor=tk.CENTER)
        self.tree.column("Amount", width=100, anchor=tk.E)
        self.tree.column("Payment Deadline", width=120, anchor=tk.CENTER)
        self.tree.column("Date Paid", width=100, anchor=tk.CENTER)
        self.tree.column("Payment Status", width=100, anchor=tk.CENTER)

        self.tree.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
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
                    formatted_record = list(record)
                    if formatted_record[4] is None:
                        formatted_record[4] = "N/A"
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=("No unpaid fees found.", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve unpaid fees: {err}")


# Organization POV | Menu Page Class ----------------------------------------------------------------------------------
class OrganizationMenuPage(BasePage):
    def __init__(self, master, app_instance):
        # We'll create our own title/header, so don't pass title to BasePage
        super().__init__(master, app_instance, "")
        self.back_button.destroy() # Remove default back button

        self.create_org_menu_layout()
        self.apply_filters_and_generate_report() # Initial load of members on startup

    def create_org_menu_layout(self):
        # Remove default title label from BasePage
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("text") == "":
                widget.destroy()

        # Top Header Frame
        header_frame = ttk.Frame(self, style='AuthPanel.TFrame', padding="15")
        header_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=10, pady=10, columnspan=2)
        header_frame.grid_columnconfigure(0, weight=0) # Icon
        header_frame.grid_columnconfigure(1, weight=1) # Welcome text
        header_frame.grid_columnconfigure(2, weight=0) # Logout button

        # Placeholder for organization icon (e.g., from an image file if available)
        ttk.Label(header_frame, text="🏛️", font=("Arial", 30)).grid(row=0, column=0, rowspan=2, padx=10) # Using an emoji
        ttk.Label(header_frame, text="Welcome, " + CURRENT_ORG_NAME, font=("Arial", 20, BOLD)).grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        ttk.Label(header_frame, text=f"Organization ID: {CURRENT_USER_ID}").grid(row=1, column=1, sticky=tk.W)

        # Active Members Count
        academic_year, semester = self.get_current_academic_period()
        if academic_year and semester: # Check if academic period was valid
            active_members_count = self.get_active_members_count_for_current_semester(academic_year, semester)
            ttk.Label(header_frame, text=f"Active members this semester ({academic_year} {semester}): {active_members_count}").grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        else:
            ttk.Label(header_frame, text="Active members count: N/A (Invalid Academic Period)").grid(row=2, column=1, sticky=tk.W, pady=(0, 5))


        ttk.Button(header_frame, text="Log Out", command=self.app.logout).grid(row=0, column=2, sticky=tk.NE, padx=10, pady=5)


        # Create a Notebook (tabs) for Member Management and Fees Management
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10, columnspan=2)
        self.grid_rowconfigure(1, weight=1) # Row for notebook
        self.grid_columnconfigure(0, weight=1) # Column for notebook
        self.grid_columnconfigure(1, weight=0) # Column for logout (already handled by header frame)


        # Member Management Tab
        self.member_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.member_tab, text="Manage Members")
        self.member_tab.grid_rowconfigure(1, weight=1) # Row for treeview
        self.member_tab.grid_columnconfigure(0, weight=0) # Column for filters/buttons (fixed width)
        self.member_tab.grid_columnconfigure(1, weight=1) # Column for treeview (expands)

        self.create_member_tab_widgets()

        # Fees Management Tab (Placeholder)
        self.fees_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.fees_tab, text="Manage Finances")
        # For demonstration, adding a button to show late payments here
        ttk.Label(self.fees_tab, text="Fees Management features:").grid(row=0, column=0, sticky=tk.W, pady=(0,5))
        ttk.Button(self.fees_tab, text="View Late Payments", command=self.app.show_view_late_payments_page, style='Login.TButton').grid(row=1, column=0, sticky=tk.W, pady=5)

    def get_current_academic_period(self):
        """Determines the current academic year and semester based on the redefined ranges."""
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month

        if 8 <= current_month <= 12: # August to December
            academic_year = f"{current_year}-{current_year + 1}"
            semester = "First"
        elif 1 <= current_month <= 5: # January to May
            academic_year = f"{current_year - 1}-{current_year}"
            semester = "Second"
        else: # June/July or other months
            messagebox.showerror("Invalid Academic Period", "Only First Semester (August-December) and Second Semester (January-May) are allowed. The current month does not fall into a recognized academic period.")
            return None, None # Return None for academic_year and semester if invalid

        return academic_year, semester

    def get_active_members_count_for_current_semester(self, academic_year, semester):
        try:
            query = """
                SELECT COUNT(DISTINCT student_no)
                FROM serves
                WHERE org_name = %s
                    AND academic_year = %s
                    AND semester = %s
                    AND status = 'Active';
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            count = cursor.fetchone()[0]
            return count
        except mysql.connector.Error as err:
            print(f"Error fetching active members count: {err}")
            return "N/A"

    def create_member_tab_widgets(self):
        # --- Left Panel: Filters & Action Buttons ---
        left_panel = ttk.Frame(self.member_tab)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=10, pady=10)
        left_panel.grid_columnconfigure(1, weight=1) # Makes entries/comboboxes expand

        # Filter Section
        filter_frame = ttk.LabelFrame(left_panel, text="Filters", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        filter_row = 0
        self.filter_vars = {} # Dictionary to hold StringVar for filters

        current_ay, current_sem = self.get_current_academic_period()
        default_ay_filter = current_ay if current_ay else ""
        default_sem_filter = current_sem if current_sem else "All"


        ttk.Label(filter_frame, text="Academic Year:").grid(row=filter_row, column=0, sticky=tk.W, pady=2)
        self.filter_vars['academic_year'] = tk.StringVar(value=default_ay_filter) # Default to current AY
        ttk.Entry(filter_frame, textvariable=self.filter_vars['academic_year']).grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
        filter_row += 1

        ttk.Label(filter_frame, text="Semester:").grid(row=filter_row, column=0, sticky=tk.W, pady=2)
        self.filter_vars['semester'] = tk.StringVar(value=default_sem_filter) # Default to All for filters
        ttk.Combobox(filter_frame, textvariable=self.filter_vars['semester'], values=["All", "First", "Second"], state="readonly").grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
        filter_row += 1

        labels_and_options = {
            "Role:": ["All", "Member", "President", "Vice President", "EAC Chairperson", "Secretary", "Finance Chairperson", "SCC Chairperson", "MC Chairperson"],
            "Status:": ["All", "Active", "Inactive", "Disaffiliated", "Alumni"],
            "Gender:": ["All", "F", "M"],
            "Degree Program:": [], # Entry, not combobox
            "Batch:": [], # Entry, not combobox
            "Committee:": ["All", "Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership"]
        }

        for label_text, options in labels_and_options.items():
            ttk.Label(filter_frame, text=label_text).grid(row=filter_row, column=0, sticky=tk.W, pady=2)
            key = label_text.replace(":", "").replace(" ", "_").lower()
            if options: # It's a combobox
                var = tk.StringVar(value=options[0]) # Default to 'All' or first option
                combobox = ttk.Combobox(filter_frame, textvariable=var, values=options, state="readonly")
                combobox.grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
                self.filter_vars[key] = var
            else: # It's an entry
                var = tk.StringVar()
                entry = ttk.Entry(filter_frame, textvariable=var)
                entry.grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
                self.filter_vars[key] = var
            filter_row += 1

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters_and_generate_report, style='Login.TButton').grid(row=filter_row, column=0, columnspan=2, pady=10)


        # Update Members Section
        update_members_frame = ttk.LabelFrame(left_panel, text="Update members", padding="10")
        update_members_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(10, 10))
        update_members_frame.grid_columnconfigure(0, weight=1) # Make buttons expand

        ttk.Button(update_members_frame, text="Add new member", command=self.app.show_add_member_page, style='Login.TButton').grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(update_members_frame, text="Edit member details", command=self.app.show_edit_membership_status_page, style='Login.TButton').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)


        # Active Members Percentage Section
        active_percentage_frame = ttk.LabelFrame(left_panel, text="Active Members Percentage", padding="10")
        active_percentage_frame.grid(row=2, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(10, 0))
        active_percentage_frame.grid_columnconfigure(0, weight=1)
        active_percentage_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(active_percentage_frame, text="Last 'n' Semesters:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.n_semesters_entry = ttk.Entry(active_percentage_frame)
        self.n_semesters_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.n_semesters_entry.insert(0, "1") # Default to last 1 semester

        ttk.Button(active_percentage_frame, text="View Percentage", command=self.view_active_members_percentage, style='Login.TButton').grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.percentage_result_label = ttk.Label(active_percentage_frame, text="", wraplength=200)
        self.percentage_result_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)


        # --- Right Panel: Table of Members ---
        # Frame to contain Treeview and Scrollbars
        tree_frame = ttk.Frame(self.member_tab)
        tree_frame.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10, rowspan=2)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.member_list_tree = ttk.Treeview(tree_frame, show="headings")
        self.member_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # Vertical Scrollbar
        member_list_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.member_list_tree.yview)
        member_list_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.member_list_tree.configure(yscrollcommand=member_list_scrollbar_y.set)

        # Horizontal Scrollbar
        member_list_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.member_list_tree.xview)
        member_list_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.member_list_tree.configure(xscrollcommand=member_list_scrollbar_x.set)

        self.set_default_treeview_columns()

    def set_default_treeview_columns(self):
        columns = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
        headings = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
        widths = (100, 180, 150, 70, 70, 100, 80, 100, 80, 120)
        anchors = (tk.CENTER, tk.W, tk.W, tk.CENTER, tk.CENTER, tk.CENTER, tk.CENTER, tk.W, tk.CENTER, tk.W)
        self.set_treeview_columns(self.member_list_tree, columns, headings, widths, anchors)

    def clear_treeview(self, tree):
        for i in tree.get_children():
            tree.delete(i)

    def set_treeview_columns(self, tree, columns, headings, widths, anchors):
        tree["columns"] = columns
        tree["displaycolumns"] = columns
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
        for col, width, anchor in zip(columns, widths, anchors):
            tree.column(col, width=width, anchor=anchor)

    def apply_filters_and_generate_report(self):
        # This function generates the main "All Members" report based on current filters
        self.clear_treeview(self.member_list_tree)
        self.set_default_treeview_columns() # Reset columns for the full member list view

        try:
            query = """
            SELECT
                m.student_no,
                CONCAT(m.first_name, ' ', IFNULL(m.middle_name, ''), ' ', m.last_name) AS full_name,
                m.degree_program,
                m.gender,
                m.batch,
                s.academic_year,
                s.semester,
                s.role,
                s.status,
                s.committee
            FROM member m
            JOIN serves s ON m.student_no = s.student_no
            WHERE s.org_name = %s
            """
            params = [CURRENT_ORG_NAME]

            # Dynamically add filters
            if self.filter_vars['academic_year'].get():
                query += " AND s.academic_year = %s"
                params.append(self.filter_vars['academic_year'].get())
            if self.filter_vars['semester'].get() != "All":
                query += " AND s.semester = %s"
                params.append(self.filter_vars['semester'].get())
            if self.filter_vars['role'].get() != "All":
                query += " AND s.role = %s"
                params.append(self.filter_vars['role'].get())
            if self.filter_vars['status'].get() != "All":
                query += " AND s.status = %s"
                params.append(self.filter_vars['status'].get())
            if self.filter_vars['gender'].get() != "All":
                query += " AND m.gender = %s"
                params.append(self.filter_vars['gender'].get())
            if self.filter_vars['degree_program'].get():
                query += " AND m.degree_program LIKE %s"
                params.append(f"%{self.filter_vars['degree_program'].get()}%")
            if self.filter_vars['batch'].get():
                query += " AND m.batch = %s"
                params.append(int(self.filter_vars['batch'].get()))
            if self.filter_vars['committee'].get() != "All":
                query += " AND s.committee = %s"
                params.append(self.filter_vars['committee'].get())

            query += " ORDER BY m.last_name, m.first_name, s.academic_year DESC, s.semester DESC;"

            cursor.execute(query, tuple(params))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.member_list_tree.insert("", "end", values=record)
            else:
                columns = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
                self.member_list_tree.insert("", "end", values=("No members found matching criteria.",) + ("",) * (len(columns) - 1))
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve members: {err}")

    def generate_active_members_only_report(self):
        self.clear_treeview(self.member_list_tree)
        self.set_default_treeview_columns() # Use default columns for consistency

        try:
            # Determine current academic year and semester using the refined logic
            academic_year, semester = self.get_current_academic_period()
            if not academic_year or not semester: # If get_current_academic_period showed an error
                return

            query = """
            SELECT
                m.student_no,
                CONCAT(m.first_name, ' ', IFNULL(m.middle_name, ''), ' ', m.last_name) AS full_name,
                m.degree_program,
                m.gender,
                m.batch,
                s.academic_year,
                s.semester,
                s.role,
                s.status,
                s.committee
            FROM member m
            JOIN serves s ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
                AND s.status = 'Active'
            ORDER BY m.last_name, m.first_name;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.member_list_tree.insert("", "end", values=record)
            else:
                columns = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
                self.member_list_tree.insert("", "end", values=(f"No active members for {academic_year} {semester}.",) + ("",) * (len(columns) - 1))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve active members: {err}")

    def view_active_members_percentage(self):
        self.percentage_result_label.config(text="") # Clear previous results

        n_semesters_str = self.n_semesters_entry.get().strip()
        if not n_semesters_str:
            messagebox.showerror("Input Error", "Please enter the number of semesters (n).")
            return
        try:
            n = int(n_semesters_str)
            if n <= 0:
                raise ValueError("n must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for 'n': {e}")
            return

        try:
            # Get the current academic period
            current_ay, current_sem = self.get_current_academic_period()
            if not current_ay or not current_sem:
                return # Error message already shown by get_current_academic_period

            semesters_to_consider = []
            
            # Determine the `n` most recent semesters.
            # This logic needs to correctly handle academic year transitions and semester order.
            # Assuming 'First' comes before 'Second' in a given academic year for ordering purposes.
            # This is a simplified approach; a more robust solution might pre-calculate
            # all possible academic periods or use a dedicated date table if available.
            
            # Get all distinct academic periods for the current organization
            cursor.execute("""
                SELECT DISTINCT academic_year, semester
                FROM serves
                WHERE org_name = %s
                ORDER BY academic_year DESC,
                         CASE semester WHEN 'First' THEN 1 ELSE 2 END DESC;
            """, (CURRENT_ORG_NAME,))
            all_org_semesters = cursor.fetchall()

            # Find the index of the current semester in the sorted list of all semesters
            current_sem_tuple = (current_ay, current_sem)
            
            try:
                # Need to iterate and convert for comparison, as current_sem_tuple might not be directly in all_org_semesters
                # This handles cases where the current academic period might not yet have members registered.
                found_current = False
                for i, (ay, sem) in enumerate(all_org_semesters):
                    if ay == current_ay and sem == current_sem:
                        semesters_to_consider = all_org_semesters[i : i + n]
                        found_current = True
                        break
                
                if not found_current: # If current_sem is not in the list, we might need to construct the periods manually
                    # This is a fallback if the current period isn't in the DB, but we still need 'n' recent.
                    # This part can be complex depending on how 'recent' is strictly defined.
                    # For simplicity, if current isn't in DB, we'll just take the 'n' most recent *from the DB*.
                    semesters_to_consider = all_org_semesters[:n]
                    if not semesters_to_consider: # If no semesters at all for the org
                         messagebox.showinfo("No Data", f"No academic records found for {CURRENT_ORG_NAME} to calculate percentage.")
                         return
                    if len(semesters_to_consider) < n:
                        messagebox.showwarning("Limited Data", f"Only {len(semesters_to_consider)} semesters available for {CURRENT_ORG_NAME}.")

            except IndexError:
                # This could happen if n is very large and goes beyond available historical data
                semesters_to_consider = all_org_semesters 
                if not semesters_to_consider:
                    messagebox.showinfo("No Data", f"No academic records found for {CURRENT_ORG_NAME} to calculate percentage.")
                    return
                messagebox.showwarning("Limited Data", f"Only {len(semesters_to_consider)} semesters available for {CURRENT_ORG_NAME}. Showing data for all available semesters.")


            if not semesters_to_consider:
                self.percentage_result_label.config(text="No relevant semesters found.")
                return

            total_active = 0
            total_inactive = 0
            details_text = f"Active vs Inactive Members for {CURRENT_ORG_NAME} (last {n} semesters):\n"
            
            for ay, sem in semesters_to_consider:
                # Query for active members in the current semester
                query_active = """
                    SELECT COUNT(DISTINCT student_no)
                    FROM serves
                    WHERE org_name = %s AND academic_year = %s AND semester = %s AND status = 'Active';
                """
                cursor.execute(query_active, (CURRENT_ORG_NAME, ay, sem))
                active_count = cursor.fetchone()[0]

                # Query for inactive members (all non-active statuses) in the current semester
                query_inactive = """
                    SELECT COUNT(DISTINCT student_no)
                    FROM serves
                    WHERE org_name = %s AND academic_year = %s AND semester = %s AND status != 'Active';
                """
                cursor.execute(query_inactive, (CURRENT_ORG_NAME, ay, sem))
                inactive_count = cursor.fetchone()[0]

                total_active += active_count
                total_inactive += inactive_count
                details_text += f"- {ay} {sem}: Active: {active_count}, Inactive: {inactive_count}\n"

            overall_total = total_active + total_inactive
            if overall_total > 0:
                active_percentage = (total_active / overall_total) * 100
                inactive_percentage = (total_inactive / overall_total) * 100
                result_text = (f"Overall (last {n} semesters):\n"
                               f"Active: {total_active} ({active_percentage:.2f}%)\n"
                               f"Inactive: {total_inactive} ({inactive_percentage:.2f}%)\n\n"
                               + details_text)
            else:
                result_text = "No member data found for the specified semesters."

            self.percentage_result_label.config(text=result_text)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to calculate percentages: {err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

class AddNewMemberPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Add New Member to {CURRENT_ORG_NAME}")
        self.create_add_member_form()

    def create_add_member_form(self):
        labels = ["Student No:", "Academic Year:", "Semester:", "Role:", "Status:", "Committee:"]
        self.entries = {}

        for i, text in enumerate(labels):
            ttk.Label(self, text=text).grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=2)

            if text == "Semester:":
                self.semester_options = ["First", "Second"]
                self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
                self.semester_combobox.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.semester_combobox.set("First")
                self.entries['semester'] = self.semester_combobox
            elif text == "Role:": 
                self.role_options = ["Member", "President", "Vice President", "EAC Chairperson", "Secretary", "Finance Chairperson", "SCC Chairperson", "MC Chairperson"]
                self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
                self.role_combobox.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.role_combobox.set("Member")
                self.entries['role'] = self.role_combobox
            elif text == "Status:": 
                self.status_options = ["Active", "Inactive", "Disaffiliated", "Alumni"]
                self.status_combobox = ttk.Combobox(self, values=self.status_options, state="readonly")
                self.status_combobox.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.status_combobox.set("Active")
                self.entries['status'] = self.status_combobox
            elif text == "Committee:": 
                self.committee_options = ["Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership"]
                self.committee_combobox = ttk.Combobox(self, values=self.committee_options, state="readonly")
                self.committee_combobox.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.committee_combobox.set("Executive")
                self.entries['committee'] = self.committee_combobox
            else:
                entry = ttk.Entry(self)
                entry.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
                self.entries[text.replace(":", "").replace(" ", "_").lower()] = entry

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


class EditMembershipStatusPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Edit Member Status for {CURRENT_ORG_NAME}")
        self.create_form()

    def create_form(self):
        ttk.Label(self, text="Student No:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.student_no_entry = ttk.Entry(self)
        self.student_no_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        ttk.Label(self, text="Academic Year:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.semester_options = ["First", "Second"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Load Member Info", command=self.load_member_info).grid(row=4, column=0, columnspan=2, pady=10)

        self.status_frame = ttk.LabelFrame(self, text="Current Status Details", padding="10")
        self.status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.N, tk.W, tk.E, tk.S), pady=10)

        ttk.Label(self.status_frame, text="Current Role:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_role_label = ttk.Label(self.status_frame, text="")
        self.current_role_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.status_frame, text="Current Status:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_status_label = ttk.Label(self.status_frame, text="")
        self.current_status_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.status_frame, text="Current Committee:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_committee_label = ttk.Label(self.status_frame, text="")
        self.current_committee_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.status_frame, text="New Role:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.role_options = ["Member", "President", "Vice President", "EAC Chairperson", "Secretary", "Finance Chairperson", "SCC Chairperson", "MC Chairperson"]
        self.new_role_combobox = ttk.Combobox(self.status_frame, values=self.role_options, state="readonly")
        self.new_role_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        ttk.Label(self.status_frame, text="New Status:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.status_options = ["Active", "Inactive", "Disaffiliated", "Alumni"]
        self.new_status_combobox = ttk.Combobox(self.status_frame, values=self.status_options, state="readonly")
        self.new_status_combobox.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        ttk.Label(self.status_frame, text="New Committee:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.committee_options = ["Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership"]
        self.new_committee_combobox = ttk.Combobox(self.status_frame, values=self.committee_options, state="readonly")
        self.new_committee_combobox.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        ttk.Button(self.status_frame, text="Update Status", command=self.update_status).grid(row=6, column=0, columnspan=2, pady=10)

        self.status_frame.grid_remove()

    def load_member_info(self):
        student_no = self.student_no_entry.get().strip()
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

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

                self.status_frame.grid()
            else:
                messagebox.showinfo("Not Found", f"Member {student_no} not found in {CURRENT_ORG_NAME} for {academic_year} {semester}.")
                self.status_frame.grid_remove()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load member status: {err}")

    def update_status(self):
        student_no = self.student_no_entry.get().strip()
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()
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
            self.load_member_info()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update membership status: {err}")


# --- Placeholder for other Organization POV pages (now mostly integrated or removed) ---
# ViewLatePaymentsPage (kept separate as it's fees-related)
class ViewLatePaymentsPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Late Payments for {CURRENT_ORG_NAME}")
        self.create_widgets_with_filters()

    def create_widgets_with_filters(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().strftime('%Y') + "-" + str(datetime.datetime.now().year + 1))

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.semester_options = ["First", "Second"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.semester_combobox.set("First")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self, columns=("Student No", "Name", "Receipt No", "Amount", "Deadline", "Date Paid", "Status"), show="headings")
        self.tree.heading("Student No", text="Student No")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Receipt No", text="Receipt Number")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Deadline", text="Payment Deadline")
        self.tree.heading("Date Paid", text="Date Paid")
        self.tree.heading("Status", text="Status")

        self.tree.column("Student No", width=100, anchor=tk.CENTER)
        self.tree.column("Name", width=150, anchor=tk.W)
        self.tree.column("Receipt No", width=100, anchor=tk.CENTER)
        self.tree.column("Amount", width=100, anchor=tk.E)
        self.tree.column("Deadline", width=120, anchor=tk.CENTER)
        self.tree.column("Date Paid", width=100, anchor=tk.CENTER)
        self.tree.column("Status", width=100, anchor=tk.CENTER)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Academic Year and Semester.")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            query = """
            SELECT
                f.student_no,
                CONCAT(m.first_name, ' ', IFNULL(m.middle_name, ''), ' ', m.last_name) AS full_name,
                f.receipt_no,
                f.amount,
                f.payment_deadline,
                f.date_paid,
                f.payment_status
            FROM fee f
            JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
            JOIN member m ON f.student_no = m.student_no
            WHERE (f.payment_status = "Late" OR f.date_paid > f.payment_deadline)
                AND s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
            ORDER BY f.date_paid DESC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[5] is None: # date_paid column
                        formatted_record[5] = "N/A"
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=("No late payments found for this period.", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve late payments: {err}")


# --- App Class (Updated to reflect the new structure) ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organization Management System")
        self.geometry("1200x900") # Adjusted size for more content

        self.current_page = None
        self.pages = {}

        if connect_db():
            self.show_auth_page()
        else:
            messagebox.showerror("Initialization Error", "Failed to connect to the database. Exiting.")
            self.destroy()

    def show_page(self, page_class_name, *args):
        if self.current_page:
            self.current_page.destroy()

        page_class = self.pages.get(page_class_name)

        if page_class:
            self.current_page = page_class(self, self, *args)
            self.current_page.tkraise()
        else:
            messagebox.showerror("Navigation Error", f"Page class '{page_class_name}' not found.")

    def show_auth_page(self):
        self.pages['AuthPage'] = AuthPage
        self.show_page('AuthPage')

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
        # OrganizationMenuPage now contains the tabs directly
        self.pages['OrganizationMenuPage'] = OrganizationMenuPage
        self.show_page('OrganizationMenuPage')

    # Removed show_organization_member_management_page as it's now integrated
    # def show_organization_member_management_page(self):
    #     self.pages['OrganizationMemberManagementPage'] = OrganizationMemberManagementPage
    #     self.show_page('OrganizationMemberManagementPage')

    # The fees management tab is still a placeholder
    def show_add_member_page(self):
        self.pages['AddNewMemberPage'] = AddNewMemberPage
        self.show_page('AddNewMemberPage')

    def show_edit_membership_status_page(self):
        self.pages['EditMembershipStatusPage'] = EditMembershipStatusPage
        self.show_page('EditMembershipStatusPage')

    def show_view_late_payments_page(self):
        self.pages['ViewLatePaymentsPage'] = ViewLatePaymentsPage
        self.show_page('ViewLatePaymentsPage')

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