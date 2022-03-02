import sys, time ,os
import threading

from vnpay import vnpay
try: 
    import queue
except ImportError: #py2
    import Queue as queue

from flask import Flask, render_template
from flask import request
from waitress import serve
import settings
import variThreading
import json

app = Flask(__name__)
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/pay',methods=["GET"])
def log_in():
    if request.method == 'POST':
        pass
    else:
        vnp = vnpay()
        print("data")
        x =  {"order":"","sts":""}
        order_id = request.args.get('vnp_TxnRef')
        print("order_id",order_id)
        amount = int(request.args.get('vnp_Amount')) / 100
        print("amount",str(amount))
        order_desc = request.args.get('vnp_OrderInfo')
        print("order_desc",order_desc)
        vnp_TransactionNo = request.args.get('vnp_TransactionNo')
        print("vnp_TransactionNo",vnp_TransactionNo)
        vnp_ResponseCode = request.args.get('vnp_ResponseCode')
        print("vnp_ResponseCode",vnp_ResponseCode)
        vnp_TmnCode = request.args.get('vnp_TmnCode')
        print("vnp_TmnCode",vnp_TmnCode)
        vnp_PayDate = request.args.get('vnp_PayDate')
        print("vnp_PayDate",vnp_PayDate)
        vnp_BankCode = request.args.get('vnp_BankCode')
        print("vnp_BankCode",vnp_BankCode)
        vnp_CardType = request.args.get('vnp_CardType')
        print("vnp_CardType",vnp_CardType)
        vnp.responseData = request.args.to_dict()
        status = ""
        print("aaa")
        x["order"]=order_id
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                status = "TT THANH CONG"
                print("TT THANH CONG")
            else:
                status = "TT ERR"
                print("TT Error")
            x["sts"]=vnp_ResponseCode
        else:
            x["sts"]=""
            print("eeee")
        variThreading.queueVNPAY.put(x)
        return "<p>Hello, World! " + status + "</p>"



class server(threading.Thread):
    
    global app
    def __init__(self):
        threading.Thread.__init__(self)
        print("Serveer init")

    def run(self):
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['debug'] = True
        serve(app, host="0.0.0.0", port=8081)
    
    def getstatus(self):
        return "aaa"
