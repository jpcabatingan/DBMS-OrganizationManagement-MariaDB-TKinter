import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import BOLD
import datetime
from shared_variables import BasePage, execute_query, fetch_one, fetch_all

class OrganizationMenuPage(BasePage):
    def __init__(self, master, app_instance, passed_org_name=None):
        page_title = "Organization Menu"
        super().__init__(master, app_instance, page_title) 
        
        self.org_name = passed_org_name 
        
        self.create_org_menu_layout()

    def create_org_menu_layout(self):
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("text") == "":
                widget.destroy()

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.header_frame = ttk.Frame(self, style='AuthPanel.TFrame', padding="15")
        self.header_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=10, pady=10, columnspan=2)
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=0)

        ttk.Label(self.header_frame, text="🏛️", font=("Arial", 30)).grid(row=0, column=0, rowspan=2, padx=10)
        ttk.Label(self.header_frame, text=f"Welcome, {self.org_name if self.org_name else 'Organization'}", font=("Arial", 20, BOLD)).grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        ttk.Label(self.header_frame, text=f"Organization ID: {self.app.current_user_id}").grid(row=1, column=1, sticky=tk.W)

        academic_year, semester = self.get_current_academic_period()
        if academic_year and semester:
            active_members_count = self.get_active_members_count_for_current_semester(academic_year, semester)
            ttk.Label(self.header_frame, text=f"Active members this semester ({academic_year} {semester}): {active_members_count}").grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        else:
            ttk.Label(self.header_frame, text="Active members count: N/A (Invalid Academic Period)").grid(row=2, column=1, sticky=tk.W, pady=(0, 5))

        ttk.Button(self.header_frame, text="Log Out", command=self.app.logout).grid(row=0, column=2, sticky=tk.NE, padx=10, pady=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10, columnspan=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.member_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.member_tab, text="Manage Members")
        self.member_tab.grid_rowconfigure(1, weight=1)
        self.member_tab.grid_columnconfigure(0, weight=0)
        self.member_tab.grid_columnconfigure(1, weight=1)

        self.create_member_tab_widgets()

        self.fees_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.fees_tab, text="Manage Finances")
        self.create_fees_tab_widgets()

    def create_fees_tab_widgets(self):
        from orgpov_fees import OrganizationFeesPage
        self.fees_page = OrganizationFeesPage(self.fees_tab, self)
        self.fees_page.pack(fill=tk.BOTH, expand=True)
            
    def get_current_academic_period(self):
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month

        if 8 <= current_month <= 12:
            academic_year = f"{current_year}-{current_year + 1}"
            semester = "First"
        elif 1 <= current_month <= 5:
            academic_year = f"{current_year - 1}-{current_year}"
            semester = "Second"
        else:
            messagebox.showerror("Invalid Academic Period", "Only First Semester (August-December) and Second Semester (January-May) are allowed. The current month does not fall into a recognized academic period.")
            return None, None

        return academic_year, semester

    def get_active_members_count_for_current_semester(self, academic_year, semester):
        count_record = fetch_one(
            """
            SELECT COUNT(DISTINCT student_no) AS member_count  -- <--- Add AS alias_name
            FROM serves
            WHERE org_name = %s
                AND academic_year = %s
                AND semester = %s
                AND status = 'Active';
            """,
            (self.app.current_org_name, academic_year, semester)
        )
        return count_record['member_count'] if count_record else 0

    def create_member_tab_widgets(self):
        left_panel = ttk.Frame(self.member_tab)
        left_panel.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=10, pady=10)
        left_panel.grid_columnconfigure(1, weight=1)

        filter_frame = ttk.LabelFrame(left_panel, text="Filters", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)

        filter_row = 0
        self.filter_vars = {}

        current_ay, current_sem = self.get_current_academic_period()
        default_ay_filter = current_ay if current_ay else ""
        default_sem_filter = current_sem if current_sem else "All"

        ttk.Label(filter_frame, text="Academic Year:").grid(row=filter_row, column=0, sticky=tk.W, pady=2)
        self.filter_vars['academic_year'] = tk.StringVar(value=default_ay_filter)
        ttk.Entry(filter_frame, textvariable=self.filter_vars['academic_year']).grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
        filter_row += 1

        ttk.Label(filter_frame, text="Semester:").grid(row=filter_row, column=0, sticky=tk.W, pady=2)
        self.filter_vars['semester'] = tk.StringVar(value=default_sem_filter)
        ttk.Combobox(filter_frame, textvariable=self.filter_vars['semester'], values=["All", "First", "Second"], state="readonly").grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
        filter_row += 1

        labels_and_options = {
            "Role:": ["All", "Member", "President", "Vice President", "EAC Chairperson", "Secretary", "Finance Chairperson", "SCC Chairperson", "MC Chairperson"],
            "Status:": ["All", "Active", "Inactive", "Disaffiliated", "Alumni"],
            "Gender:": ["All", "F", "M"],
            "Degree Program:": [],
            "Batch:": [],
            "Committee:": ["All", "Executive", "Internal Academics", "External Academics", "Secretariat", "Finance", "Socio-Cultural", "Membership"]
        }

        for label_text, options in labels_and_options.items():
            ttk.Label(filter_frame, text=label_text).grid(row=filter_row, column=0, sticky=tk.W, pady=2)
            key = label_text.replace(":", "").replace(" ", "_").lower()
            if options:
                var = tk.StringVar(value=options[0])
                combobox = ttk.Combobox(filter_frame, textvariable=var, values=options, state="readonly")
                combobox.grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
                self.filter_vars[key] = var
            else:
                var = tk.StringVar()
                entry = ttk.Entry(filter_frame, textvariable=var)
                entry.grid(row=filter_row, column=1, sticky=(tk.W, tk.E), pady=2)
                self.filter_vars[key] = var
            filter_row += 1

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters_and_generate_report, style='Login.TButton').grid(row=filter_row, column=0, columnspan=2, pady=10)

        update_members_frame = ttk.LabelFrame(left_panel, text="Update members", padding="10")
        update_members_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(10, 10))
        update_members_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(update_members_frame, text="Add new member", command=self.app.show_add_new_member_page, style='Login.TButton').grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(update_members_frame, text="Edit member details", command=self.app.show_edit_membership_status_page, style='Login.TButton').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        active_percentage_frame = ttk.LabelFrame(left_panel, text="Active Members Percentage", padding="10")
        active_percentage_frame.grid(row=2, column=0, sticky=(tk.N, tk.W, tk.E), columnspan=2, pady=(10, 0))
        active_percentage_frame.grid_columnconfigure(0, weight=1)
        active_percentage_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(active_percentage_frame, text="Last No. of Semesters").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.n_semesters_entry = ttk.Entry(active_percentage_frame)
        self.n_semesters_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.n_semesters_entry.insert(0, "1")

        ttk.Button(active_percentage_frame, text="View Percentage", command=self.view_active_members_percentage, style='Login.TButton').grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.percentage_result_label = ttk.Label(active_percentage_frame, text="")
        self.percentage_result_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        tree_frame = ttk.Frame(self.member_tab)
        tree_frame.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=10, pady=10, rowspan=3)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.member_list_tree = ttk.Treeview(tree_frame, show="headings")
        self.member_list_tree.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        member_list_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.member_list_tree.yview)
        member_list_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.member_list_tree.configure(yscrollcommand=member_list_scrollbar_y.set)

        member_list_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.member_list_tree.xview)
        member_list_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.member_list_tree.configure(xscrollcommand=member_list_scrollbar_x.set)

        self.set_default_treeview_columns()
        self.apply_filters_and_generate_report()

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
        self.clear_treeview(self.member_list_tree)
        self.set_default_treeview_columns()

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
        params = [self.app.current_org_name]

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
            try:
                batch_val = int(self.filter_vars['batch'].get())
                query += " AND m.batch = %s"
                params.append(batch_val)
            except ValueError:
                messagebox.showerror("Input Error", "Batch must be an integer.")
                return
        if self.filter_vars['committee'].get() != "All":
            query += " AND s.committee = %s"
            params.append(self.filter_vars['committee'].get())

        query += " ORDER BY m.last_name, m.first_name, s.academic_year DESC, s.semester DESC;"

        records = fetch_all(query, tuple(params))

        if records:
            for record in records:
                self.member_list_tree.insert("", "end", values=tuple(record.values()))
        else:
            columns = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
            self.member_list_tree.insert("", "end", values=("No members found matching criteria.",) + ("",) * (len(columns) - 1))

    def generate_active_members_only_report(self):
        self.clear_treeview(self.member_list_tree)
        self.set_default_treeview_columns()

        academic_year, semester = self.get_current_academic_period()
        if not academic_year or not semester:
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
        records = fetch_all(query, (self.app.current_org_name, academic_year, semester))

        if records:
            for record in records:
                self.member_list_tree.insert("", "end", values=tuple(record.values()))
        else:
            columns = ("Student No", "Full Name", "Degree Program", "Gender", "Batch", "Academic Year", "Semester", "Role", "Status", "Committee")
            self.member_list_tree.insert("", "end", values=(f"No active members for {academic_year} {semester}.",) + ("",) * (len(columns) - 1))

    def view_active_members_percentage(self):
        self.percentage_result_label.config(text="")

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

        current_ay, current_sem = self.get_current_academic_period()
        if not current_ay or not current_sem:
            return

        all_org_semesters = fetch_all("""
            SELECT DISTINCT academic_year, semester
            FROM serves
            WHERE org_name = %s
            ORDER BY academic_year DESC,
                     CASE semester WHEN 'First' THEN 1 ELSE 2 END DESC;
            """, (self.app.current_org_name,))
        
        semesters_to_consider = []
        found_current = False
        for i, record in enumerate(all_org_semesters):
            ay, sem = record['academic_year'], record['semester']
            if ay == current_ay and sem == current_sem:
                semesters_to_consider = all_org_semesters[i : i + n]
                found_current = True
                break
        
        if not found_current:
            semesters_to_consider = all_org_semesters[:n]
            if not semesters_to_consider:
                messagebox.showinfo("No Data", f"No academic records found for {self.app.current_org_name} to calculate percentage.")
                return
            if len(semesters_to_consider) < n:
                messagebox.showwarning("Limited Data", f"Only {len(semesters_to_consider)} semesters available for {self.app.current_org_name}. Showing data for all available semesters.")

        if not semesters_to_consider:
            self.percentage_result_label.config(text="No relevant semesters found.")
            return

        total_active = 0
        total_inactive = 0
        
        for record in semesters_to_consider:
            ay, sem = record['academic_year'], record['semester']
            active_count_record = fetch_one("""
                SELECT COUNT(DISTINCT student_no) AS active_count -- <--- Add AS alias_name
                FROM serves
                WHERE org_name = %s AND academic_year = %s AND semester = %s AND status = 'Active';
                """, (self.app.current_org_name, ay, sem))
            active_count = active_count_record['active_count'] if active_count_record else 0

            inactive_count_record = fetch_one("""
                SELECT COUNT(DISTINCT student_no) AS inactive_count -- <--- Add AS alias_name
                FROM serves
                WHERE org_name = %s AND academic_year = %s AND semester = %s AND status != 'Active';
                """, (self.app.current_org_name, ay, sem))
            inactive_count = inactive_count_record['inactive_count'] if inactive_count_record else 0

            total_active += active_count
            total_inactive += inactive_count
            
        overall_total = total_active + total_inactive
        if overall_total > 0:
            active_percentage = (total_active / overall_total) * 100
            inactive_percentage = (total_inactive / overall_total) * 100
            result_text = (f"Overall (last {n} semesters):\n"
                           f"Active: {total_active} ({active_percentage:.2f}%)\n"
                           f"Inactive: {total_inactive} ({inactive_percentage:.2f}%)\n")
        else:
            result_text = "No member data found for the specified semesters."

        self.percentage_result_label.config(text=result_text)