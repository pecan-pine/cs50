// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
//enough to hash zzzzzzzzzzzzzz (45 times)
//really big hash table
const unsigned int N = LENGTH * ('z') * 10 + LENGTH;
//size of dictionary
unsigned int s = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    unsigned int index = hash(word);
    if (table[index] == NULL)
    {
        //printf("index not in table: ");
        return false;
    }
    else
    {
        for (node *k = table[index]; k != NULL; k = k->next)
        {
            if (strcasecmp(word, k->word) == 0)
            {
                //printf("match found! %s / %s\n", word, k->word);
                return true;
            }
            //printf("word: %s. dictionary word: %s. Result: %i\n", word, k->word, strcasecmp(word,k->word));
        }
        return false;
    }
    //printf("'%s'", table[index]->word);
    return false;
}

// Hashes word to a number
// by adding up all letters
//each letter mod 97 (so a = 0)
unsigned int hash(const char *word)
{
    //index is the ouput
    unsigned int index = 0;
    //loop through letters of word
    for (int i = 0; word[i] != '\0'; i++)
    {
        //multiply first letter by 1, second letter by 2, third letter by 3, etc
        //up to 9th letter gets multiplied by 9
        index += ((i % 10) + 1) * tolower(word[i]);
    }
    //the hash is the sum of all letters plus the length of the word
    return index + strlen(word);
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    //open dictionary file to read
    FILE *file = fopen(dictionary, "r");
    //exit if opening the file went wrong
    if (file == NULL)
    {
        return false;
    }
    //make a word of length at most LENGTH + 1 (+1 for the end character \0)
    char word[LENGTH + 1];
    //scan file for words until end of file is reached
    //each word is temporarily stored as the char* "word"
    for (int w = fscanf(file, "%s", word); w != EOF; w = fscanf(file, "%s", word))
    {
        //create a new node (pointer to a node) to store the word in
        node *n = malloc(sizeof(node));
        //copy word into (*n).word i.e. the word associated with the node
        strcpy(n->word, word);
        //index is the index of table[] that the node will go into
        //mod N to make sure index is within bounds
        int index = hash(word) % N;
        //make the the new node point to the same node table[index] points to
        n->next = table[index];
        //make table[index] now point to n.
        table[index] = n;
        //printf("loaded %s \n", word);
        //increment s since one word was added to dictionary
        s++;
    }
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return s;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    //temporary pointer to node
    node *tmp = NULL;
    //loop through table values
    for (int i = 0; i < N; i++)
    {
        //set variable k to point to where table[i] points to
        node *k = table[i];
        //repeat until k is at end of linked list
        while (k != NULL)
        {
            //make tmp point where k is pointing
            tmp = k;
            //make k point at next node in the linked list
            k = k->next;
            //free the previous node
            free(tmp);
        }
    }
    return true;
}
