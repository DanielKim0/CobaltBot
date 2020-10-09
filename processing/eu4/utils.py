def add_quotes(string):
    if string[0] != "\"" and string[-1] != "\"":
        return "\"" + string + "\""
    else:
        return string

# used to...
LEADER_TEMPLATE = {
    "name": "",
    "dynasty": "",
    "claim": "",
    "adm": "",
    "dip": "",
    "mil": "",
    "add_ruler_personality": "",
    "add_heir_personality": "",
    "leader": "",
    "fire": "",
    "shock": "",
    "manuever": "",
    "siege": "",
}