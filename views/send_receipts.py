import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2

# Get email credentials from environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def connect_db():
    """Establish database connection."""
    return psycopg2.connect(
        dbname="rental_management",
        user="janice",
        host="localhost",
        port="5432"
    )

def send_receipt_email(payment_id):
    """Send a receipt email for a specific payment."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.receipt_number, t.full_name, t.email
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                WHERE p.id = %s AND p.status = 'paid'
            """, (payment_id,))
            payment = cur.fetchone()

    if not payment:
        print(f"⚠️ No matching payment found for Payment ID: {payment_id}")
        return

    receipt_number, tenant_name, tenant_email = payment
    print(f"🔍 Sending receipt {receipt_number} for {tenant_name} ({tenant_email})")  # Debug
    pdf_path = f"receipts/receipt_{payment_id}.pdf"

    if not os.path.exists(pdf_path):
        print(f"⚠️ Receipt PDF missing for {tenant_name} (Receipt: {receipt_number})")
        return

    # Email setup
    subject = "Payment Receipt - XYZ Property Management"
    body = f"""
    Dear {tenant_name},

    Thank you for your payment. Attached is your receipt (Receipt No: {receipt_number}).

    If you have any questions, feel free to contact us.

    Best regards,  
    XYZ Property Management  
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = tenant_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, tenant_email, msg.as_string())
        print(f"✅ Receipt sent to {tenant_email} (Receipt No: {receipt_number})")
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send receipt to {tenant_email}: {e}")

# Example usage: send_receipt_email(5)  # This will send a receipt for Payment ID 5
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        payment_id = sys.argv[1]
        print(f"🔍 Running send_receipt_email for Payment ID: {payment_id}")  # Debug log
        send_receipt_email(payment_id)
    else:
        print("⚠️ No Payment ID provided!")
