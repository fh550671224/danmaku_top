def is_list_of_tuples(obj):
    if not isinstance(obj, list):
        return False

    for item in obj:
        if not (isinstance(item, tuple) and len(item) == 2):
            return False
    return True