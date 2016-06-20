EDFDAT Explanation
=============================

The goal of this python package is to convert edf data files produced by eyelink into COM dat datafiles. 

The problem is that these two data formats have very different structures. 
edf files are provided as flexible text files that vary experiment to experiment, while dat files are binary with very strict structures. 

##flow of script

### Step 1. process edf file
This script parses a given edf file using a user defined mapping. 
edf files are populated with 3 kinds of information. 
</br>```calibration lines, message lines and sample lines.```  

the mapping file tells this script that for this given experiemnt specific messages are expected. and relate to events in the experiment. 

e.g.
if we wnt to know when the fixation was presented a message line like:
<br/>```MSG {timestamp} {message body a la "FIXATION PRESENTED"}```<br/>
would be somewhere in the edf file and the timestamp would tell us when the fixation was presented for that trial. 

after going through the edf file and getting all the information we can out of it. like what the paramset is, how many trials, etc etc.  we proceed to the next step.

### step 2. create and populate a datfile object
This step begins by creating a datfile object in memory. a datfile object is a representation of a literal .dat datafile. 

data files are organized into 1 or more discrete parts. 
every datafile begins with a directory. This file header contains information about the subject and any datasets within the file (such as their schemas location, size etc.)
Then a datfile con contain any number of datasets. Each dataset represents a single experiment. it follows a particular schema. in our labs case that schema is always sho18 (a description of which can be found elsewhere). 

a datfile object has two important data members. a directory and a list of datasets. 

but back to the flow of the script. 
a datfile object is created. initialization requires all the normal stuff found in a directory (i.e. who is the subject, yadda yadda).

after it is initialized a new dataset is added to contain the data harvested from the edf file. 
More specifically, a scho18 object is added to the datfile. scho18 is a class that describes a dataset adhering to the scho18 schema. 

this class has a function named populate. which requires all the data needed to fill a scho18 dataset. 

so the data from the edf is formatted into the proper scho18 format and passed to the datfile.scho18.populate function and the dataset is thusly filled with delicious information. in the proper way.


### step 3. write datfile object to a file

for this it is as simple as telling the datfile object to write itself to a file using the datfile.write method. and it will produce a .dat datafile. that (assuming) the mapping file is correct will be able to be analyzed by our matlab analysis programs.  


----------------------------


# Package Contents

This file has these important files. 

- dat_primitives.py
- datumobjects.py
- datfile.py
- edf.py
- \_\_main\_\_.py

I encourage you dear reader to investigate them more throughly using an ipython terminal and the help command. which will give you probably more up to date information about the objects themselves. Also feel free to enable the unittests at the bottom of each file which tests and shows example uses for each of the classes in that file. 

One more thing. in the \_\_init\_.py file you can set the printing levels for the terminal. play around with setting the levels closer to debug instead of warning. this will allow debug messages to be printed from different sources. it can quickly become a lot of text. so be careful. there is a complete transcript of all logged messages in debug.log within the package, which is completely overwritten each time the package is run.  

------

## \_\_main\_\_.py

**currently not implemented**
this is the entry point for the script. where it will orchestrate the interactions between the various other files. it's goals are thus:
1. prompt the user for an edf file and mapping file (which the user must predefine)
2. use the functions from edf.py to parse the edf file using the mapping definitions provided in the mapping file to create a dictionary of data from the edf file.  
3. create a datfile using functions from datfile.py to create and populate a new datfile object
4. finally write the datfile to an actual binary file. 

-------------

## datumobjects.py

a core concept of the datfile object is that of __datums__. in the terminology of this package a datum is a thing that holds a value. that value can be simple (like an integer or a string) or that value can be complex (like a groups of sub-datums [which in of themselves are actually just normal datums]) 

these are an important abstraction from using just lists of raw values because they can be made aware of themselves and their surroundings. This is important to making them flexible and user friendly. 

they support such things as initializing a datum and then later setting it's value, or providing a referance to a function instead of a value which can be later evaluated to find or update a value. They can also refer to and automatically update other datum objects (which is useful when one datum indicates how many values there are in a list which exists in a seperate datum)


this file contains the functions and classes having to do with datums.

the classes contained are:
- datum
- datumlist
- group
- repGroup

-------

### datum

this class defines what a datum is and how it works (with just a few exceptions) and has the following functions:

- \_\_init\_\_ 
    + initializes a new datum
- get_type
    + asserts all the conditions for a datum type or elem_type and returns the actual class referance to the dat_primitive
- set
    + sets the value of this datum. this is used for changing the value of a datum after initialization
- eval
    + in the case where a function was passed as a value to the datum. this will evaluate it, and return the result. 
    + it also casts the value to it's correct type to ensure compliance. 
    + called by set
- cast
    + casts the value of this datum to the correct type. 
    + if doing so throws some kind of error a log is made and the value is set to None
    + called by eval
- \_\_repr\_\_
    + returns a string representation of this datum
- \_\_str\_\_
    + returns a string representation of this datums
-  checkset_num_elems
    +  ensures num_elems has been correctly passed and sets the num_elems of this datum
-  checkset_elem_type
    +  ensures elem_type has been correctly passed and sets the num_elems of this datum
-  update
    + if this is a complex datum that contains subdatums. the children can call update on their parent. which will update the size and stuff of this datum. 
-  calc_size
    +  this figures out the current size of this datum in bytes. 
    +  internal functions should use this all the time, so this should always be up to date. 
-  \_\_getitem\_\_
    +  this is used by datums with indexable values (such as lists or repgroups) and returns the indicated value. 
    +  using this on a datum with an unindexable value will result in an error as it would with a raw value. 

----

### datumlist

this class is pretty much as you would expect. it's a list of datums. 
this is basically what datasets and directories are, except those classes have some additional rules they must adhere to. 

