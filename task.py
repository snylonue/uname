#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib,random,string
from datetime import datetime
from collections import defaultdict

class Task(object):
	__tids=defaultdict(lambda:False)
	__letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	def __init__(self,name='',finish_time=datetime(2199,12,31),priority=0,amount=1,tags=set([]),create_time=datetime.now(),tid=None):
		self.name=name
		self.create_time=create_time
		self.finish_time=finish_time
		self.priority=priority
		self.amount=[0,amount]
		self.tags=tags
		self.tid=self.__get_tid()
	def changeName(self,new_name):
		self.name=new_name
	def changeFinishTime(self,new_finish_time):
		self.finish_time=new_finish_time
	def changePriority(self,new_priority):
		self.priority=new_priority
	def changeAmount(self,new_amount):
		self.amount[1]=new_amount
	def updateProgess(self,progress):
		if progress>self.amount[1]:
			raise ValueError(f'Ininvalid value :{progress},progress is more than total amount')
		else:
			self.amount[0]=progress
	def add_tag(self,new_tags=set([])):
		self.tags|=new_tags
	def delete_tag(self,dels=set([])):
		self.tags^=dels
	def __get_tid(self,tid=hashlib.md5(''.join(random.choices(self.__letters,k=64))).hexdigest()):
		while self.__tids[tid]:
			pass
		self.__tids[tid]=True



