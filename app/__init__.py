from flask import Flask, request, current_app    #Flask is the class name
from config import Config   #config is the name of the Python module config.py while Config is the class name
from flask_sqlalchemy import SQLAlchemy     #Database storage and usage
from flask_migrate import Migrate       #Flask-Migrate is an extension that handles SQLAlchemy database migrations for Flask applications 
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler       #All I need to do to get emails sent out on errors is to add a SMTPHandler instance to the Flask logger object, which is app.logger
from flask_mail import Mail
import os
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

# app = Flask(__name__)     #the app used here is the variable name
# app.config.from_object(Config)
db = SQLAlchemy()        #I have added a db object that represents the database.
migrate = Migrate()   #I have added another object that represents the migration engine. 
login = LoginManager()
login.login_view = 'auth.login'  #The 'login' value above is the function (or endpoint) name for the login view. In other words, the name you would use in a url_for() call to get the URL
login.login_message = _l('Logged in Successfully')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()            #The extension is added to the Flask application
babel = Babel()


def create_app(config_class=Config):        # Factory function
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # register the auth blueprint with the application
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')         # The register_blueprint() call in this case has an extra argument, url_prefix. This is entirely optional, but Flask gives you the option to attach a blueprint under a URL prefix, so any routes defined in the blueprint get this prefix in their URLs.
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    #The code below creates a SMTPHandler instance, sets its level so that it only reports errors and not warnings, informational or debugging messages, and finally attaches it to the app.logger object from Flask.
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)     #I'm writing the log file with name microblog.log in a logs directory, which I create if it doesn't already exist . #The RotatingFileHandler class is nice because it rotates the logs, ensuring that the log files do not grow too large when the application runs for a long time. In this case I'm limiting the size of the log file to 10KB, and I'm keeping the last ten log files as backup.
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))         #The logging.Formatter class provides custom formatting for the log messages. Since these messages are going to a file, I want them to have as much information as possible. So I'm using a format that includes the timestamp, the logging level, the message and the source file and line number from where the log entry originated.
        file_handler.setLevel(logging.INFO)     #To make the logging more useful, I'm also lowering the logging level to the INFO category, both in the application logger and the file logger handler. In case you are not familiar with the logging categories, they are DEBUG, INFO, WARNING, ERROR and CRITICAL in increasing order of severity.
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])     #Here I'm using an attribute of Flask's request object called accept_languages. This object provides a high-level interface to work with the Accept-Language header that clients send with a request. 

# from app import routes, models, errors
#the app here is the directory name in which this python file is stored , models is the new module which defines the structure of the database
# from app import routes, models
from app import models