import os
import re
import logging


def collect_variables(data):
    """
    From the input filed read as lines this function extracts all the lines starting with the
    word variable and store the 'kind' (second argument) and 'value' third argument without 
    further interpreting that value. A dictionary is returned
    """
    # Read all the lines in data
    variables = {}
    for iline in data:
        # Suppress comments
        if iline.startswith('#'):
            continue
        if iline.strip().startswith('variable'):
            # Remove comments alongside with a meaningful line 
            if '#' in iline:
                line = iline[:iline.index('#')].strip()
            else:
                line = iline.strip()

            tokens = line.split()
            if len(tokens) < 4:
                raise ValueError('Wrong number of tokens in line: %s' % line)
            elif len(tokens) > 4:
                logging.warning('More than 3 tokens in line: %s' % line)

            variables[tokens[1]] = {'kind': tokens[2], 'value': tokens[3]}
    logging.debug('Variables read from input data: %d' % len(variables))

    return variables
        

def collect_rstblock(data):
    """
    Search all the lines from the input lines and extract the block of kines
    encapsulated inside RST_BEGIN and RST_END
    """
    block = []
    active = False
    for iline in data:
        if iline.strip().startswith('#') and 'RST_BEGIN' in iline:
            active = True
        elif iline.strip().startswith('#') and 'RST_END' in iline:
            active = False
        elif active:
            if iline.strip().startswith('#'):
                iline = iline.strip()[1:]
            block.append(iline.strip())
    logging.debug('Number of lines captured inside the RST block: %d' % len(block))
    for iline in block:
        logging.debug(' -> %s' % iline)

    return block


def interpret_variables(text, variables):
    
    newtext = str(text)
    captures = re.findall('\$\{([\w\d.]+)\}', newtext)
    for ikey in captures:
        logging.debug(' -> %s' % newtext)
        if ikey in variables:
            newtext = newtext.replace('${%s}' % ikey, variables[ikey]['value'])
        else:
            raise ValueError("Variable %s could not be found in variables dict" % ikey)
    if '${' in newtext:
        newtext = interpret_variables(newtext, variables)
    return newtext.strip()


def analysis_block(rstblock, variables):

    files = []
    for iline in rstblock:
        # Retrieve value
        line = interpret_variables(iline, variables)
        if '#' in line:
            line = line[:line.index('#')]
        assert(len(line.split()) == 2)
        command = line.split()[0]
        argument = line.split()[1]
        logging.debug('Checking: %s...' % command)
        if '%' in argument:
            index = 0
            while True:
                newarg = argument.replace('%', str(index))
                if os.path.isfile(newarg):
                    mtime = os.path.getmtime(newarg)
                    files.append((mtime, iline, newarg))
                    index += 1
                else:
                    logging.debug('File not found: %s' % newarg)
                    if index == 0:
                        files.append((0.0, iline, newarg))
                    break
        else:
            if os.path.isfile(argument):
                mtime = os.path.getmtime(argument)
                files.append((mtime, iline, argument))
            else:
                files.append((0.0, iline, argument))
                logging.error('File not found: %s' % argument)
                break

    # Check if there is not a single restart case
    to_uncomment = None
    has_restart = False
    for i in range(len(rstblock)):
        if rstblock[i].strip().startswith('read_restart') and files[i][0] != 0.0:
            has_restart = True
            break
    if not has_restart:
        for i in range(len(rstblock)):
            if rstblock[i].strip().startswith('read_data'):
                to_uncomment = i
                break

    # Detect with restart case is the newest
    else:
        for i in range(len(rstblock)):
            if rstblock[i].strip().startswith('read_restart'):
                logging.debug(str(files[i]))
                if files[i][0] > 0:
                    if to_uncomment is None:
                        to_uncomment = i
                    elif files[i][0] > files[to_uncomment][0]:
                        to_uncomment = i

    if to_uncomment is None:
        for i in files:
            logging.error(str(i))
    else:
        logging.debug('We should comment all the lines in the block except %d' % to_uncomment)
        logging.debug("-> %s" % rstblock[to_uncomment])

    return to_uncomment


def get_input(path):    
    # File exists
    if not os.path.exists(path):
        raise ValueError("ERROR: Could not read file: %s" % path)

    rf = open(path)
    data = rf.readlines()
    rf.close()

    check_input(data)

    rstblock = collect_rstblock(data)
    variables = collect_variables(data) 

    to_uncomment = analysis_block(rstblock, variables)

    return data, rstblock, to_uncomment


