from functools import reduce
import operator, json, time, itertools,datetime, xlsxwriter
import pandas as pd 
import matplotlib.pyplot as plt

def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)

data = json.load(open('jsondump.json'))
df = pd.DataFrame(columns=('Vehicle-Type','Speed','Vehicle Count','Time Stamp'))

index = 0

for events, subdict in data.items():
    print (events)
    for vehicles in itertools.chain(subdict):
        vtype = getFromDict(vehicles,['properties','vehicle-type'])
        speed = getFromDict(vehicles,['measures',1,'value'])
        vcount = getFromDict(vehicles,['measures',2,'value'])
        timestamp = datetime.datetime.fromtimestamp(getFromDict(vehicles,['timestamp'])/1000.0).strftime('%Y-%m-%d %H:%M:%S')
        index += 1
        df.loc[index] = [vtype,speed,vcount,timestamp]
        #print(df.loc[index])
        if (index == 1000):
            break

'''
#To save the filtered reading into a file

writer = pd.ExcelWriter('TrafficData.xlsx',engine='xlsxwriter')
df.to_excel(writer,'Sheet1')
writer.save()
'''

df.plot.scatter(x='Time Stamp', y='Speed', s=df['Vehicle Count']*200)