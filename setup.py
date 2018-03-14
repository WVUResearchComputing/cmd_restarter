from setuptools import setup, find_packages

###################################################################

NAME = "cmd_restarter"
PACKAGES = find_packages()
KEYWORDS = ["classical molecular dynamics"]
CLASSIFIERS = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Chemistry",
]
INSTALL_REQUIRES = ['numpy >= 1.12.0']

###################################################################

setup(
    name=NAME,
    version='0.18.3.14',
    author='Guillermo Avendano-Franco',
    author_email='gufranco@mail.wvu.edu',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/WVUResearchComputing/cmd_restarter',
    scripts=['scripts/cmd_restart.py'],
    license='LICENSE',
    description='Utility for automatic restarts of CMD (LAMMPS) calculations on a HPC cluster using a queue system '
                '(Torque/PBS)',
    long_description=open('README.md').read(),
    install_requires=INSTALL_REQUIRES,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
)
