def add_payment(self, tenant_dropdown, amount_paid_input, payment_date_input, 
                payment_method_input, status_input, dialog):
    """Insert a new payment record into the database and update invoice status accordingly."""
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Get values from the form
        tenant_id = tenant_dropdown.currentData()  # Get tenant ID from dropdown
        amount_paid = Decimal(amount_paid_input.text())  # Convert to Decimal for accuracy
        payment_date = payment_date_input.date().toString("yyyy-MM-dd")
        payment_method = payment_method_input.currentText().lower()  # Convert to lowercase
        status = status_input.currentText().lower()  # Convert to lowercase if needed

        # Ensure required fields are not empty
        if not tenant_id or not amount_paid or not payment_date or not payment_method:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return

        # Fetch tenant's existing credit balance
        cur.execute("SELECT credit_balance FROM tenants WHERE id = %s", (tenant_id,))
        credit_balance = cur.fetchone()[0] or Decimal(0)

        # Generate the next receipt number
        cur.execute("SELECT receipt_number FROM payments ORDER BY id DESC LIMIT 1")
        last_receipt = cur.fetchone()
        new_receipt = f"N{(int(last_receipt[0][1:]) + 1) if last_receipt else 1:03}"

        # Insert payment record
        query = """
        INSERT INTO payments (tenant_id, amount_paid, payment_date, 
                              payment_method, receipt_number, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (tenant_id, amount_paid, payment_date, 
                            payment_method, new_receipt, status))

        payment_id = cur.fetchone()[0]
        print(f"✅ Payment {payment_id} recorded: Tenant {tenant_id} paid {amount_paid}")

        # Fetch the earliest unpaid invoice
        cur.execute("""
            SELECT id, amount_due, late_fee, remaining_balance, status 
            FROM invoices 
            WHERE tenant_id = %s AND status IN ('unpaid', 'partially_paid', 'overdue')
            ORDER BY invoice_date ASC LIMIT 1
        """, (tenant_id,))
        invoice = cur.fetchone()

        if invoice:
            invoice_id, amount_due, late_fee, remaining_balance, status = invoice

            # Ensure remaining balance is correct
            if remaining_balance is None or remaining_balance == 0:
                remaining_balance = amount_due + late_fee  # Ensure correct tracking

            print(f"📜 Invoice {invoice_id} found: Amount Due = {amount_due}, Late Fee = {late_fee}, Corrected Remaining Balance = {remaining_balance}")

            # Apply payment to the invoice
            new_balance = remaining_balance - amount_paid
            print(f"💰 Payment applied: {amount_paid}, New Balance: {new_balance}")

            if new_balance <= 0:  # Full payment or overpayment
                cur.execute("""
                    UPDATE invoices 
                    SET status = 'paid', remaining_balance = 0 
                    WHERE id = %s
                """, (invoice_id,))
                print(f"✅ Invoice {invoice_id} marked as PAID")

                # If overpayment, store it as tenant credit
                overpaid_amount = abs(new_balance)
                if overpaid_amount > 0:
                    credit_balance += overpaid_amount
                    cur.execute("""
                        UPDATE tenants SET credit_balance = %s WHERE id = %s
                    """, (credit_balance, tenant_id))
                    print(f"💰 Overpayment of {overpaid_amount} stored as tenant credit (Total Credit: {credit_balance})")

            else:  # Partial payment case
                cur.execute("""
                    UPDATE invoices 
                    SET status = 'partially_paid', remaining_balance = %s 
                    WHERE id = %s
                """, (new_balance, invoice_id))
                print(f"⚠️ Invoice {invoice_id} is now PARTIALLY PAID. Remaining balance: {new_balance}")

        else:
            # If no unpaid invoice exists, store the entire amount as credit
            credit_balance += amount_paid
            cur.execute("""
                UPDATE tenants SET credit_balance = %s WHERE id = %s
            """, (credit_balance, tenant_id))
            print(f"💰 No invoice found. Entire payment stored as tenant credit (Total Credit: {credit_balance})")

        conn.commit()
        cur.close()
        conn.close()

        self.load_payments()  # Refresh payments table
        dialog.accept()  # Close the dialog
        QMessageBox.information(self, "Success", "Payment recorded successfully.")

        # Generate the receipt
        self.generate_receipt_pdf(payment_id)

    except psycopg2.Error as e:
        QMessageBox.critical(self, "Database Error", f"Failed to save payment: {e}")
        print(f"❌ Database Error: {e}")
