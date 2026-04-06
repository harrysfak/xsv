"""
Module για τη δημιουργία τελικού output και συγχώνευση δεδομένων
"""
import os
import pandas as pd
import numpy as np
from typing import List

# Import config με fallback
try:
    from . import config
except ImportError:
    import config


class OutputGenerator:
    """Κλάση για τη δημιουργία τελικού output"""

    def __init__(self, df: pd.DataFrame, metadata: dict):
        """
        Args:
            df: Επεξεργασμένο DataFrame με δεδομένα
            metadata: Dictionary με metadata (sample_ids, times, κλπ.)
        """
        self.df = df
        self.metadata = metadata
        self.filled_df = None
        self.parts_path = config.PARTS_PATH

    def drop_zero_nutrient_rows_on_filled(self, reset_index=False, verbose=True):
        if self.filled_df is None:
            raise ValueError("Πρώτα φτιάξε filled_df")

        for c in ("Fat", "Protein", "Lactose"):
            if c not in self.filled_df.columns:
                if verbose:
                    print(f"⚠️ Λείπει η στήλη {c}. Skip.")
                return self.filled_df

        def to_num(s):
            s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
            return pd.to_numeric(s, errors="coerce").fillna(0)

        fat = to_num(self.filled_df["Fat"])
        protein = to_num(self.filled_df["Protein"])
        lactose = to_num(self.filled_df["Lactose"])

        drop_mask = (fat == 0) & (protein == 0) & (lactose == 0)

        if verbose:
            print(f"🔍 Zero rows to drop: {int(drop_mask.sum())}")

        self.filled_df = self.filled_df.loc[~drop_mask].copy()

        if reset_index:
            self.filled_df.reset_index(drop=True, inplace=True)

        return self.filled_df

    def create_filled_dataframe(self) -> pd.DataFrame:
        """
        Δημιουργεί το πλήρες DataFrame με όλα τα δεδομένα

        Returns:
            pd.DataFrame: Πλήρως συμπληρωμένο DataFrame
        """
        # Source - https://stackoverflow.com/a/30522778
        # Posted by miriamsimone, modified by community
        # Retrieved 2025-12-10, License - CC BY-SA 4.0

        self.filled_df = pd.DataFrame(
            np.column_stack([
                self.metadata['sample_ids'],
                self.metadata['rep'],
                self.metadata['product'],
                self.df['Fat'],
                self.df['Protein'],
                self.df['Lactose'],
                self.df['FPD'],
                self.df['TS'],
                self.df['SNF'],
                self.metadata['date'],
                self.metadata['sample_times'],
                self.metadata['remark']
            ]),
            columns=config.TARGET_COLUMN_ORDER
        )

        print(f"✅ Δημιουργήθηκε filled DataFrame με {len(self.filled_df)} γραμμές")
        return self.filled_df

    def break_into_parts(self) -> List[pd.DataFrame]:
        if self.filled_df is None:
            raise ValueError("Πρέπει να καλέσετε πρώτα create_filled_dataframe()")

        B = config.BATCH_SIZE
        n = len(self.filled_df)
        chunks = []

        start = 0
        while start < n:
            chunks.append(self.filled_df.iloc[start:start + B])
            start += B

        return chunks

    def save_parts_to_csv(self):
        """Αποθηκεύει τα parts ως ξεχωριστά CSV αρχεία"""
        if self.filled_df is None:
            raise ValueError("Πρέπει να καλέσετε πρώτα create_filled_dataframe()")

        # Δημιουργία φακέλου parts
        os.makedirs(self.parts_path, exist_ok=True)

        # Διαχωρισμός και αποθήκευση
        chunks = self.break_into_parts()

        for idx, chunk in enumerate(chunks, 1):
            part_file = os.path.join(self.parts_path, f"p{idx}.csv")
            chunk.to_csv(part_file, index=False)

        print(f"✅ Αποθηκεύτηκαν {len(chunks)} part files στο {self.parts_path}")
 
    def get_filled_dataframe(self) -> pd.DataFrame:
        """Επιστρέφει το filled DataFrame"""
        return self.filled_df


