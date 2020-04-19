from texts import *

class TagNotFound(Exception):
	'''
	Will be raised if the tag was not found in the database.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_tag_not_exist


class TagAlreadyExists(Exception):
	'''
	Will be raised if the tag already exists.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_tag_exists


class TagNotOwned(Exception):
	'''
	Will be raised if the user is not able to do soemthing.  

	Most cases is, to delete or edit a snippet created by other user.
	'''
	def __init__(self):
		pass

	def __str__(self):
		return err_not_your_tag
