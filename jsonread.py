from functools import reduce
import operator, json, itertools,datetime #time, xlsxwriter
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
#from matplotlib import ticker
from sklearn.cluster import KMeans
from sklearn import metrics
import numpy as np
from classifier import classify

def bubble(vehicle_types):
    iter_item = 0
    bubble_size = list()
    for item in vehicle_types:
        if item == 'car':
            bubble_size.append(4)
        elif item == 'truck':
            bubble_size.append(8)
        elif item == 'motorcycle':
            bubble_size.append(0.5)
        elif item == 'other':
            bubble_size.append(0.1)
        iter_item += 1
    return bubble_size

def pearsonr(x, y):
  # Assume len(x) == len(y)
  n = len(x)
  sum_x = float(sum(x))
  sum_y = float(sum(y))
  sum_x_sq = sum(map(lambda x: pow(x, 2), x))
  sum_y_sq = sum(map(lambda x: pow(x, 2), y))
  psum = sum(map(lambda x, y: x * y, x, y))
  num = psum - (sum_x * sum_y/n)
  den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
  if den == 0: return 0
  return num / den


def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)


def jsonformat():
    data = json.load(open('json26.json'))
    df = pd.DataFrame(columns=('Vehicle-Type','Speed','Vehicle Count','Time Stamp','Hour'))
    
    index = 0
    
    for events, subdict in data.items():
        print (events)
        for vehicles in itertools.chain(subdict):
            vtype = getFromDict(vehicles,['properties','vehicle-type'])
            speed = getFromDict(vehicles,['measures',1,'value'])
            vcount = getFromDict(vehicles,['measures',2,'value'])
            #timestamp = datetime.datetime.fromtimestamp(getFromDict(vehicles,['timestamp'])/1000.0).strptime('%H')
            timestamp = mdate.epoch2num(getFromDict(vehicles,['timestamp'])/1000.0)
            hour = datetime.datetime.fromtimestamp(getFromDict(vehicles,['timestamp'])/1000.0).strftime('%H')
            #print (hour)
            index += 1
            df.loc[index] = [vtype,speed,vcount,timestamp,int(hour)]
            #print(df.loc[index])
            if (index > 2000):
                break
    
    return df

'''
#To save the filtered reading into a file

writer = pd.ExcelWriter('TrafficData.xlsx',engine='xlsxwriter')
df.to_excel(writer,'Sheet1')
writer.save()
'''

'''
#date_fmt = '%d-%m-%y %H:%M:%S'
date_fmt = '%H'
# Use a DateFormatter to set the data to the correct format.
date_formatter = mdate.DateFormatter(date_fmt)
'''
'''
#Scatter PLot Working - V1

fig, ax = plt.subplots()
ax.plot(df['Hour'],df['Speed'])
#ax.xaxis.set_major_formatter(date_formatter)
#fig.autofmt_xdate()
plt.show()
'''

'''vehicle = set(df['Vehicle-Type'])
print(vehicle)
'''

df = jsonformat()

#Bubble Chart

#print(df['Vehicle Count']*bubble(df['Vehicle-Type']))
fig = plt.figure()
ax = fig.add_subplot(111)
scat = ax.scatter(x=df['Hour'], y=df['Speed'], s=df['Vehicle Count']*bubble(df['Vehicle-Type']),label='Traffic Density')
plt.xlabel('Time Stamp (Hrs)')
plt.ylabel('Speed of Vehicle (mps)')
plt.show()

#KMeans Clustering

data1 = df[['Hour','Speed']]
data1['Vehicle Density'] = bubble(df['Vehicle-Type'])*df['Vehicle Count']
model = KMeans(n_clusters=2,init='k-means++',random_state=99999,tol=0.0001)
model.fit(data1)
data1['Class'] = model.labels_
print(metrics.cluster.silhouette_score(data1,model.labels_))
print(metrics.calinski_harabaz_score(data1,model.labels_))

#KMeans cluster Plot
colormap = np.array(['lime','red'])#,'green','black','blue'])
fig = plt.figure()
ax = fig.add_subplot(111)
scat = ax.scatter(x=df['Hour'], y=df['Speed'], s=df['Vehicle Count']*bubble(df['Vehicle-Type']),
                  c=colormap[model.labels_],label='Traffic Density')
plt.xlabel('Time Stamp (Hrs)')
plt.ylabel('Speed of Vehicle (mps)')
plt.show()

'''---------------------------- KMeans cluster analysis -----------------'''
labels = []
sil_coeffs = [] 
for n_cluster in range(2, 11):
    kmeans = KMeans(n_clusters=n_cluster).fit(data1)
    label = kmeans.labels_
    labels.append(label)
    sil_coeff = metrics.silhouette_score(data1, label, metric='euclidean')
    sil_coeffs.append(sil_coeff)
    print("For n_clusters={}, The Silhouette Coefficient is {}".format(n_cluster, sil_coeff))


'''----------------------------- Wieghted Average of Hours -------------------'''
hrs = set(data1['Hour'])
congestion = {}
for h in hrs:
    congestion[h] = sum(data1[data1['Hour']==h]['Vehicle Density'])
congestion = [c/sum(congestion) for c in congestion]
