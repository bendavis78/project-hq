#!/usr/bin/env python

import sys, os, re, shutil
from distutils import version
from subprocess import Popen, PIPE

YES = ('y', 'Y', 'yes', 'Yes')

env_dir = '.env'

if os.path.exists(env_dir):
    a = raw_input("Remove existing %s directory? [y/N]: " % env_dir)
    if a in YES:
        shutil.rmtree(env_dir)
    else:
        print "Cancelled."
        sys.exit(1)

print "Creating virtual environemnt.\n\n***** DO NOT COMMIT THE '%s' FOLDER TO VERSION CONTROL!!! ******\n\n" % env_dir
p = Popen(['virtualenv', '--no-site-packages', env_dir])
p.communicate()
if p.returncode != 0:
    sys.exit(1)

if os.path.exists('requirements.txt'):
    p = Popen(['pip', '--version'], stdout=PIPE)
    pip_version = p.communicate()[0]
    if p.returncode != 0:
        print 'Error while running pip.  Is it installed?'
        sys.exit(1)

    pip_version = re.match(r'^pip (.*?) ', pip_version).groups()[0]
    required = version.StrictVersion('0.4.0')
    current = version.StrictVersion(pip_version)
    if current < required:
        print 'Your current pip version is outdated. Version >=0.4.0 is required.'
        sys.exit(1)

    reqfile = 'requirements.txt'
    if os.path.exists('requirements_local.txt'):
        reqfile = 'requirements_local.txt'
    
    p = Popen(('pip install -E %s -r %s' % (env_dir, reqfile)).split())
    p.communicate()
    if p.returncode != 0:
        sys.exit(1)

print "\nDone.\n"

