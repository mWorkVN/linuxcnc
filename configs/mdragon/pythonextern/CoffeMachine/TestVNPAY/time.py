
from datetime import datetime
import pytz


# D?ng native date
date_time_now = datetime.now()
dateCheck=date_time_now.strftime('%Y%m%d%H%M%S')

print(date_time_now)

UTC = pytz.utc
date_time_utc_now = UTC.localize(date_time_now)
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
date_time_vntz_now = date_time_utc_now.astimezone(VN_TZ)


dateCheck=date_time_vntz_now.strftime('%Y%m%d%H%M%S')
print(dateCheck)