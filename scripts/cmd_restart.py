#!/usr/bin/env python3

import os
import argparse
import logging  
import time
import shutil
from cmd_restarter import cmd, queue


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CMD restarter')
    parser.add_argument('-p', '--pbs', metavar='<PATH>', type=str, required=True,
                        help='Filename used to submit jobs')
    parser.add_argument('-i', '--input', metavar='<PATH>', type=str, required=True,
                        help='Filename of the Input file')
    parser.add_argument('-d', '--dump', metavar='<PATH>', type=str, required=True,
                        help='Path to dump file used to count the number of steps completed')
    parser.add_argument('-m', '--max', metavar='<PATH>', type=int, required=True,
                        help='Maximum number of iterations, when the dump file reach that number, no more jobs will be submitted')

    args = parser.parse_args()
    print(args)

    username = os.getenv('USER')
    jobname = queue.get_jobname(args.pbs)

    print("CMD_RESTARTER")
    print("-------------")
    print('')
    print('Username: %s' % username)
    print('Job Name: %s' % jobname)
    print()

    log=logging.getLogger()
    log.setLevel(logging.DEBUG)

    new_submit = True
    jobid = 'no-job'

    while True:

        # Check the jobs currently on the system
        jobs = queue.get_jobs(username)        
        jobids = list(jobs.keys())
        jobidnumber = jobid.split('.')[0]

        if jobid not in jobids or os.path.isfile(jobname+'.o'+jobidnumber):
            print('Job %s (%s) not longer in queue, checking if restart is needed' % (jobname, jobid))
            if not os.path.isfile(args.dump):
                cur_iteration = 0
            else:
                cur_iteration = cmd.get_output(args.dump)

            print('Current Iteration: %d' % cur_iteration)
            print('Target number    : %d' % args.max)

            if cur_iteration < args.max:
                new_submit = True
            else:
                print('Number of iterations completed')
                break
        else:
            print('Job %s (%s) currently in queue, sleeping for 60 seconds' % (jobname, jobid))
            time.sleep(60)
            new_submit = False

        # This happens only when a new job needs to be prepared
        if new_submit:
            data, rstblock, to_uncomment = cmd.get_input(args.input)

            print('\nLines inside the RST_BEGIN -> RST_END block:')
            for i in rstblock:
                print(i)

            print('Uncommenting line:')
            print(rstblock[to_uncomment])

            index = 1 
            while True:
                bkpfile = args.input+'_BKP%03d' % index
                if not os.path.isfile(bkpfile):
                    print('Creating a backup copy at: %s' % bkpfile)
                    shutil.copy2(args.input, bkpfile)
                    break
                index+=1

            cmd.set_input(args.input, data, rstblock, to_uncomment)

            jobid = queue.submit(args.pbs)
            print('JobID created: %s' % jobid)
            new_submit = False
            time.sleep(60)
