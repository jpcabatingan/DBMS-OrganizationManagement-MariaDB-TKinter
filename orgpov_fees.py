from shared_variables import (
    BasePage, cursor, fetch_one, execute_query, fetch_all
)

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

# Organization POV - View Fees  ---------------------------------------
class OrganizationFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Manage Organization Finances")
        self.app = app_instance  
        self.sort_direction = {"amount": False}
        self.current_sort_column = None
        self.members = []
        self.back_button.grid_forget()
        self.back_button.destroy()

        self.create_widgets()

        self.load_payment_data()

    # Creates all UI elements
    def create_widgets(self):
        main_frame = self.content_frame

        summary_frame = ttk.LabelFrame(main_frame, text="Payment Summary", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(summary_frame, text="Total Paid:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.total_paid_label = ttk.Label(summary_frame, text="₱0", font=('Arial', 10, 'bold'))
        self.total_paid_label.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(summary_frame, text="Total Unpaid:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.total_unpaid_label = ttk.Label(summary_frame, text="₱0", font=('Arial', 10, 'bold'))
        self.total_unpaid_label.grid(row=0, column=3, padx=5, sticky=tk.W)

        ttk.Label(summary_frame, text="Member with Highest Debt:").grid(row=0, column=4, padx=5, sticky=tk.W)
        self.highest_debt_label = ttk.Label(summary_frame, text="None", font=('Arial', 10, 'bold'))
        self.highest_debt_label.grid(row=0, column=5, padx=5, sticky=tk.W)

        button_frame = ttk.Frame(summary_frame)
        button_frame.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(10, 0))

        ttk.Button(button_frame, text="Top 5 Highest Debt", command=self.view_top_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Payment Status", command=self.update_fee_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=5)

        filter_frame = ttk.LabelFrame(main_frame, text="Filter Options", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="As of Date:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
        self.date_entry.grid(row=2, column=1, padx=5, sticky=tk.W)
        ttk.Button(filter_frame, text="Apply Date", command=self.apply_date_filter).grid(row=2, column=2, padx=5)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.status_var = tk.StringVar(value="all")
        status_options = ["all", "paid", "unpaid", "late", "late paid"]
        ttk.OptionMenu(filter_frame, self.status_var, "all", *status_options, 
                      command=lambda _: self.filter_payments()).grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Search Name:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=5, sticky=tk.W)
        search_entry.bind("<KeyRelease>", lambda _: self.filter_payments())

        ttk.Label(filter_frame, text="Academic Year:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.year_var = tk.StringVar(value="All")
        self.year_combobox = ttk.Combobox(filter_frame, textvariable=self.year_var)
        self.year_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Semester:").grid(row=1, column=2, padx=5, sticky=tk.W)
        self.semester_var = tk.StringVar(value="All")
        self.semester_combobox = ttk.Combobox(filter_frame, textvariable=self.semester_var, 
                                            values=["All", "First Semester", "Second Semester"])
        self.semester_combobox.grid(row=1, column=3, padx=5, sticky=tk.W)

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=1, column=4, padx=5)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=(
            "receipt_no", 
            "name", 
            "amount", 
            "payment_status", 
            "payment_deadline",
            "date_paid",
            "student_no",
            "org_name",
            "academic_year",
            "semester"
        ), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        columns = {
            "receipt_no": {"text": "Receipt No", "width": 80, "anchor": tk.CENTER},
            "name": {"text": "Member Name", "width": 150, "anchor": tk.W},
            "amount": {"text": "Amount", "width": 80, "anchor": tk.CENTER},
            "payment_status": {"text": "Status", "width": 80, "anchor": tk.CENTER},
            "payment_deadline": {"text": "Due Date", "width": 100, "anchor": tk.CENTER},
            "date_paid": {"text": "Date Paid", "width": 100, "anchor": tk.CENTER},
            "student_no": {"text": "Student No", "width": 100, "anchor": tk.CENTER},
            "org_name": {"text": "Org Name", "width": 120, "anchor": tk.W},
            "academic_year": {"text": "Academic Year", "width": 120, "anchor": tk.CENTER},
            "semester": {"text": "Semester", "width": 100, "anchor": tk.CENTER}
        }

        for col, config in columns.items():
            self.tree.heading(col, text=config["text"], command=lambda c=col: self.current_sort_column(c))
            self.tree.column(col, width=config["width"], anchor=config["anchor"])
            
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

    # Loads payment records from database
    def load_payment_data(self):
        try:
            available_years = self.get_available_years()
            self.year_combobox['values'] = available_years
            
            academic_year = self.year_var.get()
            semester = self.semester_var.get()
            
            base_query = """
                SELECT 
                    f.receipt_no AS id,
                    CONCAT(m.first_name, ' ', m.last_name) AS name,
                    f.amount,
                    f.payment_status,
                    f.payment_deadline AS due_date,
                    f.date_paid,
                    f.student_no,
                    f.org_name,
                    s.academic_year,
                    s.semester
                FROM fee f
                JOIN member m ON f.student_no = m.student_no
                JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
                WHERE f.org_name = %s
            """
            
            params = [self.app.org_name]
            
            if academic_year != "All":
                base_query += " AND s.academic_year = %s"
                params.append(academic_year)
            
            if semester != "All":
                base_query += " AND s.semester = %s"
                params.append(semester)
            
            self.members = fetch_all(base_query, tuple(params))
                        
            self.filter_payments()
            self.status_bar.config(text=f"Loaded {len(self.members)} payments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payments: {str(e)}")
            self.status_bar.config(text="Error loading payments")
            self.members = []

    # Get distinct academic years from database
    def get_available_years(self):
        try:
            query = "SELECT DISTINCT academic_year FROM serves WHERE org_name = %s ORDER BY academic_year DESC"
            years = fetch_all(query, (self.app.org_name,))
            return ["All"] + [year["academic_year"] for year in years]
        except Exception as e:
            print(f"Error fetching years: {e}")
            return ["All"]
    
    # Reloads all data from database
    def refresh_data(self):
        try:
            available_years = self.get_available_years()
            self.year_combobox['values'] = available_years
            if "All" not in available_years:
                available_years.insert(0, "All")
            self.load_payment_data()
            self.status_bar.config(text="Data refreshed")
        except Exception as e:
            messagebox.showerror("Error", f"Refresh failed: {str(e)}")
    
    # Reloads data with current filters
    def apply_filters(self):
        self.load_payment_data()
        self.update_totals()

    # Applies all active filters to payment data
    def filter_payments(self):
        status_filter = self.status_var.get().lower()
        search_term = self.search_var.get().lower()
        year_filter = self.year_var.get()
        semester_filter = self.semester_var.get()

        self.tree.delete(*self.tree.get_children())

        for member in self.members:
            try:
                actual_status = self.determine_payment_status(member)
                
                status_match = (status_filter == "all") or (actual_status == status_filter)
                name_match = search_term in member["name"].lower()
                year_match = (year_filter == "All") or (member["academic_year"] == year_filter)
                semester_match = (semester_filter == "All") or (member["semester"] == semester_filter)
                
                if status_match and name_match and year_match and semester_match:
                    due_date = member["due_date"].strftime("%Y-%m-%d") if member["due_date"] else ""
                    date_paid = member["date_paid"].strftime("%Y-%m-%d") if member["date_paid"] else ""
                    
                    self.tree.insert("", tk.END, values=(
                        member["id"],
                        member["name"],
                        f"₱{float(member['amount']):,.2f}",
                        actual_status.capitalize(),
                        due_date,
                        date_paid,
                        member["student_no"],
                        member["org_name"],
                        member["academic_year"],
                        member["semester"]
                    ))
            except Exception as e:
                print(f"Error processing member data: {e}")
                continue

        self.update_totals()
        self.status_bar.config(text=f"Showing {len(self.tree.get_children())} records")

    # Calculates actual payment status
    def determine_payment_status(self, member):
        if member["date_paid"]:
            due_date = member["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            
            date_paid = member["date_paid"]
            if isinstance(date_paid, str):
                date_paid = datetime.strptime(date_paid, "%Y-%m-%d").date()
            
            if date_paid > due_date:
                return "late paid"
            return "paid"
        else:
            due_date = member["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            
            if due_date < date.today():
                return "late"
            return "unpaid"
    
    # Calculate total paid and unpaid
    def update_totals(self):
        try:
            total_paid = 0
            total_unpaid = 0
            unpaid_members = []
            
            tree_items = self.tree.get_children()
            
            if tree_items:
                for item in tree_items:
                    values = self.tree.item(item)['values']
                    amount = float(values[2].replace('₱', '').replace(',', ''))
                    status = values[3].lower()
                    
                    if status in ['paid', 'late paid']:
                        total_paid += amount
                    else:
                        total_unpaid += amount
                        unpaid_members.append({
                            'name': values[1],
                            'amount': amount
                        })
            else:
                for member in self.members:
                    try:
                        status = self.determine_payment_status(member)
                        amount = float(member["amount"])
                        
                        if status in ['paid', 'late paid']:
                            total_paid += amount
                        else:
                            total_unpaid += amount
                            unpaid_members.append({
                                'name': member["name"],
                                'amount': amount
                            })
                    except Exception as e:
                        print(f"Error processing member data for totals: {e}")
                        continue
            
            self.total_paid_label.config(text=f"₱{total_paid:,.2f} (Paid)")
            self.total_unpaid_label.config(text=f"₱{total_unpaid:,.2f} (Unpaid)")
            
            if unpaid_members:
                highest_debt = max(unpaid_members, key=lambda x: x["amount"])
                self.highest_debt_label.config(text=f"{highest_debt['name']} (₱{highest_debt['amount']:,.2f})")
            else:
                self.highest_debt_label.config(text="None")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating totals: {str(e)}")
            self.total_paid_label.config(text="₱0")
            self.total_unpaid_label.config(text="₱0")
            self.highest_debt_label.config(text="None")

    # Displays top 5 highest debts
    def view_top_debt(self):
        try:
            unpaid_members = []
            for member in self.members:
                try:
                    status = self.determine_payment_status(member)
                    if status in ['unpaid', 'late']:
                        unpaid_members.append(member)
                except Exception as e:
                    print(f"Error processing member data: {e}")
                    continue
            
            top_debtors = sorted(unpaid_members, key=lambda x: float(x["amount"]), reverse=True)[:5]
            
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for member in top_debtors:
                due_date = member["due_date"].strftime("%Y-%m-%d") if member["due_date"] else ""
                date_paid = member["date_paid"].strftime("%Y-%m-%d") if member["date_paid"] else ""
                status = self.determine_payment_status(member)
                
                self.tree.insert("", tk.END, values=(
                    member["id"],
                    member["name"],
                    f"₱{float(member['amount']):,.2f}",
                    status.capitalize(),
                    due_date,
                    date_paid,
                    member["student_no"],
                    member["org_name"],
                    member["academic_year"],
                    member["semester"]
                ))
                
            self.update_totals()
            self.status_bar.config(text=f"Showing top 5 highest debts (Total: {len(top_debtors)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show top debts: {str(e)}")
            self.status_bar.config(text="Error showing top debts")

    # Marks selected payment as paid
    def update_fee_status(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a payment record to update")
            return
            
        try:
            item_data = self.tree.item(selected_item[0])
            receipt_no = item_data['values'][0]
            current_status = item_data['values'][3].lower()
            due_date_str = item_data['values'][4]  
            amount = item_data['values'][2]  

            if current_status not in ['unpaid', 'late']:
                messagebox.showwarning("Invalid Action", 
                                    "Only unpaid can be updated.\n"
                                    "This payment was already paid.")
                return
                
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            today = date.today()
            
            is_late = today > due_date
            new_status = 'late paid' if is_late else 'paid'
            
            confirm_msg = f"Mark payment {receipt_no} as paid?\nAmount: {amount}"
            if is_late:
                confirm_msg += f"\n\nNote: This payment is {abs((today - due_date).days)} days late"
                
            confirm = messagebox.askyesno("Confirm Payment", confirm_msg)
            if not confirm:
                return
                
            query = """
                UPDATE fee 
                SET payment_status = %s, 
                    date_paid = CURDATE() 
                WHERE receipt_no = %s
            """
            execute_query(query, (new_status, receipt_no))
            
            messagebox.showinfo("Success", f"Payment {receipt_no} marked as {new_status.replace('_', ' ').title()}")
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update payment status: {str(e)}")
            
    # Apply calculation of totals as of a specific date
    def apply_date_filter(self):
        date_str = self.date_var.get()
        if not date_str:
            messagebox.showwarning("Missing Date", "Please enter a date in YYYY-MM-DD format")
            return
        
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            self.calculate_totals_as_of_date(filter_date)
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format")

    # Calculates totals as of a specific date
    def calculate_totals_as_of_date(self, target_date):
        try:
            year_filter = self.year_var.get()
            semester_filter = self.semester_var.get()
            
            base_query = """
                SELECT 
                    SUM(CASE WHEN f.date_paid IS NOT NULL AND f.date_paid <= %s THEN f.amount ELSE 0 END) AS total_paid,
                    SUM(CASE WHEN (f.date_paid IS NULL OR f.date_paid > %s) AND f.payment_deadline <= %s THEN f.amount ELSE 0 END) AS total_unpaid
                FROM fee f
                JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
                WHERE f.org_name = %s
            """
            
            params = [target_date, target_date, target_date, self.app.org_name]
            
            if year_filter != "All":
                base_query += " AND s.academic_year = %s"
                params.append(year_filter)
            
            if semester_filter != "All":
                base_query += " AND s.semester = %s"
                params.append(semester_filter)
                
            result = fetch_one(base_query, tuple(params))
            
            total_paid = float(result["total_paid"] or 0)
            total_unpaid = float(result["total_unpaid"] or 0)
            
            self.total_paid_label.config(text=f"₱{total_paid:,.2f} (Paid)")
            self.total_unpaid_label.config(text=f"₱{total_unpaid:,.2f} (Unpaid)")
            
            debt_query = """
                SELECT 
                    CONCAT(m.first_name, ' ', m.last_name) AS name,
                    f.amount
                FROM fee f
                JOIN member m ON f.student_no = m.student_no
                JOIN serves s ON f.student_no = s.student_no AND f.org_name = s.org_name
                WHERE f.org_name = %s
                AND (f.date_paid IS NULL OR f.date_paid > %s)
                AND f.payment_deadline <= %s
            """
            
            debt_params = [self.app.org_name, target_date, target_date]
            
            if year_filter != "All":
                debt_query += " AND s.academic_year = %s"
                debt_params.append(year_filter)
            
            if semester_filter != "All":
                debt_query += " AND s.semester = %s"
                debt_params.append(semester_filter)
                
            debt_query += " ORDER BY f.amount DESC LIMIT 1"
            
            highest_debt = fetch_one(debt_query, tuple(debt_params))
            
            if highest_debt:
                self.highest_debt_label.config(text=f"{highest_debt['name']} (₱{float(highest_debt['amount']):,.2f})")
            else:
                self.highest_debt_label.config(text="None")
                
            self.status_bar.config(text=f"Showing totals as of {target_date}")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating date-based totals: {str(e)}")
            self.total_paid_label.config(text="₱0")
            self.total_unpaid_label.config(text="₱0")
            self.highest_debt_label.config(text="None")