def get_output(path):
    # File exists
    if not os.path.exists(path):
        raise ValueError("ERROR: Could not read file: %s" % path)

    # Open File
    rf = open(path)
    fsize = os.path.getsize(path)

    if fsize > 10000:
        rf.seek(fsize-2000)

    data = rf.readlines()
    nvalues = 0
    cur_iteration = 0
    # Skip the first 2 lines to avoid the truncation created with the seek call 
    for iline in data[2:]:
        values = iline.split()
        if nvalues == 0:
            nvalues = len(values)
        else:
            if nvalues != len(values):
                logging.debug("WARNING: Line seems truncated, ignoring data from now on...")
                continue


        cur_value = values[0].strip()
        try:
            ci = int(cur_value)
        except ValueError:
            continue
        cur_iteration = ci

    rf.close()
    return cur_iteration


def set_input(filename, data, rstblock, to_uncomment):
    """
    Write a new Input File (filename) using the lines from 'data' and the information
    about the blocks to be commented or uncommented based on 'rstblock' and 'to_uncomment'
    """
    wf = open(filename, 'w')
    
    rst_active = False
    initonly_active = False
    restonly_active = False

    for iline in data:
        line = iline.strip()

        if '#' in line and 'RST_BEGIN' in line:
            wf.write(line+'\n')
            rst_active = True
            for i in range(len(rstblock)):
                if i == to_uncomment:
                    wf.write(rstblock[i]+'\n')
                else:
                    wf.write('# ' + rstblock[i] + '\n')

        elif '#' in line and 'RST_END' in line:
            wf.write(line+'\n')
            rst_active = False
        elif rst_active:
            pass
        elif '#' in line and 'RESTONLY_BEGIN' in line:
            wf.write(line+'\n')
            restonly_active = True
        elif '#' in line and 'RESTONLY_END' in line:
            wf.write(line+'\n')
            restonly_active = False
        elif '#' in line and 'INITONLY_BEGIN' in line:
            wf.write(line+'\n')
            initonly_active = True
        elif '#' in line and 'INITONLY_END' in line:
            wf.write(line+'\n')
            initonly_active = False
        else:
            if restonly_active and rstblock[to_uncomment].startswith('read_restart'):
                # If line is commented, uncomment it
                if line.startswith('#'):
                    line = line[1:].strip()
                    wf.write(line+'\n')
                # Write the line as it is
                else:
                    wf.write(line+'\n')

            elif initonly_active and rstblock[to_uncomment].startswith('read_data'):
                # If line is commented, uncomment it
                if line.startswith('#'):
                    line = line[1:].strip()
                    wf.write(line+'\n')
                # Write the line as it is
                else:
                    wf.write(line+'\n')


            elif restonly_active and rstblock[to_uncomment].startswith('read_data'):
                # If line is commented, keep it
                if line.startswith('#'):
                    wf.write(line+'\n')
                # Write the line commented
                else:
                    wf.write('# '+line+'\n')

            elif initonly_active and rstblock[to_uncomment].startswith('read_restart'):
                # If line is commented, keep it
                if line.startswith('#'):
                    wf.write(line+'\n')
                # Write the line commented
                else:
                    wf.write('# '+line+'\n')

            else:
                wf.write(line+'\n')




    wf.close()



def check_input(data):
    """
    Check the lines in the data input to check that the blocks are properly defined on the input file
    Checks for missing BEGIN or END lines and check also for nested blocks that must never happen 
    on the input
    """
    rst=False
    restonly=False
    initonly=False

    for iline in data:
        line = iline.strip()

        if '#' in line and 'RST_BEGIN' in line:
            assert([rst,restonly,initonly]==[False, False, False])
            rst=True
        elif '#' in line and 'RST_END' in line:
            assert([rst,restonly,initonly]==[True, False, False])
            rst=False
        elif '#' in line and 'RESTONLY_BEGIN' in line:
            assert([rst,restonly,initonly]==[False, False, False])
            restonly=True
        elif '#' in line and 'RESTONLY_END' in line:
            assert([rst,restonly,initonly]==[False, True, False])
            restonly=False
        elif '#' in line and 'INITONLY_BEGIN' in line:
            assert([rst,restonly,initonly]==[False, False, False])
            initonly=True
        elif '#' in line and 'INITONLY_END' in line:
            assert([rst,restonly,initonly]==[False, False, True])
            initonly=False

