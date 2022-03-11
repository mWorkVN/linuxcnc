# -*- coding: utf8 -*-

import sys, time ,os
import threading
import queue
from flask import Flask, render_template
from flask import request
from waitress import serve
from until.vnpay import vnpay
import setting.settings as settings
import until.variThreading as variThreading
import subprocess

#import json



class server(threading.Thread):
    
    RunVNPAY = None
    def __init__(self,RunVNPAY):
        self.RunVNPAY = RunVNPAY
        threading.Thread.__init__(self)
        processCommand = ["lsof", "-t", "-i","tcp:8081"]
        processExec = subprocess.Popen(processCommand, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        processesOut, processesErr = processExec.communicate()
        if (len(processesOut) >2):
            processSplit = processesOut.split()   
            killCommand = ["kill",'-9', processSplit[0]]
            sproc = subprocess.Popen(killCommand)
            sproc.wait()
        self.app = Flask(__name__)
        self.init()
        print("Serveer init")

    def run(self):
        self.app.jinja_env.auto_reload = True
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.config['debug'] = True
        serve(self.app, host="0.0.0.0", port=8081)
    
    def init(self):

        @self.app.route("/")
        def hello_world():
            return "<p>Vui Lòng Chờ Khởi Tạo Giao Dịch</p>"

        @self.app.route('/pay',methods=["GET"])
        def log_in():
            if request.method == 'POST':
                pass
            else:
                #vnp = vnpay()
                x =  {"order":"","sts":"","amount":"","time":""}
                order_id = request.args.get('vnp_TxnRef')
                amount = int(request.args.get('vnp_Amount')) / 100
                order_desc = request.args.get('vnp_OrderInfo')
                vnp_TransactionNo = request.args.get('vnp_TransactionNo')
                vnp_ResponseCode = request.args.get('vnp_ResponseCode')
                vnp_TmnCode = request.args.get('vnp_TmnCode')
                vnp_PayDate = request.args.get('vnp_PayDate')
                vnp_BankCode = request.args.get('vnp_BankCode')
                vnp_CardType = request.args.get('vnp_CardType')
                status = ""
                x["order"] = order_id
                x["amount"]= str(amount)
                x["time"]  = vnp_PayDate
                if (self.RunVNPAY.checkKQ(request.args.to_dict())):
                    if vnp_ResponseCode == "00":
                        status = "TT THANH CONG"
                    else:
                        status = "TT ERR"
                    x["sts"]=vnp_ResponseCode
                else:
                    x["sts"]=""
                variThreading.queueVNPAY.put(x)
                return render_template("index.html")