the importance of this object is that it is aware of multiple datums at once, and an ordering between them. this allows you to search through a datumlist for a specific datum, and figure out what the pointer to a specfic datum should be. 

it has the following functions:

- \_\_init\_\_
    + initializes a new datumlist. doesn't really do anything. besides set some initial values. 
- add
    + adds a new datum to this list. requires the same arguments as datum, so it basically just passes those on to datum.\_\_init_\_
- \_\_getitem\_\_
    + these lists support either integer indexing or indexing by name. 
- istypevalid
    + essentially the same as datum.get_type, except returns T/F.
    + not quite sure this is required.
- get
    + a utility for \_\_getitem\_\_ that searches through this list and returns the datum matching the name provided
- generate_datlist
    + used by get to generate a list of all the datums, including sub-datums within a repgroup, so they get searched through serially
    + this might need to be updated, a it may be implicated in a bug or two
- \_\_str\_\_
    + gets a string represntation of this for printing
- size_in_blocks
    + the size of this whole list in blocks (512 bytes apiece)
- size_in_words
    + the size of this whole list in words (4 bytes apiece)
- calc_size
    + figures out the size of this in whole list in bytes
- get_pointer
    + you can specify a precise datum or subdatum and this will calculate where in the dataset it will fall in bytes, offset from this datumlist

-----

### group

a group is essentially the same as a datumlist, with the exception that these are for use only inside repgroups. a repgroup will hold multiple groups all containing the same datums (however the values of each instance can be different)

e.g. <br/> 
this is a repgroup (a) containing 2 groups each with only 1 datum (b).

1. a (repGroup):
    1. b(integer in Group 1) = 2398294
    2. b(integer in Group 2) = 88888  

This class has the following functions. 

- \_\_init\_\_
    + essentially the same as when initializing a datumlist. however, groups exist within repgroups, and we need to maintain a double chain of objects in order to traverse the datumlist during searches and pointers. so it also remembers it's parent repgroup and datumlist
- generate_datlist
    + overrides datumlist.generate_datlist to include parents datumlists
- add
    + calls datumlist.add, then updates it's parents size

------

### repGroup

this is a special type for datums. most datums are simple types like integers or shorts or whatever, but some are more complicated. They are effectively the same thing. it's an object that holds a thing. that thing is usually a single value, but it can also be a repGroup object. 

repGroups have two imprtant data members. ```datums_arglist and groups``` 

the datums_arglist is a list of dictionaries, where the dictionaries contain all the arguments that should be passing into the add function of a group. It's important because all the groups in a repgroup need to have the same datums within them. so if we add a new group, that group needs to be initialized and all the datums must be added. this data member contains the information to do that. 

groups is simply a list of groups in this repGroup. they should all be initialized and maintained so that they all have the same datums at all times automatically. 

repGroups has the following functions.

- \_\_init\_\_
    + this initializes a repgroup. which doesn't really do anything except start empty lists for datums_arglist and groups, as well as set parent_datum and parent_datumlist if possible
- add_group
    + adds a group to this repgroup. and automatically populates it with all the datums this repgroup knows about, so it will be inline with all the others
- add
    + adds a new datum to all the groups in this repgroup and saves the arguments passed to a new entry in datums_argslist
- \_\_str\_\_
    + gets a str representation of this object
- \_\_getitem\_\_
    + only allows integer indexing to choose which group you would like to select
- calc_size
    + figures out how big this is in bytes. and updates self.size and parent datum.size


-----------------

## dat_primitives.py

this file contains classes that form the most low level values in this script. 
the problem is that python is far more abstracted than C++, it has no concepts of shorts and represents simple primitive values as actual objects in memory. Whereas C-type languages store them as memory in binary and reading/writing to files is pretty simple. 

these classes provide functions to read values such as these from a binary file, or to write to a binary file. they are also aware of their size and can pretty much be treated like normal values. the bulk of the work is done through the datum.cast function. 

the types we know about are:

- dat_int
- dat_short
- dat_float
- dat_uet
    + integers representing uet values are not a normal integer. they are constructed with the 3 least significant bytes from a timestamp and the least significant byte from a channel code.  
- dat_char
    + this represents a single char value.
- dat_strchunk
    + all strings must be sized to be indexed by word. i.e. even # of characters
    + so to accommodate that I implemented the normal string as a list of dat_strchunks, so each of these is 2 characters. 
- dat_str
- dat_list
    + a list is simply some number of values all of the same type in a row
    + the length should be recorded somewhere else probably. 
- dat_vec
    + unlike a list, a vector is always preceded by an integer with the number of values in the vector. i.e. lists can take up 0 bytes. but vectors always take at least 4 bytes.  


--------------

## datfile.py

this file contains the classes required to make datfiles. including 

- datfile **currently not implemented**
- dataset
- scho18
-  and any other schemas you would like to support for now we only use scho18. 

these pretty much can all be considered datumlists with extra rules. 
for instance a dataset is a datumlist that is required to start with the same 4 or 5 datums characterizing the nature of this dataset. 

scho18 is a further specification. because it takes a bunch of data and formats it into the same datums. whereas datasets in general don't have to adhere to any schema in particular. 

the only functions one would need to care about. would be the \_\_init\_\_ functions for datfile and scho18. which will require certain values, that should be pretty obvious. things like exp_date / subject_id / exp_time / desired_filename etc. and the populate function for scho18. 

the populate function takes a whole bunch of values required to fill out a sch018 schema. the arguments should be formatted according to that functions documentation. 



-----------

## edf.py

this file contains all the functions neccessary to parse both edf files as well as use the mapping files the user provides in order to parse them. 

**currently not implemented**


---------
