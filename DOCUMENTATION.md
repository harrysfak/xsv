# CSV Lab — Αναλυτική Τεκμηρίωση Κώδικα

## 1) Σκοπός εφαρμογής
Το **CSV Lab** είναι desktop εφαρμογή (Tkinter) για:
- φόρτωση εργαστηριακού Excel,
- καθαρισμό/τυποποίηση μετρήσεων,
- υπολογισμό παραγώγων (TS/SNF),
- παραγωγή χρονοσειρών δειγμάτων,
- παρεμβολή `zero` calibration blocks,
- εξαγωγή τελικού CSV ανά πρωτόκολλο.

Η εφαρμογή είναι προσανατολισμένη κυρίως σε Windows χρήση (GUI + `os.startfile`).

---

## 2) Δομή έργου

```text
/workspace/xsv
├── csv_Lab.py                  # Entry point GUI
├── config.py                   # Runtime παραμετροποίηση
├── modules/
│   ├── data_loader.py          # Ανάγνωση Excel
│   ├── data_processor.py       # Καθαρισμός + TS/SNF
│   ├── time_handler.py         # IDs, ημερομηνίες, ώρες
│   ├── zero_loader.py          # Download zero.xlsx
│   ├── zero_manager.py         # Προετοιμασία zero blocks
│   ├── output_generator.py     # Filled df, parts, final merge
│   ├── missing_row.py          # Συμπλήρωση missing a/a
│   └── ph_handler.py           # Ατελές/μη ενσωματωμένο module
└── gui/
    ├── tabs/
    │   ├── load_tab.py         # Βήμα 1 φόρτωσης
    │   ├── settings_tab.py     # Βήμα 2 ρυθμίσεων processing
    │   ├── process_tab.py      # Βήμα 3 επεξεργασίας
    │   └── results_tab.py      # Βήμα 4 αποτελεσμάτων
    ├── config_edit.py          # Popup ρυθμίσεων config.py
    ├── log.py                  # UI logger
    ├── telemetry.py            # Τοπικά στατιστικά χρήσης
    ├── set_wind.py             # Popup settings
    ├── stats_wind.py           # Popup usage stats
    └── missing_aa_dialog.py    # Dialog για missing a/a
```

---

## 3) Ροή εκτέλεσης (GUI)

1. Εκκίνηση από `csv_Lab.py` (`run_gui`).
2. Δημιουργία `CSVLabGUI` και tabs.
3. **Load tab**: φόρτωση Excel με αριθμό πρωτοκόλλου.
4. **Settings tab**: ορισμός ημερομηνίας/ώρας/φίλτρων.
5. **Process tab**:
   - έλεγχος για missing `a/a`,
   - προειδοποιήσεις για `som cells` και `antibiotics`,
   - processing data,
   - παραγωγή metadata/time,
   - zero preparation,
   - τελικό CSV output.
6. **Results tab**: εμφάνιση αποτελέσματος + open folder/file.

---

## 4) Αναλυτική περιγραφή modules

## 4.1 `modules/data_loader.py`
- Κάνει validate πρωτοκόλλου (μορφή `####-...`).
- Αναζητά `.xlsx` ή `.xls`.
- Κάνει `pd.read_excel` με αντίστοιχο engine.
- Επιστρέφει tuple: `(excel_df, csv_first_4, dash_part)`.

## 4.2 `modules/data_processor.py`
Βασικά στάδια:
- αφαίρεση άχρηστων στηλών,
- trim column names,
- dedup + drop NaN σε `a/a`,
- cast `a/a` σε int,
- rename βασικών στηλών (`proteine -> Protein` κ.λπ.),
- format δεκαδικών,
- υπολογισμός `TS`, `SNF`.

## 4.3 `modules/time_handler.py`
- parsing ημερομηνίας (`DD-MM` -> `DD/MM/YYYY`),
- parsing/παραγωγή αρχικής ώρας,
- δημιουργία sample ids,
- δημιουργία sample/zero times ανά batch.

## 4.4 `modules/zero_loader.py`
- έλεγχος ύπαρξης `zero.xlsx`,
- auto-download από Supabase αν λείπει.

## 4.5 `modules/zero_manager.py`
- φόρτωση και προετοιμασία zero dataframe,
- ενημέρωση date/time σε valid zero rows,
- δημιουργία copies ανά block,
- εξαγωγή βοηθητικού `zero.csv`.

## 4.6 `modules/output_generator.py`
- χτίζει `filled_df` με τελική διάταξη στηλών,
- κάνει split σε `parts/p1.csv`, `p2.csv`, ...,
- συνθέτει final CSV και παρεμβάλλει zero blocks,
- καθαρίζει προσωρινά part files.

