# -*- coding: utf8 -*-

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
        vnp.responseData = request.args.to_dict()
        status = ""
        x["order"]=order_id
        x["amount"]=str(amount)
        x["time"]=vnp_PayDate
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                status = "TT THANH CONG"
            else:
                status = "TT ERR"
            x["sts"]=vnp_ResponseCode
        else:
            x["sts"]=""
        variThreading.queueVNPAY.put(x)
        return render_template("payment_return.html", title= "Kết Quả Thanh toán",
                            result= "Thành công", order_id= order_id,
                            amount= amount,
                            order_desc=order_desc,
                            vnp_TransactionNo= vnp_TransactionNo,
                            vnp_ResponseCode= vnp_ResponseCode)




class createVNPAY():
    def __init__(self):
        pass
    def payment(self,price,orderID):
        order_type ='1'
        amount = price
        order_desc = 'Testr'
        bank_code = ''
        language = 'vn'
        ipaddr = '127.0.0.1'
        # Build URL Payment
        
        timebegin = datetime.datetime.now()
        time_change = datetime.timedelta(minutes=1)
        timeend = timebegin + time_change
        order_id = orderID
        self.idCheck = order_id
        self.dateCheck=timebegin.strftime('%Y%m%d%H%M%S')
        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'AGM2PN7X'
        vnp.requestData['vnp_Amount'] = amount * 100
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = self.idCheck
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type
        # Check language, default: vn
        if language and language != '':
            vnp.requestData['vnp_Locale'] = language
        else:
            vnp.requestData['vnp_Locale'] = 'vn'
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData['vnp_BankCode'] = bank_code
        
        vnp.requestData['vnp_CreateDate'] = self.dateCheck   # 20150410063022
        vnp.requestData['vnp_ExpireDate'] = timeend.strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
        print(vnpay_payment_url)
        self.machine.view.webView.load(QUrl(vnpay_payment_url))

    def query(self):
        vnp = vnpay()
        vnp.requestData = {}
        vnp.requestData['vnp_Command'] = 'querydr'
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
        vnp.requestData['vnp_TxnRef'] = self.idCheck
        vnp.requestData['vnp_OrderInfo'] = 'Kiem tra ket qua GD OrderId:' + self.idCheck
        vnp.requestData['vnp_TransDate'] = self.dateCheck  # 20150410063022
        vnp.requestData['vnp_CreateDate'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
        vnp.requestData['vnp_IpAddr'] = '127.0.0.1'
        requestUrl = vnp.get_payment_url(settings.VNPAY_API_URL, settings.VNPAY_HASH_SECRET_KEY)
        responseData = urllib.request.urlopen(requestUrl).read().decode()
        print('RequestURL:' + requestUrl)
        print('VNPAY Response:' + responseData)
        if 'Request_is_duplicate' in responseData:
            return
        data = responseData.split('&')
        for x in data:
            tmp = x.split('=')
            if len(tmp) == 2:
                vnp.responseData[tmp[0]] = urllib.parse.unquote(tmp[1]).replace('+', ' ')
        print('Validate data from VNPAY:' + str(vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY)))




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
