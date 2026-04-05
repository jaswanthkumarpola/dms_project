import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx


from utils import (
    attendance_percentage,
    status_from_percentage,
    classes_needed_to_reach_target,
)
from report import (
    build_summary_report,
    build_low_attendance_report,
    build_top_performers_report,
    build_subject_analysis_report,
    build_relations_report,
    build_graph_report,
    build_specific_attendance_report,
)


class SmartAttendanceAnalyzerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Attendance Analyzer")
        self.root.geometry("1200x760")
        self.root.minsize(1050, 680)

        # Discrete maths idea:
        # Students = set S
        # Subjects = set C
        # Attendance relation R ⊆ S × C
        self.students = set()
        self.subjects = set()
        self.records = []

        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        title = tk.Label(
            self.root,
            text="Smart Attendance Analyzer",
            font=("Helvetica", 22, "bold"),
            pady=10,
        )
        title.pack()

        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 12))

        right = tk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        # Form section
        form = ttk.LabelFrame(left, text="Add / Update Attendance Record", padding=12)
        form.pack(fill="x", pady=(0, 12))

        tk.Label(form, text="Student Name").grid(row=0, column=0, sticky="w", pady=5)
        self.student_entry = tk.Entry(form, width=28)
        self.student_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Subject").grid(row=1, column=0, sticky="w", pady=5)
        self.subject_entry = tk.Entry(form, width=28)
        self.subject_entry.grid(row=1, column=1, pady=5)

        tk.Label(form, text="Classes Attended").grid(row=2, column=0, sticky="w", pady=5)
        self.attended_entry = tk.Entry(form, width=28)
        self.attended_entry.grid(row=2, column=1, pady=5)

        tk.Label(form, text="Total Classes").grid(row=3, column=0, sticky="w", pady=5)
        self.total_entry = tk.Entry(form, width=28)
        self.total_entry.grid(row=3, column=1, pady=5)

        tk.Label(form, text="Target %").grid(row=4, column=0, sticky="w", pady=5)
        self.target_entry = tk.Entry(form, width=28)
        self.target_entry.insert(0, "75")
        self.target_entry.grid(row=4, column=1, pady=5)

        btn_row = tk.Frame(form)
        btn_row.grid(row=5, column=0, columnspan=2, pady=(12, 0))

        tk.Button(btn_row, text="Add Record", width=13, command=self.add_record).pack(side="left", padx=4)
        tk.Button(btn_row, text="Clear Fields", width=13, command=self.clear_inputs).pack(side="left", padx=4)

        # Tools
        tools = ttk.LabelFrame(left, text="Analysis Tools", padding=12)
        tools.pack(fill="x", pady=(0, 12))

        tk.Button(tools, text="Show Summary", width=24, command=self.show_summary).pack(pady=4)
        tk.Button(tools, text="Show Low Attendance", width=24, command=self.show_low_attendance).pack(pady=4)
        tk.Button(tools, text="Show Top Performers", width=24, command=self.show_top_performers).pack(pady=4)
        tk.Button(tools, text="Show Subject Analysis", width=24, command=self.show_subject_analysis).pack(pady=4)
        tk.Button(tools, text="Show Attendance Relations", width=24, command=self.show_relations_view).pack(pady=4)
        tk.Button(tools, text="Show Co-Attendance Graph", width=24, command=self.show_graph_view).pack(pady=4)
        search_box = ttk.LabelFrame(left, text="Check Particular Student", padding=12)
        search_box.pack(fill="x", pady=(12, 0))

        tk.Label(search_box, text="Student Name").grid(row=0, column=0, sticky="w", pady=5)
        self.search_student_entry = tk.Entry(search_box, width=28)
        self.search_student_entry.grid(row=0, column=1, pady=5)

        tk.Label(search_box, text="Subject (optional)").grid(row=1, column=0, sticky="w", pady=5)
        self.search_subject_entry = tk.Entry(search_box, width=28)
        self.search_subject_entry.grid(row=1, column=1, pady=5)

        tk.Button(
        search_box, text="Check Specific Attendance", width=24, command=self.show_specific_attendance).grid(row=2, column=0, columnspan=2, pady=(10, 0))
       
        # File section
        file_panel = ttk.LabelFrame(left, text="File", padding=12)
        file_panel.pack(fill="x")

        tk.Button(file_panel, text="Export CSV", width=24, command=self.export_csv).pack(pady=4)
        tk.Button(file_panel, text="Import CSV", width=24, command=self.import_csv).pack(pady=4)
        tk.Button(file_panel, text="Delete Selected", width=24, command=self.delete_selected).pack(pady=4)

        # Table
        table_frame = ttk.LabelFrame(right, text="Attendance Records", padding=10)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "student",
            "subject",
            "attended",
            "total",
            "percentage",
            "status",
            "needed",
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headings = {
            "student": "Student",
            "subject": "Subject",
            "attended": "Attended",
            "total": "Total",
            "percentage": "Attendance %",
            "status": "Status",
            "needed": "Classes Needed",
        }

        widths = {
            "student": 170,
            "subject": 130,
            "attended": 90,
            "total": 90,
            "percentage": 120,
            "status": 110,
            "needed": 130,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Output area
        output_frame = ttk.LabelFrame(right, text="Results / Insights", padding=10)
        output_frame.pack(fill="both", expand=False, pady=(12, 0))

        self.output_text = tk.Text(output_frame, height=10, wrap="word", font=("Courier", 11))
        self.output_text.pack(fill="both", expand=True)

    def add_record(self):
        student = self.student_entry.get().strip()
        subject = self.subject_entry.get().strip()
        attended_raw = self.attended_entry.get().strip()
        total_raw = self.total_entry.get().strip()
        target_raw = self.target_entry.get().strip()

        if not student or not subject or not attended_raw or not total_raw:
            messagebox.showerror("Missing data", "Please fill all fields.")
            return

        try:
            attended = int(attended_raw)
            total = int(total_raw)
            target = int(target_raw) if target_raw else 75
        except ValueError:
            messagebox.showerror("Invalid input", "Attended, Total, and Target must be integers.")
            return

        if attended < 0 or total <= 0 or attended > total:
            messagebox.showerror(
                "Invalid values",
                "Make sure 0 <= attended <= total and total > 0.",
            )
            return

        updated = False
        for rec in self.records:
            if rec["student"].lower() == student.lower() and rec["subject"].lower() == subject.lower():
                rec["student"] = student
                rec["subject"] = subject
                rec["attended"] = attended
                rec["total"] = total
                rec["target"] = target
                updated = True
                break

        if not updated:
            self.records.append(
                {
                    "student": student,
                    "subject": subject,
                    "attended": attended,
                    "total": total,
                    "target": target,
                }
            )

        self.students = {rec["student"] for rec in self.records}
        self.subjects = {rec["subject"] for rec in self.records}

        self._refresh_table()
        self.clear_inputs()

    def clear_inputs(self):
        for widget in [self.student_entry, self.subject_entry, self.attended_entry, self.total_entry]:
            widget.delete(0, tk.END)

        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, "75")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Select a record to delete.")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        student = values[0]
        subject = values[1]

        self.records = [
            rec for rec in self.records
            if not (rec["student"] == student and rec["subject"] == subject)
        ]

        self.students = {rec["student"] for rec in self.records}
        self.subjects = {rec["subject"] for rec in self.records}

        self._refresh_table()

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for rec in self.records:
            percentage = attendance_percentage(rec["attended"], rec["total"])
            status = status_from_percentage(percentage)
            needed = classes_needed_to_reach_target(
                rec["attended"],
                rec["total"],
                rec.get("target", 75),
            )

            self.tree.insert(
                "",
                tk.END,
                values=(
                    rec["student"],
                    rec["subject"],
                    rec["attended"],
                    rec["total"],
                    f"{percentage:.2f}",
                    status,
                    needed,
                ),
            )

    def write_output(self, text: str):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)

    def show_summary(self):
        self.write_output(build_summary_report(self.records, self.students, self.subjects))

    def show_low_attendance(self):
        self.write_output(build_low_attendance_report(self.records))

    def show_top_performers(self):
        self.write_output(build_top_performers_report(self.records))

    def show_subject_analysis(self):
        self.write_output(build_subject_analysis_report(self.records))

    def show_relations_view(self):
        self.write_output(build_relations_report(self.records))

    def show_graph_view(self):
        G = nx.Graph()
        subject_to_eligible_students = defaultdict(list)

     # Step 1: collect eligible students per subject
        for rec in self.records:
            percentage = attendance_percentage(rec["attended"], rec["total"])
            if percentage >= 75:
                subject_to_eligible_students[rec["subject"]].append(rec["student"])

     # Step 2: add nodes and edges
        for subject, students in subject_to_eligible_students.items():
           students = list(set(students))

        for student in students:
            G.add_node(student)

        for i in range(len(students)):
            for j in range(i + 1, len(students)):
                G.add_edge(students[i], students[j])

     # Step 3: draw graph
        plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(G)

        nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=1500,
        node_color="skyblue",
        font_size=10,
        font_weight="bold"
    )
        plt.title("Student Attendance Graph")
        plt.show()


    def export_csv(self):
        if not self.records:
            messagebox.showinfo("Export", "No records to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Attendance Data",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=["student", "subject", "attended", "total", "target"]
                )
                writer.writeheader()
                writer.writerows(self.records)

            messagebox.showinfo("Export", "Data exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Open Attendance CSV",
        )

        if not file_path:
            return

        try:
            imported_records = []
            with open(file_path, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    imported_records.append(
                        {
                            "student": row["student"].strip(),
                            "subject": row["subject"].strip(),
                            "attended": int(row["attended"]),
                            "total": int(row["total"]),
                            "target": int(row.get("target", 75)),
                        }
                    )

            self.records = imported_records
            self.students = {rec["student"] for rec in self.records}
            self.subjects = {rec["subject"] for rec in self.records}

            self._refresh_table()
            messagebox.showinfo("Import", "Data imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))
    
    def show_specific_attendance(self):
        student_name = self.search_student_entry.get().strip()
        subject_name = self.search_subject_entry.get().strip()

        if not student_name:
            messagebox.showerror("Missing Input", "Please enter a student name.")
            return

        if not subject_name:
            subject_name = None

        report = build_specific_attendance_report(
        self.records,
        student_name,
        subject_name
    )
        self.write_output(report)