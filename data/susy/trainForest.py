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

sys.path.append('../../code/python')
from RandomForest import RandomForest

def main(argv):
	outPath = "./text"

	print("Loading data")
	#NROWS = 500000
	data = np.genfromtxt("SUSY.csv", delimiter=',')#, max_rows=NROWS)
	X = data[:,1:]
	Y = data[:,0]

	XTrain,XTest,YTrain,YTest = train_test_split(X, Y, test_size=0.25)

	NTrees = [1,50]
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

		with open("text/forest_"+str(ntree)+".json",'w') as outFile:
			outFile.write(forest.str())

		with open("text/forest_"+str(ntree)+"_test.csv", 'w') as outFile:
			for x,y in zip(XTest, YTest):
				line = str(y)
				for xi in x:
					line += "," + str(xi)

				outFile.write(line + "\n")

		print("*** Summary ***")
		print("#Examples\t #Features\t Accuracy\t Avg.Tree Height")
		print(str(len(X)) + "\t" + str(len(XTrain[0])) + "\t" + str(accuracy_score(YTest, YPredicted)) + "\t" + str(forest.getAvgDepth()))

if __name__ == "__main__":
   main(sys.argv[1:])
