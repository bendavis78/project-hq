"""
This file holds the Fabric deployment settings for this project
"""
from fabric.state import env

#env.project = 'my_project'   #The name of this project
#env.repo_base = 'git@git.farstarserver.com:%s.git' % env.project #The base svn repository for this project (ie, parent of trunk)

## Directory aliases ##
# These are used in the apache vhost config file to defined directory aliases.
# You usually want at least one for your media (uploads) directory
#env.directory_aliases = {
#    '/media' : '%(base_dir)s/media'
#}

## External directories ##
## These are directories that need to exist outside of your deployment files.
## Generally this is your storage place for uploaded files, images, etc.
# env.external_dirs = ['media']

## Options ##
#env.use_virtualenv = True # create virtualenv when setting up
#env.use_south = True # automatically migrate when deploying
#env.collectstatic = True # run collectstatic command when deploying
#env.collectstatic_args = '-l' # symlink static files

## Example staging and production environments:
#def staging():
#    env.environment = 'staging'
#    env.hosts = ['testserver.example.com']  # list of hosts to connect to
#    env.server_name = 'test.example.com' # primary domain name for this environment
#
#    env.server_type = 'debian' #(use 'debian' for debian servers)
#    
#    # List of extra httpd.conf settings
#    env.httpd_conf_extra = []
#
#def production():
#    env.environment = 'production'
#    env.hosts = ['server.example.com']
#    env.server_name = 'www.example.com'
#    env.server_type = 'debian'
#    env.server_aliases = ['example.com','foo.example.com']
#
## Define the available environments:
#environments = [staging, production]
