from fabric.state import env

env.project = 'farstar-hq'   #The name of this project
env.repo_base = 'git@git.farstarserver.com:%s.git' % env.project #The base svn repository for this project (ie, parent of trunk)

# Options ##
env.use_virtualenv = True # create virtualenv when setting up
env.use_south = True # automatically migrate when deploying
env.collectstatic = True # run collectstatic command when deploying
env.collectstatic_args = '-l' # symlink static files

def production():
    env.environment = 'production'
    env.hosts = ['web1.farstarserver.com']
    env.server_type = 'debian'

# Define the available environments:
env.environments = [production]

from devtools.fabfile import *
