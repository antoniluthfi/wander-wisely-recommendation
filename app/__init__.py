from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '34.101.227.234'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wander3306wisely'
app.config['MYSQL_DB'] = 'wander_wisely'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

from app import routes