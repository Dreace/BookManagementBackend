# coding=utf-8
import json
import logging
import time
import traceback

import pymysql
from flask import Response
from flask import request

from global_config import mysql_host, mysql_password, mysql_user
from . import api
from .config import db, cursor


@api.route('/AddBook', methods=['POST'])
def handle_add_book():
    args = request.get_json()
    res = add_book(args)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/DeleteBook', methods=['POST'])
def handle_delete_book():
    args = request.get_json()
    book_id = args["bookID"]
    res = delete_book(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/UpdateBook', methods=['POST'])
def handle_update_book():
    args = request.get_json()
    res = update_book(args)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetBookList', methods=['GET'])
def handle_get_book_list():
    keywords = request.args.get("keywords")
    keywords_type = request.args.get("type")
    res = get_book_list(keywords, keywords_type)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_book_list(keywords, keywords_type):
    message = "OK"
    code = 0
    data = ""

    book_connect = pymysql.connect(mysql_host, mysql_user, mysql_password, "book", charset='utf8')
    book_cursor = book_connect.cursor()
    try:
        sql = "SELECT book.book_id,ISBN,`name`,author,price,press,is_repaid FROM book LEFT JOIN bookslip slip1 ON " \
              "slip1.book_id=book.book_id WHERE book.`%s` LIKE '%%%s%%' AND NOT EXISTS (SELECT * FROM bookslip slip2 " \
              "WHERE slip1.book_id=slip2.book_id AND slip1.is_repaid=1 AND slip2.is_repaid=0) " \
              "ORDER BY book.book_id DESC LIMIT 50" \
              % (keywords_type, keywords)
        book_cursor.execute(sql)
        db_res = book_cursor.fetchall()
        res = []
        for i in db_res:
            res.append({
                "bookID": i[0],
                "ISBN": i[1],
                "name": i[2],
                "author": i[3],
                "price": i[4],
                "press": i[5],
                "isBorrowed": True if i[6] == 0 else False
            })
        data = res
    except:
        logging.error(traceback.format_exc())
        book_connect.rollback()
        message = "查询失败"
        code = -1
    finally:
        book_cursor.close()
        book_connect.close()
    return {"message": message, "code": code, "data": data}


def update_book(book_args: dict):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "UPDATE book SET ISBN='%s',`name`='%s',author='%s',price='%s',press='%s' WHERE book_id='%s' LIMIT 200" \
              % (book_args["ISBN"], book_args["name"], book_args["author"], book_args["price"],
                 book_args["press"], book_args["bookID"])
        db.ping(reconnect=True)
        cursor.execute(sql)
        if db.affected_rows() > 0:
            message = "更新成功"
        else:
            message = "没有修改任何记录"
            code = -1
        db.commit()

    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def delete_book(book_id: str):
    message = "OK"
    code = 0
    data = ""
    if not book_id:
        message = "书籍编号不能为空"
        code = -1
    else:
        try:
            sql = "SELECT COUNT(*) FROM bookslip WHERE book_id='%s' AND is_repaid=0" % book_id
            db.ping(reconnect=True)
            cursor.execute(sql)
            db_res = cursor.fetchone()
            if db_res[0] > 0:
                message = "该书已被借出，不能删除"
                code = -1
            else:
                sql = "DELETE FROM book WHERE book_id = '%s'" % book_id
                cursor.execute(sql)
                if db.affected_rows() == 0:
                    message = "未删除任何记录"
                    code = -1
                else:
                    message = "删除成功"
                db.commit()

        except:
            logging.error(traceback.format_exc())
            db.rollback()
            message = "操作失败"
            code = -1
    return {"message": message, "code": code, "data": data}


def add_book(book_args: dict):
    message = "OK"
    code = 0
    data = ""
    try:
        book_id = "B" + str(int(time.time() * 1000))
        sql = "INSERT INTO book (book_id,ISBN,`name`,author,price,press) VALUES ('%s','%s','%s','%s','%s','%s')" \
              % (book_id, book_args["ISBN"], book_args["name"], book_args["author"], book_args["price"],
                 book_args["press"])
        db.ping(reconnect=True)
        cursor.execute(sql)
        if db.affected_rows() > 0:
            message = "添加成功"
            data = {
                "bookID": book_id
            }
        else:
            message = "添加失败"
            code = -1
        db.commit()

    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}
