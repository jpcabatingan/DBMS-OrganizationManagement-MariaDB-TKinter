# memberpov.py
# Import shared components from the new shared_variables module
from shared_variables import (
    BasePage, cursor, fetch_one, execute_query, fetch_all
)
# REMOVE CURRENT_USER_ID from this import

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD

# MemberMenuPage Class --------------------------------------------------
class MemberMenuPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Member Menu") # This calls BasePage's __init__

        # ADD THESE TWO LINES TO HIDE THE BACK BUTTON
        self.back_button.grid_forget() # Removes the button from the grid layout
        self.back_button.destroy()     # Destroys the widget itself

        # Configure columns for content_frame
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Welcome Message
        ttk.Label(self.content_frame, text=f"Welcome, {self.app.current_user_id}!", font=("Arial", 16, BOLD)).grid(row=0, column=0, columnspan=2, pady=20)

        self.create_widgets()

    def create_widgets(self):
        # Buttons for member functionalities
        btn_personal_info = ttk.Button(self.content_frame, text="View Personal Info", command=self.app.show_view_personal_info_page, style='Menu.TButton')
        btn_personal_info.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        btn_edit_personal_info = ttk.Button(self.content_frame, text="Edit Personal Info", command=self.app.show_edit_personal_info_page, style='Menu.TButton')
        btn_edit_personal_info.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        btn_registered_orgs = ttk.Button(self.content_frame, text="View Registered Organizations", command=self.app.show_view_registered_orgs_page, style='Menu.TButton')
        btn_registered_orgs.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        btn_unpaid_fees = ttk.Button(self.content_frame, text="View Unpaid Fees", command=self.app.show_view_members_unpaid_fees_page, style='Menu.TButton')
        btn_unpaid_fees.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

        btn_logout = ttk.Button(self.content_frame, text="Logout", command=self.app.logout, style='Menu.TButton')
        btn_logout.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")

        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style(self)
        style.configure('Menu.TButton',
                        font=("Arial", 12, BOLD),
                        foreground="white",
                        background="#446EE2",
                        padding=15,
                        relief="flat")
        style.map('Menu.TButton',
                  background=[('active', '#5E35B1'), ('pressed', '#4527A0')])
        style.configure('TLabel', background="#f0f0f0", foreground='black')

# ViewPersonalInfoPage Class --------------------------------------------------
class ViewPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "View Personal Information")

        self.info_labels = {}
        self.load_personal_info()

    def load_personal_info(self):
        # Access CURRENT_USER_ID via self.app.current_user_id
        student_no = self.app.current_user_id
        if not student_no:
            messagebox.showerror("Error", "No student ID found for current user.")
            self.app.show_member_menu()
            return

        query = "SELECT * FROM member WHERE student_no = %s"
        member_info = fetch_one(query, (student_no,))

        if member_info:
            data = {
                "Student No.": member_info.get('student_no', ''),
                "First Name": member_info.get('first_name', ''),
                "Middle Name": member_info.get('middle_name', ''),
                "Last Name": member_info.get('last_name', ''),
                "Degree Program": member_info.get('degree_program', ''),
                "Gender": member_info.get('gender', ''),
                "Batch": member_info.get('batch', ''),
                "Enrollment Status": member_info.get('enrollment_status', '')
            }

            row = 0
            for label_text, value in data.items():
                ttk.Label(self.content_frame, text=f"{label_text}:", font=("Arial", 12, BOLD)).grid(row=row, column=0, sticky=tk.W, pady=5, padx=10)
                ttk.Label(self.content_frame, text=str(value), font=("Arial", 12)).grid(row=row, column=1, sticky=tk.W, pady=5, padx=10)
                row += 1
        else:
            ttk.Label(self.content_frame, text="Personal information not found.", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=20)

