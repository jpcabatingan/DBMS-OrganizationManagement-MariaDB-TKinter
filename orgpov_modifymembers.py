import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD
import re
from datetime import datetime, timedelta # Import datetime and timedelta for deadline calculation
import uuid # For generating unique receipt_no

from shared_variables import BasePage, fetch_one, fetch_all, execute_query

# ADD NEW ORG MEMBER ------------------------------------------------------------
class AddNewMemberPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, title_text="Add New Organization Member")
        self.app = app_instance
        self.create_widgets()

    def create_widgets(self):
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.content_frame, text="Add New Organization Member", font=("Arial", 18, BOLD), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        row_idx = 1
        labels = ["Student No.:", "Role:", "Status:", "Committee:", "Academic Year:", "Semester:", "Batch Membership:"]
        self.entries = {}
        self.dropdowns = {}

        for label_text in labels:
            tk.Label(self.content_frame, text=label_text, font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=row_idx, column=0, sticky="w", pady=(5, 0), padx=5)
            if label_text == "Student No.:":
                entry = ttk.Entry(self.content_frame, font=("Arial", 10))
                entry.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.entries['student_no'] = entry
            elif label_text == "Role:":
                role_values = ["Member", "President", "Vice President", "Secretary", "Treasurer", "Auditor", "EAC Chairperson", "SCC Chairperson", "MC Chairperson", "Finance Chairperson", "Secretariat Chairperson"]
                dropdown = ttk.Combobox(self.content_frame, values=role_values, state="readonly", font=("Arial", 10))
                dropdown.set("Member")
                dropdown.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.dropdowns['role'] = dropdown
            elif label_text == "Status:":
                status_values = ["Active", "Inactive", "On-Leave", "Alumni", "Disaffiliated"]
                dropdown = ttk.Combobox(self.content_frame, values=status_values, state="readonly", font=("Arial", 10))
                dropdown.set("Active")
                dropdown.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.dropdowns['status'] = dropdown
            elif label_text == "Committee:":
                committee_values = ["General", "Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership", "Logistics", "Publicity"]
                dropdown = ttk.Combobox(self.content_frame, values=committee_values, state="readonly", font=("Arial", 10))
                dropdown.set("General")
                dropdown.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.dropdowns['committee'] = dropdown
            elif label_text == "Academic Year:":
                entry = ttk.Entry(self.content_frame, font=("Arial", 10))
                entry.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.entries['academic_year'] = entry
            elif label_text == "Semester:":
                semester_values = ["First Semester", "Second Semester"]
                dropdown = ttk.Combobox(self.content_frame, values=semester_values, state="readonly", font=("Arial", 10))
                dropdown.set("First Semester")
                dropdown.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.dropdowns['semester'] = dropdown
            elif label_text == "Batch Membership:":
                entry = ttk.Entry(self.content_frame, font=("Arial", 10))
                entry.grid(row=row_idx, column=1, sticky="ew", pady=(5, 0), padx=5)
                self.entries['batch_membership'] = entry

            row_idx += 1

        ttk.Button(self.content_frame, text="Add Member", command=self.add_member).grid(row=row_idx, column=0, columnspan=2, pady=20)

    # add new member that serves the org
    def add_member(self):
        student_no = self.entries['student_no'].get().strip()
        role = self.dropdowns['role'].get().strip()
        status = self.dropdowns['status'].get().strip()
        committee = self.dropdowns['committee'].get().strip()
        academic_year = self.entries['academic_year'].get().strip()
        semester = self.dropdowns['semester'].get().strip()
        batch_membership = self.entries['batch_membership'].get().strip()

        if not all([student_no, role, status, committee, academic_year, semester, batch_membership]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        if not re.match(r"20\d{2}-\d{5}", student_no):
            messagebox.showerror("Validation Error", "Student number format is incorrect. Expected: 20XX-XXXXX")
            return

        if not re.match(r"^\d{4}-\d{4}$", academic_year):
            messagebox.showerror("Validation Error", "Academic Year must be in YYYY-YYYY format (e.g., 2023-2024).")
            return
        
        try:
            batch_membership_int = int(batch_membership)
        except ValueError:
            messagebox.showerror("Validation Error", "Batch Membership must be an integer (e.g., 2023).")
            return
        
        org_details = fetch_one("SELECT org_name FROM organization WHERE org_id = %s", (self.app.current_user_id,))
        if not org_details:
            messagebox.showerror("Database Error", "Organization not found for current user.")
            return
        org_name = org_details['org_name']

        member_exists = fetch_one("SELECT student_no FROM member WHERE student_no = %s", (student_no,))
        if not member_exists:
            messagebox.showerror("Error", "Student number not found. Please register the student first.")
            return

        membership_exists = fetch_one(
            "SELECT * FROM serves WHERE org_name = %s AND student_no = %s AND academic_year = %s AND semester = %s",
            (org_name, student_no, academic_year, semester)
        )
        if membership_exists:
            messagebox.showerror("Error", "This member is already registered for the specified Academic Year and Semester in this organization.")
            return

        try:
            insert_serves_query = """
            INSERT INTO serves (student_no, org_name, academic_year, semester, role, status, committee, batch_membership)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            rows_affected = execute_query(insert_serves_query, (student_no, org_name, academic_year, semester, role, status, committee, batch_membership_int))

            if rows_affected > 0:
                # --- ADDITION FOR MEMBERSHIP FEE ---
                membership_fee_amount = 250.00 # Ensure it's a decimal for DECIMAL(10,2)
                
                # Generate a unique receipt_no
                # Option 1: UUID (more robust for uniqueness)
                receipt_no = str(uuid.uuid4()) 
                
                # Option 2: Combination (can be prone to collision if many entries at same time, but readable)
                # receipt_no = f"{student_no}-{org_name[:5]}-{academic_year.replace('-', '')}-{semester[:3]}-{datetime.now().strftime('%f')}"
                # receipt_no = receipt_no[:50] # Truncate if too long for VARCHAR(50)

                # Set payment deadline (e.g., 30 days from now)
                payment_deadline = datetime.now() + timedelta(days=30)
                
                # Default payment status
                payment_status = "Unpaid" 

                # Check if a fee record already exists for this member, org, AY, and semester
                # This helps prevent duplicate fee entries for the same membership period
                fee_exists = fetch_one(
                    "SELECT receipt_no FROM fee WHERE student_no = %s AND org_name = %s AND academic_year = %s AND semester = %s",
                    (student_no, org_name, academic_year, semester)
                )

                if not fee_exists:
                    insert_fee_query = """
                    INSERT INTO fee (receipt_no, amount, payment_deadline, payment_status, student_no, org_name, academic_year, semester)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # Pass academic_year and semester to the fee table, assuming your 'fee' table is extended
                    # If your 'fee' table DOES NOT have academic_year and semester, remove them from the query and parameters
                    fee_rows_affected = execute_query(
                        insert_fee_query, 
                        (receipt_no, membership_fee_amount, payment_deadline.strftime('%Y-%m-%d'), payment_status, student_no, org_name, academic_year, semester)
                    )
                    
                    if fee_rows_affected > 0:
                        messagebox.showinfo("Success", "Member added to organization and membership fee automatically added!")
                    else:
                        messagebox.showwarning("Warning", "Member added, but failed to automatically add membership fee. Please add it manually.")
                else:
                     messagebox.showwarning("Warning", "Member added, but a membership fee for this period already exists. Skipping fee creation.")

                if status == 'Active':
                    execute_query("UPDATE organization SET no_of_members = no_of_members + 1 WHERE org_id = %s", (self.app.current_user_id,))
                
                # Clear fields after successful addition
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                for dropdown in self.dropdowns.values():
                    if dropdown == self.dropdowns['role']:
                        dropdown.set("Member")
                    elif dropdown == self.dropdowns['status']:
                        dropdown.set("Active")
                    elif dropdown == self.dropdowns['committee']:
                        dropdown.set("General")
                    elif dropdown == self.dropdowns['semester']:
                        dropdown.set("First Semester")
                self.entries['batch_membership'].delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to add member to organization.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")


# EDIT MEMBER'S MEMBERSHIP DETAILS ------------------------------------------------------------
class EditMembershipStatusPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, title_text="Edit Member Membership Status")
        self.app = app_instance
        self.member_data = None
        self.semester_memberships = []

        self.create_widgets()

    def create_widgets(self):
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0)
        self.content_frame.grid_columnconfigure(2, weight=1)

        self.left_panel = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.left_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)

        tk.Label(self.left_panel, text="Edit member", font=("Arial", 18, BOLD), bg="#f0f0f0", fg="black").grid(row=0, column=0, sticky="w", pady=(0, 20))

        tk.Label(self.left_panel, text="Student no.", font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.student_no_entry = ttk.Entry(self.left_panel, font=("Arial", 12))
        self.student_no_entry.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        tk.Label(self.left_panel, text="Format: 20XX-XXXXX", font=("Arial", 8), fg="grey", bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=(0, 10))

        load_member_button = tk.Button(self.left_panel, text="Load Member Info",
                                        bg="#446EE2", fg="white", font=("Arial", 10, BOLD), relief="flat",
                                        padx=10, pady=5, command=self.load_member_info)
        load_member_button.grid(row=4, column=0, sticky="w", pady=(10, 20))

        tk.Label(self.left_panel, text="Member Information", font=("Arial", 14, BOLD), bg="#f0f0f0", fg="black").grid(row=5, column=0, sticky="w", pady=(10, 10))

        self.member_info_labels = {}
        info_items = ["Student ID:", "First Name:", "Middle Name:", "Last Name:"]
        for i, item in enumerate(info_items):
            tk.Label(self.left_panel, text=item, font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=6 + i, column=0, sticky="w", padx=5, pady=(2, 0))
            label = tk.Label(self.left_panel, text="", font=("Arial", 10), bg="#f0f0f0")
            label.grid(row=6 + i, column=0, sticky="w", padx=100, pady=(2, 0))
            self.member_info_labels[item] = label

        self.serves_history_frame = tk.Frame(self.left_panel, bg="#f0f0f0")
        self.serves_history_frame.grid(row=10, column=0, sticky="ew", pady=(20, 0))
        self.serves_history_frame.grid_columnconfigure(0, weight=1)

        self.serves_history_labels = []

        separator = ttk.Separator(self.content_frame, orient='vertical')
        separator.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10, pady=10, rowspan=50)


        self.right_panel = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.right_panel.grid(row=0, column=2, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)

        edit_existing_button = tk.Button(self.right_panel, text="Edit existing membership status",
                                            bg="#FF9800", fg="white", font=("Arial", 10, BOLD), relief="flat",
                                            padx=10, pady=5, command=self.show_edit_section)
        edit_existing_button.grid(row=0, column=0, sticky="e", pady=(0, 20))


        tk.Label(self.right_panel, text="Academic Year", font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.academic_year_entry = ttk.Entry(self.right_panel, font=("Arial", 12))
        self.academic_year_entry.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        tk.Label(self.right_panel, text="Format: 20XX-20XX", font=("Arial", 8), fg="grey", bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=(0, 10))

        tk.Label(self.right_panel, text="Semester", font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=(10, 0))
        semester_values = ["First Semester", "Second Semester"]
        self.semester_dropdown_select = ttk.Combobox(self.right_panel, values=semester_values, state="readonly", font=("Arial", 12))
        self.semester_dropdown_select.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        self.semester_dropdown_select.set("First Semester")

        # ADDED BATCH MEMBERSHIP INPUT FIELD TO RIGHT PANEL
        tk.Label(self.right_panel, text="Batch Membership", font=("Arial", 10, BOLD), bg="#f0f0f0").grid(row=6, column=0, sticky="w", pady=(10, 0))
        self.batch_membership_entry = ttk.Entry(self.right_panel, font=("Arial", 12))
        self.batch_membership_entry.grid(row=7, column=0, sticky="ew", pady=(0, 10))
        tk.Label(self.right_panel, text="Format: 20XX", font=("Arial", 8), fg="grey", bg="#f0f0f0").grid(row=8, column=0, sticky="w", pady=(0, 10))


        add_new_semester_button = tk.Button(self.right_panel, text="+ Add new semester membership",
                                             bg="#FF9800", fg="white", font=("Arial", 10, BOLD), relief="flat",
                                             padx=10, pady=5, command=self.add_new_semester_membership)
        # Adjusted row for the button due to new Batch Membership field
        add_new_semester_button.grid(row=9, column=0, sticky="e", pady=(10, 40))

        # Adjusted row for update_section_frame due to new Batch Membership field
        self.update_section_frame = tk.Frame(self.right_panel, bg="#f0f0f0")
        self.update_section_frame.grid(row=10, column=0, sticky="ew", pady=(10, 0))
        self.update_section_frame.grid_columnconfigure(0, weight=1)
        self.update_section_frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.update_section_frame, text="Update Information for AY XXXX - XXXX nth Semester",
                 font=("Arial", 14, BOLD), bg="#f0f0f0", fg="black").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        self.new_role_var = tk.StringVar(self.update_section_frame)
        self.new_status_var = tk.StringVar(self.update_section_frame)
        self.new_committee_var = tk.StringVar(self.update_section_frame)

        self.new_role_dropdown = ttk.Combobox(self.update_section_frame, textvariable=self.new_role_var,
                                                values=["Member", "President", "Vice President", "Secretary", "Treasurer", "Auditor", "EAC Chairperson", "SCC Chairperson", "MC Chairperson", "Finance Chairperson", "Secretariat Chairperson"],
                                                state="readonly", font=("Arial", 12))
        self.new_role_dropdown.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.new_role_var.set("<New Role>")

        self.new_status_dropdown = ttk.Combobox(self.update_section_frame, textvariable=self.new_status_var,
                                                values=["Active", "Inactive", "On-Leave", "Alumni", "Disaffiliated"],
                                                state="readonly", font=("Arial", 12))
        self.new_status_dropdown.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.new_status_var.set("<New Status>")

        self.new_committee_dropdown = ttk.Combobox(self.update_section_frame, textvariable=self.new_committee_var,
                                                    values=["General", "Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership", "Logistics", "Publicity"],
                                                    state="readonly", font=("Arial", 12))
        self.new_committee_dropdown.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.new_committee_var.set("<New Committee>")

        save_edits_button = tk.Button(self.update_section_frame, text="Save Edits",
                                        bg="#446EE2", fg="white", font=("Arial", 10, BOLD), relief="flat",
                                        padx=10, pady=5, command=self.save_edits)
        save_edits_button.grid(row=4, column=0, columnspan=2, sticky="w", pady=(20, 0))

        self.hide_update_section()

    # get member details
    def load_member_info(self):
        student_no = self.student_no_entry.get().strip()
        if not student_no:
            messagebox.showerror("Error", "Please enter a Student Number.")
            return
        
        if not re.match(r"20\d{2}-\d{5}", student_no):
            messagebox.showerror("Validation Error", "Student number format is incorrect. Expected: 20XX-XXXXX")
            return

        member = fetch_one("SELECT student_no, first_name, middle_name, last_name FROM member WHERE student_no = %s", (student_no,))

        if member:
            self.member_data = member
            self.member_info_labels["Student ID:"].config(text=member['student_no'])
            self.member_info_labels["First Name:"].config(text=member['first_name'])
            self.member_info_labels["Middle Name:"].config(text=member['middle_name'] if member['middle_name'] else "N/A")
            self.member_info_labels["Last Name:"].config(text=member['last_name'])

            org_details = fetch_one("SELECT org_name FROM organization WHERE org_id = %s", (self.app.current_user_id,))
            if not org_details:
                messagebox.showerror("Database Error", "Organization not found for current user.")
                self.clear_member_info()
                return
            current_org_name = org_details['org_name']

            self.semester_memberships = fetch_all(
                "SELECT academic_year, semester, role, status, committee, batch_membership FROM serves WHERE org_name = %s AND student_no = %s ORDER BY academic_year DESC, FIELD(semester, 'First Semester', 'Second Semester')",
                (current_org_name, student_no)
            )
            self.display_serves_history()
            self.show_update_section("Update Information for AY XXXX - XXXX nth Semester")

        else:
            self.clear_member_info()
            messagebox.showerror("Error", "Member not found.")

    # display member's history as a member of the org
    def display_serves_history(self):
        for label in self.serves_history_labels:
            label.destroy()
        self.serves_history_labels.clear()

        current_display_row = 0
        if self.semester_memberships:
            for i, membership in enumerate(self.semester_memberships):
                ay_semester_text = f"AY {membership['academic_year']} {membership['semester']}"
                ay_label = tk.Label(self.serves_history_frame, text=ay_semester_text, font=("Arial", 10, BOLD), bg="#f0f0f0")
                ay_label.grid(row=current_display_row, column=0, sticky="w", pady=(10, 0))
                self.serves_history_labels.append(ay_label)
                current_display_row += 1

                role_label = tk.Label(self.serves_history_frame, text=f"Role: {membership['role']}", font=("Arial", 10), bg="#f0f0f0")
                role_label.grid(row=current_display_row, column=0, sticky="w", padx=10)
                self.serves_history_labels.append(role_label)
                current_display_row += 1

                status_label = tk.Label(self.serves_history_frame, text=f"Status: {membership['status']}", font=("Arial", 10), bg="#f0f0f0")
                status_label.grid(row=current_display_row, column=0, sticky="w", padx=10)
                self.serves_history_labels.append(status_label)
                current_display_row += 1

                committee_label = tk.Label(self.serves_history_frame, text=f"Committee: {membership['committee']}", font=("Arial", 10), bg="#f0f0f0")
                committee_label.grid(row=current_display_row, column=0, sticky="w", padx=10)
                self.serves_history_labels.append(committee_label)
                current_display_row += 1
                
                batch_membership_label = tk.Label(self.serves_history_frame, text=f"Batch Membership: {membership['batch_membership']}", font=("Arial", 10), bg="#f0f0f0")
                batch_membership_label.grid(row=current_display_row, column=0, sticky="w", padx=10)
                self.serves_history_labels.append(batch_membership_label)
                current_display_row += 1

                current_display_row += 1

        else:
            no_history_label = tk.Label(self.serves_history_frame, text="No membership history found for this organization.", font=("Arial", 10), bg="#f0f0f0")
            no_history_label.grid(row=0, column=0, sticky="w", pady=(10,0))
            self.serves_history_labels.append(no_history_label)

    # clear membership details
    def clear_member_info(self):
        self.member_data = None
        for label in self.member_info_labels.values():
            label.config(text="")
        for label in self.serves_history_labels:
            label.destroy()
        self.serves_history_labels.clear()
        
        self.new_role_var.set("<New Role>")
        self.new_status_var.set("<New Status>")
        self.new_committee_var.set("<New Committee>")
        
        self.hide_update_section()
        self.batch_membership_entry.config(state='normal') 
        self.batch_membership_entry.delete(0, tk.END) 

    # edit membership status for a given AY and Semester
    def show_edit_section(self):
        if not self.member_data:
            messagebox.showerror("Error", "Please load member info first.")
            return

        academic_year_input = self.academic_year_entry.get().strip()
        semester_input = self.semester_dropdown_select.get().strip()

        if not academic_year_input or not semester_input:
            messagebox.showerror("Input Error", "Please enter/select Academic Year and Semester to edit.")
            return
        
        if not re.match(r"^\d{4}-\d{4}$", academic_year_input):
            messagebox.showerror("Validation Error", "Academic Year format is incorrect. Expected: 20XX-XXXX")
            return
        
        org_details = fetch_one("SELECT org_name FROM organization WHERE org_id = %s", (self.app.current_user_id,))
        if not org_details:
            messagebox.showerror("Database Error", "Organization not found for current user.")
            return
        current_org_name = org_details['org_name']

        selected_membership = fetch_one(
            "SELECT role, status, committee, batch_membership FROM serves WHERE org_name = %s AND student_no = %s AND academic_year = %s AND semester = %s",
            (current_org_name, self.member_data['student_no'], academic_year_input, semester_input)
        )

        if selected_membership:
            self.new_role_var.set(selected_membership['role'])
            self.new_status_var.set(selected_membership['status'])
            self.new_committee_var.set(selected_membership['committee'])
            self.batch_membership_entry.delete(0, tk.END)
            self.batch_membership_entry.insert(0, str(selected_membership['batch_membership']))
            self.batch_membership_entry.config(state='readonly') # Keep batch_membership read-only for existing records
            
            self.show_update_section(f"Update Information for AY {academic_year_input} {semester_input}")
            self.editing_academic_year = academic_year_input
            self.editing_semester = semester_input
            self.is_adding_new = False
        else:
            messagebox.showerror("Error", "No membership found for the specified Academic Year and Semester in this organization.")
            self.hide_update_section()
            self.batch_membership_entry.config(state='normal') 
            self.batch_membership_entry.delete(0, tk.END)

    # renew membership / add a new semester of membership
    def add_new_semester_membership(self):
        if not self.member_data:
            messagebox.showerror("Error", "Please load member info first.")
            return

        academic_year_input = self.academic_year_entry.get().strip()
        semester_input = self.semester_dropdown_select.get().strip()
        batch_membership_input = self.batch_membership_entry.get().strip()

        if not academic_year_input or not semester_input or not batch_membership_input:
            messagebox.showerror("Input Error", "Please enter/select Academic Year, Semester, and Batch Membership for the new membership.")
            return
        
        if not re.match(r"^\d{4}-\d{4}$", academic_year_input):
            messagebox.showerror("Validation Error", "Academic Year format is incorrect. Expected: 20XX-XXXX")
            return
        
        try:
            batch_membership_int = int(batch_membership_input)
        except ValueError:
            messagebox.showerror("Validation Error", "Batch Membership must be an integer (e.g., 2023).")
            return

        org_details = fetch_one("SELECT org_name FROM organization WHERE org_id = %s", (self.app.current_user_id,))
        if not org_details:
            messagebox.showerror("Database Error", "Organization not found for current user.")
            return
        current_org_name = org_details['org_name']

        existing_membership = fetch_one(
            "SELECT * FROM serves WHERE org_name = %s AND student_no = %s AND academic_year = %s AND semester = %s",
            (current_org_name, self.member_data['student_no'], academic_year_input, semester_input)
        )

        if existing_membership:
            messagebox.showerror("Error", "Membership for this Academic Year and Semester already exists. Use 'Edit existing' if you want to modify it.")
            self.show_edit_section()
            return
        
        self.new_role_var.set("Member")
        self.new_status_var.set("Active")
        self.new_committee_var.set("General")
        
        self.show_update_section(f"Add New Membership for AY {academic_year_input} {semester_input} (Batch: {batch_membership_input})")
        
        self.editing_academic_year = academic_year_input
        self.editing_semester = semester_input
        self.editing_batch_membership = batch_membership_int 
        self.is_adding_new = True
        self.batch_membership_entry.config(state='normal') # Enable batch membership for new entry

    # save edits
    def save_edits(self):
        if not self.member_data:
            messagebox.showerror("Error", "No member loaded to save edits for.")
            return
        
        student_no = self.member_data['student_no']
        new_role = self.new_role_var.get()
        new_status = self.new_status_var.get()
        new_committee = self.new_committee_var.get()

        if new_role == "<New Role>" or new_status == "<New Status>" or new_committee == "<New Committee>":
            messagebox.showerror("Input Error", "Please select valid Role, Status, and Committee.")
            return

        if not hasattr(self, 'editing_academic_year'):
            messagebox.showerror("Error", "Please select an existing membership or specify a new one first.")
            return

        academic_year = self.editing_academic_year
        semester = self.editing_semester
        batch_membership = getattr(self, 'editing_batch_membership', None) 

        org_details = fetch_one("SELECT org_name FROM organization WHERE org_id = %s", (self.app.current_user_id,))
        if not org_details:
            messagebox.showerror("Database Error", "Organization not found for current user.")
            return
        current_org_name = org_details['org_name']

        if getattr(self, 'is_adding_new', False):
            if batch_membership is None:
                messagebox.showerror("Input Error", "Batch Membership is required for new membership.")
                return

            insert_serves_query = """
            INSERT INTO serves (student_no, org_name, academic_year, semester, role, status, committee, batch_membership)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            rows_affected = execute_query(insert_serves_query, (student_no, current_org_name, academic_year, semester, new_role, new_status, new_committee, batch_membership))
            
            if rows_affected > 0:
                # --- ADDITION FOR MEMBERSHIP FEE FOR NEW SEMESTER MEMBERSHIP ---
                membership_fee_amount = 250.00
                
                # Generate a unique receipt_no
                receipt_no = str(uuid.uuid4())
                
                # Set payment deadline (e.g., 30 days from now)
                payment_deadline = datetime.now() + timedelta(days=30)
                
                # Default payment status
                payment_status = "Unpaid"

                # Check if fee already exists to prevent duplicates for the same membership period
                # NOTE: Your 'fee' table does not have academic_year and semester columns.
                # The check below would be invalid for your current 'fee' schema.
                # If you want to associate fees with specific semesters, you *must* add
                # academic_year and semester columns to your 'fee' table.
                
                # For your current 'fee' table schema, this check is only for student_no and org_name
                fee_exists = fetch_one(
                    "SELECT receipt_no FROM fee WHERE student_no = %s AND org_name = %s",
                    (student_no, current_org_name)
                )

                # IMPORTANT: If your 'fee' table truly does not have academic_year and semester,
                # then a student will only have ONE fee entry per organization regardless of semester.
                # This might not be your desired behavior for "membership fees per semester".
                # If you need per-semester fees, your `fee` table needs to be altered.
                # Assuming for now that you want to add a fee for *each* new semester membership,
                # we'll use the combined student_no, org_name, academic_year, semester for uniqueness.
                # This means your `fee` table *needs* `academic_year` and `semester` columns.

                # ***** RECOMMENDED DATABASE SCHEMA CHANGE: *****
                # ALTER TABLE fee
                # ADD COLUMN academic_year VARCHAR(10),
                # ADD COLUMN semester VARCHAR(20);
                # ALTER TABLE fee ADD UNIQUE (student_no, org_name, academic_year, semester);
                # **********************************************

                # If you proceed without the schema change, the 'fee_exists' check should be simpler:
                # fee_exists = fetch_one("SELECT receipt_no FROM fee WHERE student_no = %s AND org_name = %s", (student_no, current_org_name))
                # This would mean a student only pays one fee per organization, not per semester.

                # Assuming you WILL add academic_year and semester to your `fee` table for per-semester fees:
                fee_exists_per_semester = fetch_one(
                    "SELECT receipt_no FROM fee WHERE student_no = %s AND org_name = %s AND academic_year = %s AND semester = %s",
                    (student_no, current_org_name, academic_year, semester)
                )

                if not fee_exists_per_semester: # Use the more specific check
                    insert_fee_query = """
                    INSERT INTO fee (receipt_no, amount, payment_deadline, payment_status, student_no, org_name, academic_year, semester)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    fee_rows_affected = execute_query(insert_fee_query, (receipt_no, membership_fee_amount, payment_deadline.strftime('%Y-%m-%d'), payment_status, student_no, current_org_name, academic_year, semester))
                    
                    if fee_rows_affected > 0:
                        messagebox.showinfo("Success", f"New membership for AY {academic_year} {semester} added and fee automatically added!")
                    else:
                        messagebox.showwarning("Warning", f"New membership for AY {academic_year} {semester} added, but failed to automatically add membership fee. Please add it manually.")
                else:
                    messagebox.showwarning("Warning", f"New membership for AY {academic_year} {semester} added, but a membership fee for this period already exists. Skipping fee creation.")
                
                if new_status == 'Active':
                    execute_query("UPDATE organization SET no_of_members = no_of_members + 1 WHERE org_id = %s", (self.app.current_user_id,))
                
                self.load_member_info() # Reload to show updated history
                self.is_adding_new = False
                self.batch_membership_entry.config(state='normal') 
                self.batch_membership_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to add new membership.")
        else:
            old_membership_status = fetch_one(
                "SELECT status FROM serves WHERE org_name = %s AND student_no = %s AND academic_year = %s AND semester = %s",
                (current_org_name, student_no, academic_year, semester)
            )
            old_status = old_membership_status['status'] if old_membership_status else None

            update_query = """
            UPDATE serves SET role = %s, status = %s, committee = %s
            WHERE org_name = %s AND student_no = %s AND academic_year = %s AND semester = %s
            """
            rows_affected = execute_query(update_query, (new_role, new_status, new_committee,
                                                          current_org_name, student_no, academic_year, semester))

            if rows_affected > 0:
                if old_status != new_status:
                    if new_status == 'Active' and old_status != 'Active':
                        execute_query("UPDATE organization SET no_of_members = no_of_members + 1 WHERE org_id = %s", (self.app.current_user_id,))
                    elif new_status != 'Active' and old_status == 'Active':
                        execute_query("UPDATE organization SET no_of_members = no_of_members - 1 WHERE org_id = %s", (self.app.current_user_id,))

                messagebox.showinfo("Success", f"Membership for AY {academic_year} {semester} updated successfully!")
                self.load_member_info() # Reload to show updated history
                self.batch_membership_entry.config(state='normal') 
                self.batch_membership_entry.delete(0, tk.END) 
            else:
                messagebox.showerror("Error", "No changes made or failed to update membership.")


    def show_update_section(self, heading_text):
        self.update_section_frame.grid_slaves(row=0, column=0)[0].config(text=heading_text)
        self.update_section_frame.grid()

    def hide_update_section(self):
        self.update_section_frame.grid_forget()