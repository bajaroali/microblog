import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  """Defines the configuration settings of the app"""
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess me'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    
  #MySQL URI
  #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
  #  'mysql://root:password@localhost/db_name'
  
  MAIL_SERVER = os.environ.get('MAIL_SERVER')
  MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
  MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
  MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
  MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
  ADMINS = ['bajaroali@gmail.com']
  
  
  #Configure Upload folder for images
  UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/images/'
