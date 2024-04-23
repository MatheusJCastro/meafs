#####################################################
# MEAFS Fit Functions                               #
# Matheus J. Castro                                 #
# v1.4                                              #
# Last Modification: 04/23/2024                     #
# Contact: matheusdejesuscastro@gmail.com           #
#####################################################

from astropy.convolution import Gaussian1DKernel, convolve
from pathlib import Path
import numpy as np
import ctypes
import os


def c_init(c_name):
    # Funtion to initialize the C shared library
    c_library = ctypes.CDLL("{}".format(c_name))

    # Defining functions argument types
    c_library.bisec.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_float]
    c_library.bisec.restype = ctypes.c_int

    c_library.chi2.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                               ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_int]
    c_library.chi2.restype = ctypes.c_float

    return c_library


def chi2(spec1, spec2):
    # Function to find the chi square of two arrays

    global c_lib

    # Using C library
    spec1x = spec1[0].tolist()
    spec1y = spec1[1].tolist()

    # noinspection PyCallingNonCallable,PyTypeChecker
    spec1x = (ctypes.c_float * len(spec1x))(*spec1x)
    # noinspection PyCallingNonCallable,PyTypeChecker
    spec1y = (ctypes.c_float * len(spec1y))(*spec1y)

    spec2x = spec2[0].tolist()
    spec2y = spec2[1].tolist()

    # noinspection PyCallingNonCallable,PyTypeChecker
    spec2x = (ctypes.c_float * len(spec2x))(*spec2x)
    # noinspection PyCallingNonCallable,PyTypeChecker
    spec2y = (ctypes.c_float * len(spec2y))(*spec2y)

    return c_lib.chi2(spec1x, spec1y, len(spec1x), spec2x, spec2y, len(spec2x))

    # Using Python (slower)
    # sp1_interpol = np.array([])
    # sp2_interpol = np.array([])
    #
    # for i in spec2.iloc():
    #     pos = bisec(spec1, i[0])
    #     if pos != -1:
    #         x1 = spec1.iloc[pos][0]
    #         x2 = spec1.iloc[pos + 1][0]
    #         y1 = spec1.iloc[pos][1]
    #         y2 = spec1.iloc[pos + 1][1]
    #         x = i[0]
    #         y = y1 + (y2 - y1) / (x2 - x1) * (x - x1)
    #
    #         sp1_interpol = np.append(sp1_interpol, y)
    #         sp2_interpol = np.append(sp2_interpol, i[1])
    #
    # return sum((sp1_interpol - sp2_interpol)**2 / sp2_interpol)


def bisec(spec, lamb):
    # Function to apply the bisection script to find a number position in an array

    # Uncomment the script bellow to use the C library (slower)
    # global c_lib
    # arr = spec[0].tolist()
    # arr_c = (ctypes.c_float * len(arr))(*arr)
    #
    # index = c_lib.bisec(arr_c, len(arr), lamb)
    #
    # return index

    # Bisection Script
    if lamb < spec.iloc[0][0]:
        return -1
    elif lamb > spec.iloc[-1][0]:
        return -1
    else:
        gap = [0, len(spec) - 1]

        while True:
            new_gap = gap[0] + (gap[1] - gap[0]) // 2

            if lamb < spec.iloc[new_gap][0]:
                gap[1] = new_gap
            else:
                gap[0] = new_gap

            if gap[0] + 1 == gap[1]:
                return gap[0]


def cut_spec(spc, lamb, cut_val=1.):
    # Function to restrict the array in the desired range
    val0 = bisec(spc, lamb - cut_val)
    val1 = bisec(spc, lamb + cut_val)+1

    return spc.iloc[val0:val1]


def spec_operations(spec, lamb_desloc=0., continuum=1., convol=0.):
    # Function to apply lambda shift, continuum fit and convolution to the spectrum
    spec[0] = spec[0] + lamb_desloc
    spec[1] = spec[1] * continuum

    if convol != 0:
        try:
            # Apply the convolution using the Gaussian1DKernel function
            g = Gaussian1DKernel(stddev=convol)
            spec[1] = convolve(spec[1], g)  # convolution between the spectrum and the function above
        except ValueError:
            pass

    return spec


def fit_continuum(spec, contpars=None, iterac=1000):
    if contpars is None:
        alpha = .5
        eps = 20
    else:
        alpha = contpars[0]
        eps = contpars[1]

    eps = np.float128(10)**(-np.float128(eps))

    new_spec = spec.iloc[:, 1].values.tolist()
    median = np.median(new_spec)
    std = np.std(new_spec)
    std_old = std
    count = 0

    while True:
        for i in reversed(range(len(new_spec))):
            value = new_spec[i]
            if value > median + alpha * std or value < median - alpha * std:
                del new_spec[i]

        median = np.median(new_spec)
        std = np.std(new_spec)

        count += 1
        if count >= iterac:
            print("Maximum Iterations for Continuum fit reached. iter_max = ", iterac)
            break
        elif (std_old - std) / std <= eps:
            break
        std_old = std

    median = np.median(new_spec)
    std = np.std(new_spec)

    return median, std



c_lib = c_init(Path(os.path.dirname(__file__)).joinpath("bisec_interpol.so"))  # initialize the C library