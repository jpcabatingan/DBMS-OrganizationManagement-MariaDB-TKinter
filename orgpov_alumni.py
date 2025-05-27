import tkinter as tk
from tkinter import ttk, messagebox
import re

# import shared_variables classes
from shared_variables import BasePage, fetch_all

# Organization POV Alumni
class OrganizationAlumniPage(BasePage):
    def __init__(self, master, app_instance, page_title, passed_org_name=None):
        super().__init__(master, app_instance, page_title)
        self.org_name = passed_org_name
        self.create_alumni_layout()


    def create_alumni_layout(self):
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        alumni_filter_frame = ttk.LabelFrame(self.content_frame, text="Filter Alumni by Academic Year", padding="10")
        alumni_filter_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), pady=(0, 10), padx=(0, 0))
        alumni_filter_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(alumni_filter_frame, text="As of Academic Year:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.alumni_academic_year_entry = ttk.Entry(alumni_filter_frame)
        self.alumni_academic_year_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.alumni_academic_year_entry.insert(0, "YYYY-YYYY") 

        ttk.Button(alumni_filter_frame, text="Generate Alumni Report", command=self.view_alumni_members, style='Login.TButton').grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(0, 0), pady=(0, 0)) 
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

        self.set_alumni_treeview_columns()
        self.populate_treeview(self.member_list_tree, [], {}, full_name_key=None)


    def populate_treeview(self, tree, data, column_mapping, full_name_key=None):
        for iid in tree.get_children():
            tree.delete(iid)

        if not data:
            current_cols = list(tree["columns"])
            if tree.heading("#0")["text"] != "" and full_name_key: 
                tree.insert("", "end", text="No records found.", values=[""] * len(current_cols))
            else:
                num_cols_to_fill = len(current_cols)
                tree.insert("", "end", values=("No records found.",) + tuple([""] * (num_cols_to_fill -1 ))) 
            return

        for row_data in data:
            values_for_tree = []
            
            current_tree_columns = tree["columns"] 

            for col_id in current_tree_columns:
                data_key = column_mapping.get(col_id)
                if data_key:
                    values_for_tree.append(row_data.get(data_key, ''))
                else:
                    values_for_tree.append('')

            text_value = row_data.get(full_name_key, '') if full_name_key else ''

            tree.insert("", "end", text=text_value, values=values_for_tree)

    # table contant and headers
    def set_alumni_treeview_columns(self):
        alumni_internal_columns = (
            "student_no", "first_name", "middle_name", "last_name", "batch",
            "org_name", "role", "committee", "academic_year", "status"
        )
        alumni_display_headings = (
            "Student No.", "First Name", "Middle Name", "Last Name", "Batch",
            "Organization", "Role", "Committee", "Academic Year", "Status"
        )
        alumni_widths = (100, 120, 120, 120, 70, 200, 100, 120, 100, 80)
        alumni_anchors = (tk.CENTER, tk.W, tk.CENTER, tk.W, tk.CENTER, tk.W, tk.W, tk.W, tk.CENTER, tk.CENTER)
        
        self.set_treeview_columns(self.member_list_tree, alumni_internal_columns, alumni_display_headings, alumni_widths, alumni_anchors, use_hash0_for_fullname=False)

    # columns for table
    def set_treeview_columns(self, tree, internal_column_names, display_headings, widths, anchors, use_hash0_for_fullname=False):
        for iid in tree.get_children():
            tree.delete(iid)

        tree["columns"] = internal_column_names
        tree["displaycolumns"] = internal_column_names 

        tree.heading("#0", text="")
        tree.column("#0", width=0, stretch=tk.NO)

        if use_hash0_for_fullname:
            tree.heading("#0", text="Full Name", anchor=tk.W)
            tree.column("#0", width=150, stretch=tk.NO, anchor=tk.W)
            
        for i, col_name in enumerate(internal_column_names):
            if i < len(display_headings) and i < len(widths) and i < len(anchors):
                tree.heading(col_name, text=display_headings[i], anchor=anchors[i])
                tree.column(col_name, width=widths[i], stretch=tk.NO, anchor=anchors[i])
            else:
                tree.heading(col_name, text=col_name.replace('_', ' ').title())
                tree.column(col_name, width=100, stretch=tk.NO, anchor=tk.W)


    # view alumni members at given academic year
    def view_alumni_members(self):
        self.set_alumni_treeview_columns()

        academic_year_input = self.alumni_academic_year_entry.get().strip()

        if not academic_year_input or academic_year_input == "YYYY-YYYY":
            messagebox.showerror("Input Error", "Please enter an Academic Year (e.g., 2023-2024).")
            return

        if not re.match(r"^\d{4}-\d{4}$", academic_year_input):
            messagebox.showerror("Validation Error", "Academic Year must be in YYYY-YYYY format (e.g., 2023-2024).")
            return

        current_org_name = self.app.current_org_name

        try:
            query = """
            SELECT
                m.student_no,
                m.first_name,
                m.middle_name,
                m.last_name,
                m.batch,
                s.org_name,
                s.role,
                s.committee,
                s.academic_year,
                s.status
            FROM member m
            JOIN serves s ON m.student_no = s.student_no
            WHERE s.org_name = %s
                AND s.academic_year < %s
                AND s.status = 'Alumni'
            ORDER BY s.academic_year DESC, m.last_name, m.first_name;
            """
            alumni_members = fetch_all(query, (current_org_name, academic_year_input))

            alumni_column_mapping = {
                "student_no": "student_no",
                "first_name": "first_name",
                "middle_name": "middle_name",
                "last_name": "last_name",
                "batch": "batch",
                "org_name": "org_name",
                "role": "role",
                "committee": "committee",
                "academic_year": "academic_year",
                "status": "status"
            }
            
            self.populate_treeview(self.member_list_tree, alumni_members, alumni_column_mapping, full_name_key=None)

            if not alumni_members:
                messagebox.showinfo("No Results", f"No alumni members found for {current_org_name} as of Academic Year {academic_year_input}.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching alumni data: {e}")