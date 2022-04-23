/***************************************************/
/* Bisection and Chi Square                       */
/* Matheus J. Castro                               */
/* v1.0                                            */
/* Last Modification: 02/17/2022                   */
/* Contact: matheusdejesuscastro@gmail.com         */
/***************************************************/

// This program uses the bisection script to find position values of an array
// and calculates the chi square of two arrays
// The intention is not to run the program itself, but use it as a shared library inside python

#include<stdbool.h>
#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include<time.h>
#include<math.h>
#include<omp.h>

int bisec(float spec[], int len, float lamb){
    // Function to use the bisection script
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

float chi2(float spec1x[], float spec1y[], int len1, float spec2x[], float spec2y[], int len2){
    // Function to find the chi square of two arrays
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


int main(){
    // Main function, useless
    printf("This script is a shared library. You cannot run it as itself.\n");
	return 0;
}
