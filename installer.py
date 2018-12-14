#This file assumes that python3.X has already been
#installed on the system

import importlib.util
import subprocess
import sys


def install(package):
     subprocess.call([sys.executable, "-m", "pip", "install", package])

package_names = ["numpy", "pygame", "curses", "pip"]

for package_name in package_names:

    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(package_name +" is not installed")
        install(package_name)
        print(package_name + "has now been installed")
    else:
        print(package_name + " is installed")