# Solo usar PyMySQL si no estamos en Heroku (PostgreSQL)
import os
if 'DATABASE_URL' not in os.environ:
    import pymysql
    pymysql.install_as_MySQLdb()