import datetime
from app.config.rules import DONATION_COOLDOWN, REQUEST_COOLDOWN

def threshold_donation(date):
    """
    Calculates the date when a donor is eligible to donate again.
    Standard safety interval: 90 days.
    """
    return date +  DONATION_COOLDOWN

def threshold_request(date):
    """
    Calculates the date when a user can make a new blood request.
    Anti-spam interval: 7 days.
    """
    return date + REQUEST_COOLDOWN

def is_action_allowed(next_allowed_date, current_date):
    """
    Checks if the required time interval has passed.
    Returns True if the action is allowed, False otherwise.
    """
    return current_date >= next_allowed_date