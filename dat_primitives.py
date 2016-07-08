'''
	dat_primitives is a file to contain different primitive data
	in data files. 

	they are necessary because python doesn't have a short object. 
	also they don't nativly read and write binary files. which is a 
	desirable quality. 

	so. think of them basically as primitives from java or c. 
	you should be able to compare them, add them index them etc. 
	they should be thought of as immutable. besides for reading. 
	but once they are set they are set. 

	you can set them during initialization or by reading them from a file. 
	for this reason the value they hold might be None. nonetheless 
	the still will have a size. 

	included are all the basics you'd want
	int, shorts, float, and chars. 

	we've also included lists and vectors. 
	lists hold an array of data. they must all be the same type and have the same size. 
	much like a C array. 

	types and other arguments like elem_type and num_elems must be set during 
	initialization and can be either other dat_primitives for python primitives.
	at least ones that make sense.
	'''


from utils import tobin # (val, bincode) turns val into  binary according to code
from utils import frombin # (binstr, bincode)  turns binary into val according to code
from utils import bin2hex # (binstr) turns binary into hex str preceded by \x
from utils import all_elems_same_type # (list) T iff elems are type, Typeerr if empty/nill
from cStringIO import StringIO as sio # string-like files
from loggers import primlog
import ipdb


class dat_type(object):
	''' wrapper for primitive data types. allowing us to read and write to them'''
	__name__ = 'generic'
	value = None # the value. this can does not have to be given during init 
	size = 0 # size in bytes
	defaultvalue = 0 # not used programatically, but you can use it to set sane defaults
	isset = False # If theres a value in this 
	def __init__(self, value = None, **kwargs): 
		'''asserts value is of type making sense to this type''' 
		primlog.debug('attempting to create %s. from %s: %s'%(type(self),value,  type(value)))
		if hasattr(self, 'size'): 
			self.size = self.size # make the class variable an instance variable

		try: # attempt to caste the value provided as a recognized  
			if value != None: self.value = self.cast_type(value)
		except Exception,e: 
			raise TypeError('%s: Value %s is not a castable to %s'%(e, value, type(self)))


		self.isset = not (self.value is None) # True if Value is not None 
		# else just allow it to pass
		primlog.info('Created %s: %s'%(type(self), self.__dict__))
	def read(self, fp): 
		'''reads from binary file and sets this'''
		binstr = self.process_binstr(fp.read(self.size)) # get binstr from file
		v = frombin(binstr, self.bincode) # convert binstr to value
		self.__init__(v) # recreate this with the new value.  
		primlog.info('Read in %s bytes. %s %s'%(self.size, type(self), self.__dict__))
		return self # return this to user
	def write(self, fp): 
		'''writes bin to fp. returns address of variable written''' 
		assert self.value is not None, 'Value must be set before writing'
		loc = fp.tell() # get current location 
		binstr = tobin(self.value, self.bincode) # convert value to binstr
		fp.write(binstr) # write binstr to file moving the fpointer
		return loc # return location of data
	def process_binstr(self, binstr):
		''' children of this class can overwrite this to process 
			binary strings read in from file. 
			must return the value they want to set as the value.

			but this gives children opportunity to set other instance variables 
			as they see fit. provide in case the value encodes deeper information
			'''
		return binstr
	def __repr__(self):
		'''returns string representation of this object'''
		return str(self.value)
	def __str__(self): 
		''' returns string representation of this object'''
		return str(self.value)
	def __int__(self): 
		''' return int representation of this object'''
		return int(self.value)
	def __mul__(self,other): 
		''' multiply self.value * other'''
		return self.value * other #  self * 2
	def __rmul__(self,other): 
		''' multiply other * self.value'''
		return self.__mul__(other) # 2 * self
	def __eq__(self, v2): 
		''' True IFF self == v2'''
		return self.value == v2
	def __ne__(self, v2): 
		''' True iff self != v2'''
		return not self.__eq__(v2) # self != 2
	def __index__(self): 
		''' allows for using this object as an index in an array 
			e.g. arr[self]'''
		return self.value # array[self]
	def __hash__(self): 
		''' used for setting keys in dicts '''
		return hash(self.value) # used for comparing keys in dicts
	def __add__(self, other): 
		''' does other + self.value '''
		return other + self.value 
	def __len__(self): 
		''' returns the length of this value. only for lists'''
		return len(self.value)
