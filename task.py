#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json
import os
from datetime import datetime,date
from collections import defaultdict
from array import array

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class BaseTask(object): #__init__(self,name,priority,amount)
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
	def expt(self):
		return json.dumps(self,default=defaultJson.getJson)
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=lambda d:cls(
			name=d['name'],
			create_time=datetime.strptime(d['create_time'],'%Y-%m-%d %H:%M:%S'),
			priority=d['priority'],
			amount=d['amount']
			))
class TimeLength(object):
	def __init__(self,hours=0,minutes=0,seconds=0):
		self.hours=hours
		self.minutes=minutes
		self.seconds=seconds
		self.simple()
	def __add__(self,other):
		return TimeLength(self.hours+other.hours,self.minutes+other.minutes,self.seconds+other.seconds)
	def __str__(self):
		if self.hours:
			res=''.join(f'{self.hours}:{self.minutes}:{self.seconds}')
		elif self.minutes:
			res=''.join(f'{self.minutes}:{self.seconds}')
		else:
			res=''.join(str(self.seconds))
		return res
	def strftime(self):
		return f'{self.hours}:{self.minutes}:{self.seconds}'
	@classmethod
	def strptime(cls,strtime):
		return cls(*[int(i) for i in strtime.split(':')])
	def simple(self):
		if self.seconds>=60:
			self.minutes+=self.seconds//60
			self.seconds%=60
		if self.minutes>=60:
			self.hours+=self.minutes//60
			self.minutes%=60
	__repr__=__str__
class Ep(object):
	status_dict={0:'wish',1:'watched',2:'watching',3:'hold',4:'dropped'}
	def __init__(self,number:str,name='',status=1,length=TimeLength(minutes=23,seconds=40)):
		self.number=number
		self.name=name
		self.status=status
		self.length=length
	def __bool__(self):
		if all((number,name)):
			return True
		else:
			return False
class Eps(object):
	def __init__(self,eps):
		self.eps={ep.number:ep for ep in eps}
	def __len__(self):
		return len(self.eps)
	def __iadd__(self,other:Ep):
		if self.eps.get(other.number):
			raise ValueError(f'Ep {other.number} is exist')
		self.eps[other.number]=other
	def __isub__(self,other:Ep):
		try:
			self.eps.pop(other.number)
		except KeyError:
			raise ValueError(f'Ep {other.number} is not exist')
class Anime(BaseTask):
	def __init__(self,name='',priority=0,eps=Eps((Ep())),tid=None,create_time=datetime.now()):
		super().__init__(name=name,priority=priority,amount=len(eps),create_time=create_time,tid=tid)
		self.eps=eps
	def addEp(self,new_ep):
		try:
			self.eps+=new_ep
		except ValueError:
			raise
	def delEp(self,ep):
		try:
			self.eps-=ep
		except ValueError:
			raise
	'''
	@staticmethod
	def toJson(obj):
		if isinstance(obj,Anime):
			return {
			'name':obj.name,
			'priority':obj.priority,
			'amount':obj.amount,
			'eps':obj.eps,
			'create_time':obj.create_time,
			'tid':obj.tid,
			}
		elif isinstance(obj,Eps):
			return obj.eps
	'''
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=lambda d:cls(
			name=d['name'],
			create_time=datetime.strptime(d['create_time'],'%Y-%m-%d %H:%M:%S'),
			priority=d['priority'],
			amount=d['amount']
			eps=d['eps']
			))
class defaultJson(object):
	@classmethod
	def getJson(cls,obj):
		hooks={BaseTask:cls.fromBaseTask,TimeLength:cls.fromTimeLength,Ep:cls.fromEp,
		   Eps:cls.fromEps,Anime:cls.fromAnime,datetime:cls.fromDatetime,array:cls.fromArray,
		   set:cls.fromSet}
		return hooks[obj.__class__](obj)
	@staticmethod
	def fromTimeLength(obj):
		return obj.strftime
	@staticmethod
	def fromEp(obj):
		return {
			'number':obj.number,
			'name':obj.name,
			'status':obj.status,
			'length':obj.length
		}
	@staticmethod
	def fromEps(obj):
		return [obj.eps]
	@staticmethod
	def fromBaseTask(obj):
		return {
			'name':obj.name,
			'create_time':obj.create_time,
			'priority':obj.priority,
			'amount':obj.amount,
			}
	@staticmethod
	def fromAnime(obj):
		return {
			'name':obj.name,
			'create_time':obj.create_time,
			'priority':obj.priority,
			'amount':obj.amount,
			'eps':obj.eps
			}
	@staticmethod
	def fromDatetime(obj):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
	@staticmethod
	def fromSet(obj):
		return list(obj)
	@staticmethod
	def fromArray(obj):
		return list(obj)
