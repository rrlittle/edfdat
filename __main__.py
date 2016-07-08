''' this file contains the main stuff to actuall run this package.
	a user can run this from oe directory higher by entering `python edfdat`
	that will run the package, and __main__.py is the entrypoint.

	this prompts the user for edf files and mapping files then parses 
	it into a datfile.

	then it will drop you into an ipython interpreter so you can do whatever. 
	'''

from loggers import primlog, rglog, datumlistlog, datumlog, dsetlog
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
		datfileobj = get_datfile()
		while True:
			dset = new_dataset()
			datfileobj.add_dataset(dset)
			inp = raw_input('done? (y/n/abort)').lower()
			if inp == 'y': break
			elif inp == 'n': continue
			elif inp == 'abort': utils.exit()
		datfileobj.write()	

	def new_dataset():
		'''functino to prompt users for new dataset stuff'''
		mappfile = utils.get_mapping() # let user select mapping
		parsed = parse_edf() # turn edf file into a dic
		# apply map to parsed edf file to create a dataset object
		dset = utils.apply_map(parsed, mapfile)
		
	def get_datfile():
		'''open/ make a datfile object/file'''
		while True:
			inp = raw_input((	'would you like a new dset (y/n)'
								' n will prompt you to grab existing')).lower()
			if inp == 'y': return util.create_datfile()
			elif inp == 'n': 
				datfilpath = utils.askopenfilename(title ='please select a datfile')
				print 'opening datfiles is not implemented. please try again.'
				continue
				return datfile(open=datfilepath)
			else: '%s is not a valid option. please try again'



if __name__ == '__main__': 	
	main()