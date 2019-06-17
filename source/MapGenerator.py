# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 22:41:51 2019

@author: taha
"""
from SentimentFinder import extractSupporterCities
import folium
import pandas as pd
import csv
import json

def drawOnMap(popupText,worldMap,clr,loc):
	"""This function is used to draw a marker on the map with the specified properties

	Args:
		popupText(String): The popuptext that will be shown on the marker
		worldMap(FoliumMapObject): The map that the marker will be added to
		clr(String): The color of the marker
		loc(Tuple): A tuple of two values : latitude and longtitude of the marker

	Returns:
		None
		"""
	folium.Marker(
				location=[loc[0],loc[1]],
				   icon=folium.Icon(color=clr)).add_to(worldMap)

def fillStanceDict(firstSidePoints,secondSidePoints):
	"""This function is used to fill a disctionary that holds each city and the number of
	favs for each standing side.

	The keys of the dictionary are location tuples(latitude & longtitude)
		Args:
			firstSidePoints(List): List of cities for the first side
			secondSidePoints(List): List of cities for the second side
		Returns:
			Dictionary: A new dictionary object with all the cities and the nubmer of favs for
			both sides

	"""
	newDict  = {}
	# value index 0 for akp 1 for chp
	for point in firstSidePoints:
		if point[1] in newDict.keys():
			newDict[point[1]] = (newDict[point[1]][0] + 1,newDict[point[1]][1])
		else:
			newDict[point[1]] = (1,0)

	for point in secondSidePoints:
		if point[1] in newDict.keys():
			newDict[point[1]] =  (newDict[point[1]][0],newDict[point[1]][1]+1)
		else:
			newDict[point[1]] = (0,1)

	return newDict

def fillStanceDictNamesAsKeys(firstSidePoints,secondSidePoints):
	"""This function is used to fill a disctionary that holds each city and the number of
	favs for each standing side.

	The keys of the dictionary are city names
		Args:
			firstSidePoints(List): List of cities for the first side
			secondSidePoints(List): List of cities for the second side
		Returns:
			Dictionary: A new dictionary object with all the cities and the nubmer of favs for
			both sides

	"""
	newDict  = {}
	# value index 0 for akp 1 for chp
	for point in firstSidePoints:
		if point[0] in newDict.keys():
			newDict[point[0]] = (newDict[point[0]][0] + 1,newDict[point[0]][1])
		else:
			newDict[point[0]] = (1,0)

	for point in secondSidePoints:
		if point[0] in newDict.keys():
			newDict[point[0]] =  (newDict[point[0]][0],newDict[point[0]][1]+1)
		else:
			newDict[point[0]] = (0,1)

	return newDict

def generateMapPoints(firstSidePoints,secondSidePoints):
	"""This function is used to generate the points on a map according to datasets for each side

	The resulting map is stored ander "Results" folder as "mapMarks.html"
	Args:
		firstSidePoints(List): List of cities for the first side
		secondSidePoints(List): List of cities for the second side
	Returns:
		None
	"""
	#generates the map with the given points
	print("generating map over here")

	worldMap = folium.Map (location=[38.9637,35.2433], zoom_start=6)

	cityStanceDict = fillStanceDict(firstSidePoints,secondSidePoints)
	akps=[]
	chps=[]
	equals=[]
	for key in cityStanceDict.keys():
		if cityStanceDict[key][0] > cityStanceDict[key][1]:
			akps.append(key)
		elif cityStanceDict[key][1] > cityStanceDict[key][0]:
			chps.append(key)
		else:
			equals.append(key)

	for i in range(len(akps)):
		drawOnMap("akpStayla",worldMap,"orange",akps[i])

	for  i in range(len(chps)):
		drawOnMap("chpStayla",worldMap,"blue",chps[i])

	for i in range(len(equals)):
		drawOnMap("eşillique",worldMap,"red",equals[i])

	worldMap.save("Results/mapMarks.html")

def generateChoroplethMap(cityBoundariesPath,dataPath):
	"""This function is used to generate a chorophlet map according to datasets for each side

	The resulting map is stored ander "Results" folder as "mapChorop.html"
	Args:
		cityBoundariesPath(String): The path to the city boundaries of the Country
		dataPath(String): The path to data

	Returns:
		None

	"""

	x = open(cityBoundariesPath,encoding ="utf-8")
	geoData = x.read().replace("\n","")
	x.close()
	geo_json_data = json.loads(geoData)
	sentimentData = pd.read_csv(dataPath,encoding = "utf-8")

	m  = folium.Map (location=[38.9637,35.2433], zoom_start=6)

	m.choropleth(
			encoding = "utf-8",
			geo_data =geo_json_data,
			name="choropleth",
			data = sentimentData,
			columns = ["City", "SentimentRatio"],
			key_on = "feature.id",
			fill_color = "YlGn",
			fill_opacity = 0.7,
			line_opacity = 0.2,
			legend_name = "AKP standing over all tweets ratio %"
			)

	folium.LayerControl().add_to(m)

	m.save("Results/mapChorop.html")

def generateCitySentimentData(akpPoints,chpPoints):
	""" TBD"""
	cityDict = fillStanceDictNamesAsKeys(akpPoints,chpPoints)

	csvFile1 = open('Data/city_ratio.csv', 'w',encoding = "utf-8")
	csvWriter1 = csv.writer(csvFile1,delimiter = ",")
	csvWriter1.writerow(["City","SentimentRatio"])
	for key in cityDict.keys():
		csvWriter1.writerow([key,
		 (cityDict[key][0]+1)/(cityDict[key][0]+cityDict[key][1]+1)]) # AKP over CHP ratio
	csvFile1.close()


def main():
	"""TBD"""
	print("I am main")
	akpPoints,chpPoints = extractSupporterCities("Data/PreprocessedAkpTweets.csv",
											  "Data/PreprocessedChpTweets.csv")
	generateMapPoints(akpPoints,chpPoints)
	generateCitySentimentData(akpPoints,chpPoints)
	generateChoroplethMap("Data/tr_cities_modified.json","Data/city_ratio.csv")


if __name__ == "__main__":
	main()