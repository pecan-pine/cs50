#include <stdio.h>
int *list_giver(int numbers[]);

int main(void)
{
    int x = 3;
    int y = 4;
    int *z = &x;
    printf("x is %i, y is %i\n", x, y);
    printf("address of x is %p, address of y is %p\n", &x, &y);
    printf("z is %p, inside z is %i\n", z, *z);
    printf("setting *z to 0...\n");
    *z = 0;
    printf("x is %i, *z is %i\n", x, *z);
    int w[1] = {3};
    printf("list giver outputs %i", list_giver(&x)[1]);
}

int *list_giver(int *n)
{
    printf("It worked!\n");
    printf("n is %i\n", *n);
    int t[3] = {*n-1, *n, *n+1};
    int *ell = t;
    return ell;
}