class dat_number(dat_type):
	''' included to give all number dats a common parent, 
		that excludes str and lists'''
	__name__ = 'Generic Number'
class dat_int(dat_number):
	''' used to hold integers and give them read/write to file'''
	__name__ = 'int'
	cast_type=int # try and cast it as an int
	size = 4 # size in bytes
	bincode = 'i' # integer using struct package
class dat_short(dat_int):
	''' used to hold shorts, python doesn't normally have them'''
	__name__ = 'short'
	size = 2 # size in bytes
	bincode = 'h' # short using struct package
class dat_float(dat_number):
	''' used to hold floats'''
	__name__ = 'float'
	cast_type=float # try and cast is as a float
	size = 4 # size in bytes
	bincode = 'f' # float using struct package
class dat_char(dat_type):
	'''	used to hold idividual characters using 1 byte apiece '''
	__name__ = 'char'
	cast_type=str # try and cast it as a string 
	size = 2 # size in bytes
	bincode = 'c' # char using struct package
	defaultvalue = ' '
class dat_strchunk(dat_char):
	''' this is a chunk of a string.
		strigs are word indexed in scho18
		not byte indexed. so they require 2 characters
		so they take an even number of bytes'''
	__name__ = 'str chunk'
	chars_per_chunk = 2
	size = chars_per_chunk * dat_char.size
	bincode = str(chars_per_chunk) + 's'
	defaultvalue = dat_char.defaultvalue * chars_per_chunk
	def process_num_elems(self, listvalues):
		''' overwrite the wrapper function of ddat_list
			'''
		return dat_str.process_num_elems(dat_str(), listvalues)
	def listify(self, listvalues):
		''' turns this into a list'''
		return dat_str.listify(dat_str(), listvalues)
		
class dat_uet(dat_int):
	''' UETs are very special Integers
		they code a UET event which is composed of a time and code
		and represnt it as an integer

		just like a normal dat_type
		they can be initialized immediately or read in from a file

		the code for uet integers is:
		(recall an int is 4 bytes)
		the first 3 encodes for time as an integer
		the last byte encode the code as a short. 

		so we need to 
		add 00 to the end of time 
		and 00 to the end of code to properly read them as int and short  
		'''
	__name__ = 'UET event'
	time = None
	code = None
	def __init__(self, value=None, code=None, time=None, **kwargs):
		''' override dat_type init because initilizing a uet value
			requires encoding time and code. which don't make sense 
			in normal dat_primitives.

			value is ignored. it's just required to deal with dat_types  
			read 
			'''
		# ipdb.set_trace()
		if type(value) == dict:
			if 'code' in value and code is None: code = value['code']
			if 'time' in value and time is None: time = value['time']
		if code is not None or time is not None:
			assert code is not None and time is not None, ('When building a %s '
				'event time and code must be provided')%(type(self))
			self.code = dat_short(code)
			bin_code_file = sio()
			self.code.write(bin_code_file) # write self.code to a string
			bin_code = bin_code_file.getvalue()

			self.time = dat_int(time)
			bin_time_file = sio()
			self.time.write(bin_time_file)
			bin_time = bin_time_file.getvalue()

			bin_val = bin_time[:-1] + bin_code[0]
			self.value = frombin(bin_val, self.bincode)
		# if they aren't provided leave them none. 
		# if value gets set via read it will set them as well.
		dat_type.__init__(self,value=self.value)
	def process_binstr(self, binstr):
		''' binstr represents self.value i.e. an integer, 
			but a special int which encodes a time (first 4 bytes) and uet 
			code(last 2 bytes) 
			this method is called when reading in from a file to set self.time 
			and self.code

			this is required to return the binstr to get set as value
			'''
		assert len(binstr) == self.size, 'binstr is the wrong size!'
		bin_code = binstr[-1] + '\x00'
		code = frombin(bin_code, dat_short.bincode)
		self.code = dat_short(code)

		bin_time = binstr[0:-1] + '\x00'
		time = frombin(bin_time, dat_int.bincode)
		self.time = dat_int(time)

		return binstr
	def __str__(self): return '%s (%s/%s)'%(self.value, self.time, self.code)
