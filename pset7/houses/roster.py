# program to find the house of a given hogwarts student

from sys import argv
from sys import exit
from cs50 import SQL

if len(argv) != 2:
    print("Oops wrong number of arguments")
    exit(1)

# initialize the database
db = SQL("sqlite:///students.db")

# program takes input the house
house = argv[1].lower().capitalize()

# find all students from that house, ordered by last name
# print out student information
for row in db.execute("SELECT * FROM students WHERE house = ? ORDER BY last, first;", house):
    if row['middle'] == None:
        print(row['first'], row['last'] + ",", "born", row['birth'])
    else:
        print(row['first'], row['middle'], row['last'] + ",", "born", row['birth'])

