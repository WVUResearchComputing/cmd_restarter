#!/usr/bin/env python3

import os
import argparse
import cmd_restarter

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CMD restarter')
    parser.add_argument('-u', '--user', metavar='<USER>', type=str,
                        help='Username for queue system, if not set it will assume the value from ${USER}')
    parser.add_argument('-p', '--path', metavar='<PATH>', type=str,
                        help='Path where the CMD calculation will be performed')

    parser.add_argument('-d', '--dump', metavar='<PATH>', type=str,
                        help='Path to dump file used to count the number of steps completed')

    args = parser.parse_args()
    print(args)

    dumpfile=args.path+os.sep+args.dump
    if not os.path.isfile(dumpfile):
        raise ValueError("ERROR: Could not read dumpfile: %s" % dumpfile)

    cmd_restarter.cmd.get_input(dumpfile)
