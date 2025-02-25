#!/usr/bin/env python3
"""
Bot
"""

import urllib.request
import random
import json
import traceback
from pathlib import Path
from time import sleep

WEBHOOK_URL = json.loads(Path("conf.json").read_text())["webhook_url"]
PING_ERRORS = "<@818564860484780083>"
PING_NEW_VERSION = "<@&1342761186353090590>"

class Response:
	def __init__(self, url, status, body, headers):
		self.url = url
		self.status = status
		self.body = body
		self.headers = headers

class Date():
	def __init__(self, date):
		self.string = date
		self.date_set = set()
		
		for sub in date.split():
			self.date_set.add(sub.strip(" \t\r\n\v\f,.<>;'/:?{}[]-=_+\\|()*&^%$#@!`~"))
	
	def __eq__(self, other):
		if (len(self.date_set) == len(other.date_set)):
			for v in self.date_set:
				if v not in other.date_set:
					return False
			
			return True
		else:
			return False
	
	def __repr__(self):
		return self.string

def http_request(url, method='GET', data=None, headers={}):
	resp = urllib.request.urlopen(urllib.request.Request(url, data, method=method, headers={
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"
	} | headers))
	data = resp.read()
	r = Response(resp.url, resp.status, data, resp.headers)
	resp.close()
	
	return r

def post(url, data):
	data = json.dumps(data).encode("utf-8")
	return http_request(url, 'POST', data, {"Content-Type": "application/json"})

def send_message(content):
	print("[Message]\n" + content + "\n[/Message]")
	
	try:
		post(WEBHOOK_URL, {
			"content": content,
		})
	except:
		pass

def get_app_updated_date_play(appid):
	try:
		r = http_request(f"https://play.google.com/store/apps/details?id={appid}")
		r = r.body.decode("utf-8")
		i = r.index("Updated on")
		
		if (i < 0):
			print("Failed to parse response: String 'Updated on' not found")
			return None
		
		d = r[i:i+100]
		d = d.partition('>')[2].partition('>')[2].partition('<')[0]
		
		return d
	except:
		traceback.print_exc()
		return None

def rand_wait(base, variance):
	sleep(base + (2 * variance * (random.random() - 0.5)))

LAST_DATE = None
CONSEC_ERRORS = 0

def generate_report():
	global LAST_DATE
	global CONSEC_ERRORS
	
	date = get_app_updated_date_play("com.mediocre.smashhit")
	
	if not date:
		CONSEC_ERRORS += 1
		
		if CONSEC_ERRORS == 4:
			send_message(f"{PING_ERRORS} Failed to fetch date four times in a row! Check that the bot is still working.")
		
		return
	else:
		CONSEC_ERRORS = 0
	
	date = Date(date)
	
	if not LAST_DATE:
		print("Setting date for first time")
		LAST_DATE = date
		send_message(f"## Starting up!\nRecorded current update date as: {date}")
	else:
		if LAST_DATE != date:
			print(f"{repr(LAST_DATE)} != {repr(date)}")
			send_message(f"{PING_NEW_VERSION}\n## Smash Hit updated on Google Play!\nOld update date: {LAST_DATE}\nNew update date: {date}")
			
			LAST_DATE = date
		else:
			print(f"{repr(LAST_DATE)} == {repr(date)}")

def main():
	while True:
		generate_report()
		rand_wait(60 * 30, 60 * 4)
		# sleep(20)

if __name__ == "__main__":
	main()
