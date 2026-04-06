"""
Load Tab Module
Handles file loading and display
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import re
import pandas as pd
import config

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from modules.data_loader import DataLoader


class LoadTab:
    """Tab για φόρτωση δεδομένων"""

    def __init__(self, parent, app_reference):
        """
        Args:
            parent: Parent notebook
            app_reference: Reference to main app for accessing shared data
        """
        self.app = app_reference
        self.frame = ttk.Frame(parent, padding="20")
        self._setup_ui()

    def _setup_ui(self):
        """Δημιουργία UI"""
        # File selection
        file_frame = ttk.LabelFrame(self.frame, text="Επιλογή Αρχείου", padding="15")
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Label(file_frame, text="Αρ. Πρωτοκόλλου:", font=("Segoe UI", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.protocol_entry = ttk.Entry(file_frame, width=30, font=("Consolas", 10))
        self.protocol_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(file_frame, text="📥 Φόρτωση", command=self.load_file).grid(
            row=0, column=2, padx=5
        )

        ttk.Button(file_frame, text="🔍 Αναζήτηση", command=self.browse_file).grid(
            row=0, column=3, padx=5
        )

        # File info
        info_frame = ttk.LabelFrame(self.frame, text="Πληροφορίες Αρχείου", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.file_info_text = scrolledtext.ScrolledText(
            info_frame, height=12, state=tk.DISABLED, font=("Consolas", 9), wrap=tk.WORD
        )
        self.file_info_text.pack(fill=tk.BOTH, expand=True)

    def load_file(self):
        """Φόρτωση αρχείου"""
        protocol = self.protocol_entry.get().strip()
        if not protocol:
            messagebox.showwarning("Προειδοποίηση", "Εισάγετε αριθμό πρωτοκόλλου")
            return

        # 1. Validation πρώτα, πριν αγγίξουμε οτιδήποτε
        dash_match = re.search(r"(-\d+)", protocol)
        if not dash_match or len(protocol) < 4 or not protocol[:4].isdigit():
            messagebox.showerror("Σφάλμα", "Μη έγκυρος αριθμός πρωτοκόλλου")
            return

        # 2. Εύρεση αρχείου
        try:
            loader = DataLoader(base_path=self.app.config_editor.config_values['BASE_PATH'])
            base = loader.base_path

            excel_file = None
            for ext in (".xls", ".xlsx"):
                candidate = os.path.join(base, f"{protocol}{ext}")
                if os.path.exists(candidate):
                    excel_file = candidate
                    break

            if excel_file is None:
                messagebox.showerror(
                    "Σφάλμα",
                    f"Το αρχείο δεν βρέθηκε:\n{os.path.join(base, protocol)}.xls / .xlsx"
                )
                return

            # 3. Φόρτωση δεδομένων
            df = pd.read_excel(excel_file)

            # 4. Υπολογισμός στατιστικών
            last_aa = "—"
            repeats = "—"
            aa_col = "a/a"
            if aa_col in df.columns:
                aa_numeric = pd.to_numeric(df[aa_col], errors="coerce").dropna()
                if not aa_numeric.empty:
                    last_aa = int(aa_numeric.max())
                    repeats = len(df) - last_aa

            # 5. Αποθήκευση στο app state μόνο αφού όλα πήγαν καλά
            self.app.protocol_number = protocol
            self.app.excel_df = df
            self.app.csv_first_4 = protocol[:4]
            self.app.dash_part = dash_match.group()

            # 6. Εμφάνιση πληροφοριών
            filename = os.path.basename(excel_file)
            info = (
                f"Αρχείο: {filename}\n\n"
                f"Γραμμές: {len(df)}\n"
                f"Τελευταίο a/a: {last_aa}\n"
                f"Επαναλαμβανόμενες γραμμές: {repeats}\n\n"
                f"Στήλες:\n{', '.join(df.columns.tolist())}\n\n"
                f"Συνέχεια ρυθμίσεων ===>"
            )
            self.file_info_text.config(state=tk.NORMAL)
            self.file_info_text.delete(1.0, tk.END)
            self.file_info_text.insert(1.0, info)
            self.file_info_text.config(state=tk.DISABLED)

            self.app.logger.info(f"✅ Φορτώθηκε: {filename} ({len(df)} γραμμές)")
            messagebox.showinfo("Επιτυχία", f"Φορτώθηκε: {len(df)} γραμμές")

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))
            self.app.logger.error(f"❌ {str(e)}")
            self.app.telemetry.record_error(str(e))

    def browse_file(self):
        """Αναζήτηση αρχείου"""
        filename = filedialog.askopenfilename(
            title="Επιλογή Αρχείου",
            filetypes=[("Excel files", "*.xls *.xlsx"), ("All files", "*.*")]
        )
        if filename:
            protocol = os.path.splitext(os.path.basename(filename))[0]
            self.protocol_entry.delete(0, tk.END)
            self.protocol_entry.insert(0, protocol)
            self.load_file()

    def reset(self):
        """Reset tab"""
        self.protocol_entry.delete(0, tk.END)
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.config(state=tk.DISABLED)

    def get_frame(self):
        """Returns the frame"""
        return self.frame