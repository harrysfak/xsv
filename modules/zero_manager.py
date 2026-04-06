"""
Module για τη διαχείριση zero calibration data
"""
import os
import pandas as pd
from typing import List

# Import config με fallback
try:
    from . import config
    from .zero_loader import ensure_zero_file
except ImportError:
    import config
    from modules.zero_loader import ensure_zero_file


class ZeroDataManager:
    """Κλάση για τη διαχείριση zero calibration data"""

    def __init__(self, zero_path: str = None):
        self.zero_path = zero_path or config.ZERO_PATH
        self.zero_df = None
        self.zero_copies = []

    def load_zero_data(self, date: str) -> pd.DataFrame:
        """
        Φορτώνει το zero DataFrame και το προετοιμάζει
        
        Args:
            date: Ημερομηνία για ενημέρωση του zero DataFrame
            
        Returns:
            pd.DataFrame: Zero DataFrame
        """
        if not os.path.exists(self.zero_path):
            print(f"Το αρχείο zero δεν βρέθηκε: {self.zero_path}")
            print("Αυτόματη λήψη....")
            self.zero_path = ensure_zero_file()

        # Φόρτωση και καθαρισμός
        self.zero_df = pd.read_excel(self.zero_path).fillna("")

        # Αφαίρεση τελευταίας στήλης αν χρειάζεται
        heads = self.zero_df.columns.tolist()
        last = heads.pop()
        self.zero_df = self.zero_df.rename(columns={last: ""})

        # Ενημέρωση ημερομηνίας ΜΟΝΟ στις πραγματικές zero rows
        valid_rep_values = {'1', '2', '3', '4', '5', 'Mean', 'Sd', 'Corr'}
        rep_series = self.zero_df['Rep #'].astype(str).str.strip()
        self.zero_df.loc[rep_series.isin(valid_rep_values), 'Date'] = date

        print(f"✅ Φορτώθηκε zero DataFrame με {len(self.zero_df)} γραμμές")
        return self.zero_df

    def create_zero_copies(self, num_copies: int) -> List[pd.DataFrame]:
        """
        Δημιουργεί αντίγραφα του zero DataFrame
        
        Args:
            num_copies: Πόσα αντίγραφα να δημιουργηθούν
            
        Returns:
            List[pd.DataFrame]: Λίστα με zero DataFrames
        """
        if self.zero_df is None:
            raise ValueError("Πρέπει να φορτώσετε πρώτα το zero data με load_zero_data()")

        self.zero_copies = [self.zero_df.copy() for _ in range(num_copies)]
        print(f"✅ Δημιουργήθηκαν {len(self.zero_copies)} zero DataFrames")
        return self.zero_copies

    def update_zero_times(self, zero_times: List[str]) -> List[pd.DataFrame]:

        """
        Ενημερώνει τους χρόνους σε όλα τα zero DataFrames

        Args:
            zero_times: Λίστα με χρόνους για όλα τα zero blocks

        Returns:
            List[pd.DataFrame]: Ενημερωμένα zero DataFrames

            ===============================================

            ελεγχο για το αν δεν χρειαζονται zero_copies να μην σκαει
        """

        if not self.zero_copies:
            print("ℹ️ Δεν χρειάζονται zero blocks (zero_count=0) -> skip update_zero_times")
            return []

        times_per_block = config.ZERO_BLOCK_ROWS

        for i, zero_copy in enumerate(self.zero_copies):
            start_idx = i * times_per_block
            end_idx = start_idx + times_per_block
            current_times = zero_times[start_idx:end_idx]

            zero_copy.loc[config.ZERO_ROW_INDEX, 'Time'] = current_times

        print(f"✅ Ενημερώθηκαν χρόνοι σε {len(self.zero_copies)} zero blocks")
        return self.zero_copies

    def get_zero_copies(self) -> List[pd.DataFrame]:
        """Επιστρέφει τα zero DataFrames"""
        return self.zero_copies

    def calculate_zero_count(self, total_samples: int) -> dict:
        """
        Υπολογίζει πόσα zero blocks χρειάζονται
        
        Args:
            total_samples: Συνολικός αριθμός δειγμάτων
            
        Returns:
            dict: Πληροφορίες για zero blocks
        """
        zero_count = total_samples // config.BATCH_SIZE
        sample_remainder = total_samples % config.BATCH_SIZE
        total_rows = zero_count * config.ZERO_BLOCK_ROWS + total_samples

        info = {
            'zero_count': zero_count,
            'sample_remainder': sample_remainder,
            'total_rows': total_rows
        }

        print(f"📊 Zero blocks: {zero_count}")
        print(f"📊 Υπόλοιπα δείγματα: {sample_remainder}")
        print(f"📊 Σύνολο γραμμών: {total_rows}")

        return info

    def save_zero_csv(self, output_path: str = None):
        """
        Αποθηκεύει το zero DataFrame ως CSV
        
        Args:
            output_path: Διαδρομή αποθήκευσης (προαιρετική)
        """
        if self.zero_df is None:
            raise ValueError("Δεν υπάρχει zero DataFrame για αποθήκευση")

        output_path = output_path or os.path.join(config.APP_PATH, "zero.csv")
        self.zero_df.to_csv(output_path, index=False, lineterminator='')
        print(f"✅ Αποθηκεύτηκε zero CSV: {output_path}")


def prepare_zero_data(total_samples: int, date: str,
                      zero_times: List[str]) -> List[pd.DataFrame]:
    """
    Wrapper function για πλήρη προετοιμασία zero data
    
    Args:
        total_samples: Συνολικός αριθμός δειγμάτων
        date: Ημερομηνία ανάλυσης
        zero_times: Λίστα με χρόνους για zero blocks
        
    Returns:
        List[pd.DataFrame]: Λίστα με ενημερωμένα zero DataFrames
    """
    manager = ZeroDataManager()

    # Υπολογισμός πόσα zero blocks χρειάζονται
    zero_info = manager.calculate_zero_count(total_samples)
    if zero_info["zero_count"] == 0:
        print("ℹ️ zero_count=0 -> δεν θα δημιουργηθούν zero blocks")
        return []

    # Φόρτωση και προετοιμασία
    manager.load_zero_data(date)
    manager.create_zero_copies(zero_info['zero_count'])
    manager.update_zero_times(zero_times)

    # Αποθήκευση zero CSV
    manager.save_zero_csv()

    return manager.get_zero_copies()


if __name__ == "__main__":
    # Test του module
    print("Testing ZeroDataManager...")

    # Δημιουργία mock zero times
    test_times = ["10:00", "10:05", "10:10", "10:15", "10:20", "10:25", "10:30", "10:35"]

    try:
        manager = ZeroDataManager()
        zero_info = manager.calculate_zero_count(300)
        print(f"Zero info: {zero_info}")
    except FileNotFoundError as e:
        print(f"Σημείωση: {e}")
        print("Αυτό είναι φυσιολογικό αν δεν υπάρχει το zero.xlsx αρχείο")
