import os

with open("credentials.json","w") as f:
    f.write(os.environ["GMAIL_CREDENTIALS"])

with open("token.json","w") as f:
    f.write(os.environ["GMAIL_TOKEN"])

with open("service_account.json","w") as f:
    f.write(os.environ["SERVICE_ACCOUNT_JSON"])

    print("Secrets recreated")