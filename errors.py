from texts import *

class TagNotFound(BaseException):
	'''
	Will be raised if the tag was not found in the database.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_tag_not_exist


class TagAlreadyExists(BaseException):
	'''
	Will be raised if the tag already exists.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_tag_exists


class TagNotOwned(BaseException):
	'''
	Will be raised if the user does not match the credit.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_not_your_tag
