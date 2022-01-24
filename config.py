import os
class Config(object):
    SECRET_KEY = "99e2afce072a834abcb83aa000a19d78"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
