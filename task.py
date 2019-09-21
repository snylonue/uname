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
	def __init__(self,name,priority,progress:list,amount=1,tid=None,create_time=datetime.now()):
		self.name=name
		self.priority=priority
		try:
			self.progress=array('I',progress)
		except TypeError:
			if amount:
				self.progress=array('I',(0,amount))
			else:
				raise
		if isinstance(create_time,datetime):
			self.create_time=create_time
		elif isinstance(create_time,str):
			self.create_time=datetime.strptime(create_time,'%Y-%m-%d %H:%M:%S')
		else:
			raise TypeError
		self.tid=self.addTid(tid)
	def __str__(self):
		return self.__dict__.__str__()
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
		while tid in cls.tids:
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
		return json.loads(jsonObj,object_hook=lambda d:cls(**d))
	__repr__=__str__
class BaseTasks(object):
	def __init__(self,tasks={}):
		self.tasks=tasks
	def __getitem__(self,key):
		return self.tasks[key]
	def __setitem__(self,key,value): #not recommend,add() is easier
		self.tasks[key]=value
	@classmethod			
	def fromFiles(self,path):
		path=pathlib.Path(path).mkdir(exist_ok=True)
		tasks={}
		for x in path.iterdir():
			with open(x,'r') as f:
				try:
					task=json.loads(f.read(),object_hook=lambda:None)
				except (IOError,json.decoder.JSONDecodeError):
					raise
				else:
					tasks[task.tid]=task
		return cls(tasks)
	def add(self,new_task):
		self[new_task.tid]=new_task
	def pop(self,tid):
		try:
			self.tasks.pop(tid)
		except KeyError:
			raise ValueError(f'Tid {tid} is not exist')
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
		return obj.strftime()
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
		return {'eps':[i for i in obj.eps.values()]}
	@staticmethod
	def fromBaseTask(obj):
		return {
			'name':obj.name,
			'create_time':obj.create_time,
			'priority':obj.priority,
			'progress':obj.progress,
			'tid':obj.tid
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
class TimeLength(object):
	def __init__(self,hour=0,minute=0,second=0):
		self.hour=hour
		self.minute=minute
		self.second=second
		self.simple()
	def __add__(self,other):#add a datetime object is allowed but not recommended
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
	@property
	def seconds(self):
		return self.hour*3600+self.minute*60+self.second
	__repr__=__str__
class Ep(object):
	status_dict={0:'wish',1:'watched',2:'watching',3:'hold',4:'dropped'}
	def __init__(self,number='1',name='',status=1,length=TimeLength(minute=23,second=40)): #defaut value for number should be removed
		self.number=number
		self.name=name
		self.status=status
		if isinstance(length,TimeLength):
			self.length=length
		elif isinstance(length,str):
			self.length=TimeLength.strptime(length)
		else:
			raise TypeError
	def __bool__(self):
		if all((number,name)):
			return True
		else:
			return False
	def __str__(self):
		return self.__dict__.__str__()
		#return f'number:{self.number},name:{self.name}'
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=cls.fromDict)
	@classmethod
	def fromDict(cls,d):
		return cls(**d)
	__repr__=__str__
class Eps(object):
	def __init__(self,eps=()):
		try:
			self.eps={ep.number:ep for ep in eps}
		except (TypeError,ArithmeticError):
			raise
	def __str__(self):
		return self.eps.__str__()
	def __len__(self):
		return len(self.eps)
	def __getitem__(self,key):
		return self.eps[key]
	def add(self,new_ep):
		if self.eps.get(new_ep.number):
			raise ValueError(f'Ep {new_ep.number} is exist')
		self[new_ep.number]=new_ep
	def pop(self,number):
		try:
			self.eps.pop(number)
		except KeyError:
			raise ValueError(f'Ep {number} is not exist')
	@classmethod
	def fromJson(cls,jsonObj):
		d=json.loads(jsonObj)
		return cls([Ep(**i) for i in d['eps']])
	__repr__=__str__
class Anime(BaseTask):
	def __init__(self,name='',priority=0,eps=Eps([Ep()]),tid=None,create_time=datetime.now()):
		super().__init__(name=name,priority=priority,amount=len(eps),create_time=create_time,tid=tid)
		self.eps=eps
	def addEp(self,new_ep):
		self.eps.add(new_ep)
		self.updateAmount(len(self.eps))
	def delEp(self,number):
		self.eps.pop(number)
		self.updateAmount(len(self.eps))
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=lambda d:cls(
			name=d['name'],
			create_time=d['create_time'],
			priority=d['priority'],
			amount=d['amount'],
			eps=d['eps']
			))
