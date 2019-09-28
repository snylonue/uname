#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from task import *

def initVideos(video_info=[]):# input data format [{'name'='','priority'=0,'times'=1}]
	try:
		videos=[Video(**i) for in video_info]
	except TypeError as e:
		raise TypeError(f'Invalid info:{e.args[0].replace('__init__() got an ','')}')
	else:
		return Videos({i.tid:i for i in videos})
def recovery(path='data/videos',cls=Videos,ignore=False):
	try:
		return cls.recovery(path)
	except (OSError,TypeError,json.decoder.JSONDecodeError):
		if ignore:
			pass
		else:
			raise