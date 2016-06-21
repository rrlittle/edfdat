''' this file contains the main stuff to actuall run this package.
	a user can run this from oe directory higher by entering `python edfdat`
	that will run the package, and __main__.py is the entrypoint.

	this prompts the user for edf files and mapping files then parses 
	it into a datfile.

	then it will drop you into an ipython interpreter so you can do whatever. 
	'''

import IPython
from loggers import primlog, rglog, datumlistlog, datumlog, dsetlog
from datumobjects import datum
import datfile

def process_edf_file():
	''' this function prompts the user for an edf file and for 
		a mappings file to convert the edf files into a datfile. 

	'''
	pass 


if __name__ == '__main__': 
	process_edf_file()

IPython.embed(local_ns = locals())
