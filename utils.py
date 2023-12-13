from difflib import unified_diff

def generate_diff(origin, modified):
    original_lines = origin.splitlines()
    modified_lines = modified.splitlines()

    diff = []

    for i, line in enumerate(unified_diff(original_lines, modified_lines)):

        if i < 2:
            continue

        if i == 2:

            ds = str(line)
            ds = ds.replace("@@ ", "Modifications: ")
            ds = ds.replace(" @@", "")

            diff.append(ds)
        else:
            if line.startswith('+') or line.startswith('-'):
                diff.append(line[:1] + ' ' + line[1:])
            else:
                diff.append("=" + line)

    diff_str = "```"
    diff_str += '\n'.join(diff)
    diff_str += "```"

    return diff_str