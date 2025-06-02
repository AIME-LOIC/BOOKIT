import json
import os
date={"name":"aime","class":"l3"};
if os.path.exists('db.json'):
        with open('db.json') as file:
            try:
                buses = json.load(file)
            except:
                buses=[]
else:
       buses = []
       buses.append(date)
with open('db.json','w') as file:

    json.dump(buses,file,indent=4)


