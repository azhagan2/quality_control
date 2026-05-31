from fileinput import filename

import pandas as pd
import re
import os
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Setup
# -----------------------------

print("Current folder:", os.getcwd())

today = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")

download_folder = "Downloads"

file_name = None
original_xls = None


# -----------------------------
# Find file
# -----------------------------

for file in os.listdir(download_folder):

    print("Found attachment:", repr(file))

    if today in file and (
        file.endswith(".csv")
        or file.endswith(".xls")
    ):

        file_name = os.path.join(
            download_folder,
            file
        )

        break


if not file_name:

    print("No file found")
    exit()


print("Processing:", file_name)


# -----------------------------
# Convert xls → csv
# -----------------------------

if file_name.endswith(".xls"):

    original_xls = file_name

    print("Converting XLS to CSV...")

    temp_csv = file_name.replace(
        ".xls",
        ".csv"
    )

    excel_df = pd.read_excel(
        file_name,
        header=None,
        dtype=str
    )

    excel_df.to_csv(
        temp_csv,
        index=False,
        header=False
    )

    file_name = temp_csv

    print(
        "Converted:",
        file_name
    )


# -----------------------------
# Read CSV
# -----------------------------

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


# -----------------------------
# Parse rows
# -----------------------------

for row in rows:

    row = [

        str(x).strip()

        for x in row

    ]

    print(row)

    first_col = row[0]


    # -------------------------
    # Metric detection
    # -------------------------

    if "100sh" in first_col.lower():
        current_metric = "eb100sh"
    elif "rpm" in first_col.lower():
        current_metric = "Avg spndl rpm"
    elif "gpss" in first_col.lower():
        current_metric = "GPSS"


        print("Metric:", current_metric)

        continue


    # -------------------------
    # Machine/date header
    # -------------------------

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

                    (

                        date,
                        shift

                    )

                )

        print(
            "Shifts:",
            shifts
        )

        continue


    # -------------------------
    # Machine rows
    # -------------------------

    if first_col.isdigit():

        machine = int(

            first_col

        )

        print(
            "Machine:",
            machine
        )

        for i,val in enumerate(

            row[1:]

        ):

            if i >= len(

                shifts

            ):

                continue


            if val == "":

                continue


            try:

                final_data.append({

                    "Date":

                    shifts[i][0],

                    "Shift":

                    shifts[i][1],

                    "Machine":

                    machine,

                    "Metric":

                    current_metric,

                    "Value":

                    float(val)

                })

            except:

                pass


# -----------------------------
# Dataframe
# -----------------------------

output_df = pd.DataFrame(

    final_data

)

print(output_df)

print(

    output_df.head()

)


# -----------------------------
# Google Sheet Upload
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


# -----------------------------
# Delete files
# -----------------------------

try:

    if os.path.exists(

        file_name

    ):

        os.remove(

            file_name

        )

        print(

            f"Deleted CSV: {file_name}"

        )


    if (

        original_xls
        and
        os.path.exists(
            original_xls
        )

    ):

        os.remove(

            original_xls

        )

        print(

            f"Deleted XLS: {original_xls}"

        )


except Exception as e:

    print(

        f"Delete failed: {e}"

    )