# -*- coding: utf-8 -*-
"""
This module is aimed to train a sentiment finder through an already existing data before and
using the trained model make predictions on the sentiments of the newly crawled tweets.

The main functionality of this module is that it gives the necessary model to make predictins on
the sentiments of the given tweets.

"""
import csv
import sys
from sklearn import preprocessing
from sklearn.naive_bayes import GaussianNB


maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

SENT_THRESHOLD = 0.7

def filter(string):
	return string[string.index(',')+1:string.index('>')]

def generateFeatureList(tweetList):
	"""This function is used for generating the word features given all the tweet data

	Args:
		 tweetList(List): tweets
	Returns:
		List: feature list

		"""
	featureList = []
	counter = 0
	for tweet in tweetList:
		words = tweet.split(' ')
		for word in words:
			counter = counter + 1
			if word not in featureList:
				featureList.append(word)
	return featureList

def extractTweets(filePath):
	"""This function is used to extract tweets given the csv formatted training data

	Args:
		filePath(String): path to the training data
	Returns:
		List: tweets exctracted from the training data
		"""
	tweets = []
	with open(filePath,encoding = 'utf-8') as csvfile:
		fields=['TweetNo','IDfromTwitterAPI','Date','Content']
		tweetDict = csv.DictReader(csvfile,fieldnames=fields ,delimiter= "\t")
		for row in tweetDict:
			tweet = (row['Content'])
			tweets.append(tweet)
	tweets.pop(0)#Definitive text not data
	return tweets

def extractTweetSentiments(filePath):
	"""This function is used to exctract the sentiments of the tweets from the provided sentiment data

	Args:
		filePath(String): path to tweet Sentiments file
	Returns:
		tuple: tuple containing:
			weakSentiments(List): tweets that are classified something that is neither positive nor negative

			tweetSentiments(List) : list of tweet Sentiments
		"""
	tweetSentiments= []
	index = -1
	listOfWeakSents = []
	with open(filePath) as csvfile:
		fields=['tweetID','neg','net','pos','sarc']
		tweetSents = csv.DictReader(csvfile,fieldnames=fields ,delimiter= "\t")
		for row in tweetSents:
			ID = row['tweetID']
			row['tweetID'] = ID[:ID.index(':')]
			possibleFields = ['neg','net','pos','sarc']
			for field in possibleFields:
				row[field] = filter(row[field])

			if row['tweetID'] != 'TweetNo':
				if float(row["pos"]) >= SENT_THRESHOLD:
					tweetSentiments.append("pos")
				elif float(row["neg"]) >= SENT_THRESHOLD:
					tweetSentiments.append("neg")
				else:
					listOfWeakSents.append(index)
			index +=1
	return tweetSentiments,listOfWeakSents

def trainTestDistribute(chunkID,numChunks,featureVectors,labels):
	""" This function is used to distribute the data to chunks of training and testing

	Args:
		chunkID(int): The index of the initial chunk.
		numChunks(int): The nubmer of chunks.
		featureVectors(List): The list of feature vectors.
		labels(List): The list of labels

	Returns:
		tuple: tuple containing:
			 trainData(List): Training data

			 testData(List): Testing data

			 trainLabels(List): Training labels

			 Labels(List): Testing labels

		"""
	chunkSize = len(featureVectors) // numChunks
	testData = featureVectors[chunkID*chunkSize:(chunkID+1)*chunkSize]
	testLabels = labels[chunkID*chunkSize:(chunkID+1)*chunkSize]
	trainData = featureVectors[0:chunkID*chunkSize]+ featureVectors[(chunkID+1)*chunkSize:]
	trainLabels = labels[0:chunkID*chunkSize] + labels[(chunkID+1)*chunkSize:]

	return trainData,testData,trainLabels,testLabels

