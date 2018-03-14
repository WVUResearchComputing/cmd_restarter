Quick Start
===========

To use cmd_restarter you need:

  * The input file for LAMMPS and any other file used by LAMMPS to perform the simulation, geometries for example

  * The submission script that you will use on the cluster where you will run the jobs.

On your input file you need to add some comments that will instruct cmd_restarter about which portions of the Input will change in case you are running from scratch or restarting a previous calculation.

The input file needs to be modified to include one block like this::

  # RST_BEGIN
  # read_data ...
  # read_restart ...
  # read_restart ...
  # RST_END

The lines inside the block will be commented or uncommented based on the existance or not of the restart files amd the restart file that will be activated is the newest file from the list of restart files.

There are a couple of more blocks to specify which parts of the input are activated only for the firts run or for restart runs The blocks are::

  # INITONLY_BEGIN
  ...
  ...
  # INITONLY_END

and::

  # RESTONLY_BEGIN
  ...
  ...
  # RESTONLY_END

cmd_restarter will comment or uncomment those blocks entirely so not real comments should be inside those blocks as cmd_restarter could uncomment them leaving a unproper LAMMPS input script.

Once those changes are done, cmd_restarter can be executed as::


  cmd_restart.py -p <SUBMISSION_SCRIPT> -i <LAMMPS_INPUT> -d <DUMP_FILENAME> -m <MAX_ITERATIONS> -s <SLEEPING_TIME>

 
Tutorial
========

Using cmd_restarter is really simple. You just need to add a few comments on your LAMMPS script file, prepare a basic submission script and the script will take the responsability of submit and resubmit jobs until the number of iterations is achieved. 

We will present now a simple example using 147 particles interacting under a Lennard-Jones potential.


Lennard-Jones with 147 particles
--------------------------------

For this exercise we will use cmd_restarter  to compute a simulation of 147 particles under a Lennard-Jones force field. 
This number of particles is still too low for modern computers, we have constrained the conditions to force multiple executions as it will be case with much bigger problems.

Conside the following LAMMPS input file (in.run)::

  # 147 LJ particles
  
  units           lj
  dimension       3
  boundary        s s s
  atom_style      atomic
  
  region sbound sphere 0.00 0.00 0.00 25.000 units box side in
  
  # RST_BEGIN
  read_data LJ147.geo
  # read_restart run_a.rest
  # read_restart run_b.rest
  # RST_END
  
  include         LJ147.parm
  timestep        0.005
  run_style       verlet
  velocity        all create 0.007 1298371 mom yes rot yes dist gaussian
  
  fix             1 all nvt temp 0.007 0.007 100.0
  
  dump            2 all dcd 100 rlx_0.5_LJ147.dcd
  dump_modify  2 unwrap yes
  
  thermo_style    multi
  thermo          1000
  variable sys_step equal step
  
  fix 5 all wall/region sbound harmonic 1 1 25
  compute 1 all gyration
  
  fix Rgave all ave/time 100 5 1000 c_1 file Rg_rlx0.5_LJ147.dat
  fix extra all print 1000 "${sys_step}" screen no append steps.dat
  dump geometry all atom 1000 dump.atom
  dump d0 all image 1000 dump.*.jpg type type
  dump_modify d0 pad 8
  
  restart         1000   run_a.rest run_b.rest
  run             10000000
  
  write_restart         rlx_0.5_LJ147.rest

This is a normal LAMMPS script file, the only special element is a block of commands enclosed in some comments::


  # RST_BEGIN
  read_data LJ147.geo
  # read_restart run_a.rest
  # read_restart run_b.rest
  # RST_END

The actual state of the lines inside the block is irrelevant. You can perfectly keep all the lines ``read_...`` commented or uncommented. cmd_restarter will modify this input according to the presence or not of those restart files. If you start from scratch the files ``run_a.rest`` and ``run_b.rest`` do not exit, so the line with ``read_data`` is activated and the other lines are commented. After the first execution some or both of those restart files will be present, cmd_restarter will determine which one is newer and use it to prepare the input for restart and submit a new job to continue the simulation.


There is nothing special about the submission script, the LAMMPS input script ``in.run`` is always changed in-place, but keeping a backup copy on files eding on `...BKPXXX`. A very simple submission script will look like this (runjob.pbs)::

  #!/bin/bash
  
  #PBS -l nodes=1:ppn=2,walltime=00:5:00
  #PBS -m aeb
  #PBS -q debug
  #PBS -j oe
  
  module purge
  module load atomistic/lammps/2017.08.11
  
  cd $PBS_O_WORKDIR
  mpirun -np 2 -machinefile $PBS_NODEFILE lmp_mpi -in in.run


On this submission script we are just requesting 2 cores on the `debug` queue for 5 minutes. We are assuming that the only module needed to run LAMMPS is ``atomistic/lammps/2017.08.11``
cmd_restater can be executed using this command line::

  cmd_restart.py -p runjob.pbs -i in.run -d steps.dat -m 10000000 -s 30

The file ``steps.dat`` does not exist at the very begining, cmd_restarter just need a file that can be used to check how many iterations have been achieved in order to decide when the simulation is cosidered complete.
 
