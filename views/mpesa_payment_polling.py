import requests
import json
import psycopg2
from datetime import datetime, timedelta
import os
import sys
import threading
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db 

# Daraja API Config
IS_PRODUCTION = False  # Change to True for production

MPESA_AUTH_URL = (
    "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    if IS_PRODUCTION
    else "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
)
# Correct Transaction Fetching API
MPESA_API_URL = (
    "https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query"
    if IS_PRODUCTION
    else "https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query"
)

CONSUMER_KEY = "EatHgEWjcIoSr4pogp75doJSs5AbqQa1pQYtzQccOyoXIImU"
CONSUMER_SECRET = "JavbLOPrHzAvN1vnFvdTfsQmFJOkVHDAK6HhTTavvzVqbqCowcMtbryQRo9t1qLH"

class MpesaPoller:
    def __init__(self):
        self.access_token = None  # Initialize access token
        self.token_expiry = datetime.now()  # Initialize expiry time
        self.paybills = []

    def get_access_token(self):
        """Fetch a new access token if expired"""
        if self.access_token and datetime.now() < self.token_expiry:
            return self.access_token  # Return cached token

        print("🔄 Fetching new access token...")
        try:
            response = requests.get(
                MPESA_AUTH_URL, 
                auth=(CONSUMER_KEY, CONSUMER_SECRET)
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.token_expiry = datetime.now() + timedelta(seconds=int(data["expires_in"]))  # Store expiry time
                print(f"🔑 Auth Token: {self.access_token}")
                return self.access_token
            else:
                print(f"⚠️ Failed to get token: {response.text}")
                return None
        except requests.RequestException as e:
            print(f"❌ Network error while fetching token: {e}")
            return None
        
    def fetch_mpesa_payments(self):
        """Fetch transactions from M-Pesa API"""
        print("🚀 Fetching payments from M-Pesa API...")

        token = self.get_access_token()
        if not token:
            print("❌ Could not retrieve a valid access token.")
            return []

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT mpesa_paybill FROM apartment_payment_methods 
            WHERE mpesa_paybill IS NOT NULL AND mpesa_paybill <> ''
        """)  
        paybill_results = cur.fetchall()
        conn.close()

        self.paybills = [row[0] for row in paybill_results]

        if not self.paybills:
            print("⚠️ No valid PayBill number found in the database.")
            return []

        transactions = []
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        for paybill in self.paybills:
            print(f"📌 Fetching payments for PayBill: {paybill}")
            payload = {
                "ShortCode": paybill,
                "IdentifierType": 4,  # Set identifier type to PayBill Number
                "StartDate": (datetime.now() - timedelta(days=1)).strftime('%Y%m%d%H%M%S'),
                "EndDate": datetime.now().strftime('%Y%m%d%H%M%S')
            }

            try:
                response = requests.post(MPESA_API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    transactions.extend(data.get("Payments", []))
                else:
                    print(f"⚠️ Failed to fetch payments for {paybill}: {response.text}")
            except requests.RequestException as e:
                print(f"❌ Error fetching payments for {paybill}: {e}")

        print(f"✅ Retrieved {len(transactions)} payments.")
        return transactions

def run_in_background():
    poller = MpesaPoller()
    while True:
        poller.fetch_mpesa_payments()
        time.sleep(60)

if __name__ == "__main__":
    run_in_background()