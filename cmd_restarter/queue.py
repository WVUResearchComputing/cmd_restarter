import subprocess
import xml.etree.ElementTree as ElementTree


def get_jobs(user):
    """
    Check all the jobs submitted by a given 'user'
    Returns a dictionary with the JobIDs and names.
    """
    data = subprocess.check_output(['qstat', '-x', '-f', '-u', user])
    xmldata = ElementTree.fromstring(data)
    jobs = xmldata.findall('Job')
    ret = {}
    for ijob in jobs:
        children = ijob.getchildren()
        jobid = ijob.findall('Job_Id')[0].text
        ret[jobid] = {}
        for child in children:
            ret[jobid][child.tag] = child.text
    return ret


def submit():
    pass