def getFeatureVectors(featureList,tweets,feautureToEncodingMap,listOfWeakSents=[]):
	""" This function is used to extract featureList, according to predefined features, from the given list of tweets

	Args:

		featureList(List): List of features
		tweets(List):  List of tweets
		featureToEncodingMap(Map): Mapping of features to their specific encodings
		listOfWeakSents(List): List of weak(non positive or negative) sentiments
	Returns:
		List: List of feature vectors generated from the tweets

		"""
	featureVectors = []
	index = 0
	for tweet in tweets:
		vector = [0] * len(featureList)
		if(index not in listOfWeakSents):
			if(tweet == None):
				featureVectors.append(vector)
				continue
			for word in tweet.split(" "):
				if(word in feautureToEncodingMap.keys()):
					vector[feautureToEncodingMap[word]] = 1
			featureVectors.append(vector)
		index +=1
	return featureVectors

def findPredictionTools(trainingFilePath,tweetSentimetsFilePath):
	""" This function is used to generated the necessary tools to make predictions

	Args:
		trainingFilePath(String): Path to the training data file
		tweetSentimentsFilePath(String): Path to the tweet sentiments data file
	Returns:
		tuple: tuple containing
			bestModel(GaussianNB): Final gaussian naive bayes model

			featureList(List): List of features

			featureToEncodingMap(Dictionary): Mapping from features to encoding
		"""
	tweets = extractTweets(trainingFilePath)
	featureList = generateFeatureList(tweets)
	le = preprocessing.LabelEncoder()
	# Converting string labels into numbers.
	features_encoded=le.fit_transform(featureList)
	feautureToEncodingMap = dict(zip(featureList, features_encoded))

	tweetSentiments,listOfWeakSents = extractTweetSentiments(tweetSentimetsFilePath)

	#Convert tweets to feature vectors
	featureVectors= getFeatureVectors(featureList,tweets,feautureToEncodingMap,listOfWeakSents)

	labels=list(le.fit_transform(tweetSentiments))
	labelEncodingMap = dict(zip(labels,tweetSentiments))

	model = GaussianNB()
	k = 10
	#Do k-folding
	bestScore = 0
	bestModel = None
	for i in range(0,k):
		trainData,testData,trainLabels,testLabels = trainTestDistribute(i,k,featureVectors,labels)

		model.fit(trainData,trainLabels)

		predicted= list(model.predict(testData))
		accuracy = 0
		for i in range(len(predicted)):
			if(predicted[i] == testLabels[i]):
				accuracy +=1
		if accuracy > bestScore:
			bestScore = accuracy
			bestModel = model
	return bestModel,featureList,feautureToEncodingMap

def generatePredictions(bestModel,unlabeledTweets,featureList,feautureToEncodingMap):
	""" This function is used to generate predictions for the given unlabeled tweet data

	Args:
		bestModel(GaussianNB): Final gaussian naive bayes model
		unlabaledTweets(List): The list of tweets to be predicted
		featureList(List): List of features
		featureToEncodingMap(Dictionary): Mapping from features to encoding
	Returns:
		List: sentiment predictions of the given unlabeled tweets
		"""
	featureVectors = getFeatureVectors(featureList,unlabeledTweets,feautureToEncodingMap)
	predictions = list(bestModel.predict(featureVectors))
	return predictions

def extractUnlabeledData(filePath):
	""" This function is used to extract the unlabeled data from the csv file

	Args:
		filePath(String): Path to the file

	Returns:
		List: The list of extracted data"""
	data = []
	with open(filePath,encoding = 'utf-8') as csvfile:
		fields=['Date','Coordinates','LocationName','Content']

		tweetDict = csv.DictReader(csvfile,fieldnames=fields ,delimiter= "\t")

		for row in tweetDict:
			data.append(row)
	return data


def getTweetsFromData(data):
	tweets = []
	for row in data:
		tweets.append(row["Content"])
	return tweets

def appendPredictionsToData(data, predictions):
	for i in range(len(data)):
		data[i]["Prediction"] = predictions[i]
	return data
