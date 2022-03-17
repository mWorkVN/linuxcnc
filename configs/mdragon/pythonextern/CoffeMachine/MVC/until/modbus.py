import serial

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import serial.tools.list_ports as prtlst


class ModbusPull():
    def __init__(self):    
        self.msgError = ''
        self.initCom(1)
        

    def initCom(self,timeout = 0.5):
        PORT = self.getCOMs()
        if self.msgError == 'ok':
            self.master = modbus_rtu.RtuMaster(
                serial.Serial(port=PORT, baudrate=19200, bytesize=8, parity='N', stopbits=1, xonxoff=0)
            )
        else:self.master = None
        self.settings(timeout)
        #self.settings(1.0)

    def settings(self,set_timeout):
        if self.msgError != 'ok': return
        self.master.set_timeout(set_timeout)
        #self.master.set_verbose(True)

    def getCOMs(self):
        COMs=[]
        pts= prtlst.comports()

        for pt in pts:
            if 'USB' in pt[1]: #check 'USB' string in device description
                COMs.append(pt[0])
        try:     
            self.msgError = 'ok'
            return COMs[0]
        except:
            self.msgError = 'NO COM'
            return 0
        
        

    def getData(self,id,function,begin,end):
        dataJ = {
            's':'ok',
            'd':0
        }
        try:
            dataJ['d'] = self.master.execute(id, function, begin, end)          
        except modbus_tk.modbus.ModbusError as e:
            dataJ['s'] = 'er'
            dataJ['d'] = 1
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            dataJ['s'] = 'er'
            dataJ['d'] = 2
            #self.master.close()
        except:
            dataJ['s'] = 'er'
            dataJ['d'] = 3
            print("other")
        return dataJ
            
        

    def setData(self,id,function,begin,data):
        dataJ = {
            's':'ok',
            'd':0
        }
        try:
            dataJ['d'] = self.master.execute(id, function, begin, output_value = data)
        except modbus_tk.modbus.ModbusError as e:
            dataJ['s'] = 'er'
            dataJ['d'] = 1
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            dataJ['s'] = 'er'
            dataJ['d'] = 2
            #self.master.close()
        except:
            dataJ['s'] = 'er'
            dataJ['d'] = 3
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