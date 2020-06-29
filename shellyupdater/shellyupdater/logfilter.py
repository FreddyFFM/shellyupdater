"""
This module defines custom log filters
"""

def skip_logentry_startswith(record):
    """
    Filters Log-Entries starting with certain word(s)
    :param record:
    :return:
    """
    from .settings import LOG_SKIP_STARTSWITH
    if LOG_SKIP_STARTSWITH and record.msg.upper().startswith(tuple(LOG_SKIP_STARTSWITH.upper())):
        return False
    return True
