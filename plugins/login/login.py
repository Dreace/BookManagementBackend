# coding=utf-8
import hashlib
import json
import logging
import time
import traceback

from flask import Response
from flask import request

from . import api
from .config import session, cursor, db


@api.route('/Login', methods=['POST'])
def handle_login():
    args = request.get_json()
    name = args['name']
    password = args["password"]
    res = login(name, password)
    resp = Response(json.dumps(res), mimetype='application/json')
    if res["code"] == 0:
        resp.set_cookie("session", res["data"]["session"])
    return resp


@api.route('/Logout', methods=['POST'])
def handle_logout():
    resp = Response(json.dumps({}), mimetype='application/json')
    resp.delete_cookie("session")
    return resp


def login(name, password):
    message = "登录成功"
    code = 0
    data = ""
    if not name or not password:
        message = "账号密码不能为空"
        code = -1
    else:
        try:
            sql = "SELECT admin_id,`name` FROM admin WHERE `name`='%s' AND `password` = '%s'" % (
                name, password)
            db.ping(reconnect=True)
            cursor.execute(sql)
            db_res = cursor.fetchone()
            if db_res and db_res[1] == name:
                session_raw = "time=%s;admin_id=%s" % (time.time(), name)
                res_data = {
                    "admin_id": db_res[0],
                    "name": db_res[1]
                }
                session_id = hashlib.md5(session_raw.encode()).hexdigest()
                session.set(session_id, json.dumps(res_data), ex=86400)
                res_data["session"] = session_id
                data = res_data

            else:
                message = "账号或密码错误"
                code = -1

        except:
            logging.error(traceback.format_exc())
            db.rollback()
            message = "登录失败"
            code = -1
    return {"message": message, "code": code, "data": data}
