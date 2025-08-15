import pandas as pd
import re
from tkinter import Tk, filedialog
from tqdm import tqdm
from datetime import datetime
import os

print("\nDeveloped by Jacob Wilson - Version 0.1")
print("dfirvault@gmail.com\n")

def guess_timestamp_column(columns):
    """Try to identify the most likely timestamp column"""
    priority = ['timestamp', '@timestamp', 'time', 'datetime', 'date']
    for p in priority:
        for col in columns:
            if re.search(p, col, re.IGNORECASE):
                return col
    return None

def select_timestamp_column(df, auto_select=False):
    """Prompt user to select the timestamp column with smart suggestions"""
    if auto_select:
        return guess_timestamp_column(df.columns)
    
    print("\nCSV Headers with Sample Values (row 1):")
    if df.empty:
        print("⚠️ DataFrame is empty. Cannot determine timestamp column.")
        return None

    sample_row = df.iloc[0].to_dict()
    for i, col in enumerate(df.columns, 1):
        sample_val = sample_row.get(col, '')
        print(f"{i}. {col} - {sample_val}")

    default_guess = guess_timestamp_column(df.columns)
    if default_guess:
        example_val = sample_row.get(default_guess, 'N/A')
        print(f"\n📌 Suggested timestamp column: {default_guess} (e.g. {example_val})")

    while True:
        selection = input(f"Select timestamp column, either in Epoch time or ISO-8601 (YYYY-MM-DDTHH:MM:SSZ) [press Enter to accept '{default_guess}']: ")
        if selection.strip() == '' and default_guess:
            selected_col = default_guess
            break
        try:
            index = int(selection) - 1
            selected_col = df.columns[index]
            break
        except (IndexError, ValueError):
            print("❌ Invalid selection. Try again.")

    samples = df[selected_col].dropna().astype(str).head(5).tolist()
    print(f"\n📋 Sample values from '{selected_col}':")
    for s in samples:
        iso_version = None
        try:
            num = float(s)
            # Heuristics: 13-digit is ms, 10-digit is s
            if len(str(int(num))) >= 13:
                iso_version = datetime.utcfromtimestamp(num / 1000).isoformat() + "Z"
            elif len(str(int(num))) == 10:
                iso_version = datetime.utcfromtimestamp(num).isoformat() + "Z"
        except:
            pass

        if iso_version:
            print(f"  - {s} → {iso_version}")
        else:
            print(f"  - {s}")
    print("🔍 Make sure these are valid ISO-8601 timestamps.")

    confirm = input("✅ Proceed with this timestamp field? (y/n): ").strip().lower()
    if confirm != 'y':
        return select_timestamp_column(df)

    return selected_col

def convert_timestamps(df, timestamp_column):
    """Convert the selected timestamp column to standardized ISO format"""
    print("\n🔄 Converting timestamps...")
    
    def convert_single_timestamp(ts_val):
        if pd.isna(ts_val) or str(ts_val).strip() == '':
            return None
        try:
            # Handle numeric epoch time (seconds or milliseconds)
            if isinstance(ts_val, (int, float)) or re.match(r'^\d+(\.\d+)?$', str(ts_val)):
                ts_float = float(ts_val)
                if ts_float > 1e12:  # likely in milliseconds
                    return datetime.utcfromtimestamp(ts_float / 1000).isoformat() + 'Z'
                else:  # assume seconds
                    return datetime.utcfromtimestamp(ts_float).isoformat() + 'Z'
            else:
                return pd.to_datetime(ts_val, utc=True).isoformat()
        except Exception as e:
            print(f"⚠️ Failed to parse timestamp: {ts_val} ({e})")
            return None

    # Apply conversion with progress bar
    tqdm.pandas(desc="Converting timestamps")
    df['timestamp'] = df[timestamp_column].progress_apply(convert_single_timestamp)
    
    # Move the new column to the front
    cols = df.columns.tolist()
    cols = ['timestamp'] + [col for col in cols if col != 'timestamp']
    return df[cols]

