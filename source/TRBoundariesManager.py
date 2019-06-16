# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 16:21:56 2019

@author: taha
"""

import json

x = open("Data/tr_cities.json",encoding ="utf-8")
data = x.read().replace("\n","")
x.close()
jsonData = json.loads(data)

for feature in jsonData["features"]:
	feature["id"] = feature["properties"]["name"].lower()

newFile = open("Data/tr_cities_modified.json","w")
json.dump(jsonData,newFile)
newFile.close()
