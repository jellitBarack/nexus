import os
import sys
import signal

try:
    from flask_debugtoolbar import DebugToolbarExtension
except:
    pass

sys.path.append(os.path.dirname(__file__))
from app import *

if 'ENVIRONMENT_NAME' in os.environ:
    config_name = os.environ['ENVIRONMENT_NAME']
else:
    config_name = "production"

try:
    toolbar = DebugToolbarExtension()
except:
    pass
application = create_app(config_name)

try:
    toolbar.init_app(application)
except:
    pass

# os.kill(os.getpid(), signal.SIGINT)
if __name__ == '__main__':
    application.run()
