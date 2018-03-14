Installation
============

In order to use cmd_restarter in its current state you need:

* Python 3.4 or higher (Tested on python 3.6)
* LAMMPS (cmd_restarter do not execute LAMMPS directly, but your submission script will)
* A compatible Resource Manager such as Torque/PBS (Tested on Torque/Moab)

Using virtualenv
----------------

The safest way of installing cmd_restarter is using virtualenv. Virtualenv will create on a folder an isolated python environment, nothing outside that folder will change and if you want you can simply delete the folder and nothing will be left behind.

Creating a virtual environment is easy. Suppose that you want to create a virtual enviroment on a folder called "ve36", execute command::

   virtualenv ve36

To activate the environment execute::

   source ve36/bin/activate

After activation, you can install cmd_restarter with::

   pip install cmd_restarter

Using pip from your local python installation
---------------------------------------------

If you want to install directly on your $HOME folder execute::

   pip install cmd_restarter --user


Using the latest sources on Github
----------------------------------

Use the command::

   git clone https://github.com/WVUResearchComputing/cmd_restarter.git
 
Once the sources are downloaded, all that you have to do is setup the variable PYTHONPATH pointing to the place where you download the sources. cmd_restarter is a purely python code, so nothing need to be compiled::

   export PYTHONPATH=<PATH_TO>/cmd_restarter

 
