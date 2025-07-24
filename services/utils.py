import re

def fuck_around(source, pattern) -> str:
    match = re.search(pattern, source)
    if match:
        return match.group(1)
    else:
        return ""