# EditPersonalInfoPage Class --------------------------------------------------
class EditPersonalInfoPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Edit Personal Information")
        self.entries = {}
        self.load_data_for_editing()

    def load_data_for_editing(self):
        # Access CURRENT_USER_ID via self.app.current_user_id
        student_no = self.app.current_user_id
        if not student_no:
            messagebox.showerror("Error", "No student ID found for current user.")
            self.app.show_member_menu()
            return

        query = "SELECT * FROM member WHERE student_no = %s"
        member_info = fetch_one(query, (student_no,))

        if member_info:
            fields = [
                ("Student No.", 'student_no'),
                ("First Name", 'first_name'),
                ("Middle Name", 'middle_name'),
                ("Last Name", 'last_name'),
                ("Degree Program", 'degree_program'),
                ("Gender", 'gender'),
                ("Batch", 'batch'),
                ("Enrollment Status", 'enrollment_status')
            ]

            row = 0
            for label_text, db_column in fields:
                ttk.Label(self.content_frame, text=f"{label_text}:", font=("Arial", 12, BOLD)).grid(row=row, column=0, sticky=tk.W, pady=5, padx=10)
                
                if db_column in ['student_no', 'enrollment_status']: # Make these read-only
                    entry = ttk.Entry(self.content_frame, font=("Arial", 12), state='readonly')
                    entry.insert(0, str(member_info.get(db_column, '')))
                elif db_column == 'gender':
                    entry = ttk.Combobox(self.content_frame, values=["F", "M"], state="readonly", font=("Arial", 12))
                    entry.set(member_info.get(db_column, ''))
                else:
                    entry = ttk.Entry(self.content_frame, font=("Arial", 12))
                    entry.insert(0, str(member_info.get(db_column, '')))

                entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
                self.entries[db_column] = entry
                row += 1

            ttk.Button(self.content_frame, text="Save Changes", command=self.save_changes, style='Menu.TButton').grid(row=row, column=0, columnspan=2, pady=20)
        else:
            ttk.Label(self.content_frame, text="Personal information not found for editing.", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=20)

    def save_changes(self):
        # Access CURRENT_USER_ID via self.app.current_user_id
        student_no = self.app.current_user_id
        if not student_no:
            messagebox.showerror("Error", "No student ID found for saving changes.")
            return

        updated_data = {
            'first_name': self.entries['first_name'].get().strip(),
            'middle_name': self.entries['middle_name'].get().strip() or None,
            'last_name': self.entries['last_name'].get().strip(),
            'degree_program': self.entries['degree_program'].get().strip(),
            'gender': self.entries['gender'].get().strip(),
            'batch': self.entries['batch'].get().strip()
        }

        if not all([updated_data['first_name'], updated_data['last_name'], updated_data['degree_program'], updated_data['gender'], updated_data['batch']]):
            messagebox.showerror("Input Error", "Please fill in all required fields.")
            return

        try:
            updated_data['batch'] = int(updated_data['batch'])
        except ValueError:
            messagebox.showerror("Input Error", "Batch must be an integer.")
            return

        update_query = """
        UPDATE member
        SET first_name = %s, middle_name = %s, last_name = %s,
            degree_program = %s, gender = %s, batch = %s
        WHERE student_no = %s
        """
        params = (
            updated_data['first_name'], updated_data['middle_name'], updated_data['last_name'],
            updated_data['degree_program'], updated_data['gender'], updated_data['batch'],
            student_no
        )

        rows_affected = execute_query(update_query, params)
        if rows_affected > 0:
            messagebox.showinfo("Success", "Personal information updated successfully!")
            self.app.show_view_personal_info_page() # Go back to view the updated info
        else:
            messagebox.showerror("Error", "Failed to update personal information.")


# ViewRegisteredOrgsPage Class --------------------------------------------------
class ViewRegisteredOrgsPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Registered Organizations")
        self.create_treeview()
        self.load_registered_organizations()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.content_frame, columns=("Org ID", "Org Name", "Status"), show="headings", selectmode="browse")
        self.tree.heading("Org ID", text="Org ID")
        self.tree.heading("Org Name", text="Org Name")
        self.tree.heading("Status", text="Status")

        self.tree.column("Org ID", width=100, anchor=tk.CENTER)
        self.tree.column("Org Name", width=250, anchor=tk.W)
        self.tree.column("Status", width=150, anchor=tk.CENTER)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_registered_organizations(self):
        # Access CURRENT_USER_ID via self.app.current_user_id
        student_no = self.app.current_user_id
        if not student_no:
            messagebox.showerror("Error", "No student ID found for current user.")
            self.app.show_member_menu()
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
        SELECT o.org_id, o.org_name, mo.status
        FROM organization o
        JOIN member_of mo ON o.org_id = mo.org_id
        WHERE mo.student_no = %s
        """
        organizations = fetch_all(query, (student_no,))

        if organizations:
            for org in organizations:
                self.tree.insert("", tk.END, values=(org['org_id'], org['org_name'], org['status']))
        else:
            ttk.Label(self.content_frame, text="Not registered to any organization.", font=("Arial", 12)).pack(pady=20)

# ViewMembersUnpaidFeesPage Class --------------------------------------------------
class ViewMembersUnpaidFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Unpaid Fees")
        self.create_treeview()
        self.load_unpaid_fees()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.content_frame, columns=("Org Name", "Fee Name", "Amount", "Due Date"), show="headings", selectmode="browse")
        self.tree.heading("Org Name", text="Organization Name")
        self.tree.heading("Fee Name", text="Fee Name")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Due Date", text="Due Date")

        self.tree.column("Org Name", width=200, anchor=tk.W)
        self.tree.column("Fee Name", width=150, anchor=tk.W)
        self.tree.column("Amount", width=100, anchor=tk.CENTER)
        self.tree.column("Due Date", width=120, anchor=tk.CENTER)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_unpaid_fees(self):
        # Access CURRENT_USER_ID via self.app.current_user_id
        student_no = self.app.current_user_id
        if not student_no:
            messagebox.showerror("Error", "No student ID found for current user.")
            self.app.show_member_menu()
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
        SELECT o.org_name, f.fee_name, f.amount, f.due_date
        FROM fee_record fr
        JOIN fee f ON fr.fee_id = f.fee_id
        JOIN organization o ON f.org_id = o.org_id
        WHERE fr.student_no = %s AND fr.payment_status = 'unpaid'
        """
        unpaid_fees = fetch_all(query, (student_no,))

        if unpaid_fees:
            for fee in unpaid_fees:
                self.tree.insert("", tk.END, values=(fee['org_name'], fee['fee_name'], fee['amount'], fee['due_date']))
        else:
            ttk.Label(self.content_frame, text="You have no unpaid fees.", font=("Arial", 12)).pack(pady=20)