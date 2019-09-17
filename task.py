#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json
import os
import pathlib
from datetime import datetime,date
from collections import defaultdict
from array import array

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class BaseTask(object):
	tids=set()
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
		while tid not in cls.tids:
			tid=hash(''.join(random.choices(LETTERS,k=64)))
		cls.tids.add(tid)
		return tid
	@classmethod
	def delTid(cls,tid):
		if tid not in cls.tids:
			raise ValueError(f'tid {tid} is not exist')
		cls.tids.remove(tid)
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
class BaseTasks(object):
	def __init__(self,rec_path='data/rec'):
		self.tasks={}
		self.rec(rec_path)
	def rec(self,rec_path):
		path=pathlib.Path(rec_path).mkdir(exist_ok=True)
		for x in path.iterdir():
			with open(x,'r') as f:
				try:
					task=json.loads(f.read(),object_hook=lambda:None)
				except (IOError,json.decoder.JSONDecodeError):
					raise
				else:
					self.tasks[task.tid]=task
class defaultJson(object):
	toList=lambda obj:list(obj)
	@classmethod
	def getJson(cls,obj):
		hooks={BaseTask:cls.fromBaseTask,TimeLength:cls.fromTimeLength,
		   Ep:cls.fromEp,Eps:cls.fromEps,Anime:cls.fromAnime,
		   datetime:lambda obj:obj.strftime('%Y-%m-%d %H:%M:%S'),array:cls.toList,set:cls.toList}
		try:
			return hooks[obj.__class__](obj)
		except KeyError:
			raise
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
class TimeLength(object):
	def __init__(self,hour=0,minute=0,second=0):
		self.hour=hour
		self.minute=minute
		self.second=second
		self.simple()
	def __add__(self,other):#add a datatime object is allowed but not recommended
		try:
			new_hour=self.hour+other.hour
			new_minute=self.minute+other.minute
			new_second=self.second+other.second
		except AttributeError:
			return NotImplemented
		return TimeLength(new_hour,new_minute,new_second)
	def __sub__(self,other):
		try:
			new_hour=self.hour+other.hour
			new_minute=self.minute+other.minute
			new_second=self.second+other.second
		except AttributeError:
			return NotImplemented
		return TimeLength(new_hour,new_minute,new_second)
	def __iadd__(self,other):
		try:
			self.hour=other.hour
			self.minute=other.minute
			self.second=other.second
		except ArithmeticError:
			return NotImplemented
	def __isub__(self,other):
		try:
			self.hour=other.hour
			self.minute=other.minute
			self.second=other.second
		except ArithmeticError:
			return NotImplemented
	def __str__(self):
		if self.hour:
			return ''.join(f'{self.hour}:{self.minute}:{self.second}')
		elif self.minute:
			return ''.join(f'{self.minute}:{self.second}')
		else:
			return ''.join(str(self.second))
	def strftime(self):
		return f'{self.hour}:{self.minute}:{self.second}'
	@classmethod
	def strptime(cls,strtime):
		return cls(*[int(i) for i in strtime.split(':')])
	def simple(self):
		if self.second>=60:
			self.minute+=self.second//60
			self.second%=60
		if self.minute>=60:
			self.hour+=self.minute//60
			self.minute%=60
	__repr__=__str__
class Ep(object):
	status_dict={0:'wish',1:'watched',2:'watching',3:'hold',4:'dropped'}
	def __init__(self,number:str,name='',status=1,length=TimeLength(minute=23,second=40)):
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
	def fromJson(self,jsonObj):pass
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
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=lambda d:cls(
			name=d['name'],
			create_time=datetime.strptime(d['create_time'],'%Y-%m-%d %H:%M:%S'),
			priority=d['priority'],
			amount=d['amount']
			eps=d['eps']
			))
