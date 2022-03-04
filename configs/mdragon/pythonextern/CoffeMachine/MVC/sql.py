import sqlite3, pandas as pd, numpy as np
#if we have an excel file


class mysql():
    def __init__(self):
        #self.conn = sqlite3.connect(':memory:')
        self.totalDevice = 0
        self.conn = sqlite3.connect('items.db')
        self.loadData()
        
        self.timeout = 0

    def loadData(self):
        cur = self.conn.cursor()
        chunksize = 10
        df = pd.read_excel('data.xlsx')
        print(df)
        #for chunk in pd.read_excel('data.xlsx'):
        #   chunk.columns = chunk.columns.str.replace(' ', '_') #replacing spaces with underscores for column names
        df.to_sql(name='Table1', con=self.conn, if_exists='replace')
        cur.execute('SELECT * FROM Table1')
        names = list(map(lambda x: x[0], cur.description)) #Returns the column names
        print("Name",names)
        for row in cur:
            self.totalDevice += 1
            print(row)
        cur.close()


    def saveData(self):
        pass

    def getALL(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM Table1')
        names = list(map(lambda x: x[0], cur.description)) #Returns the column names
        cur.close()
        return cur

    def getData(self,id):
        #conn = sqlite3.connect(':memory:')
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM Table1 WHERE id='+id)
        print("cur ",cur)
        data = None
        for row in cur:
            data = row
            print("tro",row[1],row[2],row[3],row[4],row[5])
        cur.close()
        return data

if __name__ == "__main__":
    mysql = mysql()
    mysql.loadData()
    mysql.getData("1")