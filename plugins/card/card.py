# coding=utf-8
import json
import logging
import time
import traceback

from flask import Response
from flask import request

from . import api
from .config import cursor, db


@api.route('/GetCardList', methods=['GET'])
def handle_get_card_list():
    keywords = request.args.get("keywords")
    keywords_type = request.args.get("keywords_type")
    res = get_card_list(keywords, keywords_type)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetCardBorrowList', methods=['GET'])
def handle_get_card_borrow_list():
    card_id = request.args.get("cardID", "")
    res = get_card_borrow_list(card_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/DeleteCard', methods=['POST'])
def handle_delete_card():
    args = request.get_json()
    card_id = args["cardID"]
    res = delete_card(card_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/ApplyCard', methods=['POST'])
def handle_apply_card():
    args = request.get_json()
    res = apply_card(args)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/ReissueCard', methods=['POST'])
def handle_reissue_card():
    args = request.get_json()
    card_id = args["cardID"]
    res = reissue_card(card_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


@api.route('/GetPureCardList', methods=['GET'])
def handle_get_pure_card_list():
    card_id = request.args.get("cardID", "")
    res = get_pure_card_list(card_id)
    resp = Response(json.dumps(res), mimetype='application/json')
    return resp


def get_pure_card_list(card_id: str):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT card_id FROM `card` WHERE card_id LIKE '%%%s%%'" % card_id
        db.ping(reconnect=True)
        cursor.execute(sql)
        db_res = cursor.fetchall()
        res = []
        for i in db_res:
            res.append({
                "cardID": i[0],
            })
        data = res
    except:
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def reissue_card(card_id):
    message = "OK"
    code = 0
    data = ""
    try:
        new_card_id = "C" + str(int(time.time() * 1000))
        sql = "UPDATE card SET card_id='%s', `date`= %s WHERE card_id='%s'" % (new_card_id, int(time.time()), card_id)
        db.ping(reconnect=True)
        cursor.execute(sql)
        if db.affected_rows() > 0:
            message = "补办成功"
            data = {
                "cardID": new_card_id
            }
        else:
            message = "补办失败"
            code = -1
        db.commit()

    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def apply_card(args: dict):
    message = "OK"
    code = 0
    data = ""
    try:
        card_id = "C" + str(int(time.time() * 1000))
        sql = "INSERT INTO card VALUES('%s', %s, '%s', '%s', '%s')" % \
              (card_id, int(time.time()), args["cardholder"], args["telephone"], args["email"])
        db.ping(reconnect=True)
        cursor.execute(sql)
        if db.affected_rows() > 0:
            message = "开卡成功"
            data = {
                "cardID": card_id
            }
        else:
            message = "开卡失败"
            code = -1
        db.commit()
    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "操作失败"
        code = -1
    return {"message": message, "code": code, "data": data}


def delete_card(card_id: str):
    message = "OK"
    code = 0
    data = ""
    if not card_id:
        message = "卡号不能为空"
        code = -1
    else:
        try:
            sql = "SELECT COUNT(*) FROM bookslip WHERE card_id='%s' AND is_repaid=0" % card_id
            db.ping(reconnect=True)
            cursor.execute(sql)
            db_res = cursor.fetchone()
            if db_res[0] > 0:
                message = "有未还记录，不能注销"
                code = -1
            else:
                sql = "DELETE FROM card WHERE card_id = '%s'" % card_id
                cursor.execute(sql)
                if db.affected_rows() == 0:
                    message = "未删除任何记录"
                    code = -1
                else:
                    message = "注销成功"
                db.commit()

        except:
            logging.error(traceback.format_exc())
            db.rollback()
            message = "操作失败"
            code = -1
    return {"message": message, "code": code, "data": data}


def get_card_borrow_list(card_id: str):
    message = "OK"
    code = 0
    data = ""
    if not card_id:
        message = "卡号不能为空"
        code = -1
    else:
        try:
            sql = "SELECT slip_id,book_id,borrowing_time,due_time,return_time,is_repaid FROM bookslip " \
                  "WHERE card_id = '%s'" % card_id
            db.ping(reconnect=True)
            cursor.execute(sql)
            db_res = cursor.fetchall()
            if not db_res:
                message = "无结果"
                code = -1
            else:
                res = []
                for i in db_res:
                    res.append({
                        "slipID": i[0],
                        "bookID": i[1],
                        "borrowingTime": i[2],
                        "dueTime": i[3],
                        "returnTime": i[4],
                        "isRepaid": True if i[5] == 1 else False,
                    })
                data = res
        except:
            logging.error(traceback.format_exc())
            db.rollback()
            message = "查询失败"
            code = -1
    return {"message": message, "code": code, "data": data}


def get_card_list(keywords, keywords_type):
    message = "OK"
    code = 0
    data = ""
    try:
        sql = "SELECT card_id,cardholder,telephone,email,`date` FROM `card` WHERE %s LIKE '%%%s%%' LIMIT 200" % (
            keywords_type, keywords)
        db.ping(reconnect=True)
        cursor.execute(sql)
        db_res = cursor.fetchall()
        res = []
        for i in db_res:
            res.append({
                "cardID": i[0],
                "cardholder": i[1],
                "telephone": i[2],
                "email": i[3],
                "date": i[4]
            })
        data = res


    except:
        logging.error(traceback.format_exc())
        db.rollback()
        message = "查询失败"
        code = -1
    return {"message": message, "code": code, "data": data}
