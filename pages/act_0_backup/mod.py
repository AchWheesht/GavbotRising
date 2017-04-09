import os
import re

pages = os.listdir()

with open("lobby_chase.txt", "r") as file:
    lines = file.readlines()
bounce_line = [x for x in lines if x[:8] == "<bounce>"]
index = lines.index(bounce_line[0])
lines.insert(index+1, "<special><special>\n")
data = "\n".join(lines)
data = re.sub("\n\n", "\n", data)
with open("lobby_chase.txt", "w") as file:
    file.write(data)
