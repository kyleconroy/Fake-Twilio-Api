from google.appengine.ext import db
from models import base
from random import random
from hashlib import sha256

from helpers import parameters

from google.appengine.api.labs import taskqueue

import datetime

class Message(base.CommonModel):
	To = db.StringProperty()
	From = db.StringProperty()
	Body = db.StringProperty()
	DateSent = db.DateTimeProperty()
	AccountSid = db.StringProperty()
	Status = db.StringProperty()
	Direction = db.StringProperty()
	Price = db.FloatProperty()
	StatusCallback = db.StringProperty()

	@classmethod
	def new_Sid(self):
		return 'SM'+sha256(str(random())).hexdigest()

	def queueCallback(self):
		try:
			taskqueue.Queue('StatusCallbacks').add(taskqueue.Task(url='/Callbacks/SMS', params = {'SmsSid':self.Sid}))
			return True
		except Exception, e:
			logging.error(e)
			logging.error('Unable to queue the callback task')
			return False

	def send(self):
		self.Status = 'sent'
		self.Price = 0.03
		self.DateSent = datetime.datetime.now()
		self.put()
	
	def error(self):
		self.Status = 'failed'
		self.Price = 0.00
		self.put()
		
	def validate(self, request, arg_name,arg_value):
		validators = {
			'To' : parameters.valid_to_phone_number(arg_value if arg_value is not None else request.get('To',None),required=True),
			'From' : parameters.valid_from_phone_number(arg_value if arg_value is not None else request.get('From',None),required=True),
			'Body' : parameters.valid_body(arg_value if arg_value is not None else request.get('Body',None),required=True),
			'StatusCallback' : arg_value if (arg_value is not None or request is None) else parameters.standard_urls(request,'StatusCallback')
		}
		if arg_name in validators:
			return validators[arg_name]
		else:
			return True, 0, ''

	def sanitize(self, request, arg_name, arg_value):
		sanitizers = {
			'To' : arg_value if arg_value is not None else request.get('To',None),
			'From' : arg_value if arg_value is not None else request.get('From',None),
			'Body' : arg_value if arg_value is not None else request.get('Body',None),
			'StatusCallback' : arg_value if arg_value is not None else request.get('StatusCallback',None)
		}
		if arg_name in sanitizers:
			return sanitizers[arg_name]
		else:
			return arg_value