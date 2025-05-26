import mysql.connector
from mysql.connector import errorcode
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.font import BOLD
import datetime
from passlib.hash import pbkdf2_sha256 # For password hashing

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


# --- Authentication Functions (simplified for this example, focusing on GUI) ---
class AuthPage(ttk.Frame):
    def __init__(self, master, app_instance):
        super().__init__(master, padding="20")
        self.app = app_instance
        self.grid(row=0, column=0, sticky=(N, W, E, S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Authentication", font=(None, 16, BOLD)).grid(row=0, column=0, columnspan=2, pady=10)

        # Member Login/Signup
        ttk.Label(self, text="--- Member ---", font=(None, 12)).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Label(self, text="Student No:").grid(row=2, column=0, sticky=W, pady=2)
        self.member_student_no_entry = ttk.Entry(self)
        self.member_student_no_entry.grid(row=2, column=1, sticky=(W, E), pady=2)
        ttk.Button(self, text="Member Login", command=self.member_login).grid(row=3, column=0, sticky=W, pady=5)
        ttk.Button(self, text="Member Sign Up", command=self.member_signup_prompt).grid(row=3, column=1, sticky=E, pady=5)

        # Organization Login/Signup
        ttk.Label(self, text="--- Organization ---", font=(None, 12)).grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Label(self, text="Org ID:").grid(row=5, column=0, sticky=W, pady=2)
        self.org_id_entry = ttk.Entry(self)
        self.org_id_entry.grid(row=5, column=1, sticky=(W, E), pady=2)
        ttk.Label(self, text="Org Name:").grid(row=6, column=0, sticky=W, pady=2)
        self.org_name_entry = ttk.Entry(self)
        self.org_name_entry.grid(row=6, column=1, sticky=(W, E), pady=2) # Used for signup, and for login to differentiate
        ttk.Button(self, text="Organization Login", command=self.org_login).grid(row=7, column=0, sticky=W, pady=5)
        ttk.Button(self, text="Organization Sign Up", command=self.org_signup_prompt).grid(row=7, column=1, sticky=E, pady=5)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.grid_columnconfigure(1, weight=1)


    def member_login(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID
        student_no = self.member_student_no_entry.get().strip()
        if not student_no:
            messagebox.showerror("Login Error", "Please enter a Student Number.")
            return

        # No need to call connect_db here, it's already connected at app start
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
        # No finally block to disconnect_db, connection is persistent

    def member_signup_prompt(self):
        signup_window = Toplevel(self.master)
        signup_window.title("Member Sign Up")
        signup_window.geometry("400x300")

        labels = ["Student No:", "First Name:", "Middle Name:", "Last Name:", "Degree Program:", "Gender:", "Batch:"]
        entries = {}

        for i, text in enumerate(labels):
            ttk.Label(signup_window, text=text).grid(row=i, column=0, sticky=W, padx=5, pady=2)
            entry = ttk.Entry(signup_window)
            entry.grid(row=i, column=1, sticky=(W, E), padx=5, pady=2)
            entries[text.replace(":", "").replace(" ", "_").lower()] = entry

        def perform_signup():
            student_no = entries['student_no'].get().strip()
            first_name = entries['first_name'].get().strip()
            middle_name = entries['middle_name'].get().strip()
            last_name = entries['last_name'].get().strip()
            degree_program = entries['degree_program'].get().strip()
            gender = entries['gender'].get().strip()
            batch = entries['batch'].get().strip()

            if not all([student_no, first_name, last_name, degree_program, gender, batch]):
                messagebox.showerror("Input Error", "Please fill in all required fields (Student No, First Name, Last Name, Degree Program, Gender, Batch).")
                return

            # No need to call connect_db here, it's already connected at app start
            try:
                # Check if student_no already exists
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
                signup_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Batch must be an integer.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to sign up: {err}")
            # No finally block to disconnect_db, connection is persistent

        ttk.Button(signup_window, text="Sign Up", command=perform_signup).grid(row=len(labels), column=0, columnspan=2, pady=10)


    def org_login(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID, CURRENT_ORG_NAME
        org_id = self.org_id_entry.get().strip()
        org_name = self.org_name_entry.get().strip() # Use org_name for verification

        if not all([org_id, org_name]):
            messagebox.showerror("Login Error", "Please enter Org ID and Org Name.")
            return

        # No need to call connect_db here, it's already connected at app start
        try:
            cursor.execute("SELECT org_id, org_name FROM organization WHERE org_id = %s AND org_name = %s", (org_id, org_name))
            org_info = cursor.fetchone()
            if org_info:
                CURRENT_USER_TYPE = 'organization'
                CURRENT_USER_ID = org_id
                CURRENT_ORG_NAME = org_name # Store the organization name
                messagebox.showinfo("Login Success", f"Welcome, {org_info[1]} (Organization)!")
                self.app.show_organization_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid Org ID or Org Name. Please try again.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to login: {err}")
        # No finally block to disconnect_db, connection is persistent

    def org_signup_prompt(self):
        signup_window = Toplevel(self.master)
        signup_window.title("Organization Sign Up")
        signup_window.geometry("300x150")

        labels = ["Org ID:", "Org Name:"]
        entries = {}

        for i, text in enumerate(labels):
            ttk.Label(signup_window, text=text).grid(row=i, column=0, sticky=W, padx=5, pady=2)
            entry = ttk.Entry(signup_window)
            entry.grid(row=i, column=1, sticky=(W, E), padx=5, pady=2)
            entries[text.replace(":", "").replace(" ", "_").lower()] = entry

        def perform_signup():
            org_id = entries['org_id'].get().strip()
            org_name = entries['org_name'].get().strip()

            if not all([org_id, org_name]):
                messagebox.showerror("Input Error", "Please fill in all fields.")
                return

            # No need to call connect_db here, it's already connected at app start
            try:
                # Check if org_id or org_name already exists
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
                signup_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to sign up: {err}")
            # No finally block to disconnect_db, connection is persistent


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
            ORDER BY s.academic_year DESC, s.semester DESC
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
            entry = ttk.Entry(self)
            entry.grid(row=i + 1, column=1, sticky=(W, E), padx=5, pady=2)
            self.entries[text.replace(":", "").replace(" ", "_").lower()] = entry

        # Dropdowns for Role, Status, Committee (example options)
        self.role_options = ["Member", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer"]
        self.status_options = ["Active", "Inactive", "Dismissed", "Alumni"]
        self.committee_options = ["Executive", "Finance", "Logistics", "Publicity", "Internal Affairs", "External Affairs"]

        self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
        self.role_combobox.grid(row=4, column=1, sticky=(W, E), padx=5, pady=2)
        self.entries['role'] = self.role_combobox # Replace entry with combobox

        self.status_combobox = ttk.Combobox(self, values=self.status_options, state="readonly")
        self.status_combobox.grid(row=5, column=1, sticky=(W, E), padx=5, pady=2)
        self.entries['status'] = self.status_combobox # Replace entry with combobox

        self.committee_combobox = ttk.Combobox(self, values=self.committee_options, state="readonly")
        self.committee_combobox.grid(row=6, column=1, sticky=(W, E), padx=5, pady=2)
        self.entries['committee'] = self.committee_combobox # Replace entry with combobox


        ttk.Button(self, text="Add Member", command=self.add_member).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    def add_member(self):
        student_no = self.entries['student_no'].get().strip()
        academic_year = self.entries['academic_year'].get().strip()
        semester = self.entries['semester'].get().strip()
        role = self.entries['role'].get().strip()
        status = self.entries['status'].get().strip()
        committee = self.entries['committee'].get().strip()
        membership_fee = 250.00 # Fixed fee

        if not all([student_no, academic_year, semester, role, status, committee]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        # No need to call connect_db here
        try:
            # 1. Check if member exists in the MEMBER table
            cursor.execute("SELECT student_no FROM member WHERE student_no = %s", (student_no,))
            member_exists = cursor.fetchone()
            if not member_exists:
                messagebox.showerror("Error", f"Student No. {student_no} does not exist in the system. Please register the member first.")
                return

            # 2. Check if member is already serving in this organization (student_no, org_name)
            # The 'serves' table PRIMARY KEY is (student_no, org_name) so this check is important
            cursor.execute("""
                SELECT student_no FROM serves
                WHERE student_no = %s AND org_name = %s
            """, (student_no, CURRENT_ORG_NAME))
            if cursor.fetchone():
                messagebox.showerror("Error", f"Member {student_no} is already registered in {CURRENT_ORG_NAME}.")
                return

            # 3. Add to SERVES table
            insert_serves_query = """
            INSERT INTO serves (student_no, org_name, academic_year, semester, role, status, committee)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_serves_query, (student_no, CURRENT_ORG_NAME, academic_year, semester, role, status, committee))

            # 4. Add initial membership fee to FEE table
            # Generate a simple receipt number (can be improved with a more robust system)
            receipt_no = f"FEE-{student_no}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            payment_deadline = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d') # Example: 30 days from now

            insert_fee_query = """
            INSERT INTO fee (receipt_no, amount, payment_deadline, date_paid, payment_status, student_no, org_name)
            VALUES (%s, %s, %s, NULL, 'Unpaid', %s, %s)
            """
            cursor.execute(insert_fee_query, (receipt_no, membership_fee, payment_deadline, student_no, CURRENT_ORG_NAME))

            # 5. Update no_of_members in ORGANIZATION table
            update_org_query = """
            UPDATE organization SET no_of_members = no_of_members + 1 WHERE org_name = %s
            """
            cursor.execute(update_org_query, (CURRENT_ORG_NAME,))

            cnx.commit()
            messagebox.showinfo("Success", f"Member {student_no} successfully added to {CURRENT_ORG_NAME} with an initial fee of Php {membership_fee:.2f}.")
            # Clear fields after successful addition
            for entry in self.entries.values():
                if isinstance(entry, ttk.Entry):
                    entry.delete(0, END)
                elif isinstance(entry, ttk.Combobox):
                    entry.set('')

        except mysql.connector.Error as err:
            cnx.rollback() # Rollback in case of any error
            messagebox.showerror("Database Error", f"Failed to add member: {err}")
        # No finally block to disconnect_db, connection is persistent

class EditMembershipStatusPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Edit Membership Status in {CURRENT_ORG_NAME}")
        self.create_edit_form()

    def create_edit_form(self):
        ttk.Label(self, text="Student No:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.student_no_entry = ttk.Entry(self)
        self.student_no_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="New Status:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.status_options = ["Active", "Inactive", "Dismissed", "Alumni"]
        self.new_status_combobox = ttk.Combobox(self, values=self.status_options, state="readonly")
        self.new_status_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self, text="Update Status", command=self.update_status).grid(row=3, column=0, columnspan=2, pady=10)

    def update_status(self):
        student_no = self.student_no_entry.get().strip()
        new_status = self.new_status_combobox.get().strip()

        if not all([student_no, new_status]):
            messagebox.showerror("Input Error", "Please enter Student Number and select a New Status.")
            return

        # No need to call connect_db here
        try:
            # Check if the member is part of this organization
            cursor.execute("""
                SELECT student_no FROM serves
                WHERE student_no = %s AND org_name = %s
            """, (student_no, CURRENT_ORG_NAME))
            if not cursor.fetchone():
                messagebox.showerror("Error", f"Student No. {student_no} is not a member of {CURRENT_ORG_NAME}.")
                return

            update_query = """
            UPDATE serves SET status = %s
            WHERE student_no = %s AND org_name = %s
            """
            cursor.execute(update_query, (new_status, student_no, CURRENT_ORG_NAME))
            cnx.commit()
            messagebox.showinfo("Success", f"Membership status for {student_no} in {CURRENT_ORG_NAME} updated to '{new_status}' successfully!")
            self.student_no_entry.delete(0, END)
            self.new_status_combobox.set('')
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update status: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewExecutiveCommitteePage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Executive Committee Members of {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Middle Name", "Last Name", "Role", "Status", "Committee"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Committee", text="Committee")

        self.tree.column("Student No", width=90, anchor=CENTER)
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
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        academic_year = self.academic_year_entry.get().strip()

        if not academic_year:
            messagebox.showerror("Input Error", "Please enter the Academic Year.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 4)
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
                AND s.committee = 'Executive'
            ORDER BY m.last_name, m.first_name;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year))
            records = cursor.fetchall()

            if records:
                for record in records:
                    # Replace None with empty string for middle name if applicable
                    formatted_record = list(record)
                    if formatted_record[2] is None:
                        formatted_record[2] = ""
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=("No executive committee members found for the given academic year.", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve executive committee members: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewPresidentsByOrgAYPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Presidents (or other roles) of {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="Role:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.role_options = ["President", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer", "Member"] # Added common roles
        self.role_combobox = ttk.Combobox(self, values=self.role_options, state="readonly")
        self.role_combobox.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.role_combobox.set("President") # Default to President

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Middle Name", "Last Name", "Academic Year", "Semester", "Role"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Academic Year", text="Academic Year")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Role", text="Role")

        self.tree.column("Student No", width=90, anchor=CENTER)
        self.tree.column("First Name", width=100, anchor=W)
        self.tree.column("Middle Name", width=100, anchor=W)
        self.tree.column("Last Name", width=100, anchor=W)
        self.tree.column("Academic Year", width=100, anchor=CENTER)
        self.tree.column("Semester", width=80, anchor=CENTER)
        self.tree.column("Role", width=100, anchor=W)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        selected_role = self.role_combobox.get().strip()

        if not selected_role:
            messagebox.showerror("Input Error", "Please select a Role.")
            return

        # No need to call connect_db here
        try:
            # This query isn't explicitly in your provided list for presidents,
            # but it can be constructed similarly to executive committee
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                s.academic_year,
                s.semester,
                s.role
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.role = %s
            ORDER BY s.academic_year DESC,
                     CASE s.semester
                         WHEN 'Second' THEN 1
                         WHEN 'First' THEN 2
                         ELSE 3
                     END DESC; -- Order by academic year (current to past), then by semester
            """
            cursor.execute(query, (CURRENT_ORG_NAME, selected_role))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[2] is None:
                        formatted_record[2] = ""
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=(f"No members with role '{selected_role}' found for {CURRENT_ORG_NAME}.", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve members by role: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewLatePaymentsPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Late Payments for {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second", "Midyear"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Last Name", "Receipt No", "Amount", "Payment Deadline", "Date Paid", "Payment Status"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Receipt No", text="Receipt No.")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Payment Deadline", text="Deadline")
        self.tree.heading("Date Paid", text="Date Paid")
        self.tree.heading("Payment Status", text="Status")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("First Name", width=90, anchor=W)
        self.tree.column("Last Name", width=90, anchor=W)
        self.tree.column("Receipt No", width=80, anchor=CENTER)
        self.tree.column("Amount", width=80, anchor=E)
        self.tree.column("Payment Deadline", width=100, anchor=CENTER)
        self.tree.column("Date Paid", width=100, anchor=CENTER)
        self.tree.column("Payment Status", width=80, anchor=CENTER)


        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Academic Year and select a Semester.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 6)
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.last_name,
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
            ORDER BY f.date_paid DESC, f.payment_deadline ASC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[6] is None: # date_paid
                        formatted_record[6] = "N/A"
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=(f"No late payments found for {CURRENT_ORG_NAME} in {academic_year} {semester}.", "", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve late payments: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewActiveInactivePercentagePage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Active vs Inactive Members Percentage in {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()
        self.create_summary_labels()

    def create_input_fields(self):
        ttk.Label(self, text="Number of last semesters (n):").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.n_semesters_entry = ttk.Entry(self)
        self.n_semesters_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.n_semesters_entry.insert(0, "3") # Default to 3 semesters

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Academic Year", "Semester", "Status", "Count", "Percentage"), show="headings")
        self.tree.heading("Academic Year", text="Academic Year")
        self.tree.heading("Semester", text="Semester")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Count", text="Count")
        self.tree.heading("Percentage", text="Percentage")

        self.tree.column("Academic Year", width=100, anchor=CENTER)
        self.tree.column("Semester", width=80, anchor=CENTER)
        self.tree.column("Status", width=80, anchor=CENTER)
        self.tree.column("Count", width=60, anchor=E)
        self.tree.column("Percentage", width=100, anchor=E)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def create_summary_labels(self):
        self.total_members_label = ttk.Label(self, text="Total Members (Latest Semester): N/A", font=(None, 10, BOLD))
        self.total_members_label.grid(row=4, column=0, columnspan=2, sticky=W, pady=5)
        self.active_percentage_label = ttk.Label(self, text="Active Percentage (Latest Semester): N/A", font=(None, 10, BOLD))
        self.active_percentage_label.grid(row=5, column=0, columnspan=2, sticky=W, pady=2)
        self.inactive_percentage_label = ttk.Label(self, text="Inactive Percentage (Latest Semester): N/A", font=(None, 10, BOLD))
        self.inactive_percentage_label.grid(row=6, column=0, columnspan=2, sticky=W, pady=2)


    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.total_members_label.config(text="Total Members (Latest Semester): N/A")
        self.active_percentage_label.config(text="Active Percentage (Latest Semester): N/A")
        self.inactive_percentage_label.config(text="Inactive Percentage (Latest Semester): N/A")

        n_semesters_str = self.n_semesters_entry.get().strip()
        try:
            n_semesters = int(n_semesters_str)
            if n_semesters <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a positive integer for 'n' (number of semesters).")
            return

        # No need to call connect_db here
        try:
            # Get all distinct academic years and semesters for the organization
            cursor.execute("""
                SELECT DISTINCT academic_year, semester
                FROM serves
                WHERE org_name = %s
                ORDER BY academic_year DESC,
                         CASE semester
                             WHEN 'Second' THEN 1
                             WHEN 'First' THEN 2
                             WHEN 'Midyear' THEN 3
                             ELSE 4
                         END DESC;
            """, (CURRENT_ORG_NAME,))
            all_semesters = cursor.fetchall()

            if not all_semesters:
                self.tree.insert("", "end", values=("No membership data found for this organization.", "", "", "", ""))
                return

            # Select the last 'n' semesters
            relevant_semesters = all_semesters[:n_semesters]

            # Store data for overall summary
            latest_semester_total = 0
            latest_semester_active = 0
            latest_semester_inactive = 0

            for ay, sem in relevant_semesters:
                # Get total members for this academic year and semester
                cursor.execute("""
                    SELECT COUNT(student_no)
                    FROM serves
                    WHERE org_name = %s AND academic_year = %s AND semester = %s;
                """, (CURRENT_ORG_NAME, ay, sem))
                total_members_semester = cursor.fetchone()[0]

                if total_members_semester == 0:
                    self.tree.insert("", "end", values=(ay, sem, "No Members", 0, "0.00%"))
                    continue

                # Get counts for active and inactive for this semester
                cursor.execute("""
                    SELECT status, COUNT(student_no)
                    FROM serves
                    WHERE org_name = %s AND academic_year = %s AND semester = %s
                    GROUP BY status;
                """, (CURRENT_ORG_NAME, ay, sem))
                status_counts = cursor.fetchall()

                active_count = 0
                inactive_count = 0
                for status, count in status_counts:
                    if status.lower() == 'active':
                        active_count = count
                    elif status.lower() == 'inactive':
                        inactive_count = count

                active_percentage = (active_count / total_members_semester) * 100
                inactive_percentage = (inactive_count / total_members_semester) * 100

                self.tree.insert("", "end", values=(ay, sem, "Active", active_count, f"{active_percentage:.2f}%"))
                self.tree.insert("", "end", values=(ay, sem, "Inactive", inactive_count, f"{inactive_percentage:.2f}%"))

                # For the latest semester, update summary labels
                if (ay, sem) == relevant_semesters[0]:
                    latest_semester_total = total_members_semester
                    latest_semester_active = active_count
                    latest_semester_inactive = inactive_count
                    self.total_members_label.config(text=f"Total Members (Latest Semester: {ay} {sem}): {latest_semester_total}")
                    if latest_semester_total > 0:
                        self.active_percentage_label.config(text=f"Active Percentage (Latest Semester): {latest_semester_active / latest_semester_total * 100:.2f}%")
                        self.inactive_percentage_label.config(text=f"Inactive Percentage (Latest Semester): {latest_semester_inactive / latest_semester_total * 100:.2f}%")
                    else:
                        self.active_percentage_label.config(text="Active Percentage (Latest Semester): 0.00%")
                        self.inactive_percentage_label.config(text="Inactive Percentage (Latest Semester): 0.00%")

            if not relevant_semesters:
                self.tree.insert("", "end", values=("No data for the last N semesters.", "", "", "", ""))

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve percentage data: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewAlumniMembersPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Alumni Members of {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="As of Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.as_of_date_entry = ttk.Entry(self)
        self.as_of_date_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.as_of_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d')) # Default to today's date

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Middle Name", "Last Name", "Batch", "Role", "Committee", "Last Academic Year", "Status"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Batch", text="Batch")
        self.tree.heading("Role", text="Role (Last)")
        self.tree.heading("Committee", text="Committee (Last)")
        self.tree.heading("Last Academic Year", text="Last AY")
        self.tree.heading("Status", text="Status")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("First Name", width=90, anchor=W)
        self.tree.column("Middle Name", width=90, anchor=W)
        self.tree.column("Last Name", width=90, anchor=W)
        self.tree.column("Batch", width=60, anchor=CENTER)
        self.tree.column("Role", width=80, anchor=W)
        self.tree.column("Committee", width=80, anchor=W)
        self.tree.column("Last Academic Year", width=90, anchor=CENTER)
        self.tree.column("Status", width=70, anchor=CENTER)

        self.tree.grid(row=3, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        as_of_date_str = self.as_of_date_entry.get().strip()
        if not as_of_date_str:
            messagebox.showerror("Input Error", "Please enter a date.")
            return

        try:
            # Validate date format and parse it
            as_of_date = datetime.datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 8)
            # This query logic assumes 'alumni' status or academic_year < 'given date' makes them alumni.
            # I will prioritize the 'Alumni' status in the 'serves' table first,
            # and then consider those whose latest academic_year in the organization is before the given date.
            # A more robust 'alumni' definition might be needed depending on business rules.
            # For simplicity, I'll use the 'Alumni' status directly.

            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                m.batch,
                s.role,
                s.committee,
                s.academic_year,
                s.status
            FROM member m
            JOIN serves s ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.status = 'Alumni'
                AND s.academic_year <= YEAR(%s) -- Assuming academic_year is like 'YYYY-YYYY' or just 'YYYY'
            ORDER BY m.last_name, m.first_name;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, as_of_date))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[2] is None:
                        formatted_record[2] = ""
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=(f"No alumni members found for {CURRENT_ORG_NAME} as of {as_of_date_str}.", "", "", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve alumni members: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewTotalPaidUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Total Paid/Unpaid Fees for {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_display_labels()

    def create_input_fields(self):
        ttk.Label(self, text="As of Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.as_of_date_entry = ttk.Entry(self)
        self.as_of_date_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.as_of_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d')) # Default to today's date

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)

    def create_display_labels(self):
        self.unpaid_amount_label = ttk.Label(self, text="Total Unpaid Amount: Php N/A", font=(None, 12, BOLD), foreground="red")
        self.unpaid_amount_label.grid(row=3, column=0, columnspan=2, sticky=W, pady=10)

        self.paid_amount_label = ttk.Label(self, text="Total Paid Amount: Php N/A", font=(None, 12, BOLD), foreground="green")
        self.paid_amount_label.grid(row=4, column=0, columnspan=2, sticky=W, pady=5)

        self.grand_total_label = ttk.Label(self, text="Grand Total (Billed): Php N/A", font=(None, 12, BOLD))
        self.grand_total_label.grid(row=5, column=0, columnspan=2, sticky=W, pady=5)

    def generate_report(self):
        self.unpaid_amount_label.config(text="Total Unpaid Amount: Php N/A")
        self.paid_amount_label.config(text="Total Paid Amount: Php N/A")
        self.grand_total_label.config(text="Grand Total (Billed): Php N/A")

        as_of_date_str = self.as_of_date_entry.get().strip()
        if not as_of_date_str:
            messagebox.showerror("Input Error", "Please enter a date.")
            return

        try:
            as_of_date = datetime.datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 9)
            # The original query uses 0/1 for payment_status, but your schema uses "Unpaid"/"Paid".
            # I will adapt the query to use the string values from your schema.
            query = """
            SELECT
                COALESCE(SUM(CASE WHEN f.payment_status = 'Unpaid' OR f.date_paid IS NULL THEN f.amount ELSE 0 END), 0) AS unpaid_amount,
                COALESCE(SUM(CASE WHEN f.payment_status = 'Paid' AND f.date_paid IS NOT NULL THEN f.amount ELSE 0 END), 0) AS paid_amount
            FROM fee f
            WHERE f.org_name = %s AND f.payment_deadline <= %s;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, as_of_date))
            result = cursor.fetchone()

            if result:
                unpaid_amount = result[0]
                paid_amount = result[1]
                grand_total = unpaid_amount + paid_amount

                self.unpaid_amount_label.config(text=f"Total Unpaid Amount: Php {unpaid_amount:.2f}")
                self.paid_amount_label.config(text=f"Total Paid Amount: Php {paid_amount:.2f}")
                self.grand_total_label.config(text=f"Grand Total (Billed): Php {grand_total:.2f}")
            else:
                self.unpaid_amount_label.config(text="Total Unpaid Amount: Php 0.00")
                self.paid_amount_label.config(text="Total Paid Amount: Php 0.00")
                self.grand_total_label.config(text="Grand Total (Billed): Php 0.00")
                messagebox.showinfo("No Data", "No fee data found for this organization as of the given date.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve fee summary: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewHighestDebtMembersPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Member(s) with Highest Debt in {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second", "Midyear"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Last Name", "Total Debt"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Total Debt", text="Total Debt (PHP)")

        self.tree.column("Student No", width=100, anchor=CENTER)
        self.tree.column("First Name", width=150, anchor=W)
        self.tree.column("Last Name", width=150, anchor=W)
        self.tree.column("Total Debt", width=120, anchor=E)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Academic Year and select a Semester.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 10)
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.last_name,
                SUM(f.amount) AS total_debt
            FROM fee f
            JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
            JOIN member m ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
                AND (f.payment_status = 'Unpaid' OR f.date_paid IS NULL)
            GROUP BY m.student_no, m.first_name, m.last_name
            ORDER BY total_debt DESC
            LIMIT 1;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    self.tree.insert("", "end", values=record)
            else:
                self.tree.insert("", "end", values=(f"No members with unpaid fees found for {CURRENT_ORG_NAME} in {academic_year} {semester}.", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve members with highest debt: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewAllMembersByAttributesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Members of {CURRENT_ORG_NAME} by Attributes")
        self.create_input_fields() # For filtering
        self.create_treeview()

    def create_input_fields(self):
        # Filtering options (optional, but good for large lists)
        ttk.Label(self, text="Filter by Role:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.role_filter_options = ["All"] + ["Member", "Executive President", "VP Internal", "VP External", "Secretary", "Treasurer"] # Example roles
        self.role_filter_combobox = ttk.Combobox(self, values=self.role_filter_options, state="readonly")
        self.role_filter_combobox.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)
        self.role_filter_combobox.set("All")

        ttk.Label(self, text="Filter by Status:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.status_filter_options = ["All", "Active", "Inactive", "Dismissed", "Alumni"]
        self.status_filter_combobox = ttk.Combobox(self, values=self.status_filter_options, state="readonly")
        self.status_filter_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)
        self.status_filter_combobox.set("All")

        ttk.Label(self, text="Filter by Gender:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.gender_filter_options = ["All", "Male", "Female", "Other"] # Example
        self.gender_filter_combobox = ttk.Combobox(self, values=self.gender_filter_options, state="readonly")
        self.gender_filter_combobox.grid(row=3, column=1, sticky=(W, E), padx=5, pady=2)
        self.gender_filter_combobox.set("All")

        ttk.Label(self, text="Filter by Committee:").grid(row=4, column=0, sticky=W, padx=5, pady=2)
        self.committee_filter_options = ["All", "Executive", "Finance", "Logistics", "Publicity", "Internal Affairs", "External Affairs"]
        self.committee_filter_combobox = ttk.Combobox(self, values=self.committee_filter_options, state="readonly")
        self.committee_filter_combobox.grid(row=4, column=1, sticky=(W, E), padx=5, pady=2)
        self.committee_filter_combobox.set("All")

        ttk.Label(self, text="Academic Year:").grid(row=5, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=5, column=1, sticky=(W, E), padx=5, pady=2)
        self.academic_year_entry.insert(0, datetime.datetime.now().year) # Default to current year

        ttk.Label(self, text="Semester:").grid(row=6, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second", "Midyear"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=6, column=1, sticky=(W, E), padx=5, pady=2)
        # Attempt to set current semester as default
        current_month = datetime.datetime.now().month
        if 6 <= current_month <= 10: # Assuming First semester (June-Oct)
            self.semester_combobox.set("First")
        elif 11 <= current_month or current_month <= 3: # Assuming Second semester (Nov-March)
            self.semester_combobox.set("Second")
        else: # April-May
            self.semester_combobox.set("Midyear")

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=7, column=0, columnspan=2, pady=10)


    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=(
            "Student No", "First Name", "Middle Name", "Last Name",
            "Degree Program", "Gender", "Batch", "Role", "Status", "Committee"
        ), show="headings")

        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Degree Program", text="Degree Program")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Batch", text="Batch")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Committee", text="Committee")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("First Name", width=90, anchor=W)
        self.tree.column("Middle Name", width=90, anchor=W)
        self.tree.column("Last Name", width=90, anchor=W)
        self.tree.column("Degree Program", width=120, anchor=W)
        self.tree.column("Gender", width=70, anchor=CENTER)
        self.tree.column("Batch", width=60, anchor=CENTER)
        self.tree.column("Role", width=80, anchor=W)
        self.tree.column("Status", width=70, anchor=CENTER)
        self.tree.column("Committee", width=100, anchor=W)

        self.tree.grid(row=8, column=0, columnspan=3, sticky=(N, S, E, W), pady=10) # Adjusted columnspan
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0) # For scrollbar

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=8, column=3, sticky=(N, S)) # Adjusted column for scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        filter_role = self.role_filter_combobox.get().strip()
        filter_status = self.status_filter_combobox.get().strip()
        filter_gender = self.gender_filter_combobox.get().strip()
        filter_committee = self.committee_filter_combobox.get().strip()
        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Academic Year and Semester.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 1)
            base_query = """
            SELECT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                m.degree_program,
                m.gender,
                m.batch,
                s.role,
                s.status,
                s.committee
            FROM member m
            JOIN serves s
                ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
            """
            params = [CURRENT_ORG_NAME, academic_year, semester]

            if filter_role != "All":
                base_query += " AND s.role = %s"
                params.append(filter_role)
            if filter_status != "All":
                base_query += " AND s.status = %s"
                params.append(filter_status)
            if filter_gender != "All":
                base_query += " AND m.gender = %s"
                params.append(filter_gender)
            if filter_committee != "All":
                base_query += " AND s.committee = %s"
                params.append(filter_committee)

            base_query += " ORDER BY m.last_name, m.first_name;"

            cursor.execute(base_query, tuple(params))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[2] is None: # Middle name
                        formatted_record[2] = ""
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=("No members found matching the criteria.", "", "", "", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve members: {err}")
        # No finally block to disconnect_db, connection is persistent


class ViewOrgUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, f"Members with Unpaid Fees in {CURRENT_ORG_NAME}")
        self.create_input_fields()
        self.create_treeview()

    def create_input_fields(self):
        ttk.Label(self, text="Academic Year:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.academic_year_entry = ttk.Entry(self)
        self.academic_year_entry.grid(row=1, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Label(self, text="Semester:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.semester_options = ["First", "Second", "Midyear"]
        self.semester_combobox = ttk.Combobox(self, values=self.semester_options, state="readonly")
        self.semester_combobox.grid(row=2, column=1, sticky=(W, E), padx=5, pady=2)

        ttk.Button(self, text="Generate Report", command=self.generate_report).grid(row=3, column=0, columnspan=2, pady=10)

    def create_treeview(self):
        self.tree = ttk.Treeview(self, columns=("Student No", "First Name", "Middle Name", "Last Name", "Org Name", "Receipt No", "Amount", "Payment Deadline"), show="headings")
        self.tree.heading("Student No", text="Student No.")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Middle Name", text="Middle Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Org Name", text="Organization")
        self.tree.heading("Receipt No", text="Receipt No.")
        self.tree.heading("Amount", text="Amount (PHP)")
        self.tree.heading("Payment Deadline", text="Deadline")

        self.tree.column("Student No", width=80, anchor=CENTER)
        self.tree.column("First Name", width=90, anchor=W)
        self.tree.column("Middle Name", width=90, anchor=W)
        self.tree.column("Last Name", width=90, anchor=W)
        self.tree.column("Org Name", width=120, anchor=W)
        self.tree.column("Receipt No", width=80, anchor=CENTER)
        self.tree.column("Amount", width=80, anchor=E)
        self.tree.column("Payment Deadline", width=100, anchor=CENTER)

        self.tree.grid(row=4, column=0, columnspan=2, sticky=(N, S, E, W), pady=10)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky=(N, S))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        academic_year = self.academic_year_entry.get().strip()
        semester = self.semester_combobox.get().strip()

        if not all([academic_year, semester]):
            messagebox.showerror("Input Error", "Please enter Academic Year and select a Semester.")
            return

        # No need to call connect_db here
        try:
            # SQL query from your provided list (number 2)
            query = """
            SELECT DISTINCT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                s.org_name,
                f.receipt_no,
                f.amount,
                f.payment_deadline
            FROM member m
            JOIN fee f
                ON m.student_no = f.student_no
            JOIN serves s
                ON m.student_no = s.student_no AND s.org_name = f.org_name
            WHERE (f.payment_status = 'Unpaid' OR f.date_paid IS NULL)
                AND s.org_name = %s
                AND s.academic_year = %s
                AND s.semester = %s
            ORDER BY m.last_name, m.first_name, f.payment_deadline DESC;
            """
            cursor.execute(query, (CURRENT_ORG_NAME, academic_year, semester))
            records = cursor.fetchall()

            if records:
                for record in records:
                    formatted_record = list(record)
                    if formatted_record[2] is None: # Middle name
                        formatted_record[2] = ""
                    self.tree.insert("", "end", values=formatted_record)
            else:
                self.tree.insert("", "end", values=(f"No members with unpaid fees found for {CURRENT_ORG_NAME} in {academic_year} {semester}.", "", "", "", "", "", "", ""))
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to retrieve unpaid fees: {err}")
        # No finally block to disconnect_db, connection is persistent


# --- Main Application Class ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Membership Management System")
        self.root.geometry("800x600")

        # Connect to the database when the app starts
        if not connect_db():
            messagebox.showerror("Initialization Error", "Failed to connect to the database. The application will close.")
            self.root.destroy()
            return

        # Bind the closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_page = None
        self.show_auth_page()

    def on_closing(self):
        """Called when the user tries to close the window."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            disconnect_db() # Disconnect from the database
            self.root.destroy()

    def show_page(self, page_class, *args):
        if self.current_page:
            self.current_page.destroy()
        self.current_page = page_class(self.root, self, *args)
        self.current_page.grid(row=0, column=0, sticky=(N, W, E, S))

    def show_auth_page(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID, CURRENT_ORG_NAME
        CURRENT_USER_TYPE = None
        CURRENT_USER_ID = None
        CURRENT_ORG_NAME = None
        self.show_page(AuthPage)

    def show_member_menu(self):
        self.show_page(MemberMenuPage)

    def show_view_personal_info_page(self):
        self.show_page(ViewPersonalInfoPage)

    def show_edit_personal_info_page(self):
        self.show_page(EditPersonalInfoPage)

    def show_view_registered_orgs_page(self):
        self.show_page(ViewRegisteredOrgsPage)

    def show_view_members_unpaid_fees_page(self):
        self.show_page(ViewMembersUnpaidFeesPage)

    def show_organization_menu(self):
        self.show_page(OrganizationMenuPage)

    def show_add_member_page(self):
        self.show_page(AddNewMemberPage)

    def show_edit_membership_status_page(self):
        self.show_page(EditMembershipStatusPage)

    def show_view_exec_committee_page(self):
        self.show_page(ViewExecutiveCommitteePage)

    def show_view_presidents_by_ay_page(self):
        self.show_page(ViewPresidentsByOrgAYPage)

    def show_view_late_payments_page(self):
        self.show_page(ViewLatePaymentsPage)

    def show_view_active_inactive_percentage_page(self):
        self.show_page(ViewActiveInactivePercentagePage)

    def show_view_alumni_members_page(self):
        self.show_page(ViewAlumniMembersPage)

    def show_view_total_paid_unpaid_fees_page(self):
        self.show_page(ViewTotalPaidUnpaidFeesPage)

    def show_view_highest_debt_members_page(self):
        self.show_page(ViewHighestDebtMembersPage)

    def show_view_all_members_by_attributes_page(self):
        self.show_page(ViewAllMembersByAttributesPage)

    def show_view_org_unpaid_fees_page(self):
        self.show_page(ViewOrgUnpaidFeesPage)


    def logout(self):
        global CURRENT_USER_TYPE, CURRENT_USER_ID, CURRENT_ORG_NAME
        CURRENT_USER_TYPE = None
        CURRENT_USER_ID = None
        CURRENT_ORG_NAME = None
        messagebox.showinfo("Logout", "You have been logged out.")
        self.show_auth_page()

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()