class dat_list(dat_type):
	''' more advanced thing. this holds an array of values
		requires:
		__elem_type__ to be another dat_class

		optional:
		if __num_elems__ is provided constrains the length of list to 
			that. it can be int or dat_int or dat_short
		 
		'''
	__name__ = 'list'
	def __init__(self, value=None, elem_type=None, num_elems=None, **kwargs):
		''' if value provided ensures all elements are elem_type,
			if num_elems is provided it will force vale to have that many elements
			but can be overridden during self.read

			after initialization you can rest assured that this will have:
			__self.elem_type__ and it will be a dat_type
			__self.value__ which will either be an array of dat_types or None
			__self.num_elems__ which will be None (if value is None) or a dat_int
			__self.size__ which will be 0 or the length of this in bytes


			NOTE: this only supprts elem_types of simple things. like chars, floats, 
			etc. but not lists of vectors or lists of lists etc.
		'''

		primlog.debug(('Creating %s given v=%s, '
					'etyp=%s, e=%s')%(type(self), value, elem_type, num_elems))

		if value is not None: # if value provided. ensure they're all the same type
			assert all_elems_same_type(value), 'Elems of %s not all same value'%value

		# figure out elem_type
		# if elem_type is already defiend we should not overwrite it
		if (elem_type != None 				# if elem_type provided
			and not hasattr(self, 'elem_type')): # and not predefined
			# it must be a dat_type
			assert issubclass(elem_type , dat_type), ('elem_type provided %s for %s '
				'must be child of dat_type')%(elem_type, type(self))
			# it can't be listlike
			assert not issubclass(elem_type, dat_list), ('elem_type provided %s to %s'
				'must not be child of dat_list, which is a complex dat_type'
				'')%(elem_type, type(self))
			# set elem_type
			self.elem_type = elem_type
		elif (not hasattr(self, 'num_elems')	# if type not provided 
			and not hasattr(self, 'elem_type')): # and not predefined.
			# they must provide value as an array of dat_types.
			assert value != None and hasattr(value, '__iter__'), (
											'when building %s no elem_type and '
											'bad value %s')%(type(self), value)
			# value can't be empty
			assert len(value) > 0, ('You must provide initialized list'
				' to values when building %s or include elem_type')%(type(self))
			# value must have dat_types if elem_type not provided
			assert isinstance(value[0], dat_type), ('You must provide initialized list'
				' to values when building %s or include elem_type')%(type(self))
			# set elem_type
			self.elem_type = type(value[0])
		else: pass # it's been predefined.
		

		# sanity checks these should always pass unless I fuqd up 
		assert hasattr(self, 'value'), '%s should have value'%type(self)
		assert hasattr(self, 'elem_type'), '%s should have elem_type'%type(self)
		assert hasattr(self.elem_type, 'size'), ('elem_type (%s) does not '
			'appear to valid')%self.elem_type
		assert hasattr(self.elem_type, 'bincode'), ('elem_type (%s) does not '
			'appear to valid')%self.elem_type

		self.value = value

		# need to set num_elems
		if num_elems != None: # it's been provided i.e. they want to force a length 
			primlog.debug('num_elems provided. setting num_elems = %s'%num_elems)
			self.num_elems = dat_int(num_elems)
		elif self.value != None: # it's not been provided, but they gave a value
			primlog.debug('num_elems not provided. figuring out what num_elems should be') 
			if hasattr(self.elem_type, 'process_num_elems'):
				num_elems = self.elem_type.process_num_elems(self.elem_type(), self.value)
			else: num_elems = self.process_num_elems(self.value)
			self.num_elems = dat_int(num_elems) # set it to the length passed
		else: 
			primlog.debug('num_elems cannot be determined. leaving None')
			self.num_elems = None # it was not provided and can't be determined

		self.checkval() # ensures self.value has correct types and length
		self.setsize() # set the size of this it is a dat_type after all
		primlog.info('Created %s: %s'%(type(self), self.__dict__))   
	def process_num_elems(self, listvalues):
		''' returns the number of elements in the value passed in '''
		return len(listvalues)
	def checkval(self): 
		''' ensures self.value is filled with dat_types'''
		if self.value is None: return # can do nothing
		if len(self.value) == 0: return # can do nothing

		# assure myself that it's full of the same type. this is probably redundant...
		assert all_elems_same_type(self.value), ('Somehow all elems are not the same in'
						' %s')%self.value 

		# check that they are all of the right type
		if isinstance(self.value[0], self.elem_type): return # job is done

		# they are pythonic primitives cast them or throw error 
		if hasattr(self.elem_type, 'listify'):
			self.value = self.elem_type.listify(self.elem_type(), self.value) # make a 
		else: 
			self.value = self.listify(self.value) # make a 
		self.value = [self.elem_type(v) for v in self.value] # convert them to elem_type

		# if we want to contrain value to some length, ensure we do.
		if self.num_elems is not None:
			self.value += [self.elem_type(self.elem_type.defaultvalue)]*self.num_elems 
			# add a bunch of defaults to the end
			self.value = self.value[:self.num_elems]

		# ensure num_elems is up to date
		self.num_elems = dat_int(len(self.value))
		self.isset = not (self.value is None)
	def listify(self, listvalues):
		''' breaks self.value into a list that can be iterated through one by one 
			can be overwritten by subclasses'''
		return  listvalues
	def setsize(self): 
		'''calculates and sets self.size'''
		self.size=0
		if self.value is None: return
		s = 0
		for v in self.value: s += v.size
		self.size= s 
	def read(self, fp, num_elems=None): 
		'''reads from a file and fills values and things'''
		if num_elems is not None: self.num_elems = dat_int(num_elems)
		assert self.num_elems is not None, ('num_elems was not set for '
					'this %s: %s')%(type(self),self.__dict__)
		val = []
		b_read = 0
		for i in range(self.num_elems):
			b_read += self.elem_type.size
			v = frombin(fp.read(self.elem_type.size), self.elem_type.bincode)
			val.append(self.elem_type(v))
		self.__init__(val, elem_type=self.elem_type, num_elems=self.num_elems)
		primlog.info('read %s bytes. %s : %s'%(b_read, type(self), self.__dict__))
		return self
	def write(self, fp): 
		'''write to a file. returns addr where it began'''
		assert self.value is not None, 'value must be set before writing'
		loc = fp.tell()
		for v in self.value:
			v.write(fp)
		return loc
	def __getitem__(self,k): 
		''' allows you to get specfic items from this list self[k]'''
		return self.value[k] # self[2]
