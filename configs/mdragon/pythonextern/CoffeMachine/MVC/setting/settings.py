TIME_CHECK_NGUYENLIEU = 15

VNPAY_RETURN_URL = 'http://localhost:8081/pay'  # get from config
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'  # get from config
VNPAY_API_URL = 'https://sandbox.vnpayment.vn/merchant_webapi/merchant.html'
VNPAY_TMN_CODE = 'AGM2PN7X'  # Website ID in VNPAY System, get from config
VNPAY_HASH_SECRET_KEY = 'RTREZNSKLNWYXEYYFDYUEZEZXJYYPOVC'  # Secret key for create checksum,get from config

VNPAY_ERROR_CODE={
  "07": "Ford",

"07":"Trừ tiền thành công. Giao d?ch b? nghi ng?",
"09":"Th?/Tài kho?n c?a khách hàng chua dang ký d?ch v? InternetBanking t?i ngân hàng.",
"10":"Khách hàng xác th?c thông tin th?/tài kho?n không dúng quá 3 l?n",
"11":"Ðã h?t h?n ch? thanh toán. Xin quý khách vui lòng th?c hi?n l?i giao d?ch.",
"12":"Th?/Tài kho?n c?a khách hàng b? khóa.",
"13":"Quý khách nh?p sai m?t kh?u xác th?c giao d?ch (OTP). Xin quý khách vui lòng th?c hi?n l?i giao d?ch.",
"24":"Khách hàng hủy giao dịch",
"51":"Tài kho?n c?a quý khách không d? s? du d? th?c hi?n giao d?ch.",
"65":"Tài khoản c?a Quý khách dã vu?t quá h?n m?c giao d?ch trong ngày.",
"75":"Ngân hàng thanh toán dang bảo trì.",
"79":"KH nh?p sai m?t kh?u thanh toán quá s? l?n quy d?nh. Xin quý khách vui lòng th?c hi?n l?i giao d?ch",
"99":"Các l?i khác (l?i còn l?i, không có trong danh sách mã l?i dã li?t kê)"
}