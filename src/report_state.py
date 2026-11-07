"""Session-local report identity without global mutable event state."""

def report_key(image_hash, location):
    return (image_hash, location) if image_hash and location else None


def is_duplicate_report(key, submitted_keys):
    return key is not None and key in submitted_keys
