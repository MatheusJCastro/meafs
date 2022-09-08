# Multiple Element Abundance Fit Software - MEAFS
<hr/>
<hr/>

*Written by: Matheus J. Castro*  
*Under MIT License*  

<hr/>

## Aims

The MEAFS is a fitting tool software for spectra abundance analysis. The aims is to provide a medium to high analysis for each individual absorption line in a given spectrum.  
The software also fits the wavelength shift, continuum and convolution of the spectrum.

<hr/>

## Usage

The configuration is based on a single file, there is no need for installation of the software and the execution can be done in a terminal.

To download the MEAFS, go to a terminal and type (git package must be installed):

```bash
git clone https://github.com/MatheusJCastro/meafs.git
```

### Prerequisites

- Python3 need to be previously installed in the system;

- A software for creating a synthetic spectrum also need to be previously installed. This version of MEAFS is compatible with the following softwares:
    - Turbospectrum2019: [https://github.com/bertrandplez/Turbospectrum2019](https://github.com/bertrandplez/Turbospectrum2019)

- Optionally: to execute the `unify_plots.py`, a LaTeX installation must be present on the system.

### Compilation

There is one file written in C Language (`bisec_interpol.c`), the compilation directives can be found in the `comp.sh`. The C file needs to be compiled as a shared library, when using *GCC Compiler*, this can be achieved by adding the `-shared` flag.

For Linux users just add execution privileges at the `comp.sh` file and execute it in a terminal to create the binary. For that, open a terminal in the MEAFS folder and type:

```bash
chmod +x comp.sh
./comp.sh
```

### Execution

The three python files need to be adjusted for the execution of the MEAFS. The first line of each file is used to select the local of the Python3 environment, this may vary from each operating system or type of python installation. The first line of the python files using the default paths for python of each OS are:

| OS      | First line at python files                             |
|---------|--------------------------------------------------------|
| Linux   | #!/usr/bin/env python3                                 |
| macOS   | #!/usr/bin/env python3                                 |
| Windows | Erase the line and configure it to execute with python |

#### Python Files

For Linux users, add execution privileges for the files with:

```bash
chmod +x abundance_fit.py
chmod +x abundance_analysis.py
chmod +x unify_plots.py
```

The python files receive one execution parameter and it is to indicate the path to the configuration file (default name is `meafs_config.txt`, more about it later in this document). For Linux users, the execution can be achieved with:

- abundance_fit.py: `./abundance_fit.py path/to/meafs_config.txt`

- abundance_analysis.py: `./abundance_analysis.py path/to/meafs_config.txt`

- unify_plots.py: `./unify_plots.py path/to/meafs_config.txt`

<hr/>
## Analysis Process

### Configuration File

The `meafs_config.txt` file contains directives for the MEAFS execution process. All files indicated in this configuration file can be passed using relative or absolute paths.

Comments in this file are ignored and they start with `#`.

For the files that a *type* is required, there are two possible values: *tab* or *comma*. This indicates the type of column separation of the file.

The parameters are:

1. Linelist path to file;
2. Linelist type;
3. Boolean chooses (0 or 1) about the emission order presence in linelist file;
4. Abundance reference file path for elements;
5. Abundance reference file type;
6. Synthetic Spectrum Softeare to use;
7. Configuration file path for the synthetic spectrum software;
8. Synthetic Spectrum Software output file path;
9. Folder name path to save the results (if not present, the folder will be created);
10. Observed spectrum data file path (ASCII file with two columns);
11. Observed spectrum data file type.

An important observation: you can add as many spectrum data files as you want, just adding more lines at the end of the configuration file indicating the path to spectrum and the type of it. 

Example of a configuration file:

```txt
# Configuration File for MEAFS Code
# txt or csv files need specification of the type of separator at the next line
# Possible values are: tab, comma

# Linelist with the lines to analyze
Heavylist.txt
tab

# Does linelist have emission order after element?
1
# 0

# Elements Reference list
refer_values.csv
comma

# Synthetic Spectrum Software
Turbospectrum
# PFANT

# Configuration file for Synthetic Spectrum Software
Turbospectrum2019/COM-v19.1/CS31.com

# Synthetic Spectrum Output
Turbospectrum2019/COM-v19.1/syntspec/CS31-HFS-Vtest.spec

# Folder name to save results
Results

# Observed Spectra (one or more)
cs340n.dat
tab
cs437n.dat
tab
```

### Order of Execution

1. The first file to execute is the one responsible for the fitting, the file is the one named as `abundance_fit.py`. This file will create the directory where the results will be stored, a folder inside it named as `On_time_Plots` and a file named `found_values.csv`.

    The folder created contains plots for each line evaluated, showing some previous analysis. The file created is where all the results will be stored. The columns of the `found_values.csv` file are:

    1. Element name;
    2. Absorption line wavelength in Angstroms;
    3. Found Wavelength shift;
    4. Found Continuum;
    5. Found Convolution;
    6. Abundance of reference;
    7. Found Abundance;
    8. Difference between the reference and the found abundance;
    9. Chi Square of the abundance fit;
    10. Equivalent Width of the line curve fitted.

    If, for some reason, the `abundance_fit.py` file stops execution, the lines already analyzed aren't lost, since after each line the MEAFS saves the results in the `found_values.csv` file. Then, to return execution where it stopped, simply run the python again, MEAFS will automatically detect the results folder and it will remove from the execution the lines present in the `found_values.csv` file.

2. The second file, the `abundance_analysis.py` will generate some plots with the data inside the `found_values.csv` file. All files created will be stored in a folder called `Abundance_Analysis` inside the results folder defined in the configuration file.

    The script makes four types of analysis:

    1. Histograms for each element with found abundances;
    2. Histograms for each element with difference between the reference and the found abundance;
    3. Plot of each line containing the original spectrum and the synthetic one.
    4. Box plot summarizing the found abundances and their confidence levels.

3. The last python file, the `unify_plots.py`, simply create a new folder called `Unique_Plot` at the results folder and, using LaTeX, unify all plots created with `abundance_fit.py` and `abundance_analysis.py` in a five PDF file, each file for one type of analyses made.

<hr/>