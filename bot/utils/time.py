from datetime import datetime


def to_timestamp(datetime_obj: datetime, ret_type=None):
    """
    Returns UNIX timestamp from the supplied datetime object.
    """
    unix_ts = int(datetime_obj.timestamp())
    if ret_type not in [None, 'F', 'f', 'R']:
        raise ValueError('ret_type must be None (only timestamp returned), "F" (long), "f" (short), or "R" (relative).')
    if ret_type is None:
        return unix_ts
    else:
        return f'<t:{unix_ts}:{ret_type}>'
