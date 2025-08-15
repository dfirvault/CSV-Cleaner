![WindowsSandboxRemoteSession_VoxTlQkyuQ](https://github.com/user-attachments/assets/8c2ae2e5-62af-42ec-b5d4-b289dc4d37c1)

# CSV Timestamp Processor

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python tool for processing CSV files with timestamp columns, featuring both single-file and bulk processing modes with comprehensive reporting.

Available as a single click .exe or python script.

## Features

- 🕒 Automatic timestamp column detection
- 🔄 Conversion of various timestamp formats to ISO-8601 standard
- 📂 Two processing modes:
  - **Interactive single-file** mode with column verification
  - **Automatic bulk processing** for entire directories
- 📊 Detailed processing statistics:
  - Lines read/written (per file and totals)
  - Files processed/skipped
  - Success/failure counts
- 🚀 Progress bars for bulk operations
- 📁 Flexible input/output folder selection

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/csv-timestamp-processor.git
   cd csv-timestamp-processor
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   ## Usage

Run the script:

```bash
python csv_timestamp_processor.py
```
You'll be presented with a menu:
```bash
=== CSV Timestamp Processor ===
1. Process single CSV file (interactive)
2. Bulk process CSV files (automatic)
0. Exit
```

###Single File Mode
Select your input CSV file

Verify/select the timestamp column

Choose output directory

View processing summary

###Bulk Processing Mode
Select input directory (processes all CSVs recursively)

Choose output directory

View comprehensive batch statistics

### Supported Timestamp Formats
1. Unix epoch (seconds or milliseconds)
2. ISO-8601 formats
3. Various datetime string formats (auto-detected)

### Output Format
Processed files will:
- Have "_processed" appended to the filename
- Contain a new "timestamp" column as the first column
- Preserve all original data

### Requirements for python version
- Python 3.7+
- pandas
- tqdm
- tkinter (usually included with Python)

### License
MIT License - see LICENSE file

### Author
Jacob Wilson
dfirvault@gmail.com
https://github.com/dfirvault
