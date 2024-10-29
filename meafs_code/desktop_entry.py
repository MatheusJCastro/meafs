"""
| MEAFS Desktop Entry Creation
| Matheus J. Castro

| This file analyse and create aliases in the system to run MEAFS through an entry in the system menu.
"""

import desktop_file as df
from pathlib import Path
import sys
import os


def get_curr_dir():

    """
    Get the current environment running python (like anaconda or system)
    and the directory where the file is located.

    :return: the command that activates anaconda environment (if present) and the file absolute path.
    """


    def anaconda_error():
        sys.exit("Error: anaconda environment detected but path not found.")

    pre = sys.prefix
    if "anaconda" in pre:
        print("Anaconda detected.")

        pre = Path(pre).parts

        ind_anaconda = -1
        for i in range(len(pre)):
            if "anaconda" in pre[i]:
                ind_anaconda = i
                break

        if ind_anaconda == -1:
            anaconda_error()

        env_name, anaconda_path = "", ""
        try:
            env_name = pre[ind_anaconda + 2]
            anaconda_path = pre[:ind_anaconda + 1]
        except IndexError:
            anaconda_error()

        anaconda_path = Path(*anaconda_path).joinpath("bin", "conda")

        conda_activate = "{} run --no-capture-output --name {} ".format(anaconda_path, env_name)
    else:
        conda_activate = ""

    path = Path(__file__).parts[:-1]
    path = Path(path[0]).joinpath(*path[1:])

    return conda_activate, str(path)


def create():
    """Create the menu entry in the system to run MEAFS."""

    def module_create(path):
        print("Creating shortcut at: ", path)
        shortcut = df.Shortcut(path, "MEAFS", "{}python{} -m meafs_code".format(conda, vers))
        shortcut.setTitle("MEAFS")
        shortcut.setWorkingDirectory(dir)
        shortcut.setComment("Multiple Element Abundance Fit Software")
        shortcut.setIcon(icon_path)
        shortcut.setCategories("Science;X-Astrophysics;X-Astronomy;X-Education;")
        shortcut.save()

    conda, dir = get_curr_dir()
    icon_path = None

    # Get the actual Python version
    vers = str(sys.version_info.major) + "." + str(sys.version_info.minor)

    if "linux" in sys.platform:
        icon_path = str(Path(dir).joinpath("images", "Meafs_Icon.png"))
        module_create(df.getMenuPath())
    elif "win" in sys.platform and "darwin" not in sys.platform:
        import win32com.client

        icon_path = str(Path(dir).joinpath("images", "Meafs_Icon.ico"))

        fls = os.listdir(dir)
        for fl in fls:
            if "MEAFS" in fl and ".bat" in fl:
                os.remove(str(Path(dir).joinpath(fl)))

        module_create(dir)
        os.remove(str(Path(dir).joinpath("MEAFS.lnk")))

        file = open(str(Path(dir).joinpath("MEAFS.vbs")), "w")
        execFile = "Set WshShell = CreateObject(\"WScript.Shell\")\n" \
                   "WshShell.Run chr(34) & \"{}\" & Chr(34), 0\n" \
                   "Set WshShell = Nothing".format(str(Path(dir).joinpath("MEAFS.bat")))
        file.write(execFile)
        file.close()

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(Path(dir).joinpath("MEAFS.lnk")))
        shortcut.TargetPath = str(Path(dir).joinpath("MEAFS.vbs"))
        shortcut.IconLocation = icon_path
        shortcut.Save()

        src = str(Path(dir).joinpath("MEAFS.lnk"))
        print("Creating shortcut at: ", df.getDesktopPath())
        os.system("copy {} \"{}\"".format(src, df.getDesktopPath()))
        print("Creating shortcut at: ", df.getMenuPath())
        os.system("copy {} \"{}\"".format(src, df.getMenuPath()))

    print("No errors reported. Logout and login again for changes to take effect.")


def remove():
    """Remove the menu entry in the system that run MEAFS."""

    def erasing(path_fl, fl):
        path_fl = str(Path(path_fl).joinpath(fl))
        print("Removing file: ", path_fl)

        try:
            os.remove(path_fl)
            print("Done.")
        except FileNotFoundError:
            print("File {} not found.".format(path_fl))

    if "linux" in sys.platform:
        erasing(df.getMenuPath(), "MEAFS.desktop")
    elif "win" in sys.platform:
        path_to_fl = Path(__file__).parts[:-1]
        path_to_fl = Path(path_to_fl[0]).joinpath(*path_to_fl[1:])

        erasing(df.getDesktopPath(), "MEAFS.lnk")
        erasing(df.getMenuPath(), "MEAFS.lnk")
        erasing(path_to_fl, "MEAFS.vbs")
        erasing(path_to_fl, "MEAFS.lnk")
        erasing(path_to_fl, "MEAFS.bat")
