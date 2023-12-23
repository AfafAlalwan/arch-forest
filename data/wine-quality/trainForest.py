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
import joblib

sys.path.append('../../code/python')
from RandomForest import RandomForest

def main(argv):
	outPath = "./text"
	
	red = np.genfromtxt("winequality-red.csv", delimiter=';', skip_header=1)
	white = np.genfromtxt("winequality-white.csv", delimiter=';', skip_header=1)
	X = np.vstack((red[:,:-1],white[:,:-1]))
	Y = np.concatenate((red[:,-1], white[:,-1]))
	# NOTE: It seems, that SKLEarn produces an internal mapping from 0-(|Y| - 1) for classification
	# 		For some reason I was not able to extract this mapping from SKLearn ?!?!
	Y = Y-min(Y)
	print(Y)
	print(min(Y))
	print(max(Y))
	XTrain,XTest,YTrain,YTest = train_test_split(X, Y, test_size=0.25)

	with open("test.csv", 'w') as outFile:
		for x,y in zip(XTest, YTest):
			line = str(y)
			for xi in x:
				line += "," + str(xi)

			outFile.write(line + "\n")

	NTrees = [1]
	for ntree in NTrees:
		clf = RandomForestClassifier(n_estimators=ntree, n_jobs=4) 
		print("Fitting model on " + str(len(XTrain)) + " data points")
		clf.fit(XTrain,YTrain)

		print("Testing model on " + str(len(XTest)) + " data points")
		start = timeit.default_timer()
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

		loadedForest = RandomForest.RandomForestClassifier(None)
		loadedForest.fromJSON("text/forest_"+str(ntree)+".json")
		Y1 = clf.predict(XTest)
		Y2 = forest.predict(XTest)
		Y3 = loadedForest.predict(XTest)
		for y2,y3 in zip(Y2,Y3):
			if (y2 != y3):
				print("y2=",y2,"  ", "y3=",y3)

		print("\tAccuracy SK:%s" % accuracy_score(YTest, Y1))
		print("\ttargetAcc SK: %s" % sum(Y1 == YTest))
		print("\tAccuracy MY:%s" % accuracy_score(YTest, Y2))
		print("\ttargetAcc MY: %s" % sum(Y2 == YTest))

		print("Saving model to PKL on disk")
		joblib.dump(clf, "text/forest_"+str(ntree)+".pkl")
		
		print("*** Summary ***")
		print("#Examples\t #Features\t Accuracy\t Avg.Tree Height")
		print(str(len(X)) + "\t" + str(len(X[0])) + "\t" + str(accuracy_score(YTest, YPredicted)) + "\t" + str(forest.getAvgDepth()))
		
if __name__ == "__main__":
   main(sys.argv[1:])
