import pymysql

from global_config import mysql_host, mysql_password, mysql_user

book_connect = pymysql.connect(mysql_host, mysql_user, mysql_password, "book", charset='utf8')
book_cursor = book_connect.cursor()