class dat_vec(dat_list):
	''' this is effectively a list
		the only difference is that when writing to the file it is preceeded 
		by an integer describing the number of elements
	'''
	__name__ = 'vector'
	def read(self, fp):# override list, read an int first
		''' read a vec from a file'''
		b_read = 0
		n = dat_int()
		n = dat_int().read(fp)
		self.num_elems = n
		b_read += n.size
		v = []
		for i in range(self.num_elems):
			v.append(self.elem_type().read(fp))
			b_read += self.elem_type.size
		self.__init__(value=v, 
			elem_type=self.elem_type, 
			num_elems=self.num_elems)
		primlog.info('read %s bytes. %s : %s'%(b_read, type(self), self.__dict__))
		return self
	def write(self, fp): # override list. write an int first
		''' write a vec to a file'''
		assert self.value is not None, 'value must be set before writing'
		loc = fp.tell()
		self.num_elems.write(fp)
		for v in self.value:
			v.write(fp)
		return loc
	def setsize(self):
		'''figure out what the size of this is based on the num_elems and 
			elem_type then set self.size'''
		self.size = dat_int.size
		if self.value is None: return
		s = dat_int.size
		for v in self.value:
			s += v.size
		self.size = s
class dat_str(dat_list):
	''' strings are lists of dat_strchunk
		which means that they will always have an even number of characters
		that is important because dat files always maintain word alignment'''
	__name__ = 'str'
	elem_type = dat_strchunk # strings are lists of chars
	def __str__(self): 
		'''return string representation of self'''
		if self.value == None: return str(self.value)
		return ''.join([str(v) for v in self.value])
	def process_num_elems(self, listvalues):
		'''override dat_list s process_num_elems
			because if list of values is a string we need to break it into 
			4 byte words rather than single chars and len('abcd') == 4, we want 2
			throw an error if string not indexable by word is passed in '''
		# if listvalues is a list of dat_strchunks already we have nothing to do
		if len(listvalues) == 0: return 0 # if it's empty. we have nothing to do  
		if isinstance(listvalues[0], self.elem_type): return len(listvalues)

		# listvalues should be a string right now. 
		listvalues = str(listvalues) # cast values passed in as str, to assure it's a str
		
		if len(listvalues)%2 != 0: listvalues += dat_char.defaultvalue
		return len(listvalues)/2 
	def listify(self, listvalues):
		'''override dat_list's listify because if listvalues is a string 
			we need to break it into 2 char increments '''
		primlog.debug('Listifying %s'%listvalues)
		# if its empty, doesn't matter
		if len(listvalues) == 0: return listvalues
		# if it's full of self.elem_types its already good
		if isinstance(listvalues[0], self.elem_type): return listvalues

		listvalues = str(listvalues)
		primlog.debug('Cast listvalues to string -> %s'%listvalues)
		if len(listvalues)%2 != 0: listvalues += dat_char.defaultvalue
		# iterate over str in chunks of 2
		listvalues = [listvalues[i:i+2] for i in range(0,len(listvalues),2)]
		primlog.debug('listify returning %s'%listvalues)
		return listvalues


