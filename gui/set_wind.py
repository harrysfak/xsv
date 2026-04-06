import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import datetime
import sys
from datetime import datetime


class SettingsWindow:
    """Παράθυρο για App Settings (Popup)"""

    def __init__(self, parent, config_editor):
        self.window = tk.Toplevel(parent)
        self.window.title("Ρυθμίσεις Εφαρμογής")
        self.window.geometry("700x650")
        self.window.transient(parent)
        self.window.grab_set()

        self.config_editor = config_editor
        self.config_editor.load_config()

        self._setup_ui()
        self._center_window()

    def _center_window(self):
        """Κεντράρει το παράθυρο"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def _setup_ui(self):
        """Δημιουργία UI"""
        # Header
        header = tk.Frame(self.window, bg='#3498db', padx=15, pady=10)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="⚙️ Ρυθμίσεις Εφαρμογής",
            font=("Segoe UI", 14, "bold"),
            bg='#3498db',
            fg='white'
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="Επεξεργασία config.",
            font=("Segoe UI", 9),
            bg='#3498db',
            fg='white'
        ).pack(anchor=tk.W)

        # Main container με scrollbar
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === PATHS ===
        paths_frame = ttk.LabelFrame(main_frame, text="📁 Διαδρομές", padding="10")
        paths_frame.pack(fill=tk.X, pady=5)

        ttk.Label(paths_frame, text="__Base__ Φάκελος Αναζήτησης:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.base_path_var = tk.StringVar(value=self.config_editor.config_values['BASE_PATH'])
        ttk.Entry(paths_frame, textvariable=self.base_path_var, width=45).grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Button(paths_frame, text="📂", command=self._browse_base_path, width=3).grid(
            row=0, column=2
        )
        ttk.Label(paths_frame, text="__Output__ Φάκελος Αποθήκευσης:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path_var = tk.StringVar(value=self.config_editor.config_values['OUTPUT_PATH'])
        ttk.Entry(paths_frame, textvariable=self.output_path_var, width=45).grid(
            row=1, column=1, padx=5, pady=5
        )
        ttk.Button(paths_frame, text="📂", command=self._browse_output_path, width=3).grid(
            row=1, column=2
        )

        # === PROCESSING ===
        proc_frame = ttk.LabelFrame(main_frame, text="⚙️ Παράμετροι", padding="10")
        proc_frame.pack(fill=tk.X, pady=5)

        ttk.Label(proc_frame, text="Zero Batch :").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.batch_size_var = tk.IntVar(value=self.config_editor.config_values['BATCH_SIZE'])
        ttk.Spinbox(proc_frame, from_=1, to=200, textvariable=self.batch_size_var, width=15).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(proc_frame, text="Δευτερόλεπτα ανά δείγμα:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.t_sample_var = tk.IntVar(value=self.config_editor.config_values['T_SAMPLE_INCREMENT'])
        ttk.Spinbox(proc_frame, from_=1, to=300, textvariable=self.t_sample_var, width=15).grid(
            row=1, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(proc_frame, text="Δευτερόλεπτα ανά Zero:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.t_zero_var = tk.IntVar(value=self.config_editor.config_values['T_ZERO_INCREMENT'])
        ttk.Spinbox(proc_frame, from_=1, to=300, textvariable=self.t_zero_var, width=15).grid(
            row=2, column=1, sticky=tk.W, padx=5
        )

        # === DEFAULTS ===
        defaults_frame = ttk.LabelFrame(main_frame, text="📋 Προεπιλογές", padding="10")
        defaults_frame.pack(fill=tk.X, pady=5)

        ttk.Label(defaults_frame, text="DEFAULT_PRODUCT:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.default_product_var = tk.StringVar(value=self.config_editor.config_values['DEFAULT_PRODUCT'])
        ttk.Entry(defaults_frame, textvariable=self.default_product_var, width=30).grid(
            row=0, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(defaults_frame, text="DEFAULT_TIME:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.default_time_var = tk.StringVar(value=self.config_editor.config_values['DEFAULT_TIME'])
        ttk.Entry(defaults_frame, textvariable=self.default_time_var, width=15).grid(
            row=1, column=1, sticky=tk.W, padx=5
        )

        ttk.Label(defaults_frame, text="DEFAULT_REP:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.default_rep_var = tk.IntVar(value=self.config_editor.config_values['DEFAULT_REP'])


        # === FEATURES ===
        features_frame = ttk.LabelFrame(main_frame, text="✨ Features", padding="10")
        features_frame.pack(fill=tk.X, pady=5)

        self.drop_zero_var = tk.BooleanVar(
            value=self.config_editor.config_values['DROP_ZERO_NUTRIENTS']
        )
        ttk.Checkbutton(
            features_frame,
            text="DROP_ZERO_NUTRIENTS (Αφαίρεση γραμμών με Fat=Protein=Lactose=0)",
            variable=self.drop_zero_var
        ).pack(anchor=tk.W, pady=3)

        # === BUTTONS ===
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)

        ttk.Button(
            button_frame,
            text="💾 Αποθήκευση & Επανεκκίνηση",
            command=self._save_and_restart
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="❌ Ακύρωση",
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🔄 Επαναφορά",
            command=self._reload
        ).pack(side=tk.LEFT, padx=5)

    def _browse_base_path(self):
        """Browse για path"""
        folder = filedialog.askdirectory(
            title="Επιλογή Φακέλου Αναζήτησης.",
            initialdir=self.base_path_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.base_path_var.set(folder)
    def _browse_output_path(self):
        """Browse για path"""
        folder = filedialog.askdirectory(
            title="Επιλογή Φακέλου Αποθήκευσης.",
            initialdir=self.output_path_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.output_path_var.set(folder)

    def _reload(self):
        """Επαναφορά τιμών"""
        self.config_editor.load_config()
        self.base_path_var.set(self.config_editor.config_values['BASE_PATH'])
        self.output_path_var.set(self.config_editor.config_values['OUTPUT_PATH'])
        self.batch_size_var.set(self.config_editor.config_values['BATCH_SIZE'])
        self.t_sample_var.set(self.config_editor.config_values['T_SAMPLE_INCREMENT'])
        self.t_zero_var.set(self.config_editor.config_values['T_ZERO_INCREMENT'])
        self.default_product_var.set(self.config_editor.config_values['DEFAULT_PRODUCT'])
        self.default_time_var.set(self.config_editor.config_values['DEFAULT_TIME'])
        self.default_rep_var.set(self.config_editor.config_values['DEFAULT_REP'])
        self.drop_zero_var.set(self.config_editor.config_values['DROP_ZERO_NUTRIENTS'])

        messagebox.showinfo("Επιτυχία", "Οι ρυθμίσεις επαναφορτώθηκαν!")

    def _save_and_restart(self):
        """Αποθήκευση και επανεκκίνηση"""
        # Validation
        try:
            datetime.strptime(self.default_time_var.get(), "%H:%M")
        except ValueError:
            messagebox.showerror("Σφάλμα", "Μη έγκυρη μορφή ώρας! Χρησιμοποιήστε HH:MM")
            return

        if not self.base_path_var.get().strip():
            messagebox.showerror("Σφάλμα", "Το BASE_PATH δεν μπορεί να είναι κενό!")
            return

        # Confirm
        response = messagebox.askyesno(
            "Επιβεβαίωση",
            "Αποθήκευση αλλαγών και επανεκκίνηση εφαρμογής;"
        )

        if not response:
            return

        # Save
        new_values = {
            'BASE_PATH': self.base_path_var.get().strip(),
            'OUTPUT_PATH': self.output_path_var.get().strip(),
            'BATCH_SIZE': self.batch_size_var.get(),
            'T_SAMPLE_INCREMENT': self.t_sample_var.get(),
            'T_ZERO_INCREMENT': self.t_zero_var.get(),
            'DEFAULT_PRODUCT': self.default_product_var.get(),
            'DEFAULT_TIME': self.default_time_var.get(),
            'DEFAULT_REP': self.default_rep_var.get(),
            'DROP_ZERO_NUTRIENTS': self.drop_zero_var.get(),
        }

        try:
            if self.config_editor.save_config(new_values):
                self.config_editor.load_config()  # ← Ανανέωση μνήμης αμέσως
                messagebox.showinfo("Επιτυχία", "Οι ρυθμίσεις αποθηκεύτηκαν!\n\nΗ εφαρμογή θα επανεκκινηθεί.")
                self.window.destroy()

                if getattr(sys, 'frozen', False):
                    # Exe mode - σωστό Windows restart
                    os.startfile(sys.executable)
                    sys.exit(0)
                else:
                    # Script mode
                    os.execl(sys.executable, sys.executable, *sys.argv)

        except Exception as e:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αποθήκευσης ρυθμίσεων!: {e}")