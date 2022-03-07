import serial

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu


#PORT = '/dev/ttyp5'
import serial as ser
import serial.tools.list_ports as prtlst

"""
File "/home/mwork/.local/lib/python3.7/site-packages/modbus_tk/modbus_rtu.py", line 46, in parse_response
    raise ModbusInvalidResponseError("Response length is invalid {0}".format(len(response)))
modbus_tk.exceptions.ModbusInvalidResponseError: Response length is invalid 0



"""


class modbuspull():
    def __init__(self):    
        
        PORT = self.getCOMs()
        print(PORT)
        self.master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        )
        self.settings(2.0)

    def settings(self,set_timeout):
        self.master.set_timeout(set_timeout)
        self.master.set_verbose(True)

    def getCOMs(self):
        COMs=[]
        pts= prtlst.comports()

        for pt in pts:
            if 'USB' in pt[1]: #check 'USB' string in device description
                COMs.append(pt[0])
        return COMs[0]

    def getData(self,id,function,begin,end):
        dataJ = {
            'status':'ok',
            'data':''
        }
        try:
            dataJ['data'] = self.master.execute(id, function, begin, end)
        
            
        except modbus_tk.modbus.ModbusError as e:
            print("%s- Code=%d" % (e, e.get_exception_code()))
            dataJ['status'] = 'ER'
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            print("%s- Code=ModbusInvalidResponseError" % (e))
            #self.master.close()
        except:
            print("other")
        return dataJ
            
        

    def setData(self,id,function,begin,data):
        dataJ = {
            'status':'ok',
            'data':''
        }
        try:
            dataJ['data'] = self.master.execute(id, function, begin, output_value = data)
        except modbus_tk.modbus.ModbusError as e:
            print("%s- Code=%d" % (e, e.get_exception_code()))
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            print("%s- Code=ModbusInvalidResponseError" % (e))
            #self.master.close()
        except:
            print("other")
        return dataJ
            

"""
#supported modbus functions
RAW = 0
READ_COILS = 1
READ_DISCRETE_INPUTS = 2
READ_HOLDING_REGISTERS = 3
READ_INPUT_REGISTERS = 4
WRITE_SINGLE_COIL = 5
WRITE_SINGLE_REGISTER = 6
READ_EXCEPTION_STATUS = 7
DIAGNOSTIC = 8
REPORT_SLAVE_ID = 17
WRITE_MULTIPLE_COILS = 15
WRITE_MULTIPLE_REGISTERS = 16
READ_FILE_RECORD = 20
READ_WRITE_MULTIPLE_REGISTERS = 23
DEVICE_INFO = 43
"""
def main(modbusmaster):
    print(modbusmaster.getData(1,3,0,3))
    print(modbusmaster.setData(1,6,4,500)) ##WRITE_SINGLE_REGISTER
    print(modbusmaster.setData(1,16,4,[100,100,100,100,100,100,100,100])) ##WRITE_MULTIPLE_REGISTERS
if __name__ == "__main__":
    modbus = modbuspull()
    main(modbus)