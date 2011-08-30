import sys, os, site

# Use virtual environment if it exists (we have to just brute-force the pythonpath here)
env_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'env'))
if os.path.exists(env_dir):
    old_sys_path = list(sys.path)
    #get virtualenv lib dir
    from subprocess import Popen, PIPE
    cmd = 'from distutils import sysconfig as s; print s.get_python_lib()'
    p = Popen(['%s/bin/python' % env_dir, '-c', cmd], stdout=PIPE)
    path = p.communicate()[0].strip('\n')
    sys.path = [path]
    site.addsitedir(path)
    sys.path += old_sys_path

from django.core.handlers import wsgi

# Override django's handler to set the DJANGO_SETTINGS_MODULE from the one
# defined in the apache SetEnv directive
class Handler(wsgi.WSGIHandler):
    def __call__(self, environ, start_response):
        if not os.path.dirname(__file__) in sys.path:
            sys.path.append(os.path.dirname(__file__)) 
        os.environ['DJANGO_SETTINGS_MODULE'] = environ.get('DJANGO_SETTINGS_MODULE')
        os.environ['PYTHON_EGG_CACHE'] = environ.get('PYTHON_EGG_CACHE')
        
        # Set the umask to 002, so that the group member can delete files while deploying
        os.umask(0002)
        return super(Handler, self).__call__(environ, start_response)
        

application = Handler()
