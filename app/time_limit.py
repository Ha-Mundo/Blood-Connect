import datetime

def threshold_donation(base_date):
    """
    Calculates the date when a donor is eligible to donate again.
    Standard safety interval: 90 days.
    """
    threshold = datetime.timedelta(days=90)
    return base_date + threshold

def threshold_request(base_date):
    """
    Calculates the date when a user can make a new blood request.
    Anti-spam interval: 7 days.
    """
    threshold = datetime.timedelta(days=7)
    return base_date + threshold

def is_action_allowed(next_allowed_date, current_date):
    """
    Checks if the required time interval has passed.
    Returns True if the action is allowed, False otherwise.
    """
    return current_date >= next_allowed_date