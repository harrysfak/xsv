"""
Module για τη φόρτωση και την αρχική επικύρωση δεδομένων από Excel αρχεία
Windows Version
"""
import os
import re
import pandas as pd
from typing import Tuple
import xlrd
import openpyxl
import sys


# Import config με fallback
try:
    from . import config
except ImportError:
    import config



class DataLoader:

    def __init__(self, base_path=None):
        if base_path:
            self.base_path = base_path
        else:
            if getattr(sys, 'frozen', False):
                self.base_path = os.path.dirname(sys.executable)
            else:
                self.base_path = os.path.dirname(os.path.abspath(__file__))
                

    def get_user_file(self) -> Tuple[pd.DataFrame, str, str]:
        """
        Ζητά από το χρήστη τον αριθμό πρωτοκόλλου και φορτώνει το αντίστοιχο αρχείο
        
        Returns:
            Tuple[DataFrame, str, str]: (excel_df, csv_first_4, dash_part)
        """
        while True:
            user_excel = input("Πληκτρολογήστε τον Αρ. πρωτ. εργαστηρίου για το δελτίο: ")
            
            try:
                if not user_excel:
                    print("Δεν δόθηκε τιμή από τον χρήστη. Παρακαλώ δοκιμάστε ξανά.")
                    continue
                
                # Έλεγχος μορφής με regex
                dash_regx = r"(-\d+)"
                result = re.search(dash_regx, user_excel)
                
                if not result:
                    print("Δεν βρέθηκε παύλα '-' με αριθμούς μετά από αυτή. Παρακαλώ δοκιμάστε ξανά.")
                    continue
                
                dash_part = result.group()
                
                # Έλεγχος πρώτων 4 ψηφίων
                if len(user_excel) < 4 or not user_excel[:4].isdigit():
                    print("Τα πρώτα 4 ψηφία δεν είναι έγκυρα. Παρακαλώ δοκιμάστε ξανά.")
                    continue
                
                csv_first_4 = user_excel[:4]
                
                # Δημιουργία path αρχείου
                # Δημιουργία path - δοκιμή και .xls και .xlsx
                xls_path  = os.path.join(self.base_path, f"{user_excel}.xls")
                xlsx_path = os.path.join(self.base_path, f"{user_excel}.xlsx")

                if os.path.exists(xlsx_path):
                    excel_file = xlsx_path
                elif os.path.exists(xls_path):
                    excel_file = xls_path
                else:
                    print(f"Το αρχείο δεν βρέθηκε: {xls_path}")
                    self._list_available_files()
                    continue
                
                # Έλεγχος αν υπάρχει το αρχείο
                if not os.path.exists(excel_file):
                    print(f"Το αρχείο δεν βρέθηκε: {excel_file}")
                    self._list_available_files()
                    continue
                
                # Προσπάθεια ανάγνωσης Excel
                try:
                    if excel_file.endswith('.xls'):
                        excel_df = pd.read_excel(excel_file, engine='xlrd')
                    else:
                        excel_df = pd.read_excel(excel_file, engine='openpyxl')
                    print("✅ Το αρχείο φορτώθηκε επιτυχώς!")
                    print(f"Πρώτα 4 ψηφία: {csv_first_4}")
                    print(f"Dash part: {dash_part}")
                    print(f"Συνολικές γραμμές: {len(excel_df)}")
                    return excel_df, csv_first_4, dash_part
                    
                except Exception as e:
                    print(f"Αποτυχία ανάγνωσης του Excel: {e}")
                    continue
                    
            except Exception as e:
                print(f"Προέκυψε ένα απροσδόκητο σφάλμα: {e}")
                continue
    
    def _list_available_files(self):
        """Εμφανίζει τα διαθέσιμα αρχεία στον BASE_PATH"""
        if os.path.exists(self.base_path):
            available_files = [
                f for f in os.listdir(self.base_path)
                if f.endswith(('.xls', '.xlsx'))
            ]
            if available_files:
                print("\n📁 Διαθέσιμα αρχεία στον φάκελο:")
                for f in sorted(available_files)[:10]:  # Εμφάνιση μέχρι 10 αρχείων
                    print(f"  - {f}")
                if len(available_files) > 10:
                    print(f"  ... και {len(available_files) - 10} ακόμα αρχεία")
            else:
                print("❌ Δεν βρέθηκαν αρχεία .xls ή .xlsx στον φάκελο.")
                print(f"   Τοποθετήστε τα αρχεία σας στο: {self.base_path}")
        else:
            print(f"❌ Ο φάκελος '{self.base_path}' δεν βρέθηκε.")
            print(f"   Δημιουργήστε τον φάκελο ή ελέγξτε το config.py")


def load_data() -> Tuple[pd.DataFrame, str, str]:
    """
    Wrapper function για εύκολη χρήση
    
    Returns:
        Tuple[DataFrame, str, str]: (excel_df, csv_first_4, dash_part)
    """
    loader = DataLoader()
    return loader.get_user_file()


if __name__ == "__main__":
    # Test του module
    print("=" * 70)
    print("TEST: Data Loader Module")
    print("=" * 70)
    
    excel_df, csv_first_4, dash_part = load_data()
    
    print(f"\n✅ Φορτώθηκαν {len(excel_df)} γραμμές")
    print(f"Στήλες: {excel_df.columns.tolist()}")
    print("\nΠρώτες 5 γραμμές:")
    print(excel_df.head())
