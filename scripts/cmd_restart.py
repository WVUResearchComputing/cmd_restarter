#!/usr/bin/env python3

import os
import argparse
import logging  
import datetime
import time
import shutil
from cmd_restarter import cmd, queue

def create_backup(filename):
    index = 1 
    while True:
        bkpfile = filename+'_BKP%03d' % index
        if not os.path.isfile(bkpfile):
            print('Creating a backup copy %s' % bkpfile)
            shutil.copy2(filename, bkpfile)
            break
        index += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CMD restarter')
    parser.add_argument('-p', '--pbs', metavar='<PATH>', type=str, required=True,
                        help='Filename used to submit jobs')
    parser.add_argument('-i', '--input', metavar='<PATH>', type=str, required=True,
                        help='Filename of the Input file')
    parser.add_argument('-d', '--dump', metavar='<PATH>', type=str, required=True,
                        help='Path to dump file used to count the number of steps completed')
    parser.add_argument('-m', '--max', metavar='<N>', type=int, required=True,
                        help='Maximum number of iterations, when the dump file reach that number, no more jobs will '
                             'be submitted')
    parser.add_argument('-s', '--sleep', metavar='<sec>', type=int, default=600,
                        help='Number of seconds to wait before checking if job has been completed (default: 600)')

    args = parser.parse_args()
    username = os.getenv('USER')

    print("CMD_RESTARTER")
    print("-------------")
    print('')
    print('Username      : %s' % username)
    print('LAMMPS Input  : %s' % args.input)
    print('Dumb file     : %s' % args.dump)
    print('PBS Script    : %s' % args.pbs)
    print('Max Iterations: %d' % args.max)
    print('Sleep Time    : %d' % args.sleep)
    print('')

    
    if not os.path.isfile(args.input):
        print("Input File not found: %s" % args.input)

    if not os.path.isfile(args.pbs):
        print("Submission Script not found: %s" % args.pbs)

    log = logging.getLogger()
    log.setLevel(logging.INFO)

    new_submit = True
    jobid = ''

    while True:

        # Check the jobs currently on the system
        jobs = queue.get_jobs(username)        
        jobids = list(jobs.keys())
        jobidnumber = jobid.split('.')[0]

        if jobid in jobids:
            jobstate=jobs[jobid]['job_state']
            jobname = jobs[jobid]['Job_Name']

            if 'qtime' in jobs[jobid]:
                jobqtime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(jobs[jobid]['qtime'])))
            else:
                jobqtime=''
            if jobstate=='R':
                rtime=int(time.time())-int(jobs[jobid]['start_time'])
                runtime=str(datetime.timedelta(seconds=rtime))
                print('JobName: %s JobID: %s JobState: [%s] JobQtime: %s Runtime: %s' % (jobname, jobid, jobstate, jobqtime, runtime))
            else:
                print('JobName: %s JobID: %s JobState: [%s] JobQtime: %s' % (jobname, jobid, jobstate, jobqtime))


        if jobid not in jobids or (jobname is not None and  os.path.isfile(jobname+'.o'+jobidnumber)):
            if not os.path.isfile(args.dump):
                cur_iteration = 0
            else:
                cur_iteration = cmd.get_output(args.dump)

            print('\nCurrent Iteration: %d' % cur_iteration)
            print('Target number    : %d' % args.max)

            if cur_iteration < args.max:
                if os.path.exists(args.dump):
                    create_backup(args.dump)
                new_submit = True
            else:
                print('Number of iterations completed')
                break
        else:
            time.sleep(args.sleep)
            new_submit = False

        # This happens only when a new job needs to be prepared
        if new_submit:
            data, rstblock, to_uncomment = cmd.get_input(args.input)

            logging.debug('Lines inside the RST_BEGIN -> RST_END block:')
            for i in rstblock:
                logging.debug(i)

            print('Activating Line -> %s' % rstblock[to_uncomment])

            create_backup(args.input)
            cmd.set_input(args.input, data, rstblock, to_uncomment)

            jobid = queue.submit(args.pbs)
            jobname = None
            while True:
                time.sleep(1)
                jobs = queue.get_jobs(username)
                jobname = jobs[jobid]['Job_Name']
                if jobname is not None:
                    break

            print('Submited job JobID: %s' % jobid)
            new_submit = False
            time.sleep(60)
