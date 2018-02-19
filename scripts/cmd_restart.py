#!/usr/bin/env python3

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CMD restarter')
    parser.add_argument('-u', '--user', metavar='<USER>', type=str,
                        help='Username for queue system, if not set it will assume the value from ${USER}')
    parser.add_argument('-p', '--path', metavar='<PATH>', type=str,
                        help='Path where the CMD calculation will be performed')

    args = parser.parse_args()
    print(args)
