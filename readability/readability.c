#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

//program to input text and output the Coleman-Liau index (grade level) of the text

//initialize functions
int count_letters(string text);
int count_words(string text);
int count_sentences(string text);

int main(void)
{
    //get text from user, call it text
    string text = get_string("Text: ");
    //calculate the index
    float w = 100 / (float) count_words(text);
    float L = count_letters(text) * w;
    float S = count_sentences(text) * w;
    float liaw = round(0.0588 * L - 0.296 * S - 15.8);
    //convert to float to auto-round zeros away
    int grade = (int) liaw;
    //output the grade
    if (1 <= grade && grade <= 15)
    {
        printf("Grade %i\n", grade);
    }
    else if (grade < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade 16+\n");
    }
}

//count letters by asking each character if it is an alphanumeric character.
//other functions below are basically the same

int count_letters(string text)
{
    int letter_count = 0;
    int word_count = 1;
    for (int i = 0; i < strlen(text); i++)
    {
        if (isalpha(text[i]))
        {
            //printf("%c ", text[i]);
            letter_count++;
        }
    }
    return letter_count;
}

int count_words(string text)
{
    int word_count = 1;
    for (int i = 0; i < strlen(text); i++)
    {
        if (isspace(text[i]))
        {
            //printf("%c ", text[i]);
            word_count++;
        }
    }
    return word_count;
}

int count_sentences(string text)
{
    int sentence_count = 0;
    for (int i = 0; i < strlen(text); i++)
    {
        if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            //printf("%c ", text[i]);
            sentence_count++;
        }
    }
    return sentence_count;
}


