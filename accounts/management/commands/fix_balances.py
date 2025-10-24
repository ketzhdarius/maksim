from django.core.management.base import BaseCommand
from decimal import Decimal, InvalidOperation
from django.db import connection, transaction
from accounts.models import CustomUser

class Command(BaseCommand):
    help = (
        "Fix invalid balance values for CustomUser by setting them to 0.00 when "
        "Decimal conversion fails. Uses raw SQL to avoid ORM Decimal conversion "
        "errors when the DB contains corrupt values."
    )

    def handle(self, *args, **options):
        # Get model field metadata so we can validate values against max_digits
        field = CustomUser._meta.get_field('balance')
        max_digits = field.max_digits
        decimal_places = field.decimal_places
        # Maximum absolute value allowed (e.g. for max_digits=10, decimal_places=2 -> 10**8)
        max_allowed = Decimal(10) ** (max_digits - decimal_places)

        # Read raw values directly from the DB to avoid Django's Decimal conversion
        # that happens when loading model instances and can raise InvalidOperation
        # if the stored value is malformed.
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, balance FROM accounts_customuser")
            rows = cursor.fetchall()

        bad_ids = []
        for id_, balance in rows:
            try:
                # Convert using str() to handle bytes/None etc in a predictable way
                dec = Decimal(str(balance))
            except (InvalidOperation, TypeError, ValueError):
                bad_ids.append(id_)
                continue

            # If the absolute value exceeds the field's allowed maximum mark it as bad
            try:
                if abs(dec) >= max_allowed:
                    bad_ids.append(id_)
            except Exception:
                # Any unexpected error treat as bad so we can repair it
                bad_ids.append(id_)

        if not bad_ids:
            self.stdout.write(self.style.SUCCESS("No invalid balances found."))
            return

        fixed = 0
        # Update invalid rows to a clean decimal string. Use a transaction for safety.
        with transaction.atomic():
            with connection.cursor() as cursor:
                for uid in bad_ids:
                    cursor.execute("UPDATE accounts_customuser SET balance = ? WHERE id = ?", ["0.00", uid])
                    fixed += 1

        for uid in bad_ids:
            self.stdout.write(f"Fixed user id={uid} balance -> 0.00")

        self.stdout.write(self.style.SUCCESS(f"Balances fixed: {fixed}"))
