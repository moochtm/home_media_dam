

def check_key_value(dic, key, value):
    if key in dic:
        if dic[key] == value:
            return True
    return False