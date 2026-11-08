
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import csv
import time
import glob
import io
from contextlib import redirect_stdout


# --------------------------------------------------
# PROJECT SETUP
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

with redirect_stdout(io.StringIO()):
    from algorithms.closest_pair import closest_pair
    from algorithms.integer_multiplication import karatsuba_multiply


COLORS = {
    "background": "#F7F8FA",
    "white": "#FFFFFF",
    "primary": "#263B5A",
    "secondary": "#416B9B",
    "text": "#202938",
    "muted": "#667085",
    "border": "#E5E7EB",
    "success": "#16845B",
    "light_blue": "#EDF3FA"
}


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

class AlgorithmAnalyzer:

    def __init__(self, root):

        self.root = root
        self.root.title("DAA Algorithm Analyzer")
        self.root.geometry("1180x760")
        self.root.minsize(950, 600)
        self.root.configure(bg=COLORS["background"])

        self.create_layout()
        self.show_dashboard()

    # --------------------------------------------------
    # LAYOUT AND SCROLLING
    # --------------------------------------------------

    def create_layout(self):

        self.sidebar = tk.Frame(
            self.root, bg=COLORS["primary"], width=225
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(
            self.root, bg=COLORS["background"]
        )
        self.content_area.pack(side="right", fill="both", expand=True)

        self.content_canvas = tk.Canvas(
            self.content_area,
            bg=COLORS["background"],
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            self.content_area,
            orient="vertical",
            command=self.content_canvas.yview,
            bg="#DCE3EC",
            troughcolor=COLORS["background"],
            activebackground=COLORS["secondary"],
            relief="flat",
            bd=0
        )

        self.content_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(side="right", fill="y")
        self.content_canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(
            self.content_canvas, bg=COLORS["background"]
        )

        self.content_window = self.content_canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.content.bind("<Configure>", self.update_scroll_region)
        self.content_canvas.bind("<Configure>", self.update_canvas_width)
        self.content_canvas.bind("<Enter>", self.enable_mousewheel)
        self.content_canvas.bind("<Leave>", self.disable_mousewheel)

        self.create_sidebar()

    def update_scroll_region(self, event=None):
        self.content_canvas.configure(
            scrollregion=self.content_canvas.bbox("all")
        )

    def update_canvas_width(self, event):
        self.content_canvas.itemconfigure(
            self.content_window, width=event.width
        )

    def enable_mousewheel(self, event=None):
        self.content_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def disable_mousewheel(self, event=None):
        self.content_canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        self.content_canvas.yview_scroll(
            int(-event.delta / 120), "units"
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.content_canvas.yview_moveto(0)

    # --------------------------------------------------
    # REUSABLE UI HELPERS
    # --------------------------------------------------

    def create_sidebar(self):

        logo = tk.Frame(self.sidebar, bg=COLORS["primary"])
        logo.pack(fill="x", padx=20, pady=(28, 35))

        tk.Label(
            logo, text="DAA",
            font=("Segoe UI", 23, "bold"),
            fg=COLORS["white"], bg=COLORS["primary"]
        ).pack(anchor="w")

        tk.Label(
            logo, text="ALGORITHM ANALYZER",
            font=("Segoe UI", 8, "bold"),
            fg="#B9C8DA", bg=COLORS["primary"]
        ).pack(anchor="w", pady=(3, 0))

        self.separator(self.sidebar, "#526783", (18, 20))

        pages = [
            ("Dashboard", self.show_dashboard),
            ("Closest Pair", self.show_closest_pair),
            ("Integer Multiplication", self.show_integer_multiplication),
            ("Performance Analysis", self.show_performance),
            ("About Project", self.show_about)
        ]

        for name, command in pages:
            tk.Button(
                self.sidebar,
                text=name,
                command=command,
                font=("Segoe UI", 10),
                fg="#E8EEF5",
                bg=COLORS["primary"],
                activebackground="#385477",
                activeforeground=COLORS["white"],
                relief="flat",
                anchor="w",
                padx=20,
                pady=13,
                cursor="hand2",
                bd=0
            ).pack(fill="x", padx=10, pady=2)

        self.separator(self.sidebar, "#526783", (18, 25))

        tk.Label(
            self.sidebar,
            text="CS302 | Fall 2026",
            font=("Segoe UI", 9),
            fg="#B9C8DA",
            bg=COLORS["primary"]
        ).pack(side="bottom", pady=22)

    def separator(self, parent, color, padding):
        tk.Frame(parent, bg=color, height=1).pack(
            fill="x", padx=padding[0], pady=(0, padding[1])
        )

    def create_page_header(self, title, subtitle):

        header = tk.Frame(self.content, bg=COLORS["background"])
        header.pack(fill="x", padx=35, pady=(28, 22))

        tk.Label(
            header, text=title,
            font=("Segoe UI", 22, "bold"),
            fg=COLORS["text"], bg=COLORS["background"]
        ).pack(anchor="w")

        tk.Label(
            header, text=subtitle,
            font=("Segoe UI", 10),
            fg=COLORS["muted"], bg=COLORS["background"]
        ).pack(anchor="w", pady=(5, 0))

    def create_card(self, parent, **kwargs):
        return tk.Frame(
            parent,
            bg=COLORS["white"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            **kwargs
        )

    def create_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"],
            activebackground=COLORS["secondary"],
            activeforeground=COLORS["white"],
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            bd=0
        )

    def create_label(self, parent, text, size=13, bold=True):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold" if bold else "normal"),
            fg=COLORS["text"],
            bg=COLORS["white"]
        )

    def create_output(self, parent):
        output = tk.Text(
            parent,
            height=10,
            font=("Consolas", 10),
            bg="#F7F8FA",
            fg=COLORS["text"],
            relief="flat",
            padx=15,
            pady=12,
            wrap="word"
        )
        output.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        output.insert("1.0", "Your results will appear here.")
        output.config(state="disabled")
        return output

    def display_output(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def format_large_number(self, number, group_size=10):
        number = str(number)
        return " ".join(
            number[i:i + group_size]
            for i in range(0, len(number), group_size)
        )

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    def show_dashboard(self):

        self.clear_content()
        self.create_page_header(
            "Dashboard",
            "Welcome to the Design and Analysis of Algorithms project."
        )

        main = tk.Frame(self.content, bg=COLORS["background"])
        main.pack(fill="both", expand=True, padx=35, pady=(0, 30))

        welcome = tk.Frame(
            main, bg=COLORS["primary"], height=155
        )
        welcome.pack(fill="x")
        welcome.pack_propagate(False)

        tk.Label(
            welcome, text="Algorithm Laboratory",
            font=("Segoe UI", 21, "bold"),
            fg=COLORS["white"], bg=COLORS["primary"]
        ).pack(anchor="w", padx=25, pady=(28, 5))

        tk.Label(
            welcome,
            text="Explore, execute, and analyze two classic algorithms.",
            font=("Segoe UI", 10),
            fg="#DCE5EF", bg=COLORS["primary"]
        ).pack(anchor="w", padx=25)

        cp_count = len(glob.glob(
            os.path.join(PROJECT_ROOT, "datasets", "closest_pair", "*.txt")
        ))

        im_count = len(glob.glob(
            os.path.join(
                PROJECT_ROOT, "datasets",
                "integer_multiplication", "*.txt"
            )
        ))

        stats = tk.Frame(main, bg=COLORS["background"])
        stats.pack(fill="x", pady=22)

        for title, value in [
            ("Closest Pair Datasets", cp_count),
            ("Multiplication Datasets", im_count),
            ("Total Datasets", cp_count + im_count)
        ]:
            card = self.create_card(stats)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))

            tk.Label(
                card, text=title,
                font=("Segoe UI", 9),
                fg=COLORS["muted"], bg=COLORS["white"]
            ).pack(anchor="w", padx=17, pady=(15, 4))

            tk.Label(
                card, text=str(value),
                font=("Segoe UI", 23, "bold"),
                fg=COLORS["primary"], bg=COLORS["white"]
            ).pack(anchor="w", padx=17, pady=(0, 13))

        tk.Label(
            main, text="Available Algorithms",
            font=("Segoe UI", 15, "bold"),
            fg=COLORS["text"], bg=COLORS["background"]
        ).pack(anchor="w", pady=(8, 15))

        algorithms = tk.Frame(main, bg=COLORS["background"])
        algorithms.pack(fill="x")

        self.dashboard_algorithm(
            algorithms,
            "Closest Pair of Points",
            "Finds the two closest points in a 2D dataset.",
            "Divide and Conquer",
            self.show_closest_pair
        )

        self.dashboard_algorithm(
            algorithms,
            "Integer Multiplication",
            "Multiplies large integers using fewer recursive operations.",
            "Karatsuba Algorithm",
            self.show_integer_multiplication
        )

    def dashboard_algorithm(self, parent, title, description, method, command):

        card = self.create_card(parent)
        card.pack(
            side="left", fill="both", expand=True,
            padx=(0, 12), ipady=12
        )

        self.create_label(card, title).pack(
            anchor="w", padx=18, pady=(18, 8)
        )

        tk.Label(
            card, text=description,
            font=("Segoe UI", 9),
            fg=COLORS["muted"], bg=COLORS["white"],
            wraplength=300, justify="left"
        ).pack(anchor="w", padx=18)

        tk.Label(
            card, text=method,
            font=("Segoe UI", 9, "bold"),
            fg=COLORS["secondary"], bg=COLORS["white"]
        ).pack(anchor="w", padx=18, pady=12)

        self.create_button(
            card, "Open Algorithm", command
        ).pack(anchor="w", padx=18, pady=(0, 12))

    # --------------------------------------------------
    # DATASET FILE SELECTION
    # --------------------------------------------------

    def browse_file(self, variable, algorithm):

        folder = (
            "closest_pair"
            if algorithm == "closest"
            else "integer_multiplication"
        )

        initial_folder = os.path.join(
            PROJECT_ROOT, "datasets", folder
        )

        filepath = filedialog.askopenfilename(
            title="Select Input Dataset",
            initialdir=initial_folder,
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if filepath:
            variable.set(filepath)

    def create_file_display(self, parent, variable, algorithm):

        display = tk.Frame(
            parent,
            bg="#F7F8FA",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )

        display.pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )

        tk.Label(
            display,
            textvariable=variable,
            font=("Segoe UI", 9),
            fg=COLORS["muted"],
            bg="#F7F8FA",
            anchor="w"
        ).pack(fill="x", padx=12, pady=11)

        tk.Button(
            parent,
            text="Browse",
            command=lambda: self.browse_file(variable, algorithm),
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["light_blue"],
            fg=COLORS["primary"],
            activebackground="#DCE8F5",
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
            bd=0
        ).pack(side="right")

    # --------------------------------------------------
    # COMMON ALGORITHM PAGE
    # --------------------------------------------------

    def create_algorithm_page(self, title, subtitle, algorithm, button_text):

        self.clear_content()
        self.create_page_header(title, subtitle)

        main = tk.Frame(self.content, bg=COLORS["background"])
        main.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        file_card = self.create_card(main)
        file_card.pack(fill="x", pady=(0, 18))

        self.create_label(file_card, "Input Dataset").pack(
            anchor="w", padx=20, pady=(18, 12)
        )

        variable = tk.StringVar()

        file_row = tk.Frame(file_card, bg=COLORS["white"])
        file_row.pack(fill="x", padx=20, pady=(0, 18))

        self.create_file_display(file_row, variable, algorithm)

        output_card = self.create_card(main)
        output_card.pack(fill="both", expand=True)

        self.create_label(output_card, "Algorithm Results").pack(
            anchor="w", padx=20, pady=(18, 10)
        )

        status = tk.Label(
            output_card,
            text="Select a dataset and run the algorithm.",
            font=("Segoe UI", 10),
            fg=COLORS["muted"],
            bg=COLORS["white"]
        )
        status.pack(anchor="w", padx=20, pady=(0, 12))

        output = self.create_output(output_card)

        return variable, status, output, file_card

    # --------------------------------------------------
    # CLOSEST PAIR
    # --------------------------------------------------

    def show_closest_pair(self):

        self.cp_file, self.cp_status, self.cp_output, file_card = (
            self.create_algorithm_page(
                "Closest Pair of Points",
                "Find the minimum Euclidean distance between two points.",
                "closest",
                "Run Closest Pair"
            )
        )

        self.create_button(
            file_card,
            "Run Closest Pair",
            self.run_closest_pair
        ).pack(anchor="w", padx=20, pady=(0, 18))

    def run_closest_pair(self):

        filepath = self.cp_file.get()

        if not filepath:
            messagebox.showwarning(
                "No Dataset",
                "Please select a closest pair dataset first."
            )
            return

        try:

            with open(filepath, "r") as file:
                lines = file.readlines()

            number_of_points = int(lines[0].strip())
            points = []

            for line in lines[1:]:
                values = line.strip().split()
                if len(values) >= 2:
                    points.append((
                        float(values[0]),
                        float(values[1])
                    ))

            if len(points) != number_of_points:
                raise ValueError(
                    "The number of points does not match the dataset header."
                )

            if len(points) < 2:
                raise ValueError("At least two points are required.")

            start = time.perf_counter()
            pair, distance = closest_pair(points)
            execution_time = time.perf_counter() - start

            output = (
                "ALGORITHM: Closest Pair of Points\n"
                "METHOD: Divide and Conquer\n\n"
                "INPUT INFORMATION\n"
                "-----------------------------\n"
                "Dataset: " + os.path.basename(filepath) + "\n"
                "Number of Points: " + str(len(points)) + "\n\n"
                "RESULT\n"
                "-----------------------------\n"
                "Closest Point 1: " + str(pair[0]) + "\n"
                "Closest Point 2: " + str(pair[1]) + "\n"
                "Minimum Distance: " + str(distance) + "\n\n"
                "PERFORMANCE\n"
                "-----------------------------\n"
                "Time Complexity: O(n log n)\n"
                "Execution Time: " + str(execution_time) + " seconds\n"
            )

            self.display_output(self.cp_output, output)
            self.cp_status.config(
                text="Algorithm executed successfully.",
                fg=COLORS["success"]
            )

        except Exception as error:
            messagebox.showerror("Execution Error", str(error))

    # --------------------------------------------------
    # INTEGER MULTIPLICATION
    # --------------------------------------------------

    def show_integer_multiplication(self):

        (
            self.im_file,
            self.im_status,
            self.im_output,
            file_card
        ) = self.create_algorithm_page(
            "Integer Multiplication",
            "Multiply large integers using the Karatsuba algorithm.",
            "integer",
            "Run Karatsuba"
        )

        self.create_button(
            file_card,
            "Run Karatsuba",
            self.run_integer_multiplication
        ).pack(anchor="w", padx=20, pady=(0, 18))

    def run_integer_multiplication(self):

        filepath = self.im_file.get()

        if not filepath:
            messagebox.showwarning(
                "No Dataset",
                "Please select an integer multiplication dataset first."
            )
            return

        try:

            with open(filepath, "r") as file:
                lines = file.readlines()

            if len(lines) < 2:
                raise ValueError(
                    "The dataset must contain two integers."
                )

            first_number = int(lines[0].strip())
            second_number = int(lines[1].strip())

            if first_number < 0 or second_number < 0:
                raise ValueError(
                    "This implementation expects non-negative integers."
                )

            start = time.perf_counter()

            result = karatsuba_multiply(
                first_number, second_number
            )

            execution_time = time.perf_counter() - start
            correct = result == first_number * second_number

            output = (
                "ALGORITHM: Integer Multiplication\n"
                "METHOD: Karatsuba Algorithm\n\n"
                "INPUT INFORMATION\n"
                "----------------------------------------\n"
                "Dataset              : " + os.path.basename(filepath) + "\n"
                "First Number Digits  : " + str(len(str(first_number))) + "\n"
                "Second Number Digits : " + str(len(str(second_number))) + "\n\n"
                "RESULT\n"
                "----------------------------------------\n"
                "FIRST NUMBER:\n"
                + self.format_large_number(first_number) + "\n\n"
                "SECOND NUMBER:\n"
                + self.format_large_number(second_number) + "\n\n"
                "PRODUCT:\n"
                + self.format_large_number(result) + "\n\n"
                "PERFORMANCE\n"
                "----------------------------------------\n"
                "Time Complexity : O(n^1.585)\n"
                "Execution Time  : " + str(execution_time) + " seconds\n"
                "Correctness     : " + str(correct) + "\n"
            )

            self.display_output(self.im_output, output)
            self.im_status.config(
                text="Algorithm executed successfully.",
                fg=COLORS["success"]
            )

        except Exception as error:
            messagebox.showerror("Execution Error", str(error))

    # --------------------------------------------------
    # PERFORMANCE ANALYSIS
    # --------------------------------------------------

    def show_performance(self):

        self.clear_content()
        self.create_page_header(
            "Performance Analysis",
            "Compare execution times recorded during the experiments."
        )

        main = tk.Frame(self.content, bg=COLORS["background"])
        main.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        cp_path = os.path.join(
            PROJECT_ROOT, "results", "closest_pair_results.csv"
        )

        im_path = os.path.join(
            PROJECT_ROOT, "results", "integer_multiplication_results.csv"
        )

        self.create_performance_chart(
            main, "Closest Pair", cp_path
        )

        self.create_performance_chart(
            main, "Integer Multiplication", im_path
        )

    def create_performance_chart(self, parent, title, filepath):

        card = self.create_card(parent)
        card.pack(fill="both", expand=True, pady=(0, 15))

        self.create_label(card, title, 12).pack(
            anchor="w", padx=18, pady=(14, 5)
        )

        canvas = tk.Canvas(
            card,
            bg=COLORS["white"],
            height=210,
            highlightthickness=0
        )
        canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        if not os.path.exists(filepath):
            self.chart_error(
                canvas,
                "Results CSV not found. Run experiments from PowerShell first."
            )
            return

        try:

            with open(filepath, "r", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                headers = reader.fieldnames or []

            if not rows:
                raise ValueError("The CSV file is empty.")

            # Ignore invalid column headings.
            valid_headers = [
                h for h in headers
                if isinstance(h, str) and h.strip()
            ]

            time_header = None
            size_header = None

            for header in valid_headers:

                name = header.strip().lower()

                if "time" in name or "second" in name:
                    time_header = header

                if any(word in name for word in ("size", "digit", "point")):
                    size_header = header

            if time_header is None:
                raise ValueError(
                    "Could not identify the execution time column."
                )

            chart_data = []

            for row in rows:

                try:

                    raw_time = row.get(time_header)

                    if raw_time is None or not str(raw_time).strip():
                        continue

                    execution_time = float(raw_time)

                    if execution_time < 0:
                        continue

                    raw_size = (
                        row.get(size_header)
                        if size_header is not None
                        else None
                    )

                    label = (
                        str(raw_size).strip()
                        if raw_size is not None and str(raw_size).strip()
                        else str(len(chart_data) + 1)
                    )

                    chart_data.append((label, execution_time))

                except (ValueError, TypeError, AttributeError):
                    continue

            if not chart_data:
                raise ValueError("No valid timing values were found.")

            self.draw_bar_chart(canvas, chart_data)

        except Exception as error:
            self.chart_error(
                canvas, "Unable to display chart: " + str(error)
            )

    def chart_error(self, canvas, message):

        canvas.create_text(
            20, 35,
            text=message,
            anchor="w",
            fill=COLORS["muted"],
            font=("Segoe UI", 9)
        )

    def draw_bar_chart(self, canvas, chart_data):

        canvas.update_idletasks()

        width = max(canvas.winfo_width(), 450)
        height = max(canvas.winfo_height(), 190)

        left, right = 75, width - 25
        top, bottom = 15, height - 25

        maximum = max(value for label, value in chart_data)

        if maximum <= 0:
            maximum = 1

        canvas.create_line(
            left, top, left, bottom,
            fill=COLORS["border"]
        )

        canvas.create_line(
            left, bottom, right, bottom,
            fill=COLORS["border"]
        )

        count = len(chart_data)
        gap = 5
        available_height = bottom - top

        bar_height = max(
            5,
            (available_height - gap * count) / count
        )

        for index, (label, value) in enumerate(chart_data):

            y1 = top + index * (bar_height + gap)
            y2 = y1 + bar_height

            bar_width = (
                (right - left - 100) * value / maximum
            )

            canvas.create_text(
                left - 10,
                (y1 + y2) / 2,
                text=label,
                anchor="e",
                fill=COLORS["muted"],
                font=("Segoe UI", 8)
            )

            canvas.create_rectangle(
                left, y1,
                left + bar_width, y2,
                fill=COLORS["secondary"],
                outline=""
            )

            canvas.create_text(
                left + bar_width + 6,
                (y1 + y2) / 2,
                text="%.6f s" % value,
                anchor="w",
                fill=COLORS["text"],
                font=("Segoe UI", 8)
            )

    # --------------------------------------------------
    # ABOUT PROJECT
    # --------------------------------------------------

    def show_about(self):

        self.clear_content()
        self.create_page_header(
            "About Project",
            "Design and Analysis of Algorithms | CS302"
        )

        main = tk.Frame(self.content, bg=COLORS["background"])
        main.pack(fill="both", expand=True, padx=35, pady=(0, 25))

        description = self.create_card(main)
        description.pack(fill="x", pady=(0, 18))

        self.create_label(
            description, "DAA Algorithm Analyzer", 15
        ).pack(anchor="w", padx=20, pady=(20, 10))

        tk.Label(
            description,
            text=(
                "This project implements and analyzes two algorithms "
                "using the Divide and Conquer technique. "
                "Users can select input datasets, execute algorithms, "
                "view their results, and analyze execution times."
            ),
            font=("Segoe UI", 10),
            fg=COLORS["muted"],
            bg=COLORS["white"],
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        complexity = self.create_card(main)
        complexity.pack(fill="x")

        self.create_label(
            complexity, "Algorithm Information"
        ).pack(anchor="w", padx=20, pady=(18, 15))

        details = [
            ("Closest Pair of Points", "Divide and Conquer", "O(n log n)"),
            ("Integer Multiplication", "Karatsuba Algorithm", "O(n^1.585)")
        ]

        for title, method, complexity_value in details:

            row = tk.Frame(complexity, bg=COLORS["white"])
            row.pack(fill="x", padx=20, pady=(0, 15))

            self.create_label(row, title, 10).pack(anchor="w")

            tk.Label(
                row,
                text=method + "    |    Time Complexity: " + complexity_value,
                font=("Segoe UI", 9),
                fg=COLORS["secondary"],
                bg=COLORS["white"]
            ).pack(anchor="w", pady=(3, 0))


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------

def main():

    root = tk.Tk()
    app = AlgorithmAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
