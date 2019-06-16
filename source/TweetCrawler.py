# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 19:15:34 2019

@author: taha
"""
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 14:35:26 2019

@author: taha
Geo-Circle that takes Turkey inside
Position: 39.156081,35.322214 Radius: 802.86603km
"""
import tweepy
import logging
import csv
import time
import ssl
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError

NUMBER_OF_THREADS = 5
HISTORYLENGTHINDAYS = 7
WAIT_LIMIT = 1*60
WAIT_CON = 60
MAX_NUM_TWEETS = 10000

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
OAUTH_TOKEN = ""
OAUTH_TOKEN_SECRET = ""

def yieldTweetsHandlingLimits(cursor):
	"""This function is used to yield tweets from Twitter API while handling the API limitations

		Args:
			TweepyCursorObject cursor

		Returns:
			None


	"""
	while True:
		try:
			yield cursor.next()
		except (tweepy.RateLimitError, tweepy.TweepError):
			logging.exception("API limit exceeded, waiting for limit!")
			time.sleep(WAIT_LIMIT)
		except (Timeout, ssl.SSLError, ReadTimeoutError, ConnectionError) as exc:
			logging.exception("Connection timed out. Waiting to reconnect!")
			time.sleep(WAIT_CON)
def pullTweets(api,keywords,writers):
	""" This function is used to pull recent tweets about given topics and store them through given writers

		Args:
			TwitterAPIObject api object
			List keywords
			List CSVWriters

		Returns:
			None

	"""
	for i in range(len(keywords)):
		for tweet in yieldTweetsHandlingLimits(tweepy.Cursor(api.search,q=keywords[i],tweet_mode='extended',geocode= "39.156081,35.322214,802.86603km",count=100, since="2019-06-01").items(MAX_NUM_TWEETS)):
			print (tweet.created_at, tweet.full_text)
			if(tweet.user.location):
				writers[i].writerow([tweet.created_at,tweet.coordinates,tweet.user.location, tweet.full_text])

def setAPIEnvironment(consumerKey,consumerSecret,oauthToken,oauthTokenSecret):
	"""This function is used to initialize the Twitter API

		Args:
			String consumer key for twitter API
			String consumer secret for twitter API
			String oauth token for twitter API
			String oauth token secret for twitter API

		Return:
			TwitterAPI

			"""

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	api = tweepy.API(auth)
	return api





if __name__ == '__main__':
	#Create csv writers
	dir1 = 'Data/chpTweets.csv'
	dir2 = 'Data/akpTweets.csv'

	csvFile1 = open(dir1, 'a',encoding = "utf-8")
	csvWriter1 = csv.writer(csvFile1,delimiter = "\t")

	csvFile2 = open(dir2, 'a',encoding = "utf-8")
	csvWriter2 = csv.writer(csvFile2,delimiter = "\t")

	writers = [csvWriter1,csvWriter2]

	keywords = ["chp","akp"]

	api = setAPIEnvironment(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	pullTweets(api,keywords,writers)


#					tweet = api.get_status(
#				except tweepy.TweepError as e:
#					print(e)
#					if(e.api_code==88):
#						print("trying again")
#						continue
#					else:
#						break








