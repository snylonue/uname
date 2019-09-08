#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json
import os
from datetime import datetime,date
from collections import defaultdict,namedtuple
from array import array

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
Ep=namedtuple('Ep',['number','name','type','status','length'])

class BasicTask(object): #__init__(self,name,priority,amount)
	tids=defaultdict(lambda:False)
	def __init__(self,name,priority,amount,tid,create_time):
		self.name=name
		self.priority=priority
		self.progress=array('I',(0,amount))
		self.create_time=create_time
		self.tid=self.addTid(tid)
	def __del__(self):
		try:
			self.delTid(self.tid)
		except ValueError:
			pass
	def updateName(self,new_name):
		self.name=new_name
	def updatePriority(self,new_priority):
		self.priority=new_priority
	def updateAmount(self,new_amount):
		self.progress[1]=new_amount
	def updateProgess(self,progress):
		if progress>self.progress[1]:
			raise ValueError(f'progress {progress} is more than total amount {self.progress[1]}')
		else:
			self.progress[0]=progress
	@classmethod
	def addTid(cls,tid=None):
		#使用自定义tid或随机生成64位字符串并求hash
		tid=tid or hash(''.join(random.choices(LETTERS,k=64)))
		#检查tid是否被使用
		while cls.tids[tid]:
			tid=hash(''.join(random.choices(LETTERS,k=64)).encode('utf-8'))
		cls.tids[tid]=True
		return tid
	@classmethod
	def delTid(cls,tid):
		if not cls.tids[tid]:
			raise ValueError(f'tid {tid} is not exist')
		cls.tids.pop(tid)
	@classmethod
	def impt(cls,jsonObj):
		return json.loads(jsonObj,object_hook=cls.fromJson)
	def expt(self):
		return json.dumps(self,default=self.toJson)
	@staticmethod
	def toJson(obj):
		if isinstance(obj,BasicTask):
			return {
			'name':obj.name,
			'create_time':obj.create_time,
			'priority':obj.priority,
			'amount':obj.amount,
			}
		else:
			return globalToJson(obj)
	@classmethod
	def fromJson(cls,d):
		return cls(
			name=d['name'],
			create_time=datetime.strptime(d['create_time'],'%Y-%m-%d %H:%M:%S'),
			priority=d['priority'],
			amount=d['amount']
			)
class TimeLength(object):
	def __init__(self,hours=0,minutes=0,seconds=0):
		self.hours=hours
		self.minutes=minutes
		self.seconds=seconds
		self.simple()
	def __add__(self,other):
		return TimeLength(self.hours+other.hours,self.minutes+other.minutes,self.seconds+other.seconds)
	def simple(self):
		if self.seconds>=60:
			self.minutes+=self.seconds//60
			self.seconds%=60
		if self.minutes>=60:
			self.hours+=self.minutes//60
			self.minutes%=60
class Eps(object):
	def __init__(self,eps={}):
		self.eps={}
	def __add__(self,other)
class Anime(BasicTask):
	status_dict={}
	def __init__(self,name='',priority=0,amount=(0,1),eps={},tags=set(),tid=None,create_time=datetime.now()):
		super().__init__(name=name,priority=priority,amount=amount,tid=tid)
		self.create_time=create_time
		self.eps=eps
	def impt(self):pass
	def expt(self):pass

def globalToJson(obj):
	if isinstance(obj,datetime):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
	if isinstance(obj,set):
		return list(obj)
	if isinstance(obj,array):
		return list(array)