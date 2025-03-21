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

def send_invoice_email(tenant_email, tenant_name, pdf_path):
    """Send an invoice email with a PDF attachment."""
    subject = "Your Monthly Rental Invoice"
    body = f"""
    Dear {tenant_name},

    Please find attached your rental invoice for this month.

    Kindly ensure payment is made before the due date to avoid late fees.

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
    try:
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
    except FileNotFoundError:
        print(f"Error: Invoice PDF not found for {tenant_name} ({pdf_path})")
        return

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, tenant_email, msg.as_string())
        print(f"✅ Invoice sent to {tenant_email}")
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send email to {tenant_email}: {e}")

def send_all_invoices():
    """Fetch tenant emails and send invoices."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.id, t.full_name, t.email
                FROM invoices i
                JOIN tenants t ON i.tenant_id = t.id
                WHERE i.status = 'unpaid'
            """)
            invoices = cur.fetchall()

    for invoice_id, tenant_name, tenant_email in invoices:
        pdf_path = f"invoices/invoice_{invoice_id}.pdf"
        if os.path.exists(pdf_path):
            send_invoice_email(tenant_email, tenant_name, pdf_path)
        else:
            print(f"⚠️ Invoice PDF missing for {tenant_name} (ID: {invoice_id})")

# Run the script
if __name__ == "__main__":
    send_all_invoices()
