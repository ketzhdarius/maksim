from django.contrib.auth.backends import ModelBackend
from django.db import connection
from decimal import Decimal, InvalidOperation

class CleaningModelBackend(ModelBackend):
    """Custom backend that handles corrupt Decimal values on user retrieval.

    If a Decimal conversion (e.g. for `balance`) raises InvalidOperation when
    Django loads the user from the DB, this backend resets the user's balance
    to 0.00 using a direct SQL update and retries retrieval. This avoids
    crashing the request pipeline while repairing the bad value.
    """
    def get_user(self, user_id):
        try:
            return super().get_user(user_id)
        except InvalidOperation:
            # Try to repair the user's balance at the DB level and retry
            try:
                with connection.cursor() as cursor:
                    # SQLite uses ? parameter marker
                    cursor.execute(
                        "UPDATE accounts_customuser SET balance = ? WHERE id = ?",
                        [str(Decimal('0.00')), user_id]
                    )
            except Exception:
                # If repair fails, return None to avoid breaking the request
                return None
            try:
                return super().get_user(user_id)
            except Exception:
                return None

