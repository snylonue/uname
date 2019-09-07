#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import random
import json
import os
from datetime import datetime,date,timedelta
from collections import defaultdict,namedtuple
from array import array

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
Ep=namedtuple('Ep',['name','eptype','status','length','progress'])

#需要更完善的错误处理
class BasicTask(object):
	tids=defaultdict(lambda:False)
	def __init__(self,name,priority,amount,tid):
		self.name=name
		self.priority=priority
		self.amount=array('I',amount)
		self.tid=self.addTid(tid)
	def __del__(self):
		self.tids.pop(self.tid)
	def updateName(self,new_name):
		self.name=new_name
	def updatePriority(self,new_priority):
		self.priority=new_priority
	def updateAmount(self,new_amount):
		self.amount[1]=new_amount
	def updateProgess(self,progress):
		if progress>self.amount[1]:
			raise ValueError(f'progress {progress} is more than total amount {self.amount[1]}')
		else:
			self.amount[0]=progress
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
			raise ValueError(f'tid {tid} is not used')
		cls.tids[tid]=False
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
class Eps(BasicTask):
	def __init__(self,eps):
		self.eps={number+1:ep for number in range(len(eps)) for ep in eps}

class Task(BasicTask):
class Anime(BasicTask):
	status_dict={}
	def __init__(self,name='',priority=0,amount=(0,1),eps={},tags=set(),tid=None,create_time=datetime.now()):
		super().__init__(name=name,priority=priority,amount=amount,tid=tid)
		self.create_time=create_time
		self.eps=eps
	def impt(self):pass
	def expt(self):pass
class Tasks(object):
	def __init__(self):
		self.tasks={}
		self.__recovery()
	def __getitem__(self,index):
		return self.tasks[index]
	def __len__(self):
		return len(self.tasks)
	def __iter__(self):
		return self.tasks.values()
	def __recovery(self):
		try:
			rec_files=os.listdir('data/tasks')
		except OSError:
			os.mkdir('data/tasks')
		else:
			if rec_files:
				print(rec_files)
				for x in rec_files:
					with open(f'data/tasks/{x}','r') as f:
						#task=pickle.load(f)
						task=Task.impt(f.read())
						self.addTask(task)
	def save(self):
		for x in self.tasks.values():
			self.saveTask(x)
	@classmethod
	def saveTask(cls,task):
		with open(f'data/tasks/{task.tid}','w') as f:
			f.write(task.expt())
	def addTask(self,task):
		self.tasks[task.tid]=task
	def delTask(self,task,tid=None):
		tid=tid or task.tid			
		try:
			self.tasks.pop(tid)
			os.remove(f'data/tasks/{tid}')
		except KeyError:
			raise KeyError(f'task {tid} is not exist')
		except OSError:
			pass
	def createTask(self,name='',finish_time=datetime(2199,12,31),priority=0,amount=1,tags=set()):
		task=Task(name,finish_time,priority,amount,tags)
		self.tasks[task.tid]=task
		self.saveTask(task.tid)

def globalToJson(obj):
	if isinstance(obj,datetime):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
	if isinstance(obj,set):
		return list(obj)
	if isinstance(obj,array):
		return list(array)