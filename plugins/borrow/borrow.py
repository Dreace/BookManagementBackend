# coding=utf-8
import json
import logging
import time
import traceback

from flask import Response
from flask import request

from . import api
from .config import cursor, db


@api.route('/Borrow', methods=['POST'])
def handle_borrow_book():
    args = request.get_json()
    res = borrow_book(args)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/Return', methods=['POST'])
def handle_return_book():
    args = request.get_json()
    book_id = args["bookID"]
    res = return_book(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/Borrow/BookList', methods=['GET'])
def handle_get_borrow_book_list():
    book_id = request.args.get("bookID")
    res = get_borrow_book_list(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/Return/BookList', methods=['GET'])
def handle_get_return_book_list():
    book_id = request.args.get("bookID")
    res = get_return_book_list(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/Return/BookDetail', methods=['GET'])
def handle_get_return_book_detail():
    book_id = request.args.get("bookID")
    res = get_return_book_detail(book_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_return_book_detail(book_id):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT `name`,author,press,ISBN,borrowing_time,due_time FROM book,bookslip WHERE bookslip.book_id='%s' " \
              "AND bookslip.is_repaid = 0 AND book.book_id=bookslip.book_id " % book_id
        db.ping(reconnect=True)
        cursor.execute(sql)
        db_res = cursor.fetchone()
        if db_res:
            res = {
                "name": db_res[0],
                "author": db_res[1],
                "press": db_res[2],
                "ISBN": db_res[3],
                "borrowingTime": db_res[4],
                "dueTime": db_res[5],
            }
            data = res
        else:
            message = "未找到详情信息"
    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def get_return_book_list(book_id):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT book_id FROM bookslip WHERE book_id LIKE '%%%s%%' AND is_repaid=0 LIMIT 20" % book_id
        db.ping(reconnect=True)
        cursor.execute(sql)
        db_res = cursor.fetchall()
        res = []
        for i in db_res:
            res.append({
                "bookID": i[0]
            })
        data = res
    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def get_borrow_book_list(book_id):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT book.book_id FROM book LEFT JOIN bookslip slip1 ON slip1.book_id=book.book_id " \
              "WHERE book.book_id LIKE '%%%s%%' " \
              "AND (is_repaid IS NULL OR (is_repaid=1 AND NOT EXISTS (SELECT*FROM bookslip slip2 " \
              "WHERE slip1.book_id=slip2.book_id AND slip2.is_repaid=0))) LIMIT 20" % book_id
        db.ping(reconnect=True)
        cursor.execute(sql)
        db_res = cursor.fetchall()
        res = []
        for i in db_res:
            res.append({
                "bookID": i[0]
            })
        data = res
    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def return_book(book_id):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "UPDATE bookslip SET is_repaid=1,return_time=%s WHERE book_id='%s'" % (int(time.time()), book_id)
        cursor.execute(sql)
        if db.affected_rows() > 0:
            message = "还书成功"
        else:
            code = -1
            message = "没有该书借出记录"
        db.commit()
    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def borrow_book(args: dict):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT COUNT(*) FROM bookslip WHERE card_id='%s' AND is_repaid=0" % args["cardID"]
        db.ping(reconnect=True)
        cursor.execute(sql)
        count_res = cursor.fetchone()
        if len(args["bookList"]) > 10 - count_res[0]:
            message = "该借书卡最多还能借 %s 本书" % (10 - count_res[0])
            code = -1
        elif len(args["bookList"]) < 1:
            message = "书籍列表为空"
            code = -1
        else:
            slip_id = "S" + str(int(time.time() * 1000))
            borrow_time = int(time.time())
            due_time = borrow_time + 60 * 60 * 60 * 24
            success_list = []
            fail_list = []
            for book_id in args["bookList"]:
                sql = "SELECT COUNT(*) from bookslip WHERE book_id='%s' AND is_repaid = 0" % book_id
                cursor.execute(sql)
                if cursor.fetchone()[0] > 0:
                    fail_list.append(book_id)
                else:
                    sql = "INSERT INTO bookslip(slip_id,book_id,card_id,borrowing_time,due_time,is_repaid)" \
                          " VALUES('%s','%s','%s',%s,%s,0)" % (
                              slip_id, book_id, args["cardID"], borrow_time, due_time)
                    cursor.execute(sql)
                    if db.affected_rows() > 0:
                        success_list.append(book_id)
                    db.commit()
            data = {
                "slipID": slip_id,
                "successList": success_list,
                "failList": fail_list
            }

    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}
