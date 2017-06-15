import pandas as pd
from sklearn.cluster import KMeans
from functions import classify, jsonformat, bubble, ClusterAnalysis, ClusterPlot
import requests

filename = 'json26.json'
df = jsonformat(filename)

#Bubble Chart of historic data

ClusterPlot(df,2)

#KMeans Clustering

data1 = df[['Hour','Speed']]
data1['Vehicle Density'] = bubble(df['Vehicle-Type'])*df['Vehicle Count']
model = KMeans(n_clusters=2,init='k-means++',random_state=99999,tol=0.0001)
model.fit(data1)
data1['Class'] = model.labels_

#KMeans cluster Plot
ClusterPlot(df,model.labels_)
ClusterAnalysis(data1)

'''----------------------------- Weighted Average of Hours -------------------'''
hrs = set(data1['Hour'])
congestion = pd.DataFrame(columns = ['Hour','Weights'])
index = 0
for h in hrs:
    congestion.loc[index] = [h,int(sum(data1[data1['Hour']==h]['Vehicle Density']))]
    index += 1
congestion = congestion.fillna(0)
congestion['Weights'] = [c/sum(congestion['Weights']) for c in congestion['Weights']]


filename = 'jsondump.json'
df = jsonformat(filename)
data2 = df[['Hour','Speed']]
data2['Vehicle Density'] = bubble(df['Vehicle-Type'])*df['Vehicle Count']
labels = classify(data1,data2)

#Neural Net Classification Plot
ClusterPlot(df,labels)
ClusterAnalysis(data2)

hours = set(data2['Hour'])
live = pd.DataFrame(columns = ['Hour','Weights'])
index = 0
for h in hours:
    live.loc[index] = [h,sum(labels*data2[data2['Hour']==h]['Vehicle Density'])*float(congestion[congestion['Hour']==h]['Weights'])]
    index+=1

live['Weights'] = [c/sum(live['Weights']) for c in live['Weights']]


url_left = 'http://192.168.43.98:5000/left'
url_center = 'http://192.168.43.98:5000/center'


if(sum(live['Weights'])>0.5):
    print('Congestion Detected')
    response = requests.get(url_left)
else:
    print('Congestion threshold not reached')
    response = requests.get(url_center)
