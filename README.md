# cmd_restarter

Utility for automatic restarts of CMD (LAMMPS) calculations on a HPC cluster using a queue system (Torque/PBS)

Features:

  * Identify jobs in current execution
  * Read the output and verify if the job needs to be restarted
  * Introduce modifications on the input in preparation to a new execution
  * Submit and resubmit jobs as many times as needed to complete a long run simulation.
  
Limitations:

  * This code is indented to work only with Python 3
  * CMD codes supported: LAMMPS
  * Queue systems supported: Torque/PBS
  
