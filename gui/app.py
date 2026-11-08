import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import csv
import time
import glob
import io
from contextlib import redirect_stdout


# ============================================================
# PROJECT SETUP
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

with redirect_stdout(io.StringIO()):
    from algorithms.closest_pair import closest_pair
    from algorithms.integer_multiplication import karatsuba_multiply


C = {
    # Main backgrounds
    "background": "#20271D",
    "panel": "#303B2B",
    "panel_light": "#3D4936",
    "panel_alt": "#4A563F",

    # Accent colors
    "blue": "#A8B58A",
    "blue_dark": "#87966B",
    "gold": "#D6B56D",
    "mint": "#B7C99A",

    # Text colors
    "white": "#F5F0E5",
    "muted": "#D0C9B6",
    "muted_dark": "#92977F",

    # Borders and alerts
    "border": "#697252",
    "red": "#D98F78",

    # Canvas
    "canvas": "#252E22",

    # Olive theme variants
    "burgundy": "#46533A",
    "burgundy_dark": "#252E22",
    "burgundy_light": "#5B6949"
}

# Recursion-tree accents
TREE_KIND_COLOR = {
    "root": "#D6B56D",
    "z0": "#C69B58",
    "z1": "#A8B58A",
    "z2": "#B7A18A",
    "base": "#B7C99A"
}
TREE_PENDING = "#92977F"
TREE_RADIUS = 36        # circle radius
TREE_SLOT_W = 170       # horizontal space per leaf (nodes never overlap)
TREE_LEVEL_H = 150      # vertical space between levels
TREE_TOP = 60

BRANCH_ORDER = ["z0", "z1", "z2"]
BRANCH_FORMULA = {
    "z0": "b × d",
    "z1": "(a + b) × (c + d)",
    "z2": "a × c",
}
BASE_CASE_TEXT = (
    "Base case rule: if x < 100 or y < 100 (at least one operand has at most "
    "two digits), the algorithm multiplies directly instead of splitting."
)


def short(value, limit=26):
    """Shorten very long numbers so Treeview rows stay readable."""
    if value is None:
        return "..."
    text = str(value)
    if len(text) <= limit:
        return text
    half = (limit - 3) // 2
    return f"{text[:half]}...{text[-half:]}  ({len(text)} digits)"


# ============================================================
# MAIN APPLICATION
# ============================================================

