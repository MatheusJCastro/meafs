############################################################
# Unify generated plots in a single PDF file for each type #
# Matheus J. Castro                                        #
# v1.1                                                     #
# Last Modification: 03/19/2022                            #
# Contact: matheusdejesuscastro@gmail.com                  #
############################################################

# This script aims to create a single result file for each analyze type created with the abundance_fit.py and
# abundance_analysis.py scripts.
# It uses pdflatex to generate it. You can install it following the steps for your OS distribution here:
# https://www.latex-project.org/get/

import os
import sys


def write(fl_name, data):
    # Write the latex file
    with open(fl_name, 'w') as file:
        file.write(data)


def run_pdflatex(fl_name):
    # Run pdflatex command
    os.system("cd Unique_Plot && pdflatex -interaction=nonstopmode {}".format(fl_name))


def main():
    # Create necessary folder
    if not os.path.exists("Unique_Plot"):
        os.mkdir("Unique_Plot")

    dirs = ["Plots/", "Abundance_Analysis/Abundance_Hist/", 
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
        fls = os.listdir(diru)

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

        write("Unique_Plot/{}".format(fl_name), final)

        run_pdflatex(fl_name)

        # Remove temporary files
        os.remove("Unique_Plot/{}".format(fl_name))
        os.remove("Unique_Plot/{}.aux".format(fl_name[:-4]))
        os.remove("Unique_Plot/{}.log".format(fl_name[:-4]))


if __name__ == '__main__':
    main()
