/***************************************************
| Bisection and :math:`\chi^2`
| Matheus J. Castro
| v1.0

| This program uses the bisection script to find position values of an array
  and calculates the :math:`\chi^2` of two arrays.
| The goal is not to run the program itself, but use it as a shared library inside python.
***************************************************/

#include<stdbool.h>
#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include<time.h>
#include<math.h>
//#include<omp.h>

/**
Function that applies the bisection method.

:param float* spec[]: the array to look for.
:param int len: the size of the array.
:param float lamb: the value to find the index.

:returns: the left index of the searched value.
*/
int bisec(float spec[], int len, float lamb){
    if(lamb < spec[0])
        return -1;
    else if(lamb > spec[len - 1])
        return -1;
    else{
        int gap[2] = {0, len - 1};
        int new_gap;

        while(true){
            new_gap = gap[0] + (gap[1] - gap[0]) / 2;

            if(lamb < spec[new_gap])
                gap[1] = new_gap;
            else
                gap[0] = new_gap;

            if(gap[0] + 1 == gap[1])
                return gap[0];
        }
    }
}

/**
Function to find the :math:`\chi^2` of two arrays.

:param float* spec1x[]: the first 1D-array (x axis).
:param float* spec1y[]: the first 1D-array (y axis).
:param int len1: the size of the first array.
:param float* spec2x[]: the second 1D-array (x axis).
:param float* spec2y[]: the second 1D-array (y axis).
:param int len2: the size of the second array.

:returns: the :math:`\chi^2`.
*/
float chi2(float spec1x[], float spec1y[], int len1, float spec2x[], float spec2y[], int len2){
    float sp1, sp2, chi = 0;
    int pos;

    for(int i=0; i < len2; i++){
        pos = bisec(spec1x, len1, spec2x[i]);
        if(pos != -1){
            sp1 = spec1y[pos] + (spec1y[pos+1] - spec1y[pos]) / (spec1x[pos+1] - spec1x[pos]) * (spec2x[i] - spec1x[pos]);
            sp2 = spec2y[i];

            chi = chi + pow(sp1 - sp2, 2) / sp2;
        }
    }
    
    return chi;
}

/**
Just a warning to not run the code itself.

:returns: int 0.
*/
int main(){
    // Main function, useless
    printf("This script is a shared library. You cannot run it as itself.\n");
	return 0;
}
