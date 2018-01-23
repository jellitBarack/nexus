import os, sys

try:
    from flask_debugtoolbar import DebugToolbarExtension
except:
    pass

sys.path.append(os.path.dirname(__file__))
from app import *

config_name = "development"
try:
    toolbar = DebugToolbarExtension()
except:
    pass
application = create_app(config_name)
try:
    toolbar.init_app(application)
except:
    pass

if __name__ == '__main__':
    application.run()