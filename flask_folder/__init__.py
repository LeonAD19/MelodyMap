import sys
sys.dont_write_bytecode = True

from flask import Flask

### Application Factory ###
def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY']='LongAndRandomSecretKey'

    from .routes import routes
    
    app.register_blueprint(routes, url_prefix = '/')
    return app