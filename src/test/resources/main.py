from pandas import DataFrame
from tensorflow.contrib.learn import LinearRegressor
from tensorflow.contrib.layers import real_valued_column
from tensorflow.contrib.learn.python.learn.utils.input_fn_utils import InputFnOps

import numpy
import pandas
import os
import shutil
import tempfile
import tensorflow

def load_csv(name):
	return pandas.read_csv("csv/" + name)

def store_csv(df, name):
	df.to_csv("csv/" + name, index = False)

def store_savedmodel(estimator, serving_input_fn, name):
	savemodel_dir = estimator.export_savedmodel(tempfile.mkdtemp(), serving_input_fn = serving_input_fn, as_text = True)
	savemodel_dir = savemodel_dir.decode("UTF-8")

	if(os.path.isdir("savedmodel/" + name)):
		shutil.rmtree("savedmodel/" + name)
	shutil.move(savemodel_dir, "savedmodel/" + name)	

#
# Regression
#

auto_df = load_csv("Auto.csv")

auto_X = auto_df[["cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year", "origin"]]
auto_y = auto_df["mpg"]

auto_feature_columns = [real_valued_column(column) for column in auto_X.columns]

def auto_input_fn():
	features = {column : tensorflow.constant(auto_X[column].values, dtype = tensorflow.float64, shape = [auto_X[column].size, 1]) for column in auto_X.columns}
	label = tensorflow.constant(auto_y.values, dtype = tensorflow.float64, shape = [auto_y.size, 1])
	return features, label

def auto_serving_input_fn():
	feature_placeholders = {column : tensorflow.placeholder(dtype = tensorflow.float64, shape = [None, 1], name = column) for column in auto_X.columns}
	features = {column : tensor for column, tensor in feature_placeholders.items()}
	label = None
	return InputFnOps(features, label, feature_placeholders)

def build_auto(estimator, name):
	estimator.fit(input_fn = auto_input_fn, steps = 2000)

	mpg = DataFrame(estimator.predict(input_fn = auto_input_fn, as_iterable = False), columns = ["_target"])
	store_csv(mpg, name + ".csv")

	store_savedmodel(estimator, auto_serving_input_fn, name)

build_auto(LinearRegressor(feature_columns = auto_feature_columns), "LinearRegressionAuto")