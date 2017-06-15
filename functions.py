# -*- coding: utf-8 -*-
"""
Created on Fri May  5 14:55:29 2017

@author: Sanket Goutam
"""

from functools import reduce
import operator, json, itertools,datetime #time, xlsxwriter
import pandas as pd 
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.neural_network import MLPClassifier
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
import numpy as np

def classify(d1,d2):
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5,2),random_state=1)
    clf.fit(d1[['Hour','Speed','Vehicle Density']],d1['Class'])
    array = clf.predict(d2[['Hour','Speed','Vehicle Density']])
    return array

def bubble(vehicle_types):
    iter_item = 0
    bubble_size = list()
    for item in vehicle_types:
        if item == 'car':
            bubble_size.append(5)
        elif item == 'truck':
            bubble_size.append(10)
        elif item == 'motorcycle':
            bubble_size.append(1)
        elif item == 'other':
            bubble_size.append(3)
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

def ClusterAnalysis(data1):
    labels = []
    sil_coeffs = [] 
    for n_cluster in range(2, 10):
        kmeans = KMeans(n_clusters=n_cluster).fit(data1)
        label = kmeans.labels_
        labels.append(label)
        sil_coeff = metrics.silhouette_score(data1, label, metric='euclidean')
        sil_coeffs.append(sil_coeff)
        print("For n_clusters={}, The Silhouette Coefficient is {}".format(n_cluster, sil_coeff))

def jsonformat(filename):
    data = json.load(open(filename))
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
            if (index > 3000):
                break
    return df

def ClusterPlot(df,labels):
    colormap = np.array(['lime','red','royalblue'])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x=df['Hour'], y=df['Speed'], s=df['Vehicle Count']*bubble(df['Vehicle-Type']),
                      c=colormap[labels],label='Traffic Density')
    plt.xlabel('Time Stamp (Hrs)')
    plt.ylabel('Speed of Vehicle (mps)')
    plt.show()