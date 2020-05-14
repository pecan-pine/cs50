#include "helpers.h"
#include <stdio.h>
#include <math.h>
// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    BYTE *red;
    BYTE *green;
    BYTE *blue;
    int average;
    //printf("rgbtriple is %i, %i, %i\n", image[height-1][width-1].rgbtRed, image[height-1][width-1].rgbtGreen, image[height-1][width-1].rgbtBlue);
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            red = &image[i][j].rgbtRed;
            green = &image[i][j].rgbtGreen;
            blue = &image[i][j].rgbtBlue;
            average = (int) round((*red + *green + *blue) / (float) 3);
            *red = average;
            *green = average;
            *blue = average;

        }
    }
    //printf("original rgbtriple is %i, %i, %i\n", image[height-1][width-1].rgbtRed, image[height-1][width-1].rgbtGreen, image[height-1][width-1].rgbtBlue);
    //printf("new rgbtriple is %i, %i, %i\n", *red, *green, *blue);
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    //middle will be index of middle (widthwise pixel)
    int middle;
    //temporary variable to store pixel for the swap
    //pointer type
    RGBTRIPLE tmp;
    //printf("image width is even? %i, width is %i\n", (width % 2 == 0), width);
    //if width is odd, middle is the index of the middle pixel
    if (width % 2 != 0)
    {
        middle = (width - 1) / 2;
    }
    //if width is even, middle is the index of the pixel one past the exact middle
    else
    {
        middle = width / 2;
    }
    //loop over all columns, only half the row (to swap it)
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < middle; j++)
        {
            //swap image[i][j] to image[i][width - 1 - j]
            tmp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = tmp;
        }
    }

    return;
}

// Blur image
/*
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE new_image[height][width];
    int red_sum;
    int green_sum;
    int blue_sum;
    int count;
    int upper_k;
    int lower_k;
    int upper_l;
    int lower_l;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //printf("(%i, %i, %i)", image[i][j].rgbtRed, image[i][j].rgbtGreen, image[i][j].rgbtBlue);
            //set values for upper_ and lower_ k and l
            lower_k = (int) fmax(i - 1, 0);
            upper_k = (int) fmin(i + 2, height - 1);
            lower_l = (int) fmax(j - 1, 0);
            upper_l = (int) fmin(j + 2, width - 1);
            //code for interior pixels
            red_sum = 0;
            green_sum = 0;
            blue_sum = 0;
            count = 0;
            //for (int k = i - 1; k <= i + 1; k++)
            for(int k = lower_k; k < upper_k; k++)
            {
                //for (int l = j - 1; l <= j + 1; l++)
                for(int l = lower_l; l < upper_l; l++)
                {
                    count++;
                    red_sum += image[k][l].rgbtRed;
                    green_sum += image[k][l].rgbtGreen;
                    blue_sum += image[k][l].rgbtBlue;
                }
            }
            new_image[i][j].rgbtRed = (int) round(red_sum / (float) count);
            new_image[i][j].rgbtGreen = (int) round(green_sum / (float) count);
            new_image[i][j].rgbtBlue = (int) round(blue_sum / (float) count);
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = new_image[i][j].rgbtRed;
            image[i][j].rgbtGreen = new_image[i][j].rgbtGreen;
            image[i][j].rgbtBlue = new_image[i][j].rgbtBlue;
        }
    }
    //printf("count is %i\n", count);
    return;
} */

// Blur image (new version)
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE new_image[height][width];
    int red_sum;
    int green_sum;
    int blue_sum;
    int count;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //printf("(%i, %i, %i)", image[i][j].rgbtRed, image[i][j].rgbtGreen, image[i][j].rgbtBlue);
            //code for interior pixels
            red_sum = 0;
            green_sum = 0;
            blue_sum = 0;
            count = 0;
            for (int k = i - 1; k <= i + 1; k++)
            {
                for (int l = j - 1; l <= j + 1; l++)
                {
                    if (k < 0 || k > height - 1 || l < 0 || l > width - 1)
                    {
                        continue;
                    }
                    count++;
                    red_sum += image[k][l].rgbtRed;
                    green_sum += image[k][l].rgbtGreen;
                    blue_sum += image[k][l].rgbtBlue;
                }
            }
            new_image[i][j].rgbtRed = (int) round(red_sum / (float) count);
            new_image[i][j].rgbtGreen = (int) round(green_sum / (float) count);
            new_image[i][j].rgbtBlue = (int) round(blue_sum / (float) count);
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = new_image[i][j].rgbtRed;
            image[i][j].rgbtGreen = new_image[i][j].rgbtGreen;
            image[i][j].rgbtBlue = new_image[i][j].rgbtBlue;
        }
    }
    //printf("count is %i\n", count);
    return;
}


// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE new_image[height][width];
    int Gx[3][3] = {{-1, 0, 1 }, {-2, 0, 2 }, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    int Gx_red;
    int Gx_green;
    int Gx_blue;
    int Gy_red;
    int Gy_green;
    int Gy_blue;
    int G_red;
    int G_green;
    int G_blue;
    //printf("red is %i\n", image[height - 1][width - 1].rgbtRed);
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            Gx_red = 0;
            Gx_green = 0;
            Gx_blue = 0;
            Gy_red = 0;
            Gy_green = 0;
            Gy_blue = 0;
            G_red = 0;
            G_green = 0;
            G_blue = 0;
            for (int k = 0; k < 3; k++)
            {
                for (int l = 0; l < 3; l++)
                {
                    if (i - 1 + k < 0 || i - 1 + k > height - 1 || j - 1 + l < 0 || j - 1 + l > width - 1)
                    {
                        continue;
                    }
                    Gx_red += Gx[k][l] * image[i - 1 + k][j - 1 + l].rgbtRed;
                    Gx_green += Gx[k][l] * image[i - 1 + k][j - 1 + l].rgbtGreen;
                    Gx_blue += Gx[k][l] * image[i - 1 + k][j - 1 + l].rgbtBlue;
                    Gy_red += Gy[k][l] * image[i - 1 + k][j - 1 + l].rgbtRed;
                    Gy_green += Gy[k][l] * image[i - 1 + k][j - 1 + l].rgbtGreen;
                    Gy_blue += Gy[k][l] * image[i - 1 + k][j - 1 + l].rgbtBlue;
                }
            }
            //printf("Gx = %i, Gy = %i, final is %i\n", Gx_red, Gy_red, (int) round(sqrt(Gx_red * Gx_red + Gy_red * Gy_red)));
            G_red = round(sqrt(Gx_red * Gx_red + Gy_red * Gy_red));
            new_image[i][j].rgbtRed = (int) fmin(G_red, 255);
            G_green = round(sqrt(Gx_green * Gx_green + Gy_green * Gy_green));
            new_image[i][j].rgbtGreen = (int) fmin(G_green, 255);
            G_blue = round(sqrt(Gx_blue * Gx_blue + Gy_blue * Gy_blue));
            new_image[i][j].rgbtBlue = (int) fmin(G_blue, 255);
            /*image[i][j].rgbtRed = 0;
            image[i][j].rgbtBlue = 0;
            image[i][j].rgbtGreen = 0;
            */
            //printf("red is %i, green is %i, blue is %i\n", image[i][j].rgbtRed, image[i][j].rgbtGreen, image[i][j].rgbtBlue);
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = new_image[i][j].rgbtRed;
            image[i][j].rgbtGreen = new_image[i][j].rgbtGreen;
            image[i][j].rgbtBlue = new_image[i][j].rgbtBlue;
        }
    }
    //printf("new red is %i\n", image[height - 1][width - 1].rgbtRed);
    return;
}
