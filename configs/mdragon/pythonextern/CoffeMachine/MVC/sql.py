import sqlite3, pandas as pd, numpy as np
#if we have an excel file
conn = sqlite3.connect(':memory:')
cur = conn.cursor()
chunksize = 10
df = pd.read_excel('data.xlsx')

print(df)
#for chunk in pd.read_excel('data.xlsx'):
#   chunk.columns = chunk.columns.str.replace(' ', '_') #replacing spaces with underscores for column names
df.to_sql(name='Table1', con=conn, if_exists='append')
cur.execute('SELECT * FROM Table1')
names = list(map(lambda x: x[0], cur.description)) #Returns the column names
print("Name",names)
for row in cur:
    print(row)
cur.close()
cur = conn.cursor()
cur.execute('SELECT * FROM Table1 WHERE id=2')
print("cur ",cur)
for row in cur:
    print("tro",row[1],row[2],row[3],row[4],row[5])
cur.close()