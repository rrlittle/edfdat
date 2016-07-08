''' this file contains the main stuff to actuall run this package.
	a user can run this from oe directory higher by entering `python edfdat`
	that will run the package, and __main__.py is the entrypoint.

	this prompts the user for edf files and mapping files then parses 
	it into a datfile.

	then it will drop you into an ipython interpreter so you can do whatever. 
	'''

from loggers import mainlog
from datumobjects import datum
import datfile
from edf import parse_edf
import utils



class main(object):
	''' make on of these to run the main protocol. this is 
		to make this easier to use from a terminal. 
		'''
	def __init__(self):
		''' run the protocol.  involves opening a datfile
			parsing an edf and making a dataset'''
		mainlog.warn('getting the datfile!')
		datfileobj = self.get_datfile()
		while True:
			mainlog.info('new loop in main. trying to add dataset')
			dset = None
			try: # catch errors thrown by new data_set or add_dataset
				dset = self.new_dataset()
			except Exception,e: mainlog.warn((	'error while creating '
												'dataset: %s')%e)
				# stop this loop somehow
				if self.get_done(): break
				else: continue
			try:
				datfileobj.add_dataset(dset)
			except Exception,e: mainlog.warn((	'error while '
												'adding dataset: %s')%e)
			# quit if they'd like
			if self.get_done(): break
			else: continue 
		mainlog.warn('writing datfile!')
		datfileobj.write()	

	def get_done(self):
		''' promts the user to see if they're done or not
			returns T/F or ends the program '''
			while True:
				inp = raw_input('done? (y/n/abort)').lower()
				mainlog.info('done? => %s'%inp)
				if inp == 'y': 
					mainlog.warn('done adding datasets')
					return True
				elif inp == 'n': 
					mainlog.warn('adding anonter dataset')
					return False
				elif inp == 'abort': 
					mainlog.warn('aborting program. nothing saved or modifed')
					utils.exit()
				else: 
					mainlog.warn('only accepts y/n/abort not %s'%inp)

	def new_dataset(self):
		'''function to prompt users for new dataset stuff'''
		mappfile = utils.get_mapping() # let user select mapping
		parsed = parse_edf() # turn edf file into a dic
		# apply map to parsed edf file to create a dataset object
		dset = utils.apply_map(parsed, mapfile)
		return dset

	def get_datfile(self):
		'''open/ make a datfile object/file'''
		while True:
			inp = raw_input((	'would you like a new dset (y/n)'
								' n will prompt you to grab existing')).lower()
			if inp == 'y': return self.create_datfile()
			elif inp == 'n': 
				datfilpath = utils.askopenfilename(
					title ='please select a datfile'	)
				mainlog.warn(	(	'opening datfiles is not implemented. '
									'please try again.')	)
				return datfile(openexisting=datfilepath)
			else: 
				mainlog.warn('%s is not a valid option. please try again'%inp)

	def create_datfile(self):
		''' prompt user for dset info'''
		mainlog.warn('datfiles require the subject id e.g. gordon')
		inp = raw_input(('please enter the subject id (forced to'
			' %d chars)')%datfile.ANID_LEN*2) 
			# *2 because strs are counted 2 chars at a time 
		return datfile(inp)

if __name__ == '__main__': 	
	main()