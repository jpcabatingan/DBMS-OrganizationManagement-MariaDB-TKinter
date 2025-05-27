from shared_variables import (
    BasePage, cursor, fetch_one, execute_query, fetch_all
)

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD
from datetime import date, datetime

class OrganizationFeesPage(BasePage):
    def __init__(self, master, app_instance):
        super().__init__(master, app_instance, "Manage Organization Finances")
        self.app = app_instance  # Store the app instance
        self.sort_direction = {"amount": False}
        self.current_sort_column = None
        self.members = []
        self.back_button.grid_forget()
        self.back_button.destroy()
        
        # Initialize widgets first
        self.create_widgets()
        
        # Then load data
        self.load_payment_data()

    def get_current_academic_period(self):
        """Get current academic year and semester"""
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        if 8 <= current_month <= 12:
            academic_year = f"{current_year}-{current_year + 1}"
            semester = "First Semester"
        elif 1 <= current_month <= 5:
            academic_year = f"{current_year - 1}-{current_year}"
            semester = "Second Semester"
        else:
            academic_year = f"{current_year - 1}-{current_year}"
            semester = "Midyear"

        return academic_year, semester

    def create_widgets(self):
        main_frame = self.content_frame

        # Summary frame
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

        # Action buttons
        button_frame = ttk.Frame(summary_frame)
        button_frame.grid(row=1, column=0, columnspan=6, sticky=tk.W, pady=(10, 0))

        ttk.Button(button_frame, text="Top 5 Highest Debt", command=self.view_top_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Payment Status", command=self.update_fee_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=5)

        # Filter controls frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filter Options", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="As of Date:").grid(row=2, column=0, padx=5, sticky=tk.W)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
        self.date_entry.grid(row=2, column=1, padx=5, sticky=tk.W)
        ttk.Button(filter_frame, text="Apply Date", command=self.apply_date_filter).grid(row=2, column=2, padx=5)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.status_var = tk.StringVar(value="all")
        status_options = ["all", "paid", "unpaid", "late"]
        ttk.OptionMenu(filter_frame, self.status_var, "all", *status_options, 
                      command=lambda _: self.filter_payments()).grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Search Name:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=3, padx=5, sticky=tk.W)
        search_entry.bind("<KeyRelease>", lambda _: self.filter_payments())

        # Academic year and semester filters
        ttk.Label(filter_frame, text="Academic Year:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.year_var = tk.StringVar(value="All")
        self.year_combobox = ttk.Combobox(filter_frame, textvariable=self.year_var)
        self.year_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

        ttk.Label(filter_frame, text="Semester:").grid(row=1, column=2, padx=5, sticky=tk.W)
        self.semester_var = tk.StringVar(value="All")
        self.semester_combobox = ttk.Combobox(filter_frame, textvariable=self.semester_var, 
                                            values=["All", "First Semester", "Second Semester", "Midyear"])
        self.semester_combobox.grid(row=1, column=3, padx=5, sticky=tk.W)

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=1, column=4, padx=5)

        # Treeview for payment details
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("id", "name", "status", "amount", "due_date"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        columns = {
            "id": {"text": "ID", "width": 50, "anchor": tk.CENTER},
            "name": {"text": "Member Name", "width": 200, "anchor": tk.W},
            "status": {"text": "Status", "width": 100, "anchor": tk.CENTER},
            "amount": {"text": "Amount", "width": 100, "anchor": tk.CENTER},
            "due_date": {"text": "Due Date", "width": 100, "anchor": tk.CENTER}
        }

        for col, config in columns.items():
            self.tree.heading(col, text=config["text"], command=lambda c=col: self.current_sort_column(c))
            self.tree.column(col, width=config["width"], anchor=config["anchor"])

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

    def get_available_years(self):
        """Get distinct academic years from database"""
        try:
            query = "SELECT DISTINCT academic_year FROM serves WHERE org_name = %s ORDER BY academic_year DESC"
            years = fetch_all(query, (self.app.org_name,))
            return ["All"] + [year["academic_year"] for year in years]
        except Exception as e:
            print(f"Error fetching years: {e}")
            return ["All"]

    def load_payment_data(self):
        """Load payment data from database"""
        try:
            # Update year dropdown
            available_years = self.get_available_years()
            self.year_combobox['values'] = available_years
            
            academic_year = self.year_var.get()
            semester = self.semester_var.get()
            
            base_query = """
                SELECT 
                    f.receipt_no AS id,
                    CONCAT(m.first_name, ' ', m.last_name) AS name,
                    CASE 
                        WHEN f.date_paid IS NULL AND f.payment_deadline < CURDATE() THEN 'late'
                        WHEN f.date_paid IS NULL THEN 'unpaid'
                        ELSE 'paid'
                    END AS status,
                    f.amount,
                    f.payment_deadline AS due_date,
                    f.student_no,
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
            
            # Convert dates for display and verify status
            for member in self.members:
                if isinstance(member["due_date"], (date, datetime)):
                    due_date = member["due_date"]
                    member["due_date"] = due_date.strftime("%Y-%m-%d")
                    
                    # Re-check status in case database didn't calculate it correctly
                    if member["status"] == "unpaid" and due_date < datetime.now().date():
                        member["status"] = "late"
                        
            self.filter_payments()
            self.status_bar.config(text=f"Loaded {len(self.members)} payments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payments: {str(e)}")
            self.status_bar.config(text="Error loading payments")
            self.members = []

    def get_available_years(self):
        """Get distinct academic years from database plus 'All' option"""
        try:
            query = "SELECT DISTINCT academic_year FROM serves WHERE org_name = %s ORDER BY academic_year DESC"
            years = fetch_all(query, (self.app.org_name,))
            return ["All"] + [year["academic_year"] for year in years]
        except Exception as e:
            print(f"Error fetching years: {e}")
            return ["All"]
    
    def refresh_data(self):
        """Refresh data and update year dropdown"""
        try:
            available_years = self.get_available_years()
            self.year_combobox['values'] = available_years
            if "All" not in available_years:
                available_years.insert(0, "All")
            self.load_payment_data()
            self.status_bar.config(text="Data refreshed")
        except Exception as e:
            messagebox.showerror("Error", f"Refresh failed: {str(e)}")
    
    def apply_filters(self):
        """Reload data when filters change"""
        self.load_payment_data()


    def filter_payments(self):
        """Filter payments based on selected status and search term"""
        status_filter = self.status_var.get()
        search_term = self.search_var.get().lower()

        # Clear current treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter and add items to treeview
        for member in self.members:
            try:
                status_match = (status_filter == "all") or (member["status"] == status_filter)
                name_match = search_term in member["name"].lower()
                
                if status_match and name_match:
                    self.tree.insert("", tk.END, values=(
                        member["id"],
                        member["name"],
                        member["status"].capitalize(),
                        f"₱{float(member['amount']):,.2f}",
                        member["due_date"]
                    ))
            except KeyError as e:
                print(f"Missing key in member data: {e}")
                continue

        self.update_totals()
        self.status_bar.config(text=f"Showing {len(self.tree.get_children())} records")

    def update_totals(self):
        """Update the summary information with proper error handling"""
        try:
            total_paid = sum(float(m["amount"]) for m in self.members if m.get("status") == "paid")
            total_unpaid = sum(float(m["amount"]) for m in self.members if m.get("status") in ["unpaid", "late"])
            
            unpaid_members = [m for m in self.members if m.get("status") in ["unpaid", "late"]]
            highest_debt = max(unpaid_members, key=lambda x: float(x["amount"]), default=None) if unpaid_members else None

            self.total_paid_label.config(text=f"₱{total_paid:,.2f}")
            self.total_unpaid_label.config(text=f"₱{total_unpaid:,.2f}")
            
            if highest_debt:
                self.highest_debt_label.config(text=f"{highest_debt['name']} (₱{float(highest_debt['amount']):,.2f})")
            else:
                self.highest_debt_label.config(text="None")
                
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating totals: {str(e)}")
            self.total_paid_label.config(text="₱0")
            self.total_unpaid_label.config(text="₱0")
            self.highest_debt_label.config(text="None")

    def refresh_data(self):
        """Refresh all data with error handling"""
        try:
            self.load_payment_data()
            self.status_bar.config(text="Data refreshed")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {str(e)}")
            self.status_bar.config(text="Refresh failed")

    def view_top_debt(self):
        """Show top 5 highest debts in the current treeview"""
        try:
            # Filter unpaid/late members and sort by amount (descending)
            unpaid_members = [m for m in self.members if m.get("status") in ["unpaid", "late"]]
            top_debtors = sorted(unpaid_members, key=lambda x: float(x["amount"]), reverse=True)[:5]
            
            # Clear current treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Add top debtors to treeview
            for member in top_debtors:
                self.tree.insert("", tk.END, values=(
                    member["id"],
                    member["name"],
                    member["status"].capitalize(),
                    f"₱{float(member['amount']):,.2f}",
                    member["due_date"]
                ))
                
            self.update_totals()
            self.status_bar.config(text=f"Showing top 5 highest debts (Total: {len(top_debtors)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show top debts: {str(e)}")
            self.status_bar.config(text="Error showing top debts")

    def update_fee_status(self):
        """Handle payment status updates - only unpaid/late can be updated"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a payment record to update")
            return
            
        try:
            item_data = self.tree.item(selected_item[0])
            receipt_no = item_data['values'][0]
            current_status = item_data['values'][2].lower()
            
            if current_status not in ['unpaid']:
                messagebox.showwarning("Invalid Action", 
                                    "Only unpaid payments can be updated.\n"
                                    "This payment was already paid.")
                return
                
            # Confirm with user before updating
            confirm = messagebox.askyesno(
                "Confirm Update",
                f"Mark payment {receipt_no} as paid?\n"
                f"Amount: {item_data['values'][3]}"
            )
            if not confirm:
                return
                
            # Mark as paid
            query = "UPDATE fee SET date_paid = CURDATE() WHERE receipt_no = %s"
            execute_query(query, (receipt_no,))
            messagebox.showinfo("Success", f"Payment {receipt_no} marked as paid")
            
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update payment status: {str(e)}")

    def apply_date_filter(self):
        """Apply date filter and update totals"""
        date_str = self.date_var.get()
        if not date_str:
            messagebox.showwarning("Missing Date", "Please enter a date in YYYY-MM-DD format")
            return
        
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            self.calculate_totals_as_of_date(filter_date)
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format")

    def calculate_totals_as_of_date(self, target_date):
        """Calculate totals as of a specific date"""
        try:
            query = """
                SELECT 
                    SUM(CASE WHEN date_paid IS NOT NULL AND date_paid <= %s THEN amount ELSE 0 END) AS paid_total,
                    SUM(CASE WHEN date_paid IS NULL AND payment_deadline <= %s THEN amount ELSE 0 END) AS unpaid_total,
                    SUM(CASE WHEN date_paid IS NULL AND payment_deadline > %s THEN amount ELSE 0 END) AS future_unpaid
                FROM fee
                WHERE org_name = %s
            """
            result = fetch_one(query, (target_date, target_date, target_date, self.app.org_name))
            
            paid = float(result["paid_total"] or 0)
            unpaid = float(result["unpaid_total"] or 0)
            future_unpaid = float(result["future_unpaid"] or 0)
            
            self.total_paid_label.config(text=f"₱{paid:,.2f} (as of {target_date})")
            self.total_unpaid_label.config(text=f"₱{unpaid:,.2f} (as of {target_date})")
            
            # Find highest debt as of the target date
            debt_query = """
                SELECT 
                    CONCAT(m.first_name, ' ', m.last_name) AS name,
                    f.amount
                FROM fee f
                JOIN member m ON f.student_no = m.student_no
                WHERE f.org_name = %s
                AND f.date_paid IS NULL 
                AND f.payment_deadline <= %s
                ORDER BY f.amount DESC
                LIMIT 1
            """
            highest_debt = fetch_one(debt_query, (self.app.org_name, target_date))
            
            if highest_debt:
                self.highest_debt_label.config(text=f"{highest_debt['name']} (₱{float(highest_debt['amount']):,.2f})")
            else:
                self.highest_debt_label.config(text="None")
                
            self.status_bar.config(text=f"Showing totals as of {target_date}")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error calculating totals: {str(e)}")
            self.total_paid_label.config(text="₱0")
            self.total_unpaid_label.config(text="₱0")
            self.highest_debt_label.config(text="None")