#!/usr/bin/env python3

import csv,operator,sys,os
import numpy as np
import os.path
import json
import timeit
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

sys.path.append('../../code/python')
from RandomForest import RandomForest

def readFile(path):
	f = open(path, 'r')
	header = next(f)
	X = []
	Y = []

	for row in f:
		entries = row.replace("\n","").split(";")

		if entries[-1] == 'sitting':
			y = 0
		elif entries[-1] == 'standing':
			y = 1
		elif entries[-1] == 'standingup':
			y = 2
		elif entries[-1] == 'walking':
			y = 3
		elif entries[-1] == 'sittingdown':
			y = 4
		else:
			print("ERROR READING CLASSES:", entries[-1])
		
		x = []
		if entries[1] == 'Man':
			x.append(0)
		else:
			x.append(1)
			
		for e in entries[2:-1]:
			x.append(float(e.replace(",",".")))
		X.append(x)
		Y.append(y)

	return np.array(X), np.array(Y)

def main(argv):
	data = "dataset-har-PUC-Rio-ugulino.csv"
	outPath = "./text"

	X,Y = readFile(data)
	XTrain,XTest,YTrain,YTest = train_test_split(X, Y, test_size=0.25)
	
	NTrees = [25]

	with open("test.csv", 'w') as outFile:
		for x,y in zip(XTest, YTest):
			line = str(y)
			for xi in x:
				line += "," + str(xi)

			outFile.write(line + "\n")

	for ntree in NTrees:
		clf = RandomForestClassifier(n_estimators=ntree, n_jobs=4) 
		print("Fitting model on " + str(len(XTrain)) + " data points")
		clf.fit(XTrain,YTrain)

		print("Testing model on " + str(len(XTest)) + " data points")
		start = timeit.default_timer()

		for i in range(200):
			YPredicted = clf.predict(XTest)
		end = timeit.default_timer()
		print("Confusion matrix:\n%s" % confusion_matrix(YTest, YPredicted))
		print("Accuracy:%s" % accuracy_score(YTest, YPredicted))
		print("Total time: " + str(end - start) + " ms")
		print("Throughput: " + str(len(XTest) / (float(end - start)*1000)) + " #elem/ms")

		print("Saving model to JSON on disk")
		forest = RandomForest.RandomForestClassifier(None)
		forest.fromSKLearn(clf)

		if not os.path.exists("text"):
			os.makedirs("text")

		with open("text/forest_"+str(ntree)+".json",'w') as outFile:
			outFile.write(forest.str())
		
		print("Saving model to PKL on disk")
		joblib.dump(clf, "text/forest_"+str(ntree)+".pkl")

		print("*** Summary ***")
		print("#Examples\t #Features\t Accuracy\t Avg.Tree Height")
		print(str(len(X)) + "\t" + str(len(X[0])) + "\t" + str(accuracy_score(YTest, YPredicted)) + "\t" + str(forest.getAvgDepth()))
		
if __name__ == "__main__":
   main(sys.argv[1:])
