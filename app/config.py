class Config(object):
    """
    Common configurations
    """
    APPLICATION_ROOT = "/citellus"
    # Put any configurations here that are common across all environments
    REPORT_FILE_NAMES = ("citellus.json", "magui.json")
    CITELLUS_PATH = "/git/citellus"
    RC_OKAY = 10
    RC_FAILED = 20
    RC_SKIPPED = 30
    PLUGIN_STATES = { 
        10: { 
            "icon": "fa fa-check-circle-o",
            "state": "okay",
            "class": "success",
            "text_color": "text-black"
        },
        20: { 
            "icon": "pficon pficon-error-circle-o",
            "state": "failed",
            "class": "danger",
            "text_color": "text-black"
        },
        30: { 
            "icon": "pficon pficon-help",
            "state": "skipped",
            "class": "info",
            "text_color": "text-black"
        }
    }
    

class DevelopmentConfig(Config):
    """
    Development configurations
    """

    DEBUG = True
    SQLALCHEMY_ECHO = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class ProductionConfig(Config):
    """
    Production configurations
    """

    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
