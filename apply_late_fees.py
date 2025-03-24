from datetime import datetime
import psycopg2
from decimal import Decimal
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import connect_db

def apply_late_fees():
    """Check for overdue invoices and apply a fixed late fee without modifying the original amount_due."""
    conn = connect_db()
    if not conn:
        print("❌ Database connection failed.")
        return

    try:
        cur = conn.cursor()

        # Step 1: Mark unpaid invoices as 'overdue' if their due date has passed
        cur.execute("""
            UPDATE invoices
            SET status = 'overdue'
            WHERE status = 'unpaid' AND due_date < CURRENT_DATE
        """)
        conn.commit()  # Ensure status updates before applying fees

        # Fetch the fixed late fee from settings (default: 1500 Ksh)
        cur.execute("SELECT value FROM settings WHERE key = 'late_fee_fixed'")
        late_fee_fixed = Decimal(cur.fetchone()[0]) if cur.rowcount else Decimal("1500.0")  

        # Step 2: Get overdue invoices that do not already have a late fee applied
        cur.execute("""
            SELECT id, tenant_id, amount_due, COALESCE(late_fee, 0)
            FROM invoices 
            WHERE status = 'overdue' AND due_date < CURRENT_DATE
        """)
        overdue_invoices = cur.fetchall()

        for invoice_id, tenant_id, amount_due, existing_late_fee in overdue_invoices:
            if existing_late_fee == 0:  # Only apply if no late fee exists
                new_late_fee = late_fee_fixed  # Apply only the late fee

                # Update ONLY the late_fee column
                cur.execute("""
                    UPDATE invoices 
                    SET late_fee = %s
                    WHERE id = %s
                """, (new_late_fee, invoice_id))

                # Fetch tenant contact details
                cur.execute("SELECT full_name, email FROM tenants WHERE id = %s", (tenant_id,))
                tenant = cur.fetchone()
                tenant_name, tenant_email = tenant if tenant else ("Unknown", None)

                # Log application of late fee
                print(f"[{datetime.now()}] 🏠 Late fee of {late_fee_fixed} applied to Invoice {invoice_id} for {tenant_name}.")

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Late fee process completed.")

    except psycopg2.Error as e:
        print(f"⚠️ Database Error: {e}")

if __name__ == "__main__":
    apply_late_fees()
