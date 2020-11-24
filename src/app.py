from flask import Flask
from flask_cors import CORS

from .config import app_config
from .models import db, bcrypt

from .shared import mail

from .views.UserView import user_api as user_blueprint
from .views.BlogpostView import blogpost_api as blogpost_blueprint
from .views.ProjectView import project_api as project_blueprint
from .views.LayoutView import layout_api as layout_blueprint
from .views.ContractView import contract_api as contract_blueprint
from .views.PaymentView import payment_api as payment_blueprint

def create_app(env_name):
  """
  Create app
  """
  # app initiliazation
  app = Flask(__name__)

  app.config.from_object(app_config[env_name])

  # cors
  CORS(app, supports_credentials=True)

  bcrypt.init_app(app)
  
  mail.init_app(app)

  db.init_app(app)

  app.register_blueprint(user_blueprint, url_prefix='/api/v1/user')
  app.register_blueprint(blogpost_blueprint, url_prefix='/api/v1/blogpost')
  app.register_blueprint(project_blueprint, url_prefix='/api/v1/project')
  app.register_blueprint(layout_blueprint, url_prefix='/api/v1/layout')
  app.register_blueprint(contract_blueprint, url_prefix='/api/v1/contract')
  app.register_blueprint(payment_blueprint, url_prefix='/api/v1/payment')

  @app.route('/')
  def index():
    """
    example endpoint
    """
    app.logger.info('Mostrando los posts del blog')
    return 'Felicitaciones! Has instalado correctamente el backend FIDO'

  return app
