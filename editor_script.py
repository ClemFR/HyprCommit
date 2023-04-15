#!/usr/bin/python3

"""
python script to automate replacing `pick <<hash>> <message>`
with `edit ...`
"""

import sys

# get file in param name
if len(sys.argv) != 2:
    print("Usage: python3 edit.py <file>")
    exit(1)

file = sys.argv[1]
print(f"Editing file {file}")

# read file content
with open(file, "r") as f:
    content = f.readlines()
    f.close()

# replace content
new_content = []
for line in content:
    if "pick" in line:
        new_content.append(line.replace("pick", "edit"))
    else:
        new_content.append(line)

# write new content
with open(file, "w") as f:
    f.writelines(new_content)
    f.close()