def generateFavClasses(firstData,secondData):
	"""This function is used to generate the fav classes for both sides from the given datasets

		What it basically does is as following:
		given two tweet sets about opposing ideas, parties etc. it goes
		though all tweets and if the sentiment of the tweet is positive then it is
		added to fav class of the related party otherwise it is added to the fav
		class of the opposing element.

		Args:
			firstData(List) : first data set
			secondData(List) : second data set

		Returns:
			tuple: tuple contains:
				firstFavs(List): List of tweets favoring first idea

				secondFavs(List): List of tweets favoring second idea

			"""
	firstFavs = []
	secondFavs = []

	for row in firstData:
		if row["Prediction"] == 1: # Positive
			firstFavs.append(row["LocationName"])
		else:
			secondFavs.append(row["LocationName"])

	for row in secondData:
		if row["Prediction"] == 1:
			secondFavs.append(row["LocationName"])
		else:
			firstFavs.append(row["LocationName"])

	return firstFavs,secondFavs

def filterTheCityNames(dataList):
	"""This function is used to filter the names of the user locations

		Since the user location field twitter provides is a free text field that
		a user can write anything there is a need to first filter the ones
		that actually belong to a place in Turkey. This function does that by trying
		to find a Turkish city name as a substring in the location name of the user.

		Args:
			dataList(List): List of tweet data along with the other information about the tweet and the user

		Returns:
			List: new list of data with city names filtered
			"""
	cityNamesList = []
	cityCoordinates = []
	cityNamesSetList = []
	with open("Data/tr.csv",encoding = 'utf-8') as csvfile:
		fields=['city','lat','long','country',"iso2","admin","capital","population","population_proper"]
		tweetDict = csv.DictReader(csvfile,fieldnames=fields ,delimiter= ",")
		rowCount = 0
		for row in tweetDict:

			if(rowCount == 0):
				rowCount +=1
				continue
			rowCount +=1

			if(row["capital"] == None):
				continue

			if row["capital"].strip() == "admin" or row["capital"].strip() == "primary":
				cityNamesList.append(row["city"].lower().strip())
				cityCoordinates.append((float(row["lat"]),float(row["long"])))
				cityNamesSetList.append(set(row["city"].lower().strip()))

	newDataList = []
	for i in range(len(dataList)):
		cityCandidate = str(dataList[i].lower().strip())
		for j in range(len(cityNamesList)):
			cityName = cityNamesList[j]
			index = cityCandidate.find(cityName)
			if index != -1:
				newDataList.append((cityName,cityCoordinates[j]))
				break
	return newDataList

def extractSupporterCities(file1,file2):
	"""This function is used to exctract the cities that support the first and the second idea as two separate lists.

	Args:
		file1(String): Path to the tweet data of the first idea
		file2(String): Path to the tweet data of the second idea

	Returns:
		tuple: tuple contains:
			firstFavs(List): cities that support the first idea
			secondFavs(List): cities that support the second idea
		"""
	#file1 -> "Data/PreprocessedAkpTweets.csv"
	#file2 -> "Data/PreprocessedChpTweets.csv"
	trainingFilePath = "Data/preprocessedTweets.csv"
	tweetSentimentsFilePath ="Data/tweetSent.csv"
	bestModel,featureList,feautureToEncodingMap = findPredictionTools(trainingFilePath,tweetSentimentsFilePath)
	#AKP predictions
	firstData = extractUnlabeledData(file1)
	firstDataTweets = getTweetsFromData(firstData)
	firstPredictions = generatePredictions(bestModel,firstDataTweets,featureList,feautureToEncodingMap)
	firstData = appendPredictionsToData(firstData,firstPredictions)

	secondData = extractUnlabeledData(file2)
	secondDataTweets = getTweetsFromData(secondData)
	secondPredictions = generatePredictions(bestModel,secondDataTweets,featureList,feautureToEncodingMap)
	secondData = appendPredictionsToData(secondData,secondPredictions)

	firstFavs, secondFavs= generateFavClasses(firstData,secondData)
	firstFavs = filterTheCityNames(firstFavs)
	secondFavs = filterTheCityNames(secondFavs)
	return firstFavs,secondFavs

#a,b = extractSupporterCities("Data/PreprocessedAkpTweets.csv","Data/PreprocessedChpTweets.csv")