class FinalOutputAssembler:
    def __init__(self, parts_path: str = None, output_path: str = None, protocol_number: str = None):
        self.parts_path = parts_path or config.PARTS_PATH

        out_dir = os.path.dirname(output_path or config.FINAL_OUTPUT_PATH)
        proto = (protocol_number or "final").strip()
        safe = proto.replace("/", "-").replace("\\", "-")

        self.output_path = os.path.join(out_dir, f"{safe}.csv")

    def _cleanup_parts(self):
        for fname in os.listdir(self.parts_path):
            if fname.startswith("p") and fname.endswith(".csv"):
                try:
                    os.remove(os.path.join(self.parts_path, fname))
                except Exception as e:
                    print(f"⚠️ Δεν διαγράφηκε {fname}: {e}")

    def assemble_final_csv(self, zero_dfs: List[pd.DataFrame]):
        """
        Συναρμολογεί το τελικό CSV με parts και zero blocks

        Args:
            zero_dfs: Λίστα με zero DataFrames
        """
        # Εύρεση part files
        part_files = [
            f for f in os.listdir(self.parts_path)
            if f.startswith("p") and f.endswith(".csv")
        ]

        # Ταξινόμηση
        part_files = sorted(part_files, key=self._part_key)

        print(f"📄 Θα χρησιμοποιηθούν {len(part_files)} part files:")
        for f in part_files:
            print(f"   - {f}")

        # Συναρμολόγηση
        first_file = True
        zero_block_index = 0

        with open(self.output_path, "w", encoding="utf-8", newline='') as fout:
            for i, fname in enumerate(part_files):
                part_path = os.path.join(self.parts_path, fname)

                # Γράφουμε το part
                with open(part_path, "r", encoding="utf-8") as fin:
                    lines = fin.readlines()

                if first_file:
                    fout.writelines(lines)
                    first_file = False
                else:
                    fout.writelines(lines[1:])  # Χωρίς header

                # Προσθήκη zero block (αν δεν είναι το τελευταίο part)
                if i < len(part_files) - 1:
                    if zero_block_index < len(zero_dfs):
                        zero_df = zero_dfs[zero_block_index]
                        zero_csv_string = zero_df.to_csv(header=True, index=False, lineterminator='')
                        fout.write(zero_csv_string)
                        zero_block_index += 1
                    else:
                        print(f"⚠️  Προειδοποίηση: Δεν υπάρχουν αρκετά zero blocks")

        print(f"✅ Τελικό αρχείο αποθηκεύτηκε: {self.output_path}")
        print(f"📊 Συνολικές γραμμές: {self._count_lines(self.output_path)}")
        
        # 🔥 ΚΑΘΑΡΙΣΜΑ PARTS
        if os.path.exists(self.output_path) and os.path.getsize(self.output_path) > 0:
            self._cleanup_parts()
        print("🧹 Τα προσωρινά part αρχεία διαγράφηκαν.")
        
    @staticmethod
    def _part_key(name: str):
        """Helper για σωστή ταξινόμηση part files"""
        base = name[1:-4]  # Αφαίρεση 'p' και '.csv'
        try:
            return int(base)
        except ValueError:
            return base

    @staticmethod
    def _count_lines(filepath: str) -> int:
        """Μετρά τις γραμμές ενός αρχείου"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)


def generate_output(df, metadata, zero_dfs, drop_zero_nutrients: bool = True) -> str:
    """
    Wrapper function για πλήρη δημιουργία output

    Args:
        df: Επεξεργασμένο DataFrame
        metadata: Dictionary με metadata
        zero_dfs: Λίστα με zero DataFrames

    Returns:
        str: Διαδρομή τελικού αρχείου
    """

    generator = OutputGenerator(df, metadata)
    generator.create_filled_dataframe()
    if drop_zero_nutrients:
        generator.drop_zero_nutrient_rows_on_filled(reset_index=False, verbose=False)
    generator.save_parts_to_csv()

    protocol_number = metadata.get("protocol_number")
    assembler = FinalOutputAssembler(protocol_number=protocol_number)
    assembler.assemble_final_csv(zero_dfs)

    return assembler.output_path


if __name__ == "__main__":
    # Test του module
    print("Testing OutputGenerator...")
    times = 300
    # Δημιουργία mock data
    test_df = pd.DataFrame({
        'Fat': ['3.5'] * times,
        'Protein': ['3.2'] * times,
        'Lactose': ['4.8'] * times,
        'FPD': ['0.520'] * times,
        'TS': [11.5] * times,
        'SNF': [8.7] * times
    })

    test_metadata = {
        'sample_ids': [f"1234-1 {i}" for i in range(1, times + 1)],
        'rep': [1] * times,
        'product': ['AIG NEWXX'] * times,
        'date': ['12/12/2024'] * times,
        'sample_times': [f"10:{i:02d}" for i in range(times)],
        'remark': [''] * times
    }

    generator = OutputGenerator(test_df, test_metadata)
    filled = generator.create_filled_dataframe()

    print(f"Created filled DataFrame with {len(filled)} rows")
