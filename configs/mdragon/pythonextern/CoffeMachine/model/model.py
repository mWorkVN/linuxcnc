class Model(QObject):
    def __init__(self):
        self.username = ""
        self.password = ""
        robot=RobotControl()
        self.machine = Machine(robot)
        #              name     ,        giá,   số lượng,   file
        item1 = Item('caffe d'  ,      15000,    88,  "caffeden.ngc" )
        item2 = Item('caffe s'  ,      20000,    1 ,  "caffesua.ngc")
        item3 = Item('12'       ,      20000,    3 ,  "nuocngot.ngc")
        item4 = Item('23'       ,      10000,    1 ,  "nuocngot.ngc")
        item5 = Item('45'       ,      10000,    3 ,  "nuocngot.ngc")
        item6 = Item('milkshake',      15000,    5 ,  "nuocngot.ngc")

        self.machine.addItem(item1)
        self.machine.addItem(item2)
        self.machine.addItem(item3)
        self.machine.addItem(item4)
        self.machine.addItem(item5)
        self.machine.addItem(item6)

    def verify_password(self):
        return self.username == "USER" and self.password == "PASS"

    def runmachine(self):
        self.machine.run()




