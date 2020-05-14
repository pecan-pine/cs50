#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>
/*program to take input (on the command line level) of a number "shift"
program then takes input a string, and shifts the letters of 
the string over by "shift" number of letters and prints out the new
cipher string */

//main function with inputs from the command line (argc is number of arguments, argv is the array containing them)
int main(int argc, string argv[])
{
    //if there is just one argument (which should be a number)
    if (argc == 2)
    {
        for (int i = 0, n = strlen(argv[1]); i < n; i++)
        {
            if (! isdigit(argv[1][i]))
            {
                printf("Usage: ./caesar key\n");
                return 1;
            }
        }
    }
    //if there are more than one argument exit the program
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    //shift converts the command line number argument to an actual int
    int shift = atoi(argv[1]);
    //ask for a string
    string plaintext = get_string("plaintext: ");
    //preparing for the output
    printf("ciphertext: ");
    //loop through all the letters in "plaintext"
    for (int i = 0, n = strlen(plaintext); i < n; i++)
    {
        //if you find a letter
        if (isalpha(plaintext[i]))
        {
            //default case I consider is lowercase letters
            int is_upper = 0;
            //if the letter is upper case, add 32 to convert to lower case
            //use is_upper to remember it was upper case
            if (isupper(plaintext[i]))
            {
                is_upper = 1;
                plaintext[i] += 32;
            }
            //convert char to int (not sure if this is necessary)
            int c = plaintext[i];
            //variable O for offset, i.e. a = 97
            int O  = 97;
            //variable L for length, i.e. 26 letters
            int L = 26;
            //variable S for shift amount
            int S = shift;
            //first shift back by the offset, then add shift mod 26. Now add the offset back.
            int result = (c - O + S) % L + O;
            //if the char was upper case, convert back to upper case
            if (is_upper == 1)
            {
                result += -32;
            }
            //print the ciphered character
            printf("%c", result);
        }
        //if the character is not a letter, just print it
        else
        {
            printf("%c", plaintext[i]);
        }
    }
    printf("\n");
    //if everything went well, return 0
    return 0;
}