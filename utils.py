import struct as s # used to convert python primitives to c structs
import binascii as ba # convert binary to readable strings visa versa
from inspect import isclass
from datetime import datetime
import logging
from os.path import isfile
from math import ceil
from Tkinter import Tk
from tkFileDialog import askopenfilename

Tk().withdraw()

class null_logging: 
	''' an empty logger that can be used instead pf logging
		hopefully this will help stop double printing using
		the logging module. 
		'''
	def debug():pass
	def info():pass
	def warning():pass
	def error():pass
	def critical():pass
null_log = null_logging() # default logger

def frombin(binstr,bincode):
	''' returns value determined by bincode of binstr
		see struct documentation for bincode specs'''
	return s.unpack(bincode,binstr)[0]
def tobin(v,bincode):
	''' returns binstr determined by bincode of v
		see struct documentation for bincode specs'''
	return s.pack(bincode, v)
def make_logger(logname, 
	frmt='%(name)s:%(levelname)s[%(filename)s.%(funcName)s]>%(message)s', 
	fpath=None, 
	stdout=True, 
	flvl=None,
	lvl=logging.DEBUG): 
	''' makes a simple intuitive logger. every time you call this
		you can define what it will look like and where ii will go etc. 
		if fpath is provided it will log to a file given by fpath. 
		by defualt the file will have the same level as the logger. but you can
		override that with flvl to be any logging level
		CRITICAL	50
		ERROR	40
		WARNING	30
		INFO	20
		DEBUG	10
		NOTSET	0

		when this is created the logfile is truncated. but then appended to. 
		so if your manking a bunch of these you should make them all at the beginning
		so you truncate a few times and then fill it up from a varitey of sources. 
		'''
	l = logging.getLogger(logname)
	l.setLevel(logging.DEBUG) 
	# the base will see everything and handlers will decide
	f = logging.Formatter(frmt)
	if stdout: 
		sh = logging.StreamHandler()
		sh.setFormatter(f)
		sh.setLevel(lvl)
		l.addHandler(sh)
	if fpath:
		fh = logging.FileHandler(fpath, mode='a')
		fh.setFormatter(f)
		if flvl: fh.setLevel(flvl)
		else: fh.setLevel(lvl)
		l.addHandler(fh)

	return l
def truncfile(fpath):
	if isfile(fpath): # if it's an exisiting file, truncate it  
		f = open(fpath, mode='w')
		f.truncate()
		f.close()
	
def checkstr(string, length):
	'''ensures strings are the desired length'''
	return (string + " "*length)[0:length]
def all_elems_same_type(listlike):
	''' given an interable checks if they are of the same type
		returns T/F
		T iff listlike is empty or full of things with the same type'''
	try:
		types = [i.__class__ for i in listlike]
		s = set(types)
		return len(s) <= 1
	except:
		return False
def findDatum(datum_uid, datum_list, ind=False): # finds specific datum
	''' returns first instance of datum from collection of datums 
		if ind is True (False by default) return the index of 
		else returns False'''
	for i,d in enumerate(datum_list):
		if datum_uid == d.id: 
			if ind:	return i
			return d
	return None
def bin2hex(binstr):
	''' returns a string with hex values to print out nicely '''
	return ba.hexlify(binstr)
def time2timestr(timeobj):
	''' pass in a time object and returns a formatted date string
		DDMM-YY'''
	assert isinstance(timeobj, datetime), 'this function assumes a datetime object'
	day = ('00' + timeobj.day)[:-2] 
	month = ('00' + timeobj.month)[:-2]
	year = ('00' + timeobj.year)[:-2]
	return '%s%s-%s'%(day,month,year)
def roundup(decimal): return ceil(decimal)


wordsize = 4.0 # number of bytes to a word
blocksize = 512.0 # number of bytes to a block



###### TO DO
def verify_task_def(task_def_module):
	''' this ensures task definition file is 'well formatted'
		i.e. it contains everything needed to parse an edf file
		and create a dat file from it. 
		'''
	raise NotImplementedError
def load_task_defs():
	''' task definitions are saved as python modules in 
		eyelink_task_definitions 

		this loads them into the program '''
	raise NotImplementedError
