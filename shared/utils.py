import hashlib

def is_list_of_tuples(obj):
    if not isinstance(obj, list):
        return False

    for item in obj:
        if not (isinstance(item, tuple) and len(item) == 2):
            return False
    return True

def generate_hash(data):
    session_id = hashlib.sha256(data.encode('utf-8')).hexdigest()
    return session_id