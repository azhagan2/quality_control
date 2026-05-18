import os
import base64
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

creds = None

if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES
    )

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build(
    "gmail",
    "v1",
    credentials=creds
)

results = service.users().messages().list(
    userId='me',
    q='label:EB/100SH'
).execute()

messages = results.get('messages', [])

print("Found:", len(messages))

if not messages:
    print("No mails found")
    exit()
    
today = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")

print("Looking for:", today)

found = False

for msg in messages:

    msg_id = msg['id']

    message = service.users().messages().get(
        userId='me',
        id=msg_id
    ).execute()

    parts = message['payload'].get(
        'parts',
        []
    )

    for part in parts:

        filename = part.get(
            'filename',
            ''
        )

        if filename and today in filename:

            print(
                "Matched:",
                filename
            )

            attachment_id = part['body'][
                'attachmentId'
            ]

            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(
                    userId='me',
                    messageId=msg_id,
                    id=attachment_id
                )
                .execute()
            )

            data = base64.urlsafe_b64decode(
                attachment['data']
            )

            # create folder if missing
            os.makedirs(
                "Downloads",
                exist_ok=True
            )

            path = os.path.join(
                "Downloads",
                filename
            )

            with open(
                path,
                'wb'
            ) as f:

                f.write(data)

            print(
                "Saved:",
                path
            )

            found = True
            break

    if found:
        break

if not found:
    print(
        "No attachment found for today's date"
    )