## 4.7 `modules/missing_row.py`
- βρίσκει missing values της ακολουθίας `a/a`,
- ζητά user input μέσω callback,
- κάνει rollback αν ο χρήστης cancel,
- εισάγει νέες γραμμές και ξαναταξινομεί.

---

## 5) Ρυθμίσεις (`config.py`)
Κεντρικές μεταβλητές:
- `BASE_PATH`, `OUTPUT_PATH`, `PARTS_PATH`, `ZERO_PATH`, `FINAL_OUTPUT_PATH`.
- `BATCH_SIZE`, `T_SAMPLE_INCREMENT`, `T_ZERO_INCREMENT`, `ZERO_BLOCK_ROWS`.
- `COLUMN_RENAMES`, `COLS_TO_DELETE`, `TARGET_COLUMN_ORDER`.
- `DEFAULT_PRODUCT`, `DEFAULT_TIME`, `DEFAULT_REP`.
- `DROP_ZERO_NUTRIENTS`.

Πρακτικά, το GUI διαβάζει/σώζει μέρος των παραπάνω μέσω `ConfigEditor`.

---

## 6) Λάθη / απροσεξίες που εντοπίστηκαν (χωρίς αλλαγή κώδικα)

1. **README εκτός πραγματικότητας έργου**  
   Αναφέρει `main.py`, `install_one_click.bat`, `run_gui.bat`, και δομή φακέλων που δεν υπάρχουν στο repo. Αυτό δυσκολεύει onboarding/debug.  

2. **Η επιλογή προϊόντος στο Settings tab δεν εφαρμόζεται τελικά**  
   Στο processing γίνεται log του επιλεγμένου product, αλλά το metadata παράγεται από `MetadataGenerator` με `config.DEFAULT_PRODUCT` και δεν αντικαθίσταται από `settings_tab.get_product()`. Άρα το τελικό CSV δεν ακολουθεί το UI selection προϊόντος.  

3. **Πιθανό λάθος στο φίλτρο zero nutrients (τύποι δεδομένων)**  
   Στο `process_data` τα `Fat/Protein/Lactose` περνούν από `format_decimals` και καταλήγουν string values. Στο tab processing το φίλτρο συγκρίνει με αριθμητικό `0`, κάτι που μπορεί να μην αφαιρεί σωστά γραμμές με `'0'`/`'0.0'`.  

4. **Ασυνέπεια προεπιλεγμένης ώρας**  
   Η `TimeHandler.get_initial_time()` γράφει ότι αν πατηθεί Enter θα χρησιμοποιηθεί `DEFAULT_TIME`, αλλά στην πράξη δημιουργεί random λεπτά γύρω από 11:xx. Το μήνυμα/UX δεν είναι συνεπές με την υλοποίηση.  

5. **Ευθραυστότητα σε ονόματα στηλών με trailing space**  
   Το flow των missing rows χρησιμοποιεί keys όπως `"lactose "` (με κενό), που είναι εύκολο να προκαλέσει mismatch σε μελλοντικό refactor ή import διαφορετικού template.

6. **Windows-only άνοιγμα αρχείων/φακέλων χωρίς fallback**  
   Τα `open_output_folder` / `open_final_file` βασίζονται σε `os.startfile`, άρα σε non-Windows environment αποτυγχάνουν.

7. **`ph_handler.py` είναι ημιτελές και μη συνδεδεμένο**  
   Περιέχει μόνο skeleton λογική και δεν ενσωματώνεται στη βασική ροή.

8. **`data_loader.load_data()` μπορεί να ψάξει λάθος φάκελο**  
   Αν κληθεί χωρίς explicit `base_path`, χρησιμοποιεί path σχετικό με το module (`modules/`) αντί για config `BASE_PATH`, άρα πιθανό file-not-found σε CLI scenario.

---

## 7) Προτεινόμενο οργανωτικό πλάνο (χωρίς αλλαγές κώδικα)

- Να χρησιμοποιείται αυτό το έγγραφο ως “source of truth” για αρχιτεκτονική.
- Να μείνει η τρέχουσα λειτουργικότητα ως έχει και να καταγραφούν τα θέματα ως backlog fixes.
- Να ευθυγραμμιστεί το public README με το πραγματικό entrypoint (`csv_Lab.py`) και τα πραγματικά αρχεία.

---

## 8) Γρήγορη εκκίνηση (πραγματική)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python csv_Lab.py
```

> Για Windows executable mode, οι ρυθμίσεις `config.py` γράφονται δίπλα στο executable από το `ConfigEditor`.
