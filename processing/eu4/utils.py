def add_quotes(string):
    if string[0] != "\"" and string[-1] != "\"":
        return "\"" + string + "\""
    else:
        return string
