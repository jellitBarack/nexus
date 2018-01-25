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
