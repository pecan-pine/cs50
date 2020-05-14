#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    //check that the user typed in exactly one argument
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }
    //open the file, which should be the argument given when running this program
    FILE *file = fopen(argv[1], "r");
    //if something went wrong opening the file, end the program
    if (file == NULL)
    {
        printf("file '%s' not found\n", argv[1]);
        return 1;
    }
    //number of chunks
    int num_chunks = 512;
    //count of images
    int image_counter = 0;
    //filename for the image outputs
    char filename[10];
    //after the first jpeg is found, writing_jpeg gets set to 1
    //for a better program, writing jpeg could be more sophisticated
    int writing_jpeg = 0;
    //bytes_read per round
    //bytes_read should be 512 until you run out of bytes in the file
    long bytes_read = 512;
    //define img as pointer to a file. Set to NULL for now
    FILE *img;
    img = NULL;
    //make a buffer for the picture data
    unsigned char bytes[num_chunks];
    ////printf("printing bytes...\n");

    //repeat until end of file
    while (bytes_read == 512)
    {
        //read off 512 bytes from the file
        bytes_read = fread(bytes, sizeof(BYTE), num_chunks, file);
        ////printf("%lu bytes read\n", bytes_read);
        ////printf("%i: %lu bytes read\n", i, fread(bytes, sizeof(BYTE), num_chunks, file));
        ////printf("%i: byte is %i\n", i, bytes[0]);
        //check the first 4 bytes match that of a jpeg
        if (bytes[0] == 0xff && bytes[1] == 0xd8 && bytes[2] == 0xff && (bytes[3] & 0xf0) == 0xe0)
        {
            //if you've started writing jpegs already, close the previous one
            if (writing_jpeg == 1)
            {
                fclose(img);
            }
            //make a new filename like 005.jpg
            sprintf(filename, "%03i.jpg", image_counter);
            //open the file as 'img'
            img = fopen(filename, "w");
            // syntax reminder: fwrite(data, size, number, outptr)
            //write the buffer to the file
            fwrite(bytes, sizeof(BYTE), num_chunks, img);
            ////printf("jpeg %i found\n", image_counter);
            //count as 1 more jpeg
            image_counter++;
            //have found at least 1 jpeg now
            writing_jpeg = 1;
        }
        //if you already found a jpeg and there are more bytes to write, write bytes to the file img
        else if (writing_jpeg == 1 && bytes_read > 0)
        {
            fwrite(bytes, sizeof(BYTE), num_chunks, img);
        }
        //if this is the last loop, close the img file
        else if (bytes_read != 512)
        {
            fclose(img);
            fclose(file);
        }
    }
    //printf("\n");
}
