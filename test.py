import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open(
    "eb/100sh"
)

worksheet = sheet.worksheet(
    "raw_data"
)

worksheet.append_row([
    "14-05-2026",
    "1",
    "14",
    "eb100sh",
    "8.35"
])

print("Success")