# program to import csv data to sqlite database

import csv
from sys import argv
from sys import exit
from cs50 import SQL

# initialize the database and delete information from the
# student table and from sequence table
db = SQL("sqlite:///students.db")
db.execute("DELETE FROM students;")
db.execute("DELETE FROM sqlite_sequence;")

# input should be a csv file
if len(argv) != 2:
    print("Oops wrong number of arguments")
    exit(1)

# open the file and load data into database
with open(argv[1]) as file:
    # create csv reader to read the file
    reader = csv.reader(file)
    # rows have pattern name/house/birth
    # next to skip first row (header)
    next(reader)
    for row in reader:
        # names in csv file are like "Harry James Potter" or "Ron Weasley"
        # need to split into first middle last
        name_parts = row[0].split(' ')
        house = row[1]
        birth = int(row[2])
        # if there is no middle name given, assign the value None to middle name
        # sqlite will interpret this as NULL
        if len(name_parts) == 2:
            first = name_parts[0]
            middle = None
            last = name_parts[1]
        elif len(name_parts) == 3:
            first = name_parts[0]
            middle = name_parts[1]
            last = name_parts[2]
        # if a different name pattern exists, exit
        else:
            print("Name error")
            exit(2)
        # add the data to the table students
        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", first, middle, last, house, birth)

