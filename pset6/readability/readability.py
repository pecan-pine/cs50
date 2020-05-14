'''Program to compute the 'grade level' of a text
based on it's "coleman liaw" index'''

import re
# ask for input text
text = input("Text: ")
# program counts a word as a space
words = re.findall(' ', text)
# the last word (or first word?) gets no space after it, so add 1
W = len(words) + 1
# a sentence is either . or ? or ! (i.e. a sentence ends with those characters)
sentences = re.findall('\.|\?|!', text)
S = 100 * len(sentences) / W
# a letter is a-z or A-Z
letters = re.findall('[a-zA-Z]', text)
L = 100 * len(letters) / W
# compute index
liaw = int(round(0.0588 * L - 0.296 * S - 15.8))

# depending on index, assign grade levels
if 1 <= liaw and liaw < 16:
    print("Grade", liaw)
elif liaw < 1:
    print("Before Grade 1")
else:
    print("Grade 16+")