def select_input_file():
    """Open file dialog to select input CSV file"""
    print("\n📂 Select input CSV file...")
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    root.destroy()
    return file_path

def select_input_folder():
    """Open folder dialog to select input folder"""
    print("\n📂 Select folder containing CSV files...")
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

def select_output_folder():
    """Open folder dialog to select output location"""
    print("\n📂 Select output folder...")
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

def save_output_file(input_path, output_folder, df):
    """Save the modified DataFrame to a new CSV file in selected location"""
    original_filename = os.path.basename(input_path)
    output_filename = os.path.splitext(original_filename)[0] + "_processed.csv"
    output_path = os.path.join(output_folder, output_filename)
    
    lines_written = len(df)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved {lines_written} lines to: {output_path}")
    return output_path, lines_written

def process_single_file():
    """Process a single CSV file with user interaction"""
    csv_path = select_input_file()
    if not csv_path:
        print("No file selected. Exiting.")
        return
    
    try:
        print("\n📄 Reading CSV file...")
        df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False, on_bad_lines='warn')
        lines_read = len(df)
        print(f"📊 Read {lines_read} lines from input file")
        df = df.where(pd.notnull(df), None)
        
        timestamp_column = select_timestamp_column(df)
        if not timestamp_column:
            print("No timestamp column selected. Exiting.")
            return
            
        output_folder = select_output_folder()
        if not output_folder:
            print("No output folder selected. Exiting.")
            return
            
        processed_df = convert_timestamps(df, timestamp_column)
        output_path, lines_written = save_output_file(csv_path, output_folder, processed_df)
        
        print("\n" + "="*50)
        print("📝 Processing Summary:")
        print(f"• Input file: {os.path.basename(csv_path)}")
        print(f"• Lines read: {lines_read}")
        print(f"• Output file: {os.path.basename(output_path)}")
        print(f"• Lines written: {lines_written}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

def process_bulk_files():
    """Process all CSV files in a folder (including subfolders) automatically"""
    input_folder = select_input_folder()
    if not input_folder:
        print("No input folder selected. Exiting.")
        return
        
    output_folder = select_output_folder()
    if not output_folder:
        print("No output folder selected. Exiting.")
        return
    
    # Find all CSV files recursively
    csv_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print("No CSV files found in the selected folder.")
        return
    
    print(f"\nFound {len(csv_files)} CSV files to process...")
    
    success_count = 0
    total_lines_read = 0
    total_lines_written = 0
    
    for csv_path in tqdm(csv_files, desc="Processing files"):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False, on_bad_lines='warn')
            lines_read = len(df)
            total_lines_read += lines_read
            df = df.where(pd.notnull(df), None)
            
            timestamp_column = select_timestamp_column(df, auto_select=True)
            if not timestamp_column:
                print(f"\n⚠️ Could not auto-detect timestamp column in: {os.path.basename(csv_path)}")
                continue
                
            processed_df = convert_timestamps(df, timestamp_column)
            _, lines_written = save_output_file(csv_path, output_folder, processed_df)
            total_lines_written += lines_written
            success_count += 1
            
        except Exception as e:
            print(f"\n⚠️ Error processing {os.path.basename(csv_path)}: {str(e)}")
    
    print("\n" + "="*50)
    print("📝 Bulk Processing Summary:")
    print(f"• Files found: {len(csv_files)}")
    print(f"• Files successfully processed: {success_count}")
    print(f"• Files failed: {len(csv_files) - success_count}")
    print(f"• Total lines read: {total_lines_read}")
    print(f"• Total lines written: {total_lines_written}")
    print("="*50 + "\n")

def main():
    """Main menu function"""
    while True:
        print("\n=== CSV Timestamp Processor ===")
        print("1. Process single CSV file (interactive)")
        print("2. Bulk process CSV files (automatic)")
        print("0. Exit")

        choice = input("Enter choice: ").strip()

        if choice == '1':
            process_single_file()
        elif choice == '2':
            process_bulk_files()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
