#/bin/bash

#gcc -Wall -pedantic -O3 bisec_interpol.c -o bisec_interpol.o -lm
gcc -Wall -pedantic -O3 bisec_interpol.c -o bisec_interpol.so -shared
