class ControlVal():
    __slots__ = ['valveModbus','stateModbus']
    def __init__(self,valveModbus):
        self.valveModbus=valveModbus
        self.stateModbus = 'ok'
        self.valveModbus.settings(0.1)
    def run(self):
        pass

    def getData(self,id,function,begin,end):
        value = self.valveModbus.getData(id, function, begin, end)
        self.stateModbus = value['s']     
        return value        

    def setData(self,id,function,begin,data):
        value = self.valveModbus.setData(id, function, begin,  data)
        if value['s'] == 'ok':
            return True
        else: 
            self.stateModbus = 'er'
            return False

    def checkError(self,id):
        value = self.valveModbus.getData(id, 1, 0, 1)
        self.stateModbus = value['s']          
