#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import json
import pathlib
from datetime import datetime,date
from collections import defaultdict,namedtuple
from array import array
from timetool import *

Progress=namedtuple('Progress',['finished','total'])

class BaseTask(object):
	tids=set()
	__timetype={datetime:lambda x:x,str:lambda x:datetime.strptime(x,'%Y-%m-%d %H:%M:%S')}
	__LETTERS='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	def __init__(self,name,priority,progress,amount=1,tid=None,create_time=datetime.now()):
		self.name=name
		self.priority=priority
		self.progress=Progress(0,progress)
		try:
			self.create_time=self.__timetype[create_time.__class__](create_time)
		except KeyError:
			raise TypeError(f'Unsupport type {create_time.__class__.__name__} for create_time')
		self.tid=self.addTid(tid)
	def __repr__(self):
		return self.__dict__.__str__()
	def __del__(self):
		try:
			self.delTid(self.tid)
		except (ValueError,AttributeError):
			pass
	def updateName(self,new_name):
		self.name=new_name
	def updateProgess(self,new_progress=(0,1)):
		self.progress=Progress(*new_progress)
	@classmethod
	def addTid(cls,tid=None):
		tid=tid or hash(''.join(random.choices(cls.__LETTERS,k=32)))
		while tid in cls.tids:
			tid=hash(''.join(random.choices(cls.__LETTERS,k=32)))
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
class BaseTasks(object):
	inc_cls=BaseTask
	savepath='data/tasks'
	def __init__(self,tasks={}):
		self.tasks=tasks
	def __getitem__(self,key):
		return self.tasks[key]
	def __setitem__(self,key,value): #not recommend,add() is easier
		self.tasks[key]=value
	def __iter__(self):
		return iter(self.tasks.values())
	def __repr__(self):
		return self.tasks.__str__()
	@classmethod			
	def fromFiles(cls,path):
		tasks={}
		path=pathlib.Path(path)
		for x in path.iterdir():
			with open(x,'r') as f:
				try:
					task=cls.inc_cls.fromJson(f.read())
				except (OSError,TypeError,json.decoder.JSONDecodeError):
					raise
				else:
					tasks[task.tid]=task
		return cls(tasks)
	def toFiles(self,path=None):
		path=path or self.savepath
		path=path.strip('/').strip('\\')
		pathlib.Path(path).mkdir(exist_ok=True)
		for k,v in self.tasks.items():
			try:
				with open(f'{path}/{k}.json','w') as f:
					f.write(v.expt())
			except (OSError,json.decoder.JSONDecodeError):
				raise
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
		   Ep:cls.fromEp,Eps:cls.fromEps,Video:cls.fromVideo,
		   datetime:cls.fromDatetime,array:cls.toList,set:cls.toList,Progress:cls.toList}
		try:
			return hooks[obj.__class__](obj)
		except KeyError:
			raise TypeError(f'Unsupport type: {obj.__class__.__name__}')
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
	def fromVideo(obj):
		return {
			'name':obj.name,
			'create_time':obj.create_time,
			'priority':obj.priority,
			'eps':obj.eps,
			'tid':obj.tid
			}
	@staticmethod
	def fromDatetime(obj):
		return obj.strftime('%Y-%m-%d %H:%M:%S')
class Ep(object):
	status_dict={0:'wish',1:'watched',2:'watching',3:'hold',4:'dropped'}
	__tlentype={TimeLength:lambda x:x,str:lambda x:TimeLength.strptime(x)}
	def __init__(self,number='1',name='',status=1,length=TimeLength()): #defaut value for number should be removed
		self.number=number
		self.name=name
		self.status=status
		try:
			self.length=self.__tlentype[length.__class__](length)
		except TypeError:
			raise ValueError
		except KeyError:
			raise TypeError
	def __bool__(self):
		if all((number,name)):
			return True
		else:
			return False
	def __repr__(self):
		return f'''Ep {self.number}:{self.name},{self.status},{self.length}'''
		#return f'number:{self.number},name:{self.name}'
	@classmethod
	def fromJson(cls,jsonObj):
		return json.loads(jsonObj,object_hook=cls.fromDict)
	@classmethod
	def fromDict(cls,d):
		return cls(**d)
class Eps(object):
	def __init__(self,eps=()):
		try:
			self.eps={ep.number:ep for ep in eps}
		except (TypeError,ArithmeticError):
			raise
	def __repr__(self):
		n='\n      '
		return f'''Eps:
      {n.join([str(i) for i in self.eps.values()])}
		'''
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
		return cls.fromDict(d)
	@classmethod
	def fromDict(cls,d):
		return cls((Ep(**i) for i in d['eps']))
class Video(BaseTask):
	def __init__(self,name='',priority=0,eps=Eps([Ep()]),times=1,tid=None,create_time=datetime.now()):
		super().__init__(name=name,priority=priority,progress=len(eps),create_time=create_time,tid=tid)
		self.eps=eps
		self.times=times
	def __repr__(self):
		return f'''Video {self.name} {self.progress[0]}/{self.progress[1]}:priority:{self.priority},
    {self.eps}
			'''
	def addEp(self,new_ep):
		self.eps.add(new_ep)
		self.updateAmount(len(self.eps))
	def delEp(self,number):
		self.eps.pop(number)
		self.updateAmount(len(self.eps))
	def addTime(self):
		self.times+=1
	def updateTime(self,new_times):
		self.times=new_times
	@classmethod
	def fromJson(cls,jsonObj):
		d=json.loads(jsonObj)
		eps=Eps.fromDict(d['eps'])
		d.pop('eps')
		return cls(**d,eps=eps)
	@classmethod
	def fromDict(cls,d): # format:{'name':name,'info':[{'number':number,'name':'length':},{'number':'number','name':'length':}]}
		return cls(name=d['name'],eps=Eps((Ep(**i) for i in d['info'])))
class Videos(BaseTasks):
	inc_cls=Video
	savepath='data/videos'
	def __init__(self,videos={}):
		super().__init__(videos)
	def __repr__(self):
		n='\n  '
		return f'''Videos:
  {n.join([str(i) for i in self.tasks.values()])}'''
	@classmethod
	def fromOnes(cls,videos=()):
		return cls({i.tid:i for i in videos})
	def search(self,name):
		for x in self:
			if x.name==name:
				return x
		raise ValueError(f'{name} not found')
	def add_by_detail(self,name,ep_infos=[{'number':'2','name':'default1','length':'25:00'},{'number':'2','name':'default2'}]):
		self.add(self.inc_cls(name=name,eps=Eps([Ep(**i) for i in ep_infos])))
