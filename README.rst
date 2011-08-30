============
Requirements
============
Most of our django applications require the following:
* python 2.5 or 2.6
* postgresql >= 8.2
* python-psycopg2

Consult each app's documentation for other requirements.


===============
Getting Started
===============
To get started, make sure you have django installed correctly. Your 
DJANGO_SETTINGS_MODULE environment variable should be set to either "settings" 
or "settings.development"

1. copy settings/development.py.example to settings/development.py, and modify 
   database information
2. create an empty database
3. run ``./makenv.py``
4. run ``./manage.py syncdb --migrate``
5. run ``./manage.py runserver``
6. navigate to http://localhost:8000


Loading dummy data
==================
To do anything worthwile, you'll need some dummy data to work with. Some apps
come with "fixtures" that you can load to give you dummy data to work with.
To load the fixture into your database, run (for exmaple):

1. ``./manage.py loaddata <app name>/fixtures/dummy_data``

Consult the application's documentation for details on what fixtures or custom
commands are available.


Reset script
============
For your convenience, we also provide a "reset" shell script. Running this
script will drop and re-create your database, run syncdb, run migrations, and
load any dummy_data fixtures.  This is convenient when you want to bring your
database back to a "clean slate" with all the default dummy data already set
up.  It goes without saying that this should *NEVER* be run on a production
site.


==========
Deployment
==========
NOTE: If you need to deploy, you need to install fabric. Try just typing:

``sudo easy_install fabric``

if that doesn't work,  download fabric from http://nongnu.org/fab,  and follow 
instructions for building manually (it's not that hard)

Once you're ready to deploy,  and you've checked in your changes, run 
``fab [environment] deploy`` where ``[environment]`` is either "production" or 
"staging", eg: 

``fab production deploy``

Run ``fab list`` to see a list of all possible commands/tasks.

Deploying branches for testing
==============================
Sometimes you might want to set up an environment separate from your normal
staging environment to test your branch.  The process for this is nothing
special, it just involves creating a new environment config.  To make this
easy, you can "inherit" from your default staging invironment in your
deploy_settings.py like so::

    def staging_mybranch():
	    staging()
		env.branch = 'mybranch'
		env.server_name = 'mybranch.test.example.com'

If you need a separate settings file for your branch (eg, if you need a
different database), make sure and set env.environment to the module name of
your settings file, eg:  ``env.environment = 'staging_mybranch'``.  Then, in
your settings/staging_mybranch.py file,  you can do this::

    from staging import *  #Use all default staging settings
	DATABASE_NAME = 'mysite_staging_mybranch'

Then, just run ``fab staging_mybranch setup`` to set up the new branch site on
the server.

==========
Migrations
==========
Any time you make a change to your django models, that change also requires a 
change in the database.  This is also known as "schema evolution". A simple
"syncdb" command won't actually "sync" up your database with your model 
changes. For example, if you add or remove a model field, syncdb will not make
that same change in the database. Syncdb only adds new models. There's a reason
for this -- Read http://code.djangoproject.com/wiki/SchemaEvolution#Usecases 
for differentuse cases.

The solution is to keep track of each individual database changes, and apply
them as necessary. This also makes deploying your changes much easier, as 
you only have to run one "migrate" command, which you've already tested 
(hopefully) on your development site.

This project uses South migrations. It is recommended that you read up on their
documentation at http://south.aeracode.org/.  For most changes, you can use the
following command to create a new migration:

``./manage.py schemamigration <app name> <migration name> --auto``

The "--auto" flag will tell South to auto-detect the changes in your model
since the last migration. Once it finishes, make sure you check the created
file and make sure everything looks right.  The autodetection feature is
still pretty new, and can get it wrong from time to time.
