base36_chars = [];

# Initializing the characters used to define the base-36 set.
for i in range(0, 10):
    base36_chars.append(str(i))
for i in range(ord('A'), ord('Z') + 1):
    base36_chars.append(chr(i))

def int_to_base36(value, digits=0):
    """Converts an integer to a base-36 string using 0-9, A-Z to represent the digits 0-35,
       respectively."""
    output = ""

    output += base36_chars[value % 36]
    value = int(value / 36)

    while value > 0:
        output = base36_chars[value % 36] + output
        value = int(value / 36)

    length = len(output)
    while length < digits:
        output = "0" + output
        length += 1

    return output
