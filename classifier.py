# -*- coding: utf-8 -*-
"""
Created on Fri May  5 14:55:29 2017

@author: 212601212
"""

from sklearn.neural_network import MLPClassifier

def classify(d):
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5,2),random_state=1)
    array = clf.fit(d['Hour','Speed','Vehicle Density'],d['Class'])
    return array
