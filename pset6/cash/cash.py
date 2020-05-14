# keep asking for amount until user gives a nonnegative float
while True:
    try:
        amt = round(100 * float(input("Change owed: ")))
        if amt < 0:
            continue
        else:
            break
    except ValueError:
        continue

coin_counter = 0

# make change takes and amount (in cents)
# and a denomination (in cents)


def make_change(amt, denom):
    # use coin_counter and amt as a global variable
    global coin_counter
    # add the number of denom that fits into amt to coin_counter
    coin_counter += int(amt / denom)
    # what is left after making change
    amt = amt % denom
    return amt
    

for denom in [25, 10, 5, 1]:
    if amt == 0:
        break
    elif amt >= denom:
        # print(f"making change with {denom}'s")
        amt = make_change(amt, denom)

print(coin_counter)
