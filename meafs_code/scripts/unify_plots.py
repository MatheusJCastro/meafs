#!/usr/bin/env python3
"""
| MEAFS Unify generated plots in a single PDF file for each type
| Matheus J. Castro

| This script aims to create a single result file for each analyze type created with the abundance_fit.py and
  abundance_analysis.py scripts.
| It uses pdflatex to generate it. You can install it following the steps for your OS distribution here:
  https://www.latex-project.org/get/

| For this code work, it must be in the same folder as the *abundance_fit.py* file
"""

import os
import sys

# Import the main script
try:
    import abundance_fit as ab_fit
except ModuleNotFoundError:
    from . import abundance_fit as ab_fit


def write(fl_name, data):
    """
    Write the data in a file.

    :param fl_name: file name.
    :param data: data to be written.
    """

    # Write the latex file
    with open(fl_name, 'w') as file:
        file.write(data)


def run_pdflatex(fl_name, folder):
    """
    Run the ``pdflatex`` command to generate the unified PDF.

    :param fl_name: file name.
    :param folder: directory where the file should be created.
    """

    # Run pdflatex command
    os.system("cd {}Unique_Plot && pdflatex -interaction=nonstopmode {}".format(folder, fl_name))


def main(args):
    """
    Main function that read the plot files.

    :param args: command line arguments.
    """

    # Arguments Menu Call
    config_name = ab_fit.args_menu(args)

    # Read Configuration File
    list_name, refer_name, type_synth, config_fl, conv_name, folder, observed_name = ab_fit.read_config(config_name)

    # Create necessary folder
    if not os.path.exists(folder+"Unique_Plot"):
        os.mkdir(folder+"Unique_Plot")

    dirs = ["On_time_Plots/", "Abundance_Analysis/Abundance_Hist/",
            "Abundance_Analysis/Difference_Hist/", "Abundance_Analysis/Lines_Plot/"]

    # Create latex structure
    pre = r"\documentclass[hidelinks,oneside]{abntex2}" + "\n" +\
          r"\usepackage{graphicx}" + "\n" +\
          r"\usepackage{caption}" + "\n" +\
          r"\usepackage{float}" + "\n" + "\n" +\
          r"\begin{document}" + "\n"

    pos = "\n" + r"\end{document}"

    # Create the plots for each analyze type
    for diru in dirs:
        fls = os.listdir(folder+diru)

        figs = ""
        for fl in fls:
            img_path = "../" + diru + fl
            
            pre_img = "\t" + r"\begin{figure}[H]" + "\n" + "\t" + "\t" + r"\center" + "\n"
            pos_img = "\t" + r"\end{figure}" + "\n" + "\n"
            
            img = "\t" + "\t" + r"\includegraphics[width=1\linewidth]{" + img_path + r"}" + "\n"
            cap = "\t" + "\t" + r"\caption*{" + fl.replace("_", r"\_") + r"}" + "\n"

            figs += pre_img + img + cap + pos_img

        final = pre + figs + pos

        fl_name = "{}.tex".format(diru.split("/")[1])
        if fl_name == ".tex":
            fl_name = "{}.tex".format(diru.split("/")[0])

        write(folder+"Unique_Plot/{}".format(fl_name), final)

        run_pdflatex(fl_name, folder)

        # Remove temporary files
        os.remove(folder+"Unique_Plot/{}".format(fl_name))
        os.remove(folder+"Unique_Plot/{}.aux".format(fl_name[:-4]))
        os.remove(folder+"Unique_Plot/{}.log".format(fl_name[:-4]))

        os.system("cp {}Abundance_Analysis/Abundance_box.pdf {}Unique_Plot/".format(folder, folder))


if __name__ == '__main__':
    arg = sys.argv[1:]
    main(arg)
