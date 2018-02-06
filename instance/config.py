# date +%s | sha256sum | base64 | head -c 64 ; echo
SECRET_KEY = 'Xn8ynOypnfuwVfNj0Hhpav1LVkWBlMX8K6qUSdee6TQCq3w8+B31QH6C3rkhW'
SQLALCHEMY_DATABASE_URI = 'sqlite:////var/www/citellus/db/citellus.db'
GOOGLE_ID = "679364469390-kvsqonm1u00renqnobnmvcivkjc6900j.apps.googleusercontent.com"
GOOGLE_SECRET = "vMp7uTBmxlzZFnywlUkLMC6z"
"""
IDP_SETTINGS = {
   'auth.redhat.com': {
       "metadata": {
           "local": ['https://auth.redhat.com/auth/realms/EmployeeIDP/protocol/saml/descriptor']
       }
   },
   'auth.stage.redhat.com': {
       "metadata": {
            "local": ['https://auth.stage.redhat.com/auth/realms/EmployeeIDP/protocol/saml/descriptor']
       }
   }
}
"""