class unittests():
	'''contiains testing code for development'''
	def __init__(self):
		''' every primitive can be set initially, or be read into
			then it can be printed or written to a file

			test that with each type 
			'''
		primlog.warn('### Primitive Unit tests\n')
		self.inttest()
		self.shorttest()
		self.floattest()
		self.chartest()
		self.uettest()
		self.listtest() # test complex dat_types
		self.vectest()
		self.strtest()
		primlog.warn('### Primitive Unit Tests Passed!\n#####################\n\n\n')

	def inttest(self): 
		primlog.warn('###Testing Integers\n')
		primlog.warn('###dat_int(5)  printing and writing')
		d = dat_int(5)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_int().read(5 = x05x00x00x00)')
		s = sio('\x05\x00\x00\x00')
		d = dat_int()
		d.read(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_int(dat_int(5))  printing and writing')
		d = dat_int(dat_int(5))
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Integers Complete\n##########\n\n')
	def shorttest(self): 
		primlog.warn('###Testing Shorts\n')
		primlog.warn('###dat_short(5)  printing and writing')
		d = dat_short(5)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_short().read(5 = x05x00)')
		s = sio('\x05\x00')
		d = dat_short()
		d.read(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Shorts Complete\n##########\n\n')
	def floattest(self): 
		primlog.warn('###Testing Floats\n')
		primlog.warn('###dat_float(5.6)  printing and writing')
		d = dat_float(5.6)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_float().read(5.6 = 33 33 b3 40)')
		s = sio('\x33\x33\xb3\x40')
		d = dat_float()
		d.read(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Floats Complete\n##########\n\n')
	def chartest(self): 
		primlog.warn('###Testing Chars\n')
		primlog.warn('###dat_char(a)  printing and writing')
		d = dat_char('a')
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_char().read(a = 61)')
		s = sio('\x61')
		d = dat_char()
		d.read(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Chars Complete\n##########\n\n')

	def uettest(self): 
		primlog.warn('###Testing UETs\n')
		primlog.warn('###dat_uet(time=80000,code=9)  printing and writing')
		d = dat_uet(time=80000,code=9)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###UETs Complete\n##########\n\n')

	def listtest(self): 
		primlog.warn('###Testing lists\n')
		primlog.warn('###dat_list([1,2,3],elem_type=dat_int)  printing and writing')
		d = dat_list([1,2,3],elem_type=dat_int)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_list([1,2,3],elem_type=dat_int,num_elems=6)')
		d = dat_list([1,2,3],elem_type=dat_int,num_elems=6)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###lists Complete\n##########\n\n')
	def vectest(self): 
		primlog.warn('###Testing Vectors\n')
		primlog.warn('###dat_vec([1,2,3],elem_type=dat_int)  printing and writing')
		d = dat_vec([1,2,3],elem_type=dat_int)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Vectors Complete\n##########\n\n')

	def strtest(self): 
		primlog.warn('###Testing Strs\n')
		primlog.warn('###dat_str(abc)  printing and writing')
		d = dat_str('abc')
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_str(abc, num_elems=6)  printing and writing')
		d = dat_str('abc',num_elems=6)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###dat_list(abc, elem_type=dat_strchunk, num_elems=6)')
		d = dat_list('abc',num_elems=6,elem_type=dat_strchunk)
		s = sio()
		d.write(s)
		primlog.warn('###prints: %s, writes: %s'%(d,bin2hex(s.getvalue())))
		primlog.warn('###Strs Complete\n##########\n\n')
# unittests()