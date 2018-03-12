Introduction
============

cmd_restarter is a small program that provide the allows continuos executions of large Classical Molecular Dynamics (CMD) simulations using the internal restart capabilities of the CMD program.

In its current version, a proof of concept has been created limited to work only with LAMMPS as CMD code and Torque/PBS as resource manager. The code is extensible in principle to other CMD codes and Resource Managers.

cmd_restarter manages the submission and resubmission of jobs on a cluster doing the necessary changes on the Input file and monitoring the job and resubmit new jobs as many times as needed until a certain number of iterations is achieved.

Consider this problem: You need to run a CMD simulation on LAMMPS that takes weeks, but all that you have on your cluster is a queue that allow you to run for 1 day. Without cmd_restarter the best that you can do is submit the job and wait until it finishes. Once the job is not loger in execution, do appropiated changes on the input file for a restart and resubmit the job again and again until you reach the number of iterations that you need. 

Using a few comments on your input file and declaring the number of iterations needed, cmd_restarter will take control of the submission and resubmission from you. The code is intended to run on the head node of a cluster, with minimal CPU usage. The quickstart section will offer you a simple usage case.
