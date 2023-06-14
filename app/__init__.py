from flask import Flask
from flask_mysqldb import MySQL
import os


app = Flask(__name__)

app.config['MYSQL_HOST'] = '34.101.227.234'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wander3306wisely'
app.config['MYSQL_DB'] = 'wander_wisely'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

from app import routes

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)