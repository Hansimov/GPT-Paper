"""
* Wheels for torch 2.0 · Issue #4901 · facebookresearch/detectron2
  * https://github.com/facebookresearch/detectron2/issues/4901#issuecomment-1502990928
"""
import distutils
import os
import subprocess
import sys
from pathlib import Path

detectron2_path = Path(__file__).parents[2] / "detectron2"
dist = distutils.core.run_setup(detectron2_path / "setup.py")

install_packages = dist.install_requires
# install_packages_str = " ".join([f"'{x}'" for x in dist.install_requires])
print(install_packages)

# "fvcore>=0.1.5,<0.1.6",  # required like this to make it pip installable
# "iopath>=0.1.7,<0.1.10",

for install_package in install_packages:
    print(f"Installing: {install_package}")
    subprocess.run(f"pip install {install_package}", shell=True)
    # subprocess.run(f"pip install {install_packages_str}", shell=True)


sys.path.insert(0, os.path.abspath(str(detectron2_path)))
