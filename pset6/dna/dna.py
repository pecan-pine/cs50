'''Program to identify people from their dna sequences
assuming the sequence is stored in a list.
The program finds repeating patterns and compares
them to known counts. If a dna sequence matches all counts,
a person is found'''

import re
import csv
from sys import argv

# the program takes a csv file then a txt file in its argument
if len(argv) != 3:
    print("Oops wrong number of arguments")
    exit(1)

# new dictionary to store dna data in
dna_dict = {}

# open two copies of the csv file
with open(argv[1], newline='') as csvfile:
    with open(argv[1], newline='') as csvcopy:
        # make one copy into a csv dictreader and the other into a csv reader
        dictreader = csv.DictReader(csvfile)
        reader = csv.reader(csvcopy)
        # the list of given sequences is in the first row of the file
        sequence_list = next(reader)[1:]
        # empty name list, then add names (first item of each row after the first)
        # first row is not called since next(reader) ran once
        name_list = []
        for row in reader:
            name_list.append(row[0])
        # make a new dictionary in dna_dict, one for each name
        for row in dictreader:
            dna_dict[row['name']] = {}
            # for a given name's dictionary, add the number for each sequence
            for sequence in sequence_list:
                dna_dict[row['name']][sequence] = int(row[sequence])

with open(argv[2]) as dnafile:
    # dna is the person's dna as a string
    dna = dnafile.readline()
    # unknown_dna dict to store the data
    unknown_dna = {}
    # for loop to fill in data
    for sequence in sequence_list:
        # initialize for the while loop
        # no sequences found yet
        # it doesn't seem to matter whether sequence_count
        # is initialized as 0 or 1
        sequence_count = 1
        # so that while loop can start, put '' into sequences_found
        sequences_found = ['']
        while (sequences_found != []):
            # the regular expression searches for (sequence) repeated
            # sequence_count number of times. If there is no appearance of
            # the sequence, the regular expression returns '[]' and the
            # while loop will exit
            sequences_found = re.findall(f'({sequence}){{{sequence_count}}}', dna)
            # if at least sequence_count of the pattern sequence was found,
            # increase the sequence count by 1. If none of the sequence was found
            # at all, sequence count is left as 1
            # sequences_found gets one count added for each repetition of
            # the sequence, so it ends up being the actual count plus 1
            if(sequences_found != []):
                sequence_count += 1
        # subtract 1 to get actual sequence count
        sequence_count -= 1
        # set unknown_dna key for sequence to be the count
        unknown_dna[sequence] = sequence_count

# look_up_dna is a function in order to be able to break out 
# of the inner for loop


def look_up_dna(dna_dict, name_list, sequence_list, unknown_dna):
    # loop through all names
    for name in name_list:
        # number of dna sequence matches
        match_counter = 0
        # loop through all sequences
        for sequence in sequence_list:
            # if the sequence number found matches the one corresponding
            # to this name, add 1 to the match counter
            if dna_dict[name][sequence] == unknown_dna[sequence]:
                match_counter += 1
        # if all sequences match, we've found the person!
        if match_counter == len(sequence_list):
            return print(name)
    # if the given dna matches no names, return "no match"
    return print("No match")


look_up_dna(dna_dict, name_list, sequence_list, unknown_dna)
