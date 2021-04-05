from flask import Flask
from datetime import datetime, date
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from uuid import uuid1
import yaml
import sys

app = Flask(__name__)

app.config['SECRET_KEY']= '231fabd16d7ca913df4539ac4bc45a68'

db = yaml.load(open(sys.path[0]+'/app/db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

bcrypt = Bcrypt(app)

mysql = MySQL(app)


from app import routes