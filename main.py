import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkinter.font import BOLD
import re

# Import only what is necessary from shared_variables
from shared_variables import (
    DB_CONFIG, cnx, cursor,
    connect_db, disconnect_db, execute_query, fetch_one, fetch_all, BasePage
)

from orgpov import OrganizationMenuPage
from orgpov_modifymembers import AddNewMemberPage, EditMembershipStatusPage
# from orgpov_fees import OrganizationFeesPage # Uncomment when ready

from memberpov import MemberMenuPage, ViewPersonalInfoPage, EditPersonalInfoPage, ViewRegisteredOrgsPage, ViewMembersUnpaidFeesPage

class AuthPage(ttk.Frame):
    def __init__(self, master, app_instance):
        super().__init__(master, padding="0")
        self.app = app_instance # app_instance is the main App class
        self.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

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
        self.signup_gender_combobox = ttk.Combobox(member_panel, values=["F", "M"], state="readonly", font=("Arial", 12))
        self.signup_gender_combobox.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.signup_gender_combobox.set("F")
        ttk.Label(member_panel, text="Format: F / M", font=("Arial", 8), foreground='grey').grid(row=11, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Middle Name", font=("Arial", 10, BOLD)).grid(row=12, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_middle_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_middle_name_entry.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Label(member_panel, text="Optional", font=("Arial", 8), foreground='grey').grid(row=14, column=0, sticky=tk.W, pady=(0, 10))

        # RE-ADDED BATCH TO MEMBER SIGNUP
        ttk.Label(member_panel, text="Batch", font=("Arial", 10, BOLD)).grid(row=12, column=1, sticky=tk.W, pady=(10, 0))
        self.signup_batch_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_batch_entry.grid(row=13, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(member_panel, text="Format: 20XX", font=("Arial", 8), foreground='grey').grid(row=14, column=1, sticky=tk.W, pady=(0, 10))

        ttk.Label(member_panel, text="Last Name", font=("Arial", 10, BOLD)).grid(row=15, column=0, sticky=tk.W, pady=(10, 0))
        self.signup_last_name_entry = ttk.Entry(member_panel, font=("Arial", 12))
        self.signup_last_name_entry.grid(row=16, column=0, columnspan=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(0,5))
        ttk.Button(member_panel, text="Sign-up", style='Login.TButton', command=self.member_signup).grid(row=16, column=1, sticky=tk.E, padx=(5,0))

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
        student_no = self.member_student_no_entry.get().strip()
        if not student_no:
            messagebox.showerror("Login Error", "Please enter a Student Number.")
            return

        member_info = fetch_one("SELECT student_no, first_name FROM member WHERE student_no = %s", (student_no,))
        if member_info:
            self.app.current_user_type = 'member'
            self.app.current_user_id = student_no
            messagebox.showinfo("Login Success", f"Welcome, {member_info['first_name']} (Member)!")
            self.app.show_member_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid Student Number. Please try again.")

    def member_signup(self):
        student_no = self.signup_student_no_entry.get().strip()
        first_name = self.signup_first_name_entry.get().strip()
        middle_name = self.signup_middle_name_entry.get().strip()
        last_name = self.signup_last_name_entry.get().strip()
        degree_program = self.signup_degree_program_entry.get().strip()
        gender = self.signup_gender_combobox.get().strip()
        batch = self.signup_batch_entry.get().strip() # RE-ADDED BATCH

        # ADDED BATCH TO VALIDATION
        if not all([student_no, first_name, last_name, degree_program, gender, batch]):
            messagebox.showerror("Input Error", "Please fill in all required fields (Student No, First Name, Last Name, Degree Program, Gender, Batch).")
            return
        
        if not re.match(r"20\d{2}-\d{5}", student_no):
            messagebox.showerror("Validation Error", "Student number format is incorrect. Expected: 20XX-XXXXX")
            return
        
        # RE-ADDED BATCH INT CONVERSION
        try:
            batch_int = int(batch)
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
            return

        if fetch_one("SELECT student_no FROM member WHERE student_no = %s", (student_no,)):
            messagebox.showerror("Signup Error", "Student Number already exists.")
            return

        insert_query = """
        INSERT INTO member (student_no, first_name, middle_name, last_name, degree_program, gender, batch)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # RE-ADDED BATCH TO INSERT PARAMETERS
        rows_affected = execute_query(insert_query, (student_no, first_name, middle_name if middle_name else None, last_name, degree_program, gender, batch_int))
        
        if rows_affected > 0:
            messagebox.showinfo("Sign Up Success", "Member registered successfully!")
            self.signup_student_no_entry.delete(0, tk.END)
            self.signup_first_name_entry.delete(0, tk.END)
            self.signup_middle_name_entry.delete(0, tk.END)
            self.signup_last_name_entry.delete(0, tk.END)
            self.signup_degree_program_entry.delete(0, tk.END)
            self.signup_gender_combobox.set("F")
            # RE-ADDED BATCH TO CLEARING
            self.signup_batch_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Signup Error", "Failed to register member.")


    def org_login(self):
        org_id = self.org_id_entry.get().strip()

        if not org_id:
            messagebox.showerror("Login Error", "Please enter Org ID.")
            return

        org_info = fetch_one("SELECT org_id, org_name FROM organization WHERE org_id = %s", (org_id,))
        if org_info:
            self.app.current_user_type = 'organization'
            self.app.current_user_id = org_id
            self.app.current_org_name = org_info['org_name']
            messagebox.showinfo("Login Success", f"Welcome, {self.app.current_org_name} (Organization)!")
            self.app.show_organization_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid Org ID. Please try again.")

    def org_signup(self):
        org_id = self.signup_org_id_entry.get().strip()
        org_name = self.signup_org_name_entry.get().strip()

        if not all([org_id, org_name]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return
        
        if not re.match(r"^\d{5}$", org_id):
            messagebox.showerror("Validation Error", "Organization ID format is incorrect. Expected: XXXXX (5 digits)")
            return

        if fetch_one("SELECT org_id FROM organization WHERE org_id = %s OR org_name = %s", (org_id, org_name)):
            messagebox.showerror("Signup Error", "Organization ID or Name already exists.")
            return

        insert_query = """
        INSERT INTO organization (org_id, org_name, no_of_members)
        VALUES (%s, %s, 0)
        """
        rows_affected = execute_query(insert_query, (org_id, org_name))
        
        if rows_affected > 0:
            messagebox.showinfo("Sign Up Success", "Organization registered successfully!")
            self.signup_org_id_entry.delete(0, tk.END)
            self.signup_org_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Signup Error", "Failed to register organization.")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Organization Management System")
        self.geometry("1200x920")

        self.current_page = None
        self.pages = {}
        self.current_user_type = None
        self.current_user_id = None
        self.current_org_name = None

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
        self.pages['OrganizationMenuPage'] = OrganizationMenuPage
        self.show_page('OrganizationMenuPage', self.current_org_name)

    def show_add_new_member_page(self):
        self.pages['AddNewMemberPage'] = AddNewMemberPage
        self.show_page('AddNewMemberPage')

    def show_edit_membership_status_page(self):
        self.pages['EditMembershipStatusPage'] = EditMembershipStatusPage
        self.show_page('EditMembershipStatusPage')

    def show_org_fees_page(self):
        messagebox.showinfo("Coming Soon", "Organization Fees page is not yet implemented.")

    def logout(self):
        self.current_user_type = None
        self.current_user_id = None
        self.current_org_name = None
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