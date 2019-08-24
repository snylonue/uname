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
		self.tid=tid or self.__get_tid()
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
	def __get_tid(self,tid=hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()):
		#随机生成64位字符串并求md5
		while self.tids[tid]:
			tid=hashlib.md5(''.join(random.choices(LETTERS,k=64)).encode('utf-8')).hexdigest()
		self.tids[tid]=True
		return tid
	__repr__=__str__
class Tasks(object):
	def __init__(self):
		self.tasks=self.recovery()
	def recovery(self):
		try:
			rec_files=os.listdir('data/tasks')
		except OSError as e:
			os.mkdir('data/tasks')
			return {}
		else:
			if rec_files:
				res={}
				for x in rec_files:
					with open(f'data/tasks/{x}','rb') as f:
						task=pickle.load(f) #计划使用json序列化
						res[task.tid]=task
						task.tids[task.tid]=True
						'''
						jsonTask=f.read()
						task=json.load(jsonTask,object_hook=lambda x:Task(x['name'],x['finish_time'],x['priority'],x['amount'],x['tags'],x['tid'],x['create_time']))
					'''
					#os.remove(f'data/tasks/{x}')
				return res
			else:
				return {}
	def saveTask(self,tid):
		for k,v in self.tasks.items():
			with open(f'data/tasks/{k}','wb') as f:
				f.write(pickle.dumps(v))

		'''
		jsonTask=json.dumps(self.tasks[tid],default=toJson)
		with open(f'data/tasks/{tid}','w') as f:
			f.write(jsonTask)
			'''
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
'''
def toJson(obj):
	if isinstance(obj,date):
		return {'year':obj.year,
				'month':obj.month,
				'day':obj.day,
				'hour':obj.hour,
				'minute':obj.minute,
				'second':obj.second,
				'microsecond':obj.microsecond
			}
	elif isinstance(obj,Task):
		return {'name':obj.name,
				'create_time':obj.create_time,
				'finish_time':obj.finish_time,
				'priority':obj.priority,
				'amount':obj.amount,
				'tags':obj.tags,
				'tid':obj.tid
		}
	elif isinstance(obj,set):
		pass
	else:
		return obj.__dict__
'''