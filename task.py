#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib,random,json,os,pickle
from datetime import datetime,date
from collections import defaultdict

LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

#需要更完善的错误处理
class Task(object):
	tids=defaultdict(lambda:False) #
	def __init__(self,name='',finish_time=datetime(2199,12,31),priority=0,amount=1,tags=set(),tid=None,create_time=datetime.now()):
		#创建时不应传入tid,create_time
		self.name=name
		self.create_time=create_time
		self.finish_time=finish_time
		self.priority=priority
		self.amount=[0,amount]
		self.tags=tags
		self.tid=self.add_tid(tid)
	def __del__(self):
		self.tids.pop(self.tid)
	def __str__(self):
		return f'{self.name} {self.create_time} {self.finish_time} {self.priority} {self.amount} {self.tags} {self.tid}'
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
			raise ValueError(f'Invalid value :{progress},progress is more than total amount')
		else:
			self.amount[0]=progress
	def add_tag(self,new_tags=set()):
		self.tags|=new_tags
	def delete_tag(self,dels=set()):
		self.tags-=dels
	'''
	def __get_tid(self,tid=hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()):
		#随机生成64位字符串并求md5
		while self.tids[tid]:
			tid=hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()
		self.tids[tid]=True
		return tid
	'''
	@classmethod
	def add_tid(cls,tid=None):
		#使用自定义tid或随机生成64位字符串并求md5
		tid=tid or hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()
		#检查tid是否被使用
		while cls.tids[tid]:
			tid=hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()
		cls.tids[tid]=True
		return tid
	@classmethod
	def del_tid(cls,tid):
		if not cls.tids[tid]:
			raise ValueError(f'tid {tid} is not used')
		cls.tids[tid]=False
	def expt(self):
		return json.dumps(self,default=self.toJson)
	@classmethod
	def impt(cls,jsonObj):
		return json.loads(jsonObj,object_hook=cls.fromJson)
	@staticmethod
	def toJson(obj):
		if isinstance(obj,Task):
			return {
			'name':obj.name,
			'create_time':obj.create_time,
			'finish_time':obj.finish_time,
			'priority':obj.priority,
			'amount':obj.amount,
			'tags':obj.tags,
			'tid':obj.tid
			}
		if isinstance(obj,datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		if isinstance(obj,set):
			return list(obj)
	@staticmethod
	def fromJson(d):
		return Task(
			name=d['name'],
			create_time=datetime.strptime(d['create_time'],'%Y-%m-%d %H:%M:%S'),
			finish_time=datetime.strptime(d['finish_time'],'%Y-%m-%d %H:%M:%S'),
			priority=d['priority'],
			amount=d['amount'],
			tags=set(d['tags']),
			tid=d['tid']
			)
	__repr__=__str__
class Tasks(object):
	def __init__(self):
		self.tasks={}
		self.__recovery()
	def __recovery(self):
		try:
			rec_files=os.listdir('data/tasks')
		except OSError as e:
			os.mkdir('data/tasks')
		else:
			if rec_files:
				print(rec_files)
				for x in rec_files:
					with open(f'data/tasks/{x}','r') as f:
						#task=pickle.load(f)
						task=Task.impt(f.read())
						try:
							self.addTask(task)
						except ValueError as e:		
							task.tid=task.add_tid() #重新分配tid
							self.addTask(task)
	def save(self):
		for _,v in self.tasks.items():
			self.saveTask(v)
	@classmethod
	def saveTask(cls,task):
		with open(f'data/tasks/{task.tid}','w') as f:
			f.write(task.expt())
	def addTask(self,task):
		if self.tasks.get(task.tid):
			raise ValueError(f'task {tid} is exists')
		self.tasks[task.tid]=task
	def delTask(self,tid):
		self.tasks.pop(tid)
		try:
			os.remove(f'data/tasks/{tid}')
		except IOError as e:
			pass
	def createTask(self,name='',finish_time=datetime(2199,12,31),priority=0,amount=1,tags=set()):
		task=Task(name,finish_time,priority,amount,tags)
		self.tasks[task.tid]=task
		self.saveTask(task.tid)
