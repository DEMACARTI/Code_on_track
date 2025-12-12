from dateutil.relativedelta import relativedelta
from datetime import datetime

def compute_expiry(manufacture_date, warranty_months):
    if not manufacture_date or warranty_months is None:
        return None
    # Ensure manufacture_date is a datetime object if it's not already
    # (Assuming it comes from DB as date or datetime)
    return manufacture_date + relativedelta(months=warranty_months)
