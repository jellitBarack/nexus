import os

from logging.config import dictConfig
try:
    from flask_debugtoolbar import DebugToolbarExtension
except:
    pass


dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": { "debug_format": { "format": "%(filename)-8s | %(module)-12s | %(funcName)s | %(lineno)d : %(message)s" }},
    "handlers": { "console": { "class": "logging.StreamHandler", "formatter": "debug_format", "stream": "ext://sys.stdout" }}
})

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
try:
    toolbar = DebugToolbarExtension()
except:
    pass
app = create_app(config_name)
try:
    toolbar.init_app(app)
except:
    pass

if __name__ == '__main__':
    app.run()
