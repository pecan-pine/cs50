
# keep asking for height until user gives an integer between 1 and 8
while True:
    try:
        h = int(input("Height: "))
        if h < 1 or h > 8:
            continue
        else:
            break
    except ValueError:
        continue

for i in range(h):
    print((h-i-1) * " " + (i+1) * "#")