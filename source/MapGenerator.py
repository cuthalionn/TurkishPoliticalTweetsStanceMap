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
	""" Draws on map """
	folium.Marker(
				location=[loc[0],loc[1]],
				   icon=folium.Icon(color=clr)).add_to(worldMap)

def fillStanceDict(akpPoints,chpPoints):
	newDict  = {}
	# value index 0 for akp 1 for chp
	for point in akpPoints:
		if point[1] in newDict.keys():
			newDict[point[1]] = (newDict[point[1]][0] + 1,newDict[point[1]][1])
		else:
			newDict[point[1]] = (1,0)

	for point in chpPoints:
		if point[1] in newDict.keys():
			newDict[point[1]] =  (newDict[point[1]][0],newDict[point[1]][1]+1)
		else:
			newDict[point[1]] = (0,1)

	return newDict

def fillStanceDictNamesAsKeys(akpPoints,chpPoints):
	newDict  = {}
	# value index 0 for akp 1 for chp
	for point in akpPoints:
		if point[0] in newDict.keys():
			newDict[point[0]] = (newDict[point[0]][0] + 1,newDict[point[0]][1])
		else:
			newDict[point[0]] = (1,0)

	for point in chpPoints:
		if point[0] in newDict.keys():
			newDict[point[0]] =  (newDict[point[0]][0],newDict[point[0]][1]+1)
		else:
			newDict[point[0]] = (0,1)

	return newDict

def generateMapPoints(akpPoints,chpPoints):
	#generates the map with the given points
	print("generating map over here")

	worldMap = folium.Map (location=[38.9637,35.2433], zoom_start=6)

	cityStanceDict = fillStanceDict(akpPoints,chpPoints)
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

	worldMap.save("Results/map.html")

def generateChoroplethMap():
	x = open("Data/tr_cities_modified.json",encoding ="utf-8")
	geoData = x.read().replace("\n","")
	x.close()
	geo_json_data = json.loads(geoData)
	sentimentData = pd.read_csv("Data/city_ratio.csv",encoding = "utf-8")

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

	m.save("Results/map2.html")

def generateCitySentimentData(akpPoints,chpPoints):
	cityDict = fillStanceDictNamesAsKeys(akpPoints,chpPoints)

	csvFile1 = open('Data/city_ratio.csv', 'w',encoding = "utf-8")
	csvWriter1 = csv.writer(csvFile1,delimiter = ",")
	csvWriter1.writerow(["City","SentimentRatio"])
	for key in cityDict.keys():
		csvWriter1.writerow([key,
		 (cityDict[key][0]+1)/(cityDict[key][0]+cityDict[key][1]+1)]) # AKP over CHP ratio
	csvFile1.close()


def main():
	print("I am main")
	akpPoints,chpPoints = extractSupporterCities("Data/PreprocessedAkpTweets.csv",
											  "Data/PreprocessedChpTweets.csv")
	generateMapPoints(akpPoints,chpPoints)
	generateCitySentimentData(akpPoints,chpPoints)
	generateChoroplethMap()


if __name__ == "__main__":
	main()