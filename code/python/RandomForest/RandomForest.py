import concurrent.futures as cf
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from multiprocessing import Pool
from sklearn.tree import _tree

import numpy as np

from .ClassificationTrees import ArchTree
from .RegressionTrees import ExtraRegressionTree
from .RegressionTrees import GradientRegressionTree

from .Forest import Forest

class RandomForest(Forest):
	def __init__(self, numTrees = 1, basetype = "Extra", bootstrap_sample = False, min_splits = 2):
		super().__init__()
		self.numTrees = numTrees
		self.basetype = basetype
		self.bootstrap_sample = bootstrap_sample
		self.min_splits = min_splits

	def _fit(self,indices):
		tree = self.generateTree()
		tree.fit(self.X[indices],self.Y[indices])
		return tree

	def fit(self,X,Y):
		self.X = X
		self.Y = Y
		indices = []
		for i in range(0, self.numTrees):
			if self.bootstrap_sample:
				indices.append(np.random.choice(len(X), len(X), replace=True))
			else:
				indices.append([i for i in range(len(X))])

		# do the actual training
		pool = Pool(1) # TODO: DO MORE HERE LATER
		self.trees = pool.map(self._fit, indices)

	def predict(self,X):
		raise NotImplementedError("This function should not be called directly, but only by a sub-class")
	
	def generateTree(self):
		raise NotImplementedError("This function should not be called directly, but only by a sub-class")

class RandomForestClassifier(RandomForest):
	def __init__(self, numTrees = 1, basetype = "Arch", bootstrap_sample = False, min_splits = 2):
		super().__init__()
		self.numTrees = numTrees
		self.basetype = basetype
		self.bootstrap_sample = bootstrap_sample
		self.min_splits = min_splits

	def generateTree(self):
		if self.basetype == "Arch":
			return ArchTree(self.min_splits)
		else:
			raise NotImplementedError("Could not found given tree class")

	def predict(self,X):
		YPred = []
		for x in X:
			classes = {}
			for t in self.trees:
				ypred = t.predict([x])[0]
				if ypred in classes:
					classes[ypred] += 1
				else:
					classes[ypred] = 1
			ypred = max(classes, key=classes.get)
			YPred.append(ypred)
		return YPred

class RandomForestRegressor(RandomForest):
	def __init__(self, numTrees = 1, basetype = "Extra", bootstrap_sample = False, min_splits = 2):
		super().__init__(numTrees, basetype, bootstrap_sample, min_splits)

	def generateTree(self):
		if self.basetype == "Extra":
			return ExtraRegressionTree(self.min_splits)
		elif self.basetype == "SGD":
			# TODO Ignore min_splits
			return GradientRegressionTree(self.min_splits)
		else:
			raise NotImplementedError("Could not found given tree class")
		

	def predict(self,X):
		YPred = []
		for x in X:
			y = 0
			for t in self.trees:
				y += t.predict([x])[0]
			YPred.append(y / self.numTrees)
		return YPred