from functools import reduce
import operator, json, time, itertools,datetime, xlsxwriter
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

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
        #timestamp = datetime.datetime.fromtimestamp(getFromDict(vehicles,['timestamp'])/1000.0).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = mdate.epoch2num(getFromDict(vehicles,['timestamp'])/1000.0)
        #hour = datetime.datetime.fromtimestamp(getFromDict(vehicles,['timestamp'])/1000.0).strftime('%H')
        #print (hour)
        index += 1
        df.loc[index] = [vtype,speed,vcount,timestamp]
        #print(df.loc[index])
        if (index == 5000):
            break

'''
#To save the filtered reading into a file

writer = pd.ExcelWriter('TrafficData.xlsx',engine='xlsxwriter')
df.to_excel(writer,'Sheet1')
writer.save()
'''

date_fmt = '%d-%m-%y %H:%M:%S'

# Use a DateFormatter to set the data to the correct format.
date_formatter = mdate.DateFormatter(date_fmt)

'''
#Scatter PLot Working - Bubble Scatter isn't

fig, ax = plt.subplots()
ax.plot_date(df['Time Stamp'],df['Speed'])
ax.xaxis.set_major_formatter(date_formatter)
fig.autofmt_xdate()
plt.show()
'''

#Bubble Chart

fig = plt.figure()
ax = fig.add_subplot(111)
scat = ax.scatter(x=df['Time Stamp'], y=df['Speed'], s=df['Vehicle Count']*2, c=df['Speed'],
label='Traffic Density')
ax.xaxis.set_major_formatter(date_formatter)
fig.autofmt_xdate()
plt.xlabel('Time Stamp')
plt.ylabel('Speed of Vehicle')
plt.show()