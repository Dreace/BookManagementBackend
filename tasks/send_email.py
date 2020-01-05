# from redis_connect import redis_session as session
import locale
import logging
import math
import smtplib
import time
import traceback
from email.mime.text import MIMEText

from mysql_connect import book_cursor as cursor, book_connect as db
from scheduler import scheduler

locale.setlocale(locale.LC_CTYPE, 'chinese')
mail_host = 'smtp.mxhichina.com'
mail_user = 'info@dreace.top'
mail_pass = '&fNF&U7BPAHZmy2A'
sender = 'info@dreace.top'


def send_email():
    sql = "SELECT bookslip.card_id,email,GROUP_CONCAT(bookslip.book_id) FROM bookslip,card,book WHERE is_repaid = 0" \
          " AND due_time-UNIX_TIMESTAMP() < 604800 AND bookslip.card_id=card.card_id AND bookslip.book_id=book.book_id " \
          "GROUP BY card_id"
    db.ping(reconnect=True)
    cursor.execute(sql)
    db_res = cursor.fetchall()
    for res in db_res:
        book_id_list = res[2].split(',')
        content = ""
        time_now = int(time.time())
        for index, book_id in enumerate(book_id_list):
            sql = "SELECT `name`,borrowing_time,due_time from bookslip,book WHERE bookslip.book_id='%s'" \
                  " AND book.book_id=bookslip.book_id AND is_repaid=0" % book_id
            cursor.execute(sql)
            db_res = cursor.fetchone()
            borrowing_time = time.strftime(u"%Y年%m月%d日", time.localtime(db_res[1]))
            due_time = time.strftime(u"%Y年%m月%d日", time.localtime(db_res[2]))
            days = math.ceil((db_res[2] - time_now) / 86400)
            if days > 0:
                content += "%s.《%s》于%s借阅，将于%s（%s天后）逾期\n" % (index + 1, db_res[0], borrowing_time, due_time, days)
            else:
                content += "%s.《%s》于%s借阅，已于%s（%s天前）逾期\n" % (index + 1, db_res[0], borrowing_time, due_time, -days)
        content += "请及时到馆归还书籍"
        message = MIMEText(content, 'plain', 'utf-8')
        message['Subject'] = '您有 %s 本借阅书籍即将（已）逾期' % len(book_id_list)
        message['From'] = sender
        message['To'] = res[1]

        try:
            smtp = smtplib.SMTP()
            smtp.connect(mail_host, 25)
            smtp.login(mail_user, mail_pass)
            smtp.sendmail(sender, [res[1]], message.as_string())
            smtp.quit()
            logging.info("%s 邮件发送成功" % res[1])
        except smtplib.SMTPException as e:
            logging.info("%s 邮件发送失败" % res[1])
            logging.error(traceback.format_exc())


scheduler.add_job(send_email, 'cron', hour=12)
# # scheduler.add_job(send_email, 'interval', seconds=10)
# scheduler.add_job(send_email)
