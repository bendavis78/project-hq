#!/usr/bin/env python

# This was modified from the original manage.py to work with our 
# multiple environments

import sys, os

if os.path.exists(".env") and not os.environ.get('VIRTUAL_ENV'):
    if os.environ.get('RUN_MAIN'):
        sys.stderr.write("Using virtual environment \".env\"\n")
    activate_this = os.path.join(os.path.dirname(__file__), '.env', 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

from django.core import management

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')

if not settings_module or settings_module == "settings":
    settings_module = "settings.development"

# Adjust the path so that we can find our settings module
sys.path.append(os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

if __name__ == "__main__":
    management.execute_from_command_line()
