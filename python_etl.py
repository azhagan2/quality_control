import pandas as pd
import re
import os
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Find today's downloaded file
# -----------------------------


print("Current folder:", os.getcwd())

print("Root files:")
print(os.listdir())

if os.path.exists("Downloads"):
    print("Downloads folder exists")
    print(os.listdir("Downloads"))
else:
    print("Downloads folder missing")

today = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")

download_folder = "Downloads"

file_name = None

for file in os.listdir(download_folder):
    print("Found attachment:", repr(file))
    if today in file and file.endswith(".csv"):
        file_name = os.path.join(
            download_folder,
            file)
        break

if not file_name:
    print("No file found")
    exit()

print("Processing:", file_name)

# IMPORTANT
df = pd.read_csv(
    file_name,
    header=None,
    dtype=str,
    keep_default_na=False
)

rows = df.values.tolist()

final_data = []
current_metric = None
shifts = []

for row in rows:

    row = [str(x).strip() for x in row]

    print(row)     # TEMP debug

    first_col = row[0]

    # detect metric section
    if "eb/100sh" in first_col.lower():

        current_metric = "eb100sh"

        print("Metric:", current_metric)

        continue

    # detect machine header
    if "M/c. No." in first_col:

        shifts = []

        for col in row[1:]:

            m = re.search(
                r'(\d{2}-\d{2}-\d{4})\s+\((\d)\)',
                col
            )

            if m:

                date = m.group(1)
                shift = m.group(2)

                shifts.append(
                    (date, shift)
                )

        print("Shifts:", shifts)

        continue


    # machine rows
    if first_col.isdigit():

        machine = int(first_col)

        print("Machine:", machine)

        for i,val in enumerate(row[1:]):

            if i >= len(shifts):
                continue

            if val == "":
                continue

            try:

                final_data.append({

                    "Date": shifts[i][0],
                    "Shift": shifts[i][1],
                    "Machine": machine,
                    "Metric": current_metric,
                    "Value": float(val)

                })

            except:
                pass


output_df = pd.DataFrame(final_data)

print(output_df)

print(output_df.head())

# -----------------------------
# upload to google sheet
# -----------------------------

SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
"https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    'service_account.json',
    scopes=SCOPES
)

client = gspread.authorize(
    creds
)

sheet = client.open(
    "eb/100sh"
)

worksheet = sheet.worksheet(
    "raw_data"
)

worksheet.append_rows(
    output_df.values.tolist()
)

print(
    "Google sheet updated"
)

try:

    os.remove(file_name)

    print(
        f"Deleted: {file_name}"
    )

except Exception as e:

    print(
        f"Delete failed: {e}"
    )