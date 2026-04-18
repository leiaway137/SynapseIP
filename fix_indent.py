with open("main.py", "r") as f:
    lines = f.readlines()
for i in range(393, 498):
    if lines[i].strip():
        lines[i] = "    " + lines[i]
with open("main.py", "w") as f:
    f.writelines(lines)
