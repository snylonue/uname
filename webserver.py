import task
import json
from tornado import ioloop
from tornado import web

class BaseHandler(web.RequestHandler):
	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
class MainHandler(BaseHandler):
	def get(self):
		self.write({'data':json.loads(userTask.toJsons())})

app=web.Application([web.url(r'/task',MainHandler)])

if __name__ == '__main__':
	userTask=task.Videos().fromFiles('data/videos')
	app.listen(8888)
	ioloop.IOLoop.current().start()