class AlgorithmAnalyzer:

    def __init__(self, root):
        self.root = root
        self.root.title("DAA Lab | Algorithm Analyzer")
        self.root.geometry("1320x900")
        self.root.minsize(1000, 700)
        self.root.configure(bg=C["background"])

        self.current_page = "Dashboard"
        self.trace_events = []
        self.visual_index = 0
        self.playing = False
        self.after_id = None

        self.current_algorithm = None
        self.current_points = []
        self.current_numbers = (0, 0)
        self.current_result = None

        # Karatsuba recursion-tree data
        self.karatsuba_tree = None
        self.tree_information = None
        self.reset_tree_state()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "DAA.TCombobox", fieldbackground=C["panel_light"],
            background=C["panel_light"], foreground=C["white"],
            arrowcolor=C["gold"], bordercolor=C["border"]
        )
        self.style.configure(
            "DAA.Treeview", background=C["burgundy_dark"], foreground=C["white"],
            fieldbackground=C["burgundy_dark"], bordercolor=C["gold"],
            rowheight=32, font=("Segoe UI", 10)
        )
        self.style.configure(
            "DAA.Treeview.Heading", background=C["burgundy"],
            foreground=C["gold"], font=("Segoe UI", 9, "bold")
        )
        self.style.map(
            "DAA.Treeview",
            background=[("selected", C["burgundy_light"])],
            foreground=[("selected", C["white"])]
        )

        self.build_shell()
        self.show_dashboard()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def reset_tree_state(self):
        self.karatsuba_root = None
        self.karatsuba_nodes = []
        self.selected_node = None
        self.tree_recenter = False

    # ========================================================
    # APPLICATION SHELL
    # ========================================================

    def build_shell(self):
        self.header = tk.Frame(self.root, bg=C["panel"], height=82)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        brand = tk.Frame(self.header, bg=C["panel"])
        brand.pack(side="left", padx=(25, 25), pady=13)
        tk.Label(brand, text="DAA LAB", font=("Segoe UI", 20, "bold"),
                 fg=C["white"], bg=C["panel"]).pack(anchor="w")
        tk.Label(brand, text="ALGORITHM ANALYZER", font=("Segoe UI", 8, "bold"),
                 fg=C["gold"], bg=C["panel"]).pack(anchor="w")

        nav = tk.Frame(self.header, bg=C["panel"])
        nav.pack(side="left", fill="y", expand=True, padx=8)

        self.nav_buttons = {}
        pages = [
            ("Dashboard", self.show_dashboard),
            ("Closest Pair", self.show_closest_pair),
            ("Karatsuba", self.show_karatsuba),
            ("Performance", self.show_performance),
            ("About", self.show_about),
        ]
        for label, command in pages:
            button = tk.Button(
                nav, text=label, command=command,
                font=("Segoe UI", 10, "bold"), fg=C["muted"], bg=C["panel"],
                activeforeground=C["gold"], activebackground=C["panel_light"],
                relief="flat", bd=0, padx=15, pady=12, cursor="hand2"
            )
            button.pack(side="left", padx=2, pady=17)
            self.nav_buttons[label] = button

        tk.Label(self.header, text="CS302  |  FALL 2026",
                 font=("Segoe UI", 9, "bold"),
                 fg=C["gold"], bg=C["panel"]).pack(side="right", padx=25)

        self.body = tk.Frame(self.root, bg=C["background"])
        self.body.pack(fill="both", expand=True)

        self.page_canvas = tk.Canvas(self.body, bg=C["background"],
                                     highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.body, orient="vertical",
                                       command=self.page_canvas.yview)
        self.page_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.page_canvas.pack(side="left", fill="both", expand=True)

        self.page = tk.Frame(self.page_canvas, bg=C["background"])
        self.page_window = self.page_canvas.create_window(
            (0, 0), window=self.page, anchor="nw"
        )
        self.page.bind("<Configure>", self.update_scroll_region)
        self.page_canvas.bind("<Configure>", self.update_page_width)
        self.page_canvas.bind("<Enter>", self.bind_mousewheel)
        self.page_canvas.bind("<Leave>", self.unbind_mousewheel)

    def update_scroll_region(self, event=None):
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox("all"))

    def update_page_width(self, event):
        self.page_canvas.itemconfigure(self.page_window, width=event.width)

    def bind_mousewheel(self, event=None):
        self.page_canvas.bind_all("<MouseWheel>", self.mousewheel)

    def unbind_mousewheel(self, event=None):
        self.page_canvas.unbind_all("<MouseWheel>")

    def mousewheel(self, event):
        # Let the Treeview scroll itself when the mouse is over it.
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is not None and widget is getattr(self, "tree_canvas", None):
            self.tree_canvas.yview_scroll(int(-event.delta / 120), "units")
            return
        if isinstance(widget, tk.Text):
            return
        self.page_canvas.yview_scroll(int(-event.delta / 120), "units")

    def close_app(self):
        self.stop_playback()
        self.root.destroy()

    def clear_page(self):
        self.stop_playback()
        for widget in self.page.winfo_children():
            widget.destroy()
        self.page_canvas.yview_moveto(0)

    def set_active_nav(self, page_name):
        self.current_page = page_name
        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.configure(bg=C["panel_alt"], fg=C["gold"],
                                 activebackground=C["panel_alt"])
            else:
                button.configure(bg=C["panel"], fg=C["muted"],
                                 activebackground=C["panel_light"])

    # ========================================================
    # REUSABLE UI HELPERS
    # ========================================================

    def page_header(self, title, subtitle):
        frame = tk.Frame(self.page, bg=C["background"])
        frame.pack(fill="x", padx=32, pady=(26, 20))
        tk.Label(frame, text=title, font=("Segoe UI", 23, "bold"),
                 fg=C["white"], bg=C["background"]).pack(anchor="w")
        tk.Label(frame, text=subtitle, font=("Segoe UI", 10),
                 fg=C["muted"], bg=C["background"]).pack(anchor="w", pady=(5, 0))

    def section_card(self, parent, title, subtitle=None):
        card = tk.Frame(parent, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 16))
        heading = tk.Frame(card, bg=C["panel"])
        heading.pack(fill="x", padx=20, pady=(16, 10))
        tk.Label(heading, text=title, font=("Segoe UI", 13, "bold"),
                 fg=C["white"], bg=C["panel"]).pack(anchor="w")
        if subtitle:
            tk.Label(heading, text=subtitle, font=("Segoe UI", 9),
                     fg=C["muted"], bg=C["panel"]).pack(anchor="w", pady=(4, 0))
        return card

    def make_button(self, parent, text, command, primary=True):
        bg = C["gold"] if primary else C["panel_light"]
        fg = C["background"] if primary else C["white"]
        return tk.Button(
            parent, text=text, command=command,
            font=("Segoe UI", 9, "bold"), bg=bg, fg=fg,
            activebackground=C["blue"], activeforeground=C["background"],
            relief="flat", bd=0, padx=17, pady=10, cursor="hand2"
        )

    def make_output(self, parent, height=8):
        box = tk.Text(
            parent, height=height, wrap="word", font=("Consolas", 9),
            bg=C["canvas"], fg=C["white"], insertbackground=C["gold"],
            relief="flat", padx=14, pady=12
        )
        box.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        box.insert("1.0", "Run the algorithm to display its results.")
        box.configure(state="disabled")
        return box

    def set_output(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def format_number(self, number, group_size=10):
        value = str(number)
        sign = ""
        if value.startswith("-"):
            sign, value = "-", value[1:]
        chunks = [value[i:i + group_size]
                  for i in range(0, len(value), group_size)]
        return sign + " ".join(chunks)

    def make_status(self, parent, text):
        label = tk.Label(parent, text=text, font=("Segoe UI", 9),
                         fg=C["muted"], bg=C["panel"])
        label.pack(anchor="w", padx=20, pady=(0, 14))
        return label

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):
        self.clear_page()
        self.set_active_nav("Dashboard")
        self.page_header(
            "Dashboard",
            "Explore and execute the algorithms implemented for CS302."
        )

        main = tk.Frame(self.page, bg=C["background"])
        main.pack(fill="both", padx=32, pady=(0, 30))

        hero = tk.Frame(main, bg=C["panel_alt"], height=175)
        hero.pack(fill="x", pady=(0, 18))
        hero.pack_propagate(False)
        tk.Label(hero, text="Welcome to the Algorithm Laboratory",
                 font=("Segoe UI", 22, "bold"),
                 fg=C["white"], bg=C["panel_alt"]).pack(anchor="w", padx=25, pady=(30, 8))
        tk.Label(hero,
                 text="Visualize recursive execution, inspect results, and analyze performance.",
                 font=("Segoe UI", 10), fg=C["muted"],
                 bg=C["panel_alt"]).pack(anchor="w", padx=25)

        cp_count = len(glob.glob(os.path.join(
            PROJECT_ROOT, "datasets", "closest_pair", "*.txt")))
        im_count = len(glob.glob(os.path.join(
            PROJECT_ROOT, "datasets", "integer_multiplication", "*.txt")))

        stats = tk.Frame(main, bg=C["background"])
        stats.pack(fill="x", pady=(0, 22))
        for title, value in [
            ("Closest Pair Datasets", cp_count),
            ("Karatsuba Datasets", im_count),
            ("Total Datasets", cp_count + im_count),
        ]:
            card = tk.Frame(stats, bg=C["panel"],
                            highlightbackground=C["border"], highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(card, text=title, font=("Segoe UI", 9),
                     fg=C["muted"], bg=C["panel"]).pack(anchor="w", padx=17, pady=(14, 4))
            tk.Label(card, text=str(value), font=("Segoe UI", 25, "bold"),
                     fg=C["gold"], bg=C["panel"]).pack(anchor="w", padx=17, pady=(0, 13))

        tk.Label(main, text="Available Algorithms",
                 font=("Segoe UI", 15, "bold"),
                 fg=C["white"], bg=C["background"]).pack(anchor="w", pady=(0, 12))

        cards = tk.Frame(main, bg=C["background"])
        cards.pack(fill="x")
        self.dashboard_card(
            cards, "Closest Pair of Points",
            "Find the two closest points in a two-dimensional dataset.",
            "Divide and Conquer  |  O(n log n)", self.show_closest_pair)
        self.dashboard_card(
            cards, "Karatsuba Multiplication",
            "Multiply large integers using three recursive products.",
            "Karatsuba  |  O(n^1.585)", self.show_karatsuba)

    def dashboard_card(self, parent, title, description, complexity, command):
        card = tk.Frame(parent, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Label(card, text=title, font=("Segoe UI", 13, "bold"),
                 fg=C["white"], bg=C["panel"]).pack(anchor="w", padx=18, pady=(18, 8))
        tk.Label(card, text=description, font=("Segoe UI", 9),
                 fg=C["muted"], bg=C["panel"], wraplength=400,
                 justify="left").pack(anchor="w", padx=18)
        tk.Label(card, text=complexity, font=("Segoe UI", 9, "bold"),
                 fg=C["gold"], bg=C["panel"]).pack(anchor="w", padx=18, pady=13)
        self.make_button(card, "Open Algorithm", command,
                         primary=False).pack(anchor="w", padx=18, pady=(0, 18))

    # ========================================================
    # COMMON ALGORITHM PAGE
    # ========================================================

    def create_algorithm_page(self, page_name, title, subtitle, folder):
        self.clear_page()
        self.set_active_nav(page_name)
        self.page_header(title, subtitle)

        # Old tree widgets were destroyed by clear_page().
        self.karatsuba_tree = None
        self.tree_information = None
        self.tree_canvas = None
        self.reset_tree_state()

        main = tk.Frame(self.page, bg=C["background"])
        main.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        input_card = self.section_card(
            main, "01  |  INPUT DATASET",
            "Choose a prepared input file, then run the algorithm.")

        file_row = tk.Frame(input_card, bg=C["panel"])
        file_row.pack(fill="x", padx=20, pady=(0, 12))

        path_var = tk.StringVar(value="No dataset selected")
        tk.Label(file_row, textvariable=path_var, font=("Segoe UI", 9),
                 fg=C["muted"], bg=C["panel_light"],
                 anchor="w").pack(side="left", fill="x", expand=True,
                                  padx=(0, 10), ipady=11)

        def browse():
            filename = filedialog.askopenfilename(
                title="Select input dataset",
                initialdir=os.path.join(PROJECT_ROOT, "datasets", folder),
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                path_var.set(filename)

        self.make_button(file_row, "Browse", browse,
                         primary=False).pack(side="left")

        run_row = tk.Frame(input_card, bg=C["panel"])
        run_row.pack(fill="x", padx=20, pady=(0, 17))
        run_button = self.make_button(run_row, "Run Algorithm", lambda: None)
        run_button.pack(side="left")
        status = self.make_status(run_row, "Ready. Select a dataset to begin.")
        status.pack(side="left", padx=(15, 0), pady=0)

        if page_name == "Karatsuba":
            self.build_karatsuba_section(main)
        else:
            self.build_live_execution_section(main)

        result_card = self.section_card(
            main, "03  |  FINAL RESULTS",
            "The measured result and performance information are displayed here.")
        self.result_output = self.make_output(result_card, height=9)

        self.trace_events = []
        self.visual_index = 0
        self.current_algorithm = page_name

        return path_var, status, run_button

    def build_live_execution_section(self, main):
        # Closest Pair only: canvas + Previous / Play / Next playback.
        visual_card = self.section_card(
            main, "02  |  LIVE EXECUTION",
            "Inspect the algorithm's actual execution events.")

        canvas = tk.Canvas(visual_card, height=390, bg=C["canvas"],
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        explanation = tk.Label(
            visual_card,
            text="The execution visualization will appear here after you run the algorithm.",
            font=("Segoe UI", 9), fg=C["muted"], bg=C["panel"],
            anchor="w", justify="left", wraplength=1050)
        explanation.pack(fill="x", padx=20, pady=(0, 12))

        controls = tk.Frame(visual_card, bg=C["panel"])
        controls.pack(fill="x", padx=18, pady=(0, 17))

        previous = self.make_button(controls, "◀ Previous",
                                    self.previous_step, primary=False)
        previous.pack(side="left", padx=(0, 7))
        play = self.make_button(controls, "▶ Play",
                                self.toggle_playback, primary=True)
        play.pack(side="left", padx=7)
        next_button = self.make_button(controls, "Next ▶",
                                       self.next_step, primary=False)
        next_button.pack(side="left", padx=7)

        tk.Label(controls, text="Speed", font=("Segoe UI", 9, "bold"),
                 fg=C["muted"], bg=C["panel"]).pack(side="left", padx=(25, 7))
        speed = ttk.Combobox(controls, state="readonly", width=8,
                             values=["0.5x", "1x", "2x"], style="DAA.TCombobox")
        speed.set("1x")
        speed.pack(side="left")

        counter = tk.Label(controls, text="Step 0 / 0",
                           font=("Segoe UI", 9, "bold"),
                           fg=C["gold"], bg=C["panel"])
        counter.pack(side="right", padx=5)

        self.visual_canvas = canvas
        self.visual_explanation = explanation
        self.visual_counter = counter
        self.play_button = play
        self.previous_button = previous
        self.next_button = next_button
        self.speed_box = speed

        previous.configure(state="disabled")
        play.configure(state="disabled")
        next_button.configure(state="disabled")

    def build_karatsuba_section(self, main):
        # Karatsuba: circle-and-edge recursion tree + information panel.
        card = self.section_card(
            main, "02  |  RECURSION TREE",
            "Click a recursive circle to expand or collapse its z0, z1, z2 children. "
            "Click any circle to inspect it.")

        legend = tk.Frame(card, bg=C["panel"])
        legend.pack(fill="x", padx=20, pady=(0, 8))
        for text, color in [("Root", TREE_KIND_COLOR["root"]),
                            ("z0", TREE_KIND_COLOR["z0"]),
                            ("z1", TREE_KIND_COLOR["z1"]),
                            ("z2", TREE_KIND_COLOR["z2"]),
                            ("Base case (leaf)", TREE_KIND_COLOR["base"])]:
            tk.Label(legend, text="●", font=("Segoe UI", 12),
                     fg=color, bg=C["panel"]).pack(side="left")
            tk.Label(legend, text=text, font=("Segoe UI", 9),
                     fg=C["muted"], bg=C["panel"]).pack(side="left", padx=(2, 14))
        tk.Label(legend, text="+ collapsed     − expanded",
                 font=("Segoe UI", 9, "bold"),
                 fg=C["gold"], bg=C["panel"]).pack(side="left", padx=(10, 0))

        frame = tk.Frame(card, bg=C["burgundy_dark"],
                         highlightbackground=C["gold"], highlightthickness=1)
        frame.pack(fill="x", padx=18, pady=(0, 10))

        canvas = tk.Canvas(frame, height=480, bg=C["burgundy_dark"],
                           highlightthickness=0)
        xscroll = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        xscroll.pack(side="bottom", fill="x")
        yscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<Configure>", lambda e: self.draw_recursion_tree())

        info = tk.Text(
            card, height=14, wrap="word", font=("Consolas", 10),
            bg=C["burgundy_dark"], fg=C["white"], relief="flat",
            padx=14, pady=10, highlightbackground=C["gold"],
            highlightthickness=1)
        info.pack(fill="x", padx=18, pady=(0, 16))
        info.tag_configure("title", foreground=C["gold"],
                           font=("Segoe UI", 12, "bold"))
        info.tag_configure("key", foreground=C["gold"],
                           font=("Consolas", 10, "bold"))
        info.tag_configure("note", foreground=C["muted"])
        info.insert("1.0", "Run Karatsuba, then click a circle to inspect its working.")
        info.configure(state="disabled")

        self.tree_canvas = canvas
        self.tree_information = info

        # No playback on this page.
        self.play_button = None
        self.previous_button = None
        self.next_button = None
        self.speed_box = None

    # ========================================================
    # DATASET READING
    # ========================================================

    def read_closest_dataset(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()
        if not lines:
            raise ValueError("The selected dataset is empty.")

        expected = int(lines[0].strip())
        points = []
        for line in lines[1:]:
            values = line.split()
            if len(values) >= 2:
                points.append((float(values[0]), float(values[1])))

        if len(points) != expected:
            raise ValueError(
                f"Dataset header says {expected} points, but {len(points)} were read.")
        if len(points) < 2:
            raise ValueError("At least two points are required.")
        return points

    def read_integer_dataset(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
        if len(lines) < 2:
            raise ValueError("The dataset must contain two integers.")
        return int(lines[0]), int(lines[1])

    # ========================================================
    # TRACE PLAYBACK
    # ========================================================

    def prepare_trace(self, events):
        self.stop_playback()
        self.trace_events = events
        self.visual_index = 0

        state = "normal" if events else "disabled"
        self.previous_button.configure(state=state)
        self.play_button.configure(state=state)
        self.next_button.configure(state=state)

        if events:
            self.show_step(0)

    def previous_step(self):
        if self.visual_index > 0:
            self.show_step(self.visual_index - 1)

    def next_step(self):
        if self.visual_index < len(self.trace_events) - 1:
            self.show_step(self.visual_index + 1)
        else:
            self.stop_playback()

    def toggle_playback(self):
        if not self.trace_events:
            return
        if self.playing:
            self.stop_playback()
        else:
            if self.visual_index >= len(self.trace_events) - 1:
                self.show_step(0)
            self.playing = True
            self.play_button.configure(text="Ⅱ Pause")
            self.schedule_next()

    def schedule_next(self):
        if not self.playing:
            return
        if self.visual_index >= len(self.trace_events) - 1:
            self.stop_playback()
            return
        factor = {"0.5x": 2.0, "1x": 1.0, "2x": 0.5}.get(self.speed_box.get(), 1.0)
        self.after_id = self.root.after(int(650 * factor), self.advance_playback)

    def advance_playback(self):
        self.after_id = None
        if not self.playing:
            return
        self.show_step(self.visual_index + 1)
        self.schedule_next()

    def stop_playback(self):
        self.playing = False
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        if getattr(self, "play_button", None) is not None:
            try:
                self.play_button.configure(text="▶ Play")
            except tk.TclError:
                pass

    def show_step(self, index):
        if not self.trace_events:
            return

        self.visual_index = max(0, min(index, len(self.trace_events) - 1))
        event = self.trace_events[self.visual_index]

        explanation = self.draw_closest_event(event)

        self.visual_explanation.configure(text=explanation)
        self.visual_counter.configure(
            text=f"Step {self.visual_index + 1} / {len(self.trace_events)}")

    # ========================================================
    # CLOSEST PAIR
    # ========================================================

    def show_closest_pair(self):
        path_var, status, run_button = self.create_algorithm_page(
            "Closest Pair", "Closest Pair of Points",
            "Watch divide-and-conquer split the points, inspect the strip, and identify the closest pair.",
            "closest_pair")
        run_button.configure(
            command=lambda: self.run_closest_pair(path_var, status))

    def run_closest_pair(self, path_var, status):
        filepath = path_var.get()
        if not filepath or filepath == "No dataset selected":
            messagebox.showwarning(
                "Dataset required",
                "Please browse and select a closest-pair dataset.")
            return

        try:
            points = self.read_closest_dataset(filepath)

            start = time.perf_counter()
            measured_result = closest_pair(points)
            elapsed = time.perf_counter() - start

            events = []
            traced_result = closest_pair(points, trace_callback=events.append)
            if traced_result != measured_result:
                raise RuntimeError(
                    "Traced execution did not match the measured result.")

            pair, distance = measured_result
            self.current_points = points
            self.current_result = measured_result
            self.current_algorithm = "Closest Pair"

            result_text = (
                "ALGORITHM: Closest Pair of Points\n"
                "METHOD: Divide and Conquer\n\n"
                f"Dataset: {os.path.basename(filepath)}\n"
                f"Number of points: {len(points)}\n\n"
                f"Closest point 1: {pair[0]}\n"
                f"Closest point 2: {pair[1]}\n"
                f"Minimum distance: {distance:.10f}\n\n"
                "TIME COMPLEXITY: O(n log n)\n"
                f"Execution time: {elapsed:.8f} seconds\n"
                "Correctness: Verified"
            )
            self.set_output(self.result_output, result_text)
            status.configure(text="Execution completed successfully.", fg=C["mint"])
            self.prepare_trace(events)

        except Exception as error:
            messagebox.showerror("Closest Pair Error", str(error))
            status.configure(text="Execution failed.", fg=C["red"])

    def draw_closest_event(self, event):
        canvas = self.visual_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 700)
        height = max(canvas.winfo_height(), 330)
        points = self.current_points
        if not points:
            return "No points are available to visualize."

        margin = 45
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = max(max_x - min_x, 1)
        range_y = max(max_y - min_y, 1)
        plot_w = width - 2 * margin
        plot_h = height - 2 * margin

        def xy(point):
            px = margin + ((point[0] - min_x) / range_x) * plot_w
            py = height - margin - ((point[1] - min_y) / range_y) * plot_h
            return px, py

        for i in range(1, 6):
            gx = margin + plot_w * i / 6
            gy = margin + plot_h * i / 6
            canvas.create_line(gx, margin, gx, height - margin, fill="#37422F")
            canvas.create_line(margin, gy, width - margin, gy, fill="#37422F")

        canvas.create_text(margin, 15, text="2D POINT DISTRIBUTION",
                           fill=C["gold"], anchor="w",
                           font=("Segoe UI", 10, "bold"))

        event_type = event.get("type")
        depth = event.get("depth", 0)

        active_points = set()
        left_points = set(event.get("left_points", []))
        right_points = set(event.get("right_points", []))
        strip_points = set(event.get("strip", []))
        pair_to_highlight = event.get("pair")
        compare_pair = None

        if event_type == "base_start":
            active_points = set(event.get("points", []))
        elif event_type == "divide":
            active_points = left_points | right_points
        elif event_type == "strip":
            active_points = strip_points
        elif event_type in ("compare", "strip_compare"):
            compare_pair = (event.get("point1"), event.get("point2"))
            active_points = set(compare_pair)

        if event_type == "divide":
            mid_x = event.get("mid_x")
            if mid_x is not None:
                line_x, _ = xy((mid_x, min_y))
                canvas.create_line(line_x, margin, line_x, height - margin,
                                   fill=C["gold"], width=2, dash=(7, 4))
                canvas.create_text(line_x + 7, margin + 12, text="DIVIDE",
                                   fill=C["gold"], anchor="w",
                                   font=("Segoe UI", 8, "bold"))

        if event_type == "strip":
            mid_x = event.get("mid_x")
            distance = event.get("minimum_distance", 0)
            if mid_x is not None:
                left_coord = xy((mid_x - distance, min_y))[0]
                right_coord = xy((mid_x + distance, min_y))[0]
                canvas.create_rectangle(
                    left_coord, margin, right_coord, height - margin,
                    fill="#5A5430", stipple="gray25", outline=C["gold"])

        for point in points:
            px, py = xy(point)
            color, radius = C["muted_dark"], 3
            if point in left_points:
                color, radius = C["blue"], 5
            if point in right_points:
                color, radius = C["mint"], 5
            if point in strip_points:
                color, radius = C["gold"], 5
            if point in active_points:
                color, radius = C["gold"], 6
            canvas.create_oval(px - radius, py - radius, px + radius,
                               py + radius, fill=color, outline="")

        if compare_pair and all(p is not None for p in compare_pair):
            p1, p2 = xy(compare_pair[0]), xy(compare_pair[1])
            canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                               fill=C["blue"], width=3)

        if pair_to_highlight and len(pair_to_highlight) == 2:
            try:
                p1, p2 = xy(pair_to_highlight[0]), xy(pair_to_highlight[1])
                canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                   fill=C["gold"], width=4)
                for px, py in (p1, p2):
                    canvas.create_oval(px - 8, py - 8, px + 8, py + 8,
                                       outline=C["gold"], width=2)
            except (TypeError, ValueError):
                pass

        descriptions = {
            "algorithm_start": f"Algorithm started with {event.get('total_points')} points.",
            "recursive_start": f"Recursive call at depth {depth}: processing {len(event.get('points', []))} points.",
            "divide": f"Divide step at recursion depth {depth}. The points are split around x = {event.get('mid_x')}.",
            "base_start": f"Base case: {len(event.get('points', []))} points. The algorithm checks pairs directly.",
            "compare": f"Brute-force comparison: {event.get('point1')} and {event.get('point2')}. Distance = {event.get('distance', 0):.6f}.",
            "base_complete": f"Base case complete. Best pair: {event.get('pair')}; distance = {event.get('distance')}.",
            "combine": f"Combine step: compare left distance {event.get('left_distance')} with right distance {event.get('right_distance')}. Current best distance = {event.get('distance')}.",
            "strip": f"Strip created. {len(event.get('strip', []))} points are inside the strip.",
            "strip_compare": f"Cross-boundary comparison: {event.get('point1')} and {event.get('point2')}. Distance = {event.get('distance', 0):.6f}.",
            "new_minimum": f"New minimum found: {event.get('pair')} with distance {event.get('distance')}.",
            "recursive_complete": f"Recursive subproblem complete. Best pair: {event.get('pair')}; distance = {event.get('distance')}.",
            "algorithm_complete": f"Algorithm complete. Closest pair: {event.get('pair')}; minimum distance = {event.get('distance')}.",
        }
        return descriptions.get(event_type, f"Processing event: {event_type}")

    # ========================================================
    # KARATSUBA: PAGE AND RUN
    # ========================================================

    def show_karatsuba(self):
        path_var, status, run_button = self.create_algorithm_page(
            "Karatsuba", "Karatsuba Integer Multiplication",
            "Click the circles to expand the recursion tree and inspect every z0, z1 and z2 call.",
            "integer_multiplication")
        run_button.configure(
            command=lambda: self.run_karatsuba(path_var, status))

    def run_karatsuba(self, path_var, status):
        filepath = path_var.get()
        if not filepath or filepath == "No dataset selected":
            messagebox.showwarning(
                "Dataset required",
                "Please browse and select a Karatsuba dataset.")
            return

        try:
            x, y = self.read_integer_dataset(filepath)

            start = time.perf_counter()
            measured_result = karatsuba_multiply(x, y)
            elapsed = time.perf_counter() - start

            events = []
            traced_result = karatsuba_multiply(x, y, trace_callback=events.append)
            if traced_result != measured_result:
                raise RuntimeError(
                    "Traced execution did not match the measured result.")

            correct = measured_result == x * y

            self.current_numbers = (x, y)
            self.current_result = measured_result
            self.current_algorithm = "Karatsuba"

            # Build the (in-memory) recursion model, then show level 1 only.
            self.build_karatsuba_tree(events)

            result_text = (
                "ALGORITHM: Karatsuba Integer Multiplication\n"
                f"Dataset: {os.path.basename(filepath)}\n\n"
                f"First operand digits: {len(str(abs(x)))}\n"
                f"Second operand digits: {len(str(abs(y)))}\n\n"
                "FIRST NUMBER:\n" + self.format_number(x) + "\n\n"
                "SECOND NUMBER:\n" + self.format_number(y) + "\n\n"
                "PRODUCT:\n" + self.format_number(measured_result) + "\n\n"
                f"Recursive calls (tree nodes): {len(self.karatsuba_nodes)}\n"
                "BASE CASE: direct multiplication when x < 100 or y < 100\n"
                "TIME COMPLEXITY: O(n^1.585)\n"
                f"Execution time: {elapsed:.8f} seconds\n"
                f"Correctness: {correct}"
            )
            self.set_output(self.result_output, result_text)
            status.configure(text="Execution completed successfully.", fg=C["mint"])

            self.populate_karatsuba_tree()

        except Exception as error:
            messagebox.showerror("Karatsuba Error", str(error))
            status.configure(text="Execution failed.", fg=C["red"])

    # ========================================================
    # KARATSUBA: RECURSION MODEL BUILT FROM THE REAL TRACE
    # ========================================================

    def build_karatsuba_tree(self, events):
        # Turn the flat trace into a parent/child tree (z0, z1, z2 children).
        self.karatsuba_root = None
        self.karatsuba_nodes = []
        stack = []

        for event in events:
            event_type = event.get("type")

            if event_type == "recursive_start":
                node = {
                    "x": event.get("x"), "y": event.get("y"),
                    "depth": event.get("depth", 0),
                    "branch": event.get("branch"),
                    "result": None, "split": None, "middle": None,
                    "children": {}, "pending_branch": None,
                    "parent": None, "expanded": False,
                }
                if stack:
                    parent = stack[-1]
                    branch = event.get("branch") or parent.get("pending_branch")
                    if branch not in BRANCH_ORDER:
                        branch = "z0"
                    node["branch"] = branch
                    node["parent"] = parent
                    parent["children"][branch] = node
                elif self.karatsuba_root is None:
                    self.karatsuba_root = node

                self.karatsuba_nodes.append(node)
                stack.append(node)

            elif event_type == "split" and stack:
                stack[-1]["split"] = {k: event.get(k)
                                      for k in ("a", "b", "c", "d", "m")}

            elif event_type == "branch_start" and stack:
                stack[-1]["pending_branch"] = event.get("branch")

            elif event_type == "middle_term" and stack:
                stack[-1]["middle"] = {k: event.get(k) for k in
                                       ("z1_product", "z2", "z0", "result")}

            elif event_type == "recursive_complete" and stack:
                node = stack.pop()
                node["result"] = event.get("result")
                node["depth"] = event.get("depth", node["depth"])

            elif event_type == "algorithm_complete":
                if self.karatsuba_root is not None:
                    self.karatsuba_root["result"] = event.get("result")

    def is_base_node(self, node):
        return (node is not None and node.get("split") is None
                and not node["children"])

    def visible_children(self, node):
        if not node.get("expanded"):
            return []
        return [node["children"][b] for b in BRANCH_ORDER
                if b in node["children"]]

    def populate_karatsuba_tree(self):
        root = self.karatsuba_root
        self.selected_node = root
        self.tree_recenter = True
        if root is not None:
            root["expanded"] = bool(root["children"])
            self.show_node_information(root)
        self.draw_recursion_tree()

    # ========================================================
    # KARATSUBA: CIRCLE-AND-EDGE TREE DRAWING
    # ========================================================

    @staticmethod
    def tiny(value, limit=8):
        text = str(value)
        if len(text) <= limit:
            return text
        return f"{text[:3]}…{text[-3:]}"

    def draw_recursion_tree(self):
        canvas = self.tree_canvas
        if canvas is None:
            return
        try:
            canvas.delete("all")
        except tk.TclError:
            return

        cw = max(canvas.winfo_width(), 500)
        root = self.karatsuba_root

        if root is None:
            canvas.create_text(
                cw / 2, 220, text="Run Karatsuba to generate the recursion tree.",
                fill=C["muted"], font=("Segoe UI", 11))
            canvas.configure(scrollregion=(0, 0, cw, 480))
            return

        # ---- layout: leaves get consecutive slots, parents are centred ----
        positions, order = {}, []
        state = {"slot": 0, "levels": 0}

        def place(node, level):
            state["levels"] = max(state["levels"], level)
            order.append(node)
            kids = self.visible_children(node)
            if not kids:
                x = state["slot"] * TREE_SLOT_W + TREE_SLOT_W / 2
                state["slot"] += 1
            else:
                xs = [place(k, level + 1) for k in kids]
                x = (xs[0] + xs[-1]) / 2
            positions[id(node)] = (x, TREE_TOP + level * TREE_LEVEL_H)
            return x

        place(root, 0)

        total_w = state["slot"] * TREE_SLOT_W
        total_h = max(480, TREE_TOP + state["levels"] * TREE_LEVEL_H + 130)
        offset = max(0, (cw - total_w) / 2)          # keep the tree centred
        canvas.configure(scrollregion=(0, 0, max(cw, total_w), total_h))

        r = TREE_RADIUS

        # ---- edges first (so circles sit on top) ----
        for node in order:
            px, py = positions[id(node)]
            for kid in self.visible_children(node):
                cx, cy = positions[id(kid)]
                canvas.create_line(px + offset, py + r, cx + offset, cy - r,
                                   fill="#B08D57", width=1.5)

        # ---- nodes ----
        for node in order:
            x, y = positions[id(node)]
            x += offset
            is_root = node is root
            is_base = self.is_base_node(node)
            branch = node.get("branch")
            kind = "root" if is_root else ("base" if is_base else branch)
            accent = TREE_KIND_COLOR.get(kind, C["gold"])
            name = "ROOT" if is_root else str(branch)
            expanded = bool(node.get("expanded")) and not is_base
            tag = f"n{id(node)}"

            if node is getattr(self, "selected_node", None):
                canvas.create_oval(x - r - 8, y - r - 8, x + r + 8, y + r + 8,
                                   outline=C["white"], width=1, dash=(4, 3),
                                   tags=(tag,))

            if is_base and not is_root:
                fill, outline, width = "#465B3D", C["mint"], 2
                text_color, sub_color = "#F5F0E5", "#D0D9B9"
            else:
                fill = accent
                outline = C["white"] if expanded else "#252E22"
                width = 4 if expanded else 2
                text_color, sub_color = "#252E22", "#303B2B"

            canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill,
                               outline=outline, width=width, tags=(tag,))
            canvas.create_text(x, y - 9, text=name, fill=text_color,
                               font=("Segoe UI", 11, "bold"), tags=(tag,))
            result = node.get("result")
            canvas.create_text(
                x, y + 11,
                text=f"= {self.tiny(result)}" if result is not None else "...",
                fill=sub_color, font=("Consolas", 8, "bold"), tags=(tag,))

            # Expansion indicator on recursive nodes.
            if not is_base:
                canvas.create_oval(x - 10, y + r - 10, x + 10, y + r + 10,
                                   fill=C["burgundy_dark"], outline=C["gold"],
                                   width=2, tags=(tag,))
                canvas.create_text(x, y + r, text="−" if expanded else "+",
                                   fill=C["gold"],
                                   font=("Segoe UI", 12, "bold"), tags=(tag,))

            # Operands + depth label below the circle.
            label = canvas.create_text(
                x, y + r + 30,
                text=f"{self.tiny(node.get('x'), 9)} × {self.tiny(node.get('y'), 9)}"
                     f"\ndepth {node.get('depth')}",
                fill=C["white"], font=("Consolas", 9), justify="center",
                tags=(tag,))
            bx1, by1, bx2, by2 = canvas.bbox(label)
            backing = canvas.create_rectangle(
                bx1 - 3, by1 - 1, bx2 + 3, by2 + 1,
                fill=C["burgundy_dark"], outline="", tags=(tag,))
            canvas.tag_lower(backing, label)

            canvas.tag_bind(tag, "<Button-1>",
                            lambda e, n=node: self.on_node_click(n))
            canvas.tag_bind(tag, "<Enter>",
                            lambda e: canvas.configure(cursor="hand2"))
            canvas.tag_bind(tag, "<Leave>",
                            lambda e: canvas.configure(cursor=""))

        # Bring the root into view the first time a wide tree is drawn.
        if getattr(self, "tree_recenter", False):
            self.tree_recenter = False
            if total_w > cw:
                root_x = positions[id(root)][0]
                canvas.xview_moveto(max(0, (root_x - cw / 2) / total_w))
            canvas.yview_moveto(0)

    def on_node_click(self, node):
        self.selected_node = node
        if node["children"]:                       # recursive node: toggle
            node["expanded"] = not node.get("expanded", False)
        self.show_node_information(node)
        self.draw_recursion_tree()

    # ========================================================
    # KARATSUBA: INFORMATION PANEL
    # ========================================================

    def write_tree_info(self, title, fields, notes=""):
        box = self.tree_information
        if box is None:
            return
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", title + "\n", "title")
        for name, value in fields:
            box.insert("end", f"{name}: ", "key")
            box.insert("end", f"{value}\n")
        if notes:
            box.insert("end", "\n" + notes, "note")
        box.configure(state="disabled")
        box.yview_moveto(0)

    def show_node_information(self, node):
        if node is None:
            return

        x, y = node.get("x"), node.get("y")
        parent = node.get("parent")
        branch = node.get("branch")
        is_base = self.is_base_node(node)
        result = node.get("result")
        name = "Root" if parent is None else branch

        fields = [
            ("Branch", name),
            ("Operand X", short(x, 70)),
            ("Operand Y", short(y, 70)),
            ("Multiplication", f"{short(x, 30)} × {short(y, 30)}"),
            ("Result", short(result, 70) if result is not None else "calculating..."),
            ("Recursion depth", node.get("depth")),
        ]

        if parent is None:
            fields.append(("Formula", "x × y   (the original problem)"))
        else:
            fields.append(("Formula", f"{branch} = {BRANCH_FORMULA[branch]}"))
            ps = parent.get("split")
            if ps:
                a, b, c, d = ps["a"], ps["b"], ps["c"], ps["d"]
                substituted = {
                    "z0": f"{b} × {d}",
                    "z1": f"({a} + {b}) × ({c} + {d})",
                    "z2": f"{a} × {c}",
                }[branch]
                fields.append(("Substituted", short(substituted, 90)))

        if is_base:
            fields.append(("Status", "BASE CASE (leaf node)"))
        else:
            state = "expanded" if node.get("expanded") else "collapsed - click to expand"
            fields.append(("Status", f"RECURSIVE NODE ({state})"))

        notes = []
        if is_base:
            small = []
            try:
                if abs(int(x)) < 100:
                    small.append(f"X = {x} is below 100")
                if abs(int(y)) < 100:
                    small.append(f"Y = {y} is below 100")
            except (TypeError, ValueError):
                pass
            why = " and ".join(small) if small else "an operand is below 100"
            notes.append(
                "EXPLANATION: the base-case rule is x < 100 or y < 100 (at least "
                f"one operand has at most two digits). Here {why}, so direct "
                f"multiplication is performed: {short(x, 30)} × {short(y, 30)} = "
                f"{short(result, 40)}. No further recursion is required."
            )
        else:
            sp = node.get("split") or {}
            notes.append(
                "EXPLANATION: both operands are at least 100, so they are split at "
                f"m = {sp.get('m')}: X = a·10^m + b (a = {short(sp.get('a'), 20)}, "
                f"b = {short(sp.get('b'), 20)}) and Y = c·10^m + d "
                f"(c = {short(sp.get('c'), 20)}, d = {short(sp.get('d'), 20)}). "
                "Three recursive products follow: z0 = b × d, z2 = a × c and "
                "(a + b) × (c + d)."
            )
            mid = node.get("middle")
            if mid:
                notes.append(
                    "MIDDLE TERM: z1 = z1_product − z2 − z0 = "
                    f"{short(mid['z1_product'], 20)} − {short(mid['z2'], 20)} − "
                    f"{short(mid['z0'], 20)} = {short(mid['result'], 30)}.  "
                    "Final: result = z2 × 10^(2m) + z1 × 10^m + z0."
                )

        if parent is not None and branch == "z1" and parent.get("middle"):
            pm = parent["middle"]
            notes.append(
                "z1 BRANCH NOTE: this circle holds the raw product "
                f"(a+b)×(c+d) = {short(pm['z1_product'], 30)}. The parent turns it "
                "into the middle term: z1 = z1_product − z2 − z0 = "
                f"{short(pm['z1_product'], 20)} − {short(pm['z2'], 20)} − "
                f"{short(pm['z0'], 20)} = {short(pm['result'], 30)}."
            )

        self.write_tree_info(
            f"{name}   |   {short(x, 24)} × {short(y, 24)}",
            fields, "\n\n".join(notes))

    # ========================================================
    # PERFORMANCE
    # ========================================================

    def show_performance(self):
        self.clear_page()
        self.set_active_nav("Performance")
        self.page_header(
            "Performance Analysis",
            "Compare execution times recorded by the experiment runner.")

        main = tk.Frame(self.page, bg=C["background"])
        main.pack(fill="both", padx=32, pady=(0, 30))

        self.performance_chart(
            main, "Closest Pair — Execution Time",
            os.path.join(PROJECT_ROOT, "results", "closest_pair_results.csv"))
        self.performance_chart(
            main, "Karatsuba — Execution Time",
            os.path.join(PROJECT_ROOT, "results", "integer_multiplication_results.csv"))

    def performance_chart(self, parent, title, filepath):
        card = self.section_card(parent, title)
        canvas = tk.Canvas(card, height=270, bg=C["canvas"], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        if not os.path.exists(filepath):
            canvas.create_text(
                20, 25, text="Results CSV not found. Run run_experiments.py first.",
                fill=C["muted"], anchor="w", font=("Segoe UI", 9))
            return

        try:
            with open(filepath, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                headers = reader.fieldnames or []

            time_col = next((h for h in headers if h and (
                "time" in h.lower() or "second" in h.lower())), None)
            size_col = next((h for h in headers if h and any(
                t in h.lower() for t in ("size", "digit", "point"))), None)

            if not time_col or not rows:
                raise ValueError("Could not find valid timing data.")

            data = []
            for row in rows:
                try:
                    value = float(row[time_col])
                    label = (str(row.get(size_col)) if size_col
                             else str(len(data) + 1))
                    data.append((label, value))
                except (ValueError, TypeError, KeyError):
                    continue

            if not data:
                raise ValueError("No valid timing rows were found.")

            self.draw_horizontal_bars(canvas, data)

        except Exception as error:
            canvas.create_text(20, 25, text=f"Unable to display chart: {error}",
                               fill=C["red"], anchor="w", font=("Segoe UI", 9))

    def draw_horizontal_bars(self, canvas, data):
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 650)
        height = max(canvas.winfo_height(), 250)
        left, right, top = 95, width - 105, 20
        row_h = min(22, (height - 35) / max(len(data), 1))
        maximum = max((v for _, v in data), default=1) or 1

        for i, (label, value) in enumerate(data):
            y = top + i * row_h
            bar_w = max(2, (right - left) * value / maximum)
            canvas.create_text(left - 10, y + 7, text=label, fill=C["muted"],
                               anchor="e", font=("Segoe UI", 8))
            canvas.create_rectangle(left, y, left + bar_w, y + 13,
                                    fill=C["blue"] if i % 2 == 0 else C["gold"],
                                    outline="")
            canvas.create_text(min(left + bar_w + 7, width - 75), y + 7,
                               text=f"{value:.6f}s", fill=C["white"],
                               anchor="w", font=("Segoe UI", 8))

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):
        self.clear_page()
        self.set_active_nav("About")
        self.page_header(
            "About Project",
            "Design and Analysis of Algorithms | CS302 | Fall 2026")

        main = tk.Frame(self.page, bg=C["background"])
        main.pack(fill="both", padx=32, pady=(0, 30))

        card = self.section_card(
            main, "DAA Algorithm Analyzer",
            "An interactive application for algorithm execution and performance analysis.")
        description = (
            "This project implements two divide-and-conquer algorithms: "
            "Closest Pair of Points and Karatsuba Integer Multiplication. "
            "Users can load input datasets, execute the algorithms, inspect "
            "their actual execution events, and review performance measurements."
        )
        tk.Label(card, text=description, font=("Segoe UI", 10),
                 fg=C["muted"], bg=C["panel"], wraplength=1000,
                 justify="left").pack(anchor="w", padx=20, pady=(0, 20))

        info = self.section_card(main, "Algorithm Information")
        rows = [
            ("Closest Pair of Points", "Divide and Conquer", "O(n log n)"),
            ("Integer Multiplication", "Karatsuba Algorithm", "O(n^1.585)"),
        ]
        for name, method, complexity in rows:
            row = tk.Frame(info, bg=C["panel_light"])
            row.pack(fill="x", padx=20, pady=(0, 10))
            tk.Label(row, text=name, font=("Segoe UI", 10, "bold"),
                     fg=C["white"], bg=C["panel_light"]).pack(side="left", padx=12, pady=12)
            tk.Label(row, text=f"{method}   |   {complexity}",
                     font=("Segoe UI", 9), fg=C["gold"],
                     bg=C["panel_light"]).pack(side="right", padx=12)

# ============================================================
# APPLICATION ENTRY POINT
# ============================================================
def main():
    root = tk.Tk()
    AlgorithmAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()