import os


def get_input(path):
    # File exists
    if not os.path.exists(path):
        raise ValueError("ERROR: Could not read file: %s" % path)

    # Open File
    rf=open(path)
    fsize=os.path.getsize(path)

    if fsize>10000:
        rf.seek(fsize-2000)

    data=rf.readlines()
    nvalues=0
    # Skip the first 2 lines to avoid the truncation created with the seek call 
    for iline in data[2:]:
        values=iline.split()
        if nvalues==0:
            nvalues=len(values)
        else:
            if nvalues!=len(values):
                print("WARNING: Line seems truncated, ignoring data from now on...")
                break

        cur_value=values[0].strip()
        cur_iteration=int(cur_value)
        print(cur_iteration)

    return cur_iteration

def get_output(path):
    pass


def set_input(path):
    pass

def set_output(path):
    pass
