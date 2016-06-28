Developer Notes
================

Todo
----------
1. implement Datfile class within datfile.py
    
    this class would represent an entire datfile object. 
    every datfile is composed of a directory and a number of 
    datasets. 

    - \_\_init\_\_  it will need to initialize a directory and an empty list of datasets.
     
    - add_dataset funciton. it probably would be easiest to pass it a populated dataset object. then developers should probably be prompted with all the arguments required, you'd also have to specify what dataset schema you'd like to use. which would require extra meta-data somehow. or involve a more complex call. However then you would rely on the user to set the dataset id, which could result in malformed datfiles. but since we're using this to make new datfiles every time it won't be that bad. a workaround would be to overwrite the datset id within this function, which is viable. 
        + this function would add an entry to the directory and save the dataset object in an array of it's datasets.
        + one complex thing would be to figure out the pointer to the block where the dataset lives. we don't really have a way to find pointers between datalists. 
        + this class would be a child of a datumlist, so it can calculate it's own size already (inherited from datumlist). You can mod the size by block size (512 bytes) to figure out how many blocks this takes. then the next block is where the dataset starts.
    - write function. which will write the directory to a file, then fill up the rest of the block with null bytes (or just use seek to force the file to be big enough). and finally write each dataset, being sure to align the blocks. 

2. implement directory class within datfile.py
    
    this is exaclty like a dataset. except that it has some different datums yeah. so this should be supes easy. 

    - \_\_init\_\_ this function takes the required datums and asserts their correct. and sets them
    
    - add_dataset this funciton should takes a dataset object and adds it to the directory. basically you need to populate the diretory header entry for the dataset. all the required stuff is already in the datset. 

3. implement edf.py
    
    this will require a bunch of functions to parse edf files. most of those are already implemented in parseedf.py in the test-scripts edf_learning_environment on my github (https://github.com/rrlittle/edfdat_learning_environment)

    it will also need a function that takes a mapper (yet to be precisely defined) that will be able to create a dataset object from the stuff in the eyelink file. that will be very experiment specific and also have to understand some stuff about what the dataset needs. probably making some assumptions too. 

4. implement \_\_main\_\_.py

    this will prompt you for a edf file, mapping file and what dataset to use (maybe. that might be handled by the mapping file.)

    and then do all the things. 

    1. parse the edf file. 
    2. use the mapping file/script to produce a datset 
    3. initialize datfile
    4. add the dataset
    5. write it to a file

5. implement mapping script plugins. 

    this is the only part that really will take a bit of thought. 
    we need to figure out a way to define all the required datums for the datasets populate function. 

    probably this will take the form of a python file. 
    all variables such as channels and things that don't change can be predefined within the file. 
    it could import a specific dataset and initialize it there. 

    it also needs to parse the messages embedded into the eyelink experiment. and figure out what they mean. that will be stuff like was the experiment successful or not. things of that nature. 

    probably how it will work is developers will make a new one for every experiment and include the in a special directory that will be loaded when main is run using the sys.listdir() and \_\_import\_\_() trick 




General EDFDAT Explanation
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


> Help on module edfdat.datumobjects in edfdat
> 
> NAME
>     edfdat.datumobjects - This file contains datums and stuff made form datums such as datum lists
> 
> FILE
>     /home/silverfish/Documents/populin/datedf workspace/edfdat/datumobjects.py
> 
> DESCRIPTION
>     
>     
>     We need a way to organize the raw data into sets. 
>     we'll call these datumlists in general.
>     
>     because in general they are just list of datum objects. 
>     
>     This file contains the datumlist class as well as it's subclasses. 
>     e.g. groups (used by repeatgroups)
>     e.g. dset headers (mandatory for all datasets in datafiles)
>     e.g. directory (a special dataset at the beginning of all dat files 
>         describing what dsets are in the datfile)
>     e.g. specific data schemas e.g. sho18
>     
>     when creating a dataset you are really defining a schema. with the option of 
>     filling it in. which if you want it full of data you probably should. 
>     
>     to use a dataset first declare it. 
>     dset = dataset(<mandatory header stuff as python primitives>)
>     
>         if you don't include the stuff you will not be able to write it. 
>         but again, you're really just defining a schema. so it doesn't have to 
>         contain any actual data.
>     
>     then add datums to fit your schema
>     dset.add(<datum defininition>)
>     
>         the datum defininitions are exactly the same as the datums.datum class
>         With the major exception that you can provide other datum names instead of 
>         values for any kwarg values including elem_type,num_elems, etc.
>         but not for typ or value 
>     
>         again they don't need to be filled. a datum is a placeholder in a schema. 
>         they can't be written to a file unless they can be evaluated to a value
>         but they can still exist. (datums are data too!)
>     
>     e.g.
>         see datum documentation for more on why 
>     
>         dset.add('Num Vars', 'int')
>         dset.add('Vars', 'rg', num_elems='Num Vars') 
>             # the above links the number of groups in 'Vars' to the value of 'Num Vars' 
>             # i.e. 'NUM Vars has just been set to 0, because this has no groups
>     
>         dset['Vars'].add('Name', 'str', num_elems=4) # 8 characters  
>         dset['Vars'].add('Type', 'short')
>         dset['Vars'].add('Words', 'short')
>         dset['Vars'].add('Value', 'list', elem_type='Type', num_elems='Words')
>             # the above added 4 datums to the repeatGroup 'Vars'
>             # which defines a single variable that we want to save.
>             # the type of the variable is coded by a short 
>             # the number of 4byte words in the variable is defined by the 'Words' datum
>             # the value of the variable is saved in 'Value' 
>     
>             # the Value 'datum' is the most important as it's the most complex
>             # When you define the type of a datum by specifying another datum  
>             # the datum referred will not be set upon updating the value datum
>             # i.e. once we set value, the 'Words' datum will be updated but the 'Type'
>             #     datum will not. 
>     
>         dset['Vars'].add_group() # adds a group to the repeat group
>             # this command created a group within the repGroup and 4 datums empty
>             # within that as if these were called:
>             #   datum('Name','str',num_elems=4)
>             #   t = datum('Type','short')
>             #   w = datum('Words','short')
>             #   datum('Value','list',elem_type=t,num_elems=w) 
>             # this implies that datums must be able to take datum arguments. 
>             # this also updates 'Num vars' to 1
>     
>         dset['Vars'][0]['Name'].set('var1') # this gets expanded to 8 char2 (8 words)
>         dset['Vars'][0]['Type'].set(1) # codes for an int array
>     
>         # BAD!!!
>         dset['Vars'][0]['Value'].set('hello world') # elem_type is set to int!
>             # threw error
>     
>         # Good  
>         dset['Vars'][0]['Value'].set([1,2,3]) # elem_type is set to int!
>             # this set num_elems to be 3, because we tried to evaluate 'Words' and 
>             # it returned None. as it wasn't set
>     
>         #---------------- NEXT GROUP
>     
>         dset['Vars'].add_group() # adds a group to the repeat group
>             # this also updates 'Num vars' to 2
>     
>         dset['Vars'][1]['Name'].set('var2') # this gets expanded to 8 char2 (8 words)
>         dset['Vars'][1]['Type'].set(3) # codes for an str
>         dset['Vars'][1]['Words'].set(2)
>         dset['Vars'][1]['Value'].set('hello world') # saves 'hell'  
>             # this does not update 'Words', rather it truncates the value 
>             # this is the same operation as before. but now Words evaluated to 2. 
>     
>     
>         dset.add('Extra var', 'int', value=1) # adds and sets the datum right away. 
>         
>         print dset
>         > NUM VARS [int] : 2
>           Data [rg] :
>             0   -   Name [str]: 'var1    '
>                     Type [short]: 1
>                     Words [short]: 3
>                     Value [list]: [1,2,3]
>             1   -   Name [str]: 'var2    '
>                     Type [short]: 3
>                     Words [short]: 2
>                     Value [list]: 'hell'
>          Extra var [int]: 1
>         dset.write(sio()) # writes to a file 
>         # Num vars        [0]name                [0]type [0]Words  [0]Value[0] ...
>         > 02 00 00 00 | 76 61 72 31 20 20 20 20 | 01 00 | 03 00 | 01 00 00 00 | ...
> 
> CLASSES
>     __builtin__.object
>         datum
>         datumlist
>             group
>     datmlistunittests
>     datumunittests
>     repGroup
>     exceptions.Exception(exceptions.BaseException)
>         elem_typeError
>         num_elemError
>         typError
>         val_func_error
>     
>     class datmlistunittests
>      |  Methods defined here:
>      |  
>      |  __init__(self)
>      |  
>      |  testdatumlist(self)
>      |  
>      |  testdatumlistwithrepgroup(self)
>     
>     class datum(__builtin__.object)
>      |  this is the holder for all data objects in 
>      |  a data file. 
>      |  every one must have a name. 
>      |  and a type. 
>      |  
>      |  some types require or can accept different kwargs. 
>      |  for instance.
>      |  type 'str' can accept num_elem = # which forces it to be # chars long. 
>      |  type 'list' requires elem_type = simple_type, which forces all elems to be type
>      |  
>      |  num_elems and elem_type can also be Number datum objects. 
>      |  the value contained by the datum will be evaluated and use in place. 
>      |  a referance to the datum itself will also be saved as self.num_elems_datum 
>      |  and self.elem_type_datum.
>      |  
>      |  num_elems_datum, if its not set when this is set (and this is an applicable type)
>      |  num_elems_datum will be updated when this is set. 
>      |  
>      |  elem_type_datum ,ust be set before this is set.
>      |  
>      |  Methods defined here:
>      |  
>      |  __getitem__(self, k)
>      |  
>      |  __init__(self, name, typ, val=None, num_elems=None, elem_type=None, code=None, time=None, description='no description', parent_datumlist=None)
>      |      we need to parse these slightly differently for each of the 
>      |      different types. also we need to allow for functions
>      |  
>      |  __repr__(self)
>      |  
>      |  __str__(self)
>      |  
>      |  calc_size(self)
>      |  
>      |  cast(self, value)
>      |      casts value to self.elem_type, uses various kwargs this knows about
>      |  
>      |  checkset_elem_type(self, elem_type)
>      |  
>      |  checkset_num_elems(self, num_elems)
>      |      checks that num_elems is decent 
>      |      and sets things appropritatley for the set call
>      |  
>      |  eval(self)
>      |      returns the value of this datum. that is if this contains a function
>      |      it will update the value and return it.
>      |  
>      |  get_type(self, typ)
>      |      asserts all the conditions for a datum type or elem_type
>      |      and returns the actual class referance to the dat_primitive
>      |  
>      |  set(self, value)
>      |      sets the value of this datum. if we have a function call it, then
>      |  
>      |  update(self)
>      |      updates self.__dict__
>      |      from self.value. used when value is a repeat group 
>      |      and changes without interfacing with this datum at all. 
>      |      so the repgroup will get updated and change it's num_elems
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors defined here:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  attrs_to_update = ['num_elems', 'size', 'isset', 'add_group', 'add']
>      |  
>      |  code = None
>      |  
>      |  description = None
>      |  
>      |  did = None
>      |  
>      |  elem_type = None
>      |  
>      |  func = None
>      |  
>      |  isset = False
>      |  
>      |  name = None
>      |  
>      |  num_elems = None
>      |  
>      |  parent_datumlist = None
>      |  
>      |  recognized_types = {1: <class 'edfdat.dat_primitives.dat_int'>, 2: <cl...
>      |  
>      |  time = None
>      |  
>      |  typ = None
>      |  
>      |  value = None
>     
>     class datumlist(__builtin__.object)
>      |  this is a list of datums. 
>      |  
>      |  you can add datums to this list one by one. by calling datumlist.add
>      |  this func will construct a new datum. just as if you constructed a new datum
>      |  manually. however this has the added advantage of being aware of other datums.
>      |  Due to this you can avoid passing values to datums directly.
>      |  
>      |  you can instead refer to other datums by name for certain kwargs. 
>      |  When it comes time to create the new datum the referred datums will be evaluated
>      |  and the value in those datums will be passed to the newly constructed datum. 
>      |  
>      |  if the datum referred is not set at the time, the behavior varies depending 
>      |  on the kwarg indicated. 
>      |  
>      |  see the add foo docs for specifics. but an example is if you use a datum 
>      |  to define num_elems, and don't set the referred datum
>      |  then after setting the new datum the referred datum will be updated
>      |  
>      |  Methods defined here:
>      |  
>      |  __getitem__(self, k)
>      |  
>      |  __init__(self)
>      |  
>      |  __str__(self)
>      |  
>      |  add(self, name, typ, value=None, num_elems=None, elem_type=None, code=None, time=None, description=None)
>      |      add a new datum to this datumlist
>      |      this constructs a datum. which can be quite an involved thing. 
>      |      
>      |      _dname__ is the name of the new datum. 
>      |      
>      |      __typ__ is the type that the datum will be. this must be a string or integer
>      |       representing a dat_type, see datum docs for more.
>      |      
>      |      _dvalue__ will be the value of the created datum. this is not neccessary to 
>      |      include. as you can set the value of the datum later. 
>      |      
>      |      
>      |      __num_elems__ can be provided for lists, vectors, and strings. if provided 
>      |      they will constrian the length of their values. however this can be overridden
>      |      in the case of vectors by reading a file.
>      |      
>      |      this can be another datum name as well. If it refers to another datum, and 
>      |      that datum is not set, updating this datum (via set) will update that datum.
>      |      however, updating that datum after this datum will not change this datum. 
>      |      If the referred datum is set. then the value of that datum will be used to 
>      |      constrain this datums value.  
>      |      
>      |      __elem_type__ required for lists and vectors. must be a string or int 
>      |      representing a dat_type. see datum docs for more. It can also be a ref to 
>      |      another datum. that datum must be able to be evaluated before creating this 
>      |      datum
>      |  
>      |  calc_size(self)
>      |  
>      |  generate_datlist(self)
>      |      for a generic datlist it simply returns self.datums. but subclasses can 
>      |      overridden this func and generate new ones to search through. basically 
>      |      in an effort to enumerate the namespace availble to individual datums if 
>      |      referance ing other datums.
>      |  
>      |  get(self, name, pos=False)
>      |      generates a datumlist to search through then returns the first datum
>      |      of the indicated name or None
>      |      if pos is True, returns byte offset from beginning of datumlist as
>      |      well as datum in dict with keys pos and datum
>      |  
>      |  get_pointer(self, datums, ret_datum=False)
>      |      returns word where specified datums are from
>      |      datums should be a list describing the hirearchical 
>      |      location of the desired location. 
>      |      e.g. to find b,1c,2d in the datum list constructed like so
>      |      a: sasd
>      |      b:
>      |          1-c:
>      |              1-d:adskhfjd
>      |              2-d:asdasdf
>      |          2-c:
>      |              1-d:asdkfasdf
>      |              2-d:sdaflsf
>      |      you would provide datums like so:
>      |      [{name:b},{name:c,index:1},{name:d,index:2}]
>      |      if any index is out of range an IndexError will be raised.
>      |      if this path can't be found. -1 will be returned
>      |      if ret_datum is true. will return datum, loc
>      |  
>      |  istypevalid(self, dtyp)
>      |      assures that dtyp is either a recognized type or
>      |      is the name of a known datum
>      |  
>      |  size_in_blocks(self)
>      |  
>      |  size_in_words(self)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors defined here:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  datums = []
>     
>     class datumunittests
>      |  Methods defined here:
>      |  
>      |  __init__(self)
>      |  
>      |  pass_datums_to_datums(self)
>      |  
>      |  repGroup(self)
>      |  
>      |  set_simple_datums_later(self)
>      |  
>      |  simple_datum(self)
>     
>     class elem_typeError(exceptions.Exception)
>      |  for use if elem_type is wrong
>      |  
>      |  Method resolution order:
>      |      elem_typeError
>      |      exceptions.Exception
>      |      exceptions.BaseException
>      |      __builtin__.object
>      |  
>      |  Data descriptors defined here:
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.Exception:
>      |  
>      |  __init__(...)
>      |      x.__init__(...) initializes x; see help(type(x)) for signature
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from exceptions.Exception:
>      |  
>      |  __new__ = <built-in method __new__ of type object>
>      |      T.__new__(S, ...) -> a new object with type S, a subtype of T
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.BaseException:
>      |  
>      |  __delattr__(...)
>      |      x.__delattr__('name') <==> del x.name
>      |  
>      |  __getattribute__(...)
>      |      x.__getattribute__('name') <==> x.name
>      |  
>      |  __getitem__(...)
>      |      x.__getitem__(y) <==> x[y]
>      |  
>      |  __getslice__(...)
>      |      x.__getslice__(i, j) <==> x[i:j]
>      |      
>      |      Use of negative indices is not supported.
>      |  
>      |  __reduce__(...)
>      |  
>      |  __repr__(...)
>      |      x.__repr__() <==> repr(x)
>      |  
>      |  __setattr__(...)
>      |      x.__setattr__('name', value) <==> x.name = value
>      |  
>      |  __setstate__(...)
>      |  
>      |  __str__(...)
>      |      x.__str__() <==> str(x)
>      |  
>      |  __unicode__(...)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from exceptions.BaseException:
>      |  
>      |  __dict__
>      |  
>      |  args
>      |  
>      |  message
>     
>     class group(datumlist)
>      |  these are the things that get held in a repeat group
>      |  we need to
>      |  
>      |  Method resolution order:
>      |      group
>      |      datumlist
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  __init__(self, parent_datumlist, parent_repGroup)
>      |  
>      |  add(self, name, typ, value=None, num_elems=None, elem_type=None, code=None, time=None, description=None)
>      |      wrapper for super add. we need to update self.parent_datumlist.size
>      |  
>      |  generate_datlist(self)
>      |      overrides datumlist.generate_datlist this includes parents datums 
>      |      as well as self's datums.
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  parent_datumlist = None
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from datumlist:
>      |  
>      |  __getitem__(self, k)
>      |  
>      |  __str__(self)
>      |  
>      |  calc_size(self)
>      |  
>      |  get(self, name, pos=False)
>      |      generates a datumlist to search through then returns the first datum
>      |      of the indicated name or None
>      |      if pos is True, returns byte offset from beginning of datumlist as
>      |      well as datum in dict with keys pos and datum
>      |  
>      |  get_pointer(self, datums, ret_datum=False)
>      |      returns word where specified datums are from
>      |      datums should be a list describing the hirearchical 
>      |      location of the desired location. 
>      |      e.g. to find b,1c,2d in the datum list constructed like so
>      |      a: sasd
>      |      b:
>      |          1-c:
>      |              1-d:adskhfjd
>      |              2-d:asdasdf
>      |          2-c:
>      |              1-d:asdkfasdf
>      |              2-d:sdaflsf
>      |      you would provide datums like so:
>      |      [{name:b},{name:c,index:1},{name:d,index:2}]
>      |      if any index is out of range an IndexError will be raised.
>      |      if this path can't be found. -1 will be returned
>      |      if ret_datum is true. will return datum, loc
>      |  
>      |  istypevalid(self, dtyp)
>      |      assures that dtyp is either a recognized type or
>      |      is the name of a known datum
>      |  
>      |  size_in_blocks(self)
>      |  
>      |  size_in_words(self)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from datumlist:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from datumlist:
>      |  
>      |  datums = []
>     
>     class num_elemError(exceptions.Exception)
>      |  for use if num_elems is wrong
>      |  
>      |  Method resolution order:
>      |      num_elemError
>      |      exceptions.Exception
>      |      exceptions.BaseException
>      |      __builtin__.object
>      |  
>      |  Data descriptors defined here:
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.Exception:
>      |  
>      |  __init__(...)
>      |      x.__init__(...) initializes x; see help(type(x)) for signature
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from exceptions.Exception:
>      |  
>      |  __new__ = <built-in method __new__ of type object>
>      |      T.__new__(S, ...) -> a new object with type S, a subtype of T
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.BaseException:
>      |  
>      |  __delattr__(...)
>      |      x.__delattr__('name') <==> del x.name
>      |  
>      |  __getattribute__(...)
>      |      x.__getattribute__('name') <==> x.name
>      |  
>      |  __getitem__(...)
>      |      x.__getitem__(y) <==> x[y]
>      |  
>      |  __getslice__(...)
>      |      x.__getslice__(i, j) <==> x[i:j]
>      |      
>      |      Use of negative indices is not supported.
>      |  
>      |  __reduce__(...)
>      |  
>      |  __repr__(...)
>      |      x.__repr__() <==> repr(x)
>      |  
>      |  __setattr__(...)
>      |      x.__setattr__('name', value) <==> x.name = value
>      |  
>      |  __setstate__(...)
>      |  
>      |  __str__(...)
>      |      x.__str__() <==> str(x)
>      |  
>      |  __unicode__(...)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from exceptions.BaseException:
>      |  
>      |  __dict__
>      |  
>      |  args
>      |  
>      |  message
>     
>     class repGroup
>      |  a repgroup is a possible value for a datum. 
>      |  
>      |  defined by datum(NAME, 'rg', num_elems=None) num_elems can be either a datum or
>      |      integer 
>      |  
>      |  and filled via two methods. add, which overrides datumlists, and adds a new datum 
>      |  archetype
>      |  and add_group. which adds a group. all groups will have the same datums in them
>      |  and adding a datum will add it to all of them. 
>      |  
>      |  these also support numeric indexing to access group objects. which are simply 
>      |  further datumlists.
>      |  
>      |  Methods defined here:
>      |  
>      |  __getitem__(self, k)
>      |  
>      |  __init__(self, parent_datum=None, parent_datumlist=None, num_elems=None, **kwargs)
>      |      initializing a repeat group doesn't do much. it will assign 
>      |      self.parent_datumlist to be the provided parent_datumlist 
>      |      and assert that it is in fact a datumlist. 
>      |      
>      |      __parent_datum__ is the datum containing this. 
>      |          we need it in order to keep 
>      |      __parent_datumlist__ passed a datumlist. this will be used to append 
>      |      parent_datumlist to searches when looking for matching datums because
>      |      we are allowed to search on this level as well as on higher levels up to 
>      |      the root datumlist
>      |      
>      |      __num_elems__ passed a dat_int or None. corresponds to the number of groups 
>      |          in this. keep self.num_elems updated with the current number of datums in 
>      |          this.
>      |  
>      |  __str__(self)
>      |  
>      |  add(self, name, typ, value=None, num_elems=None, elem_type=None, code=None, time=None, description=None)
>      |      this overrides datumlist.add because it must add the datum to every 
>      |      group as well as self.datums
>      |  
>      |  add_group(self)
>      |  
>      |  calc_size(self)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  datums_arglist = None
>      |  
>      |  groups = None
>      |  
>      |  parent_datum = None
>      |  
>      |  parent_datumlist = None
>     
>     class typError(exceptions.Exception)
>      |  for use when typ is wrong
>      |  
>      |  Method resolution order:
>      |      typError
>      |      exceptions.Exception
>      |      exceptions.BaseException
>      |      __builtin__.object
>      |  
>      |  Data descriptors defined here:
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.Exception:
>      |  
>      |  __init__(...)
>      |      x.__init__(...) initializes x; see help(type(x)) for signature
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from exceptions.Exception:
>      |  
>      |  __new__ = <built-in method __new__ of type object>
>      |      T.__new__(S, ...) -> a new object with type S, a subtype of T
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from exceptions.BaseException:
>      |  
>      |  __delattr__(...)
>      |      x.__delattr__('name') <==> del x.name
>      |  
>      |  __getattribute__(...)
>      |      x.__getattribute__('name') <==> x.name
>      |  
>      |  __getitem__(...)
>      |      x.__getitem__(y) <==> x[y]
>      |  
>      |  __getslice__(...)
>      |      x.__getslice__(i, j) <==> x[i:j]
>      |      
>      |      Use of negative indices is not supported.
>      |  
>      |  __reduce__(...)
>      |  
>      |  __repr__(...)
>      |      x.__repr__() <==> repr(x)
>      |  
>      |  __setattr__(...)
>      |      x.__setattr__('name', value) <==> x.name = value
>      |  
>      |  __setstate__(...)
>      |  
>      |  __str__(...)
>      |      x.__str__() <==> str(x)
>      |  
>      |  __unicode__(...)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from exceptions.BaseException:
>      |  
>      |  __dict__
>      |  
>      |  args
>      |  
>      |  message
>     
>     class val_func_error(exceptions.Exception)
>      |  for use if value is a func and it throws an error
>      |  
>      |  Method resolution order:
>      |      val_func_error
>      |      exceptions.Exception
>      |      exceptions.BaseException
>      |      __builtin__.object
>      |  
>      |  Data descripto

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

> Help on module edfdat.dat_primitives in edfdat
> 
> NAME
>     edfdat.dat_primitives
> 
> FILE
>     /home/silverfish/Documents/populin/datedf workspace/edfdat/dat_primitives.py
> 
> DESCRIPTION
>     dat_primitives is a file to contain different primitive data
>     in data files. 
>     
>     they are necessary because python doesn't have a short object. 
>     also they don't nativly read and write binary files. which is a 
>     desirable quality. 
>     
>     so. think of them basically as primitives from java or c. 
>     you should be able to compare them, add them index them etc. 
>     they should be thought of as immutable. besides for reading. 
>     but once they are set they are set. 
>     
>     you can set them during initialization or by reading them from a file. 
>     for this reason the value they hold might be None. nonetheless 
>     the still will have a size. 
>     
>     included are all the basics you'd want
>     int, shorts, float, and chars. 
>     
>     we've also included lists and vectors. 
>     lists hold an array of data. they must all be the same type and have the same size. 
>     much like a C array. 
>     
>     types and other arguments like elem_type and num_elems must be set during 
>     initialization and can be either other dat_primitives for python primitives.
>     at least ones that make sense.
> 
> CLASSES
>     __builtin__.object
>         dat_type
>             dat_char
>                 dat_strchunk
>             dat_list
>                 dat_str
>                 dat_vec
>             dat_number
>                 dat_float
>                 dat_int
>                     dat_short
>                     dat_uet
>     unittests
>     
>     class dat_char(dat_type)
>      |  used to hold idividual characters using 1 byte apiece
>      |  
>      |  Method resolution order:
>      |      dat_char
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Data and other attributes defined here:
>      |  
>      |  bincode = 'c'
>      |  
>      |  cast_type = <type 'str'>
>      |      str(object='') -> string
>      |      
>      |      Return a nice string representation of the object.
>      |      If the argument is a string, the return value is the same object.
>      |  
>      |  defaultvalue = ' '
>      |  
>      |  size = 2
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_float(dat_number)
>      |  used to hold floats
>      |  
>      |  Method resolution order:
>      |      dat_float
>      |      dat_number
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Data and other attributes defined here:
>      |  
>      |  bincode = 'f'
>      |  
>      |  cast_type = <type 'float'>
>      |      float(x) -> floating point number
>      |      
>      |      Convert a string or number to a floating point number, if possible.
>      |  
>      |  size = 4
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_int(dat_number)
>      |  used to hold integers and give them read/write to file
>      |  
>      |  Method resolution order:
>      |      dat_int
>      |      dat_number
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Data and other attributes defined here:
>      |  
>      |  bincode = 'i'
>      |  
>      |  cast_type = <type 'int'>
>      |      int(x=0) -> int or long
>      |      int(x, base=10) -> int or long
>      |      
>      |      Convert a number or string to an integer, or return 0 if no arguments
>      |      are given.  If x is floating point, the conversion truncates towards zero.
>      |      If x is outside the integer range, the function returns a long instead.
>      |      
>      |      If x is not a number or if base is given, then x must be a string or
>      |      Unicode object representing an integer literal in the given base.  The
>      |      literal can be preceded by '+' or '-' and be surrounded by whitespace.
>      |      The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
>      |      interpret the base from the string as an integer literal.
>      |      >>> int('0b100', base=0)
>      |      4
>      |  
>      |  size = 4
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_list(dat_type)
>      |  more advanced thing. this holds an array of values
>      |  requires:
>      |  __elem_type__ to be another dat_class
>      |  
>      |  optional:
>      |  if __num_elems__ is provided constrains the length of list to 
>      |          that. it can be int or dat_int or dat_short
>      |  
>      |  Method resolution order:
>      |      dat_list
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  __getitem__(self, k)
>      |      allows you to get specfic items from this list self[k]
>      |  
>      |  __init__(self, value=None, elem_type=None, num_elems=None, **kwargs)
>      |      if value provided ensures all elements are elem_type,
>      |      if num_elems is provided it will force vale to have that many elements
>      |      but can be overridden during self.read
>      |      
>      |      after initialization you can rest assured that this will have:
>      |      __self.elem_type__ and it will be a dat_type
>      |      __self.value__ which will either be an array of dat_types or None
>      |      __self.num_elems__ which will be None (if value is None) or a dat_int
>      |      __self.size__ which will be 0 or the length of this in bytes
>      |      
>      |      
>      |      NOTE: this only supprts elem_types of simple things. like chars, floats, 
>      |      etc. but not lists of vectors or lists of lists etc.
>      |  
>      |  checkval(self)
>      |      ensures self.value is filled with dat_types
>      |  
>      |  listify(self, listvalues)
>      |      breaks self.value into a list that can be iterated through one by one 
>      |      can be overwritten by subclasses
>      |  
>      |  process_num_elems(self, listvalues)
>      |      returns the number of elements in the value passed in
>      |  
>      |  read(self, fp, num_elems=None)
>      |      reads from a file and fills values and things
>      |  
>      |  setsize(self)
>      |      calculates and sets self.size
>      |  
>      |  write(self, fp)
>      |      write to a file. returns addr where it began
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  size = 0
>      |  
>      |  value = None
>     
>     class dat_number(dat_type)
>      |  included to give all number dats a common parent, 
>      |  that excludes str and lists
>      |  
>      |  Method resolution order:
>      |      dat_number
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  size = 0
>      |  
>      |  value = None
>     
>     class dat_short(dat_int)
>      |  used to hold shorts, python doesn't normally have them
>      |  
>      |  Method resolution order:
>      |      dat_short
>      |      dat_int
>      |      dat_number
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Data and other attributes defined here:
>      |  
>      |  bincode = 'h'
>      |  
>      |  size = 2
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_int:
>      |  
>      |  cast_type = <type 'int'>
>      |      int(x=0) -> int or long
>      |      int(x, base=10) -> int or long
>      |      
>      |      Convert a number or string to an integer, or return 0 if no arguments
>      |      are given.  If x is floating point, the conversion truncates towards zero.
>      |      If x is outside the integer range, the function returns a long instead.
>      |      
>      |      If x is not a number or if base is given, then x must be a string or
>      |      Unicode object representing an integer literal in the given base.  The
>      |      literal can be preceded by '+' or '-' and be surrounded by whitespace.
>      |      The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
>      |      interpret the base from the string as an integer literal.
>      |      >>> int('0b100', base=0)
>      |      4
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_str(dat_list)
>      |  strings are lists of dat_strchunk
>      |  which means that they will always have an even number of characters
>      |  that is important because dat files always maintain word alignment
>      |  
>      |  Method resolution order:
>      |      dat_str
>      |      dat_list
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  __str__(self)
>      |      return string representation of self
>      |  
>      |  listify(self, listvalues)
>      |      override dat_list's listify because if listvalues is a string 
>      |      we need to break it into 2 char increments
>      |  
>      |  process_num_elems(self, listvalues)
>      |      override dat_list s process_num_elems
>      |      because if list of values is a string we need to break it into 
>      |      4 byte words rather than single chars and len('abcd') == 4, we want 2
>      |      throw an error if string not indexable by word is passed in
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  elem_type = <class 'edfdat.dat_primitives.dat_strchunk'>
>      |      this is a chunk of a string.
>      |      strigs are word indexed in scho18
>      |      not byte indexed. so they require 2 characters
>      |      so they take an even number of bytes
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_list:
>      |  
>      |  __getitem__(self, k)
>      |      allows you to get specfic items from this list self[k]
>      |  
>      |  __init__(self, value=None, elem_type=None, num_elems=None, **kwargs)
>      |      if value provided ensures all elements are elem_type,
>      |      if num_elems is provided it will force vale to have that many elements
>      |      but can be overridden during self.read
>      |      
>      |      after initialization you can rest assured that this will have:
>      |      __self.elem_type__ and it will be a dat_type
>      |      __self.value__ which will either be an array of dat_types or None
>      |      __self.num_elems__ which will be None (if value is None) or a dat_int
>      |      __self.size__ which will be 0 or the length of this in bytes
>      |      
>      |      
>      |      NOTE: this only supprts elem_types of simple things. like chars, floats, 
>      |      etc. but not lists of vectors or lists of lists etc.
>      |  
>      |  checkval(self)
>      |      ensures self.value is filled with dat_types
>      |  
>      |  read(self, fp, num_elems=None)
>      |      reads from a file and fills values and things
>      |  
>      |  setsize(self)
>      |      calculates and sets self.size
>      |  
>      |  write(self, fp)
>      |      write to a file. returns addr where it began
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  size = 0
>      |  
>      |  value = None
>     
>     class dat_strchunk(dat_char)
>      |  this is a chunk of a string.
>      |  strigs are word indexed in scho18
>      |  not byte indexed. so they require 2 characters
>      |  so they take an even number of bytes
>      |  
>      |  Method resolution order:
>      |      dat_strchunk
>      |      dat_char
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  listify(self, listvalues)
>      |      turns this into a list
>      |  
>      |  process_num_elems(self, listvalues)
>      |      overwrite the wrapper function of ddat_list
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  bincode = '2s'
>      |  
>      |  chars_per_chunk = 2
>      |  
>      |  defaultvalue = '  '
>      |  
>      |  size = 4
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_char:
>      |  
>      |  cast_type = <type 'str'>
>      |      str(object='') -> string
>      |      
>      |      Return a nice string representation of the object.
>      |      If the argument is a string, the return value is the same object.
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_type(__builtin__.object)
>      |  wrapper for primitive data types. allowing us to read and write to them
>      |  
>      |  Methods defined here:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __init__(self, value=None, **kwargs)
>      |      asserts value is of type making sense to this type
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  __str__(self)
>      |      returns string representation of this object
>      |  
>      |  process_binstr(self, binstr)
>      |      children of this class can overwrite this to process 
>      |      binary strings read in from file. 
>      |      must return the value they want to set as the value.
>      |      
>      |      but this gives children opportunity to set other instance variables 
>      |      as they see fit. provide in case the value encodes deeper information
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors defined here:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  size = 0
>      |  
>      |  value = None
>     
>     class dat_uet(dat_int)
>      |  UETs are very special Integers
>      |  they code a UET event which is composed of a time and code
>      |  and represnt it as an integer
>      |  
>      |  just like a normal dat_type
>      |  they can be initialized immediately or read in from a file
>      |  
>      |  the code for uet integers is:
>      |  (recall an int is 4 bytes)
>      |  the first 3 encodes for time as an integer
>      |  the last byte encode the code as a short. 
>      |  
>      |  so we need to 
>      |  add 00 to the end of time 
>      |  and 00 to the end of code to properly read them as int and short
>      |  
>      |  Method resolution order:
>      |      dat_uet
>      |      dat_int
>      |      dat_number
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  __init__(self, value=None, code=None, time=None, **kwargs)
>      |      override dat_type init because initilizing a uet value
>      |      requires encoding time and code. which don't make sense 
>      |      in normal dat_primitives.
>      |      
>      |      value is ignored. it's just required to deal with dat_types  
>      |      read
>      |  
>      |  __str__(self)
>      |  
>      |  process_binstr(self, binstr)
>      |      binstr represents self.value i.e. an integer, 
>      |      but a special int which encodes a time (first 4 bytes) and uet 
>      |      code(last 2 bytes) 
>      |      this method is called when reading in from a file to set self.time 
>      |      and self.code
>      |      
>      |      this is required to return the binstr to get set as value
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes defined here:
>      |  
>      |  code = None
>      |  
>      |  time = None
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_int:
>      |  
>      |  bincode = 'i'
>      |  
>      |  cast_type = <type 'int'>
>      |      int(x=0) -> int or long
>      |      int(x, base=10) -> int or long
>      |      
>      |      Convert a number or string to an integer, or return 0 if no arguments
>      |      are given.  If x is floating point, the conversion truncates towards zero.
>      |      If x is outside the integer range, the function returns a long instead.
>      |      
>      |      If x is not a number or if base is given, then x must be a string or
>      |      Unicode object representing an integer literal in the given base.  The
>      |      literal can be preceded by '+' or '-' and be surrounded by whitespace.
>      |      The base defaults to 10.  Valid bases are 0 and 2-36.  Base 0 means to
>      |      interpret the base from the string as an integer literal.
>      |      >>> int('0b100', base=0)
>      |      4
>      |  
>      |  size = 4
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_type:
>      |  
>      |  __add__(self, other)
>      |      does other + self.value
>      |  
>      |  __eq__(self, v2)
>      |      True IFF self == v2
>      |  
>      |  __hash__(self)
>      |      used for setting keys in dicts
>      |  
>      |  __index__(self)
>      |      allows for using this object as an index in an array 
>      |      e.g. arr[self]
>      |  
>      |  __int__(self)
>      |      return int representation of this object
>      |  
>      |  __mul__(self, other)
>      |      multiply self.value * other
>      |  
>      |  __ne__(self, v2)
>      |      True iff self != v2
>      |  
>      |  __repr__(self)
>      |      returns string representation of this object
>      |  
>      |  __rmul__(self, other)
>      |      multiply other * self.value
>      |  
>      |  read(self, fp)
>      |      reads from binary file and sets this
>      |  
>      |  write(self, fp)
>      |      writes bin to fp. returns address of variable written
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data descriptors inherited from dat_type:
>      |  
>      |  __dict__
>      |      dictionary for instance variables (if defined)
>      |  
>      |  __weakref__
>      |      list of weak references to the object (if defined)
>      |  
>      |  ----------------------------------------------------------------------
>      |  Data and other attributes inherited from dat_type:
>      |  
>      |  defaultvalue = 0
>      |  
>      |  isset = False
>      |  
>      |  value = None
>     
>     class dat_vec(dat_list)
>      |  this is effectively a list
>      |  the only difference is that when writing to the file it is preceeded 
>      |  by an integer describing the number of elements
>      |  
>      |  Method resolution order:
>      |      dat_vec
>      |      dat_list
>      |      dat_type
>      |      __builtin__.object
>      |  
>      |  Methods defined here:
>      |  
>      |  read(self, fp)
>      |      read a vec from a file
>      |  
>      |  setsize(self)
>      |      figure out what the size of this is based on the num_elems and 
>      |      elem_type then set self.size
>      |  
>      |  write(self, fp)
>      |      write a vec to a file
>      |  
>      |  ----------------------------------------------------------------------
>      |  Methods inherited from dat_list:
>      |  
>      |  __getitem__(self, k)
>      |      allows you to get specfic items from this list self[k]
>      |  
>      |  __init__(self, value=None, elem_type=None, num_elems=None, **kwargs)
>      |      if value provided ensures all elements are elem_type,
>      |      if num_elems is provided it will force vale to have that many elements
>      |      but can be overridden during self.read
>      |      
>      |      after initialization you can rest assured that this will have:
>      |      __self.elem_type__ and it will be a dat_type
>      |      __self.value__ which will either be an array of dat_types or None
>      |      __self.num_elems__ which will be None (if value is None) or a dat_int
>      |      __self.size__ which will be 0 or the length of this in bytes
>      |      
>      |      
>      |      NOTE: this only supprts elem_types of simple things. like chars, floats, 
>      |      etc. but not lists of vectors or lists of lists etc.
>      |  
>      |  checkval(self)
>      |      ensures self.value is filled with dat_types
>      |  
>      |  listify(self, listvalues)
>      |      breaks self.value i


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


the class datfile is composed of a directory and a list of datasets.
with the ability to write them to a file. 


> Help on module edfdat.datfile in edfdat
> 
> NAME
>     edfdat.datfile
> 
> FILE
>     /home/silverfish/Documents/populin/datedf workspace/edfdat/datfile.py
> 
> CLASSES
>     unittests
>     edfdat.datumobjects.datumlist(__builtin__.object)
>         dataset
>             sho18
>     
>    class dataset(edfdat.datumobjects.datumlist)
>     |  A dataset is a special datumlist
>     |  where the first set of datums are always the same.
>     |  SCHNAM TYPE STRING LENGTH 8
>     |  RECLNT                        /* in blocks */
>     |  ANID TYPE STRING LENGTH 12
>     |  DSID TYPE STRING LENGTH 12
>     |  DATE TYPE STRING LENGTH 8
>     |  TIME                          /* in 10ths of seconds since midnight */
>     |  EXTYP TYPE STRING LENGTH 4
>     |  
>     |  after that it's just a normal datumlist an you're free to
>     |  set up whatever schema you'd like.
>     |  
>     |  Method resolution order:
>     |      dataset
>     |      edfdat.datumobjects.datumlist
>     |      __builtin__.object
>     |  
>     |  Methods defined here:
>     |  
>     |  __init__(self, SCHNAM=None, ANID=None, DSID=None, DATE=None, TIME=None, EXTYP=None)
>     |      sets up the header for this dataset
>     |      requires:
>     |      SCHNAM # str, name of schema
>     |      ANID # str, name of subject
>     |      DSID # str, subject id
>     |      DATE # str, date in the form DDMM-YY
>     |      TIME # int, time of exp in 10ths/sec since midnight
>     |      EXTYP # str, type of Experiment i.e. COM
>     |  
>     |  assert_consistent_list_len(self, listolists)
>     |      asserts that this is a list of lists
>     |      and that all interior lists are of the same length
>     |  
>     |  assert_consistent_list_of_dicts(self, listodicts)
>     |      checks the listodicts is a list of dicts
>     |      and that each dict has the same keys
>     |      
>     |      raises AssertionError if it, else return None
>     |  
>     |  assert_list_of_type(self, lst, typ)
>     |      asserts that lst is a list with elements of typ or empty
>     |  
>     |  check_presence(self, keyword, repgrplist)
>     |      check if keyword is present in repgrplist
>     |      keyword is str
>     |      repgrplist is list of dicts
>     |      used for UDATA, ANDATA, CMDATA
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data and other attributes defined here:
>     |  
>     |  ANID_LEN = 6
>     |  
>     |  DATE_LEN = 4
>     |  
>     |  DSID_LEN = 6
>     |  
>     |  EXP_LEN = 2
>     |  
>     |  SCHNAM_LEN = 4
>     |  
>     |  ----------------------------------------------------------------------
>     |  Methods inherited from edfdat.datumobjects.datumlist:
>     |  
>     |  __getitem__(self, k)
>     |  
>     |  __str__(self)
>     |  
>     |  add(self, name, typ, value=None, num_elems=None, elem_type=None, code=None, time=None, description=None)
>     |      add a new datum to this datumlist
>     |      this constructs a datum. which can be quite an involved thing. 
>     |      
>     |      _dname__ is the name of the new datum. 
>     |      
>     |      __typ__ is the type that the datum will be. this must be a string or integer
>     |       representing a dat_type, see datum docs for more.
>     |      
>     |      _dvalue__ will be the value of the created datum. this is not neccessary to 
>     |      include. as you can set the value of the datum later. 
>     |      
>     |      
>     |      __num_elems__ can be provided for lists, vectors, and strings. if provided 
>     |      they will constrian the length of their values. however this can be overridden
>     |      in the case of vectors by reading a file.
>     |      
>     |      this can be another datum name as well. If it refers to another datum, and 
>     |      that datum is not set, updating this datum (via set) will update that datum.
>     |      however, updating that datum after this datum will not change this datum. 
>     |      If the referred datum is set. then the value of that datum will be used to 
>     |      constrain this datums value.  
>     |      
>     |      __elem_type__ required for lists and vectors. must be a string or int 
>     |      representing a dat_type. see datum docs for more. It can also be a ref to 
>     |      another datum. that datum must be able to be evaluated before creating this 
>     |      datum
>     |  
>     |  calc_size(self)
>     |  
>     |  generate_datlist(self)
>     |      for a generic datlist it simply returns self.datums. but subclasses can 
>     |      overridden this func and generate new ones to search through. basically 
>     |      in an effort to enumerate the namespace availble to individual datums if 
>     |      referance ing other datums.
>     |  
>     |  get(self, name, pos=False)
>     |      generates a datumlist to search through then returns the first datum
>     |      of the indicated name or None
>     |      if pos is True, returns byte offset from beginning of datumlist as
>     |      well as datum in dict with keys pos and datum
>     |  
>     |  get_pointer(self, datums, ret_datum=False)
>     |      returns word where specified datums are from
>     |      datums should be a list describing the hirearchical 
>     |      location of the desired location. 
>     |      e.g. to find b,1c,2d in the datum list constructed like so
>     |      a: sasd
>     |      b:
>     |          1-c:
>     |              1-d:adskhfjd
>     |              2-d:asdasdf
>     |          2-c:
>     |              1-d:asdkfasdf
>     |              2-d:sdaflsf
>     |      you would provide datums like so:
>     |      [{name:b},{name:c,index:1},{name:d,index:2}]
>     |      if any index is out of range an IndexError will be raised.
>     |      if this path can't be found. -1 will be returned
>     |      if ret_datum is true. will return datum, loc
>     |  
>     |  istypevalid(self, dtyp)
>     |      assures that dtyp is either a recognized type or
>     |      is the name of a known datum
>     |  
>     |  size_in_blocks(self)
>     |  
>     |  size_in_words(self)
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data descriptors inherited from edfdat.datumobjects.datumlist:
>     |  
>     |  __dict__
>     |      dictionary for instance variables (if defined)
>     |  
>     |  __weakref__
>     |      list of weak references to the object (if defined)
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data and other attributes inherited from edfdat.datumobjects.datumlist:
>     |  
>     |  datums = []
    
    class sho18(dataset)
>     |  this class represents a dataset that adheres to the scho18
>     |  schema. 
>     |  
>     |  basically this calss adds one useful function. 
>     |  that's the populate function. which takes a nicely formatted
>     |  dictionary of values and fills this instance with those values.
>     |  
>     |  Method resolution order:
>     |      sho18
>     |      dataset
>     |      edfdat.datumobjects.datumlist
>     |      __builtin__.object
>     |  
>     |  Methods defined here:
>     |  
>     |  checkADCH(self, ADCH)
>     |      checks that ADCH is of the form:
>     |      ADCH    ,   [    #           A/D channels
>     |                      {   ACHAN: int, A/D channel no.
>     |                          SRATE: float, sampling rate Hz
>     |                          ASAMPT: float, sampling time in sec
>     |                          NSAMP: int, no. A/D samples
>     |                      }
>     |                  ]
>     |  
>     |  checkCOF(self, COFS)
>     |      asserts COFS is of the form:
>     |      COILCOF: [
>     |          {      COFX:  real, A/D channel number for X-position 
>     |                 COFY:  real, A/D channel number for Y-position 
>     |          }
>     |      ]
>     |  
>     |  checkCOILINF(self, COILINF)
>     |      checks COILINF is in the form:
>     |      COILINF ,   [   # Coil configuration
>     |                      {   COILPOS: str, Coil position e.g. LEFTEAR
>     |                          ADCHX:  A/D channel number for X-position   
>     |                          ADCHY:  A/D channel number for Y-position 
>     |                          COILCOF: [
>     |                              {      COFX:  real, A/D channel number for X-position 
>     |                                     COFY:  real, A/D channel number for Y-position 
>     |                              }
>     |                          ]
>     |                      }
>     |                  ]
>     |  
>     |  checkDATA(self, DATA)
>     |      checks DATA is of the form:
>     |      DATA    ,   [
>     |                      {   UDATA: [{time: , code:}] spike time data 
>     |                          ANDATA: [
>     |                                      [int] sampled analog data
>     |                                  ]
>     |                          CMDATA: [
>     |                                      [int] sampled CM Data
>     |                                  ]
>     |                          DERV:   [
>     |                                      {   DERVNAM: str, name of derived variable
>     |                                          DERVTYP: int, variable type
>     |                                          DERVAL: list or str, value of variable 
>     |                                      }
>     |                                  ]
>     |                      }
>     |                  ]
>     |  
>     |  checkPOS(self, POS, name)
>     |      checks that POS is of the form:
>     |      POS     ,   [
>     |                      {   AZIM: float, LED azimuth position (-180 to +180) 
>     |                          ELEV: float, LED elevation pos. (-90 to +90)
>     |                      }
>     |                  ]
>     |  
>     |  checkSTATTB(self, STATTB)
>     |      checks STATTB is of the form:
>     |      STATTB  ,   [    # status table
>     |                     {   STVARS: [   # status variables
>     |                                     {   NAME: str, name of variable
>     |                                         TYPE: int, variable type
>     |                                         VAL: list or str, value of variable 
>     |                                     }
>     |                                 ] 
>     |                     }
>     |                 ]
>     |  
>     |  checkSUBTPAR(self, SUBTPAR)
>     |      checks SUBTPAR is in the proper format
>     |      SUBTPAR ,   [   # Subtasks
>     |                      [  # subtask parameters
>     |                          {   'NAM': Sub-Task Variable name
>     |                              'TYP': Var type 1=int,2=fp,3=char
>     |                              'VAL': variable value
>     |                          }
>     |                      ]
>     |                  ]
>     |  
>     |  checkUET(self, UDATA)
>     |      Checks UDATA is of the form
>     |      UDATA:  [
>     |          {   code:
>     |              time: 
>     |          }
>     |      ]
>     |  
>     |  checkVars(self, VARSRG, name)
>     |      asserts that VARSRG has the std variable repgroup layout
>     |      [{  NAME: 
>     |          TYPE:
>     |          VAL:
>     |      }]
>     |  
>     |  check_repgroups_form(self, FXPAR, SUBTPAR, ADCH, COILINF, LEDPOS, SPKPOS, DATA, STATTB)
>     |      checks that all the rep groups passed in are of the correct form
>     |  
>     |  populate(self, SP1CH=None, STRTCH=None, TERMCH=None, INWCH=None, REWCH=None, ENDCH=None, TBASE=None, STFORM=None, RNSEED=None, TGRACL1=None, TSPOTL1=None, TGRACL2=None, TSPOTL2=None, SPONTIM=None, ISDREW=None, ISDNOREW=None, ATTLOW=None, ATTHIGH=None, ATTINC=None, SCAPEND=None, FXPAR=None, COMENT=None, SUBTPAR=None, AVOLC=None, AVCC=None, ANBITS=None, ADCH=None, COILCODE=None, COILINF=None, AVOLCCM=None, AVCCCM=None, ANBITSCM=None, ACHANCM=None, LEDPOS=None, SPKPOS=None, DATA=None, STATTB=None)
>     |      this function takes the following:
>     |      SP1CH   ,  # int       Spikes UET channel number
>     |      STRTCH  ,  # int       Start sync. UET channel number
>     |      TERMCH  ,  # int       Terminate UET channel number
>     |      INWCH   ,  # int       Enter Window UET channel number
>     |      REWCH   ,  # int       Reward start UET channel number
>     |      ENDCH   ,  # int       End Trial UET channel number
>     |      TBASE   ,  # float     UET times base in seconds
>     |      STFORM  ,  # int       Status table format code
>     |      LSTAT   ,  # int       Location of Status table
>     |      RNSEED  ,  # int       Seed used for random number generator
>     |      TGRACL1 ,  # float     Grace time for LED-1 ? (secs)
>     |      TSPOTL1 ,  # float     Time to spot LED-1 ? (secs)
>     |      TGRACL2 ,  # float     Grace time for LED-2 ? (secs)
>     |      TSPOTL2 ,  # float     Time to spot LED-2 ? (secs)
>     |      SPONTIM ,  # float     Spontaneous time ? (secs)
>     |      ISDREW  ,  # float     Inter-seq delay after reward (secs)
>     |      ISDNOREW,  # float     Inter-seq delay after no-reward (secs)
>     |      ATTLOW  ,  # float     Attenuator low value (dB)
>     |      ATTHIGH ,  # float     Attenuator High value (dB)
>     |      ATTINC  ,  # float     Attn. Step size (dB)
>     |      SCAPEND ,  # str  8    Schema name for appended data
>     |      FXPAR   ,  [    # Fixed parameter variables give like so...
>     |                      {   'NAM' :  Variable name
>     |                          'TYP' :  Var type 1=int,2=fp,3=char
>     |                          'VAL' :  Variable value pass as array or str
>     |                      }
>     |                  ]
>     |      COMENT  ,  # STRING LENGTH 60   Subjective comment
>     |      SUBTPAR ,   [   # SUBTPAR
>     |                      [  # SUBTPARV
>     |                          {   'NAM': Sub-Task Variable name
>     |                              'TYP': Var type 1=int,2=fp,3=char
>     |                              'VAL': variable value
>     |                          }
>     |                      ]
>     |                  ]
>     |      AVOLC   ,   # TYPE REAL     Voltage conversion factor
>     |      AVCC    ,   #               Voltage Conversion Code
>     |      ANBITS  ,   #               No. of bits per sample 16/32
>     |      ADCH    ,   [    #           A/D channels
>     |                      {   ACHAN: int, A/D channel no.
>     |                          SRATE: float, sampling rate Hz
>     |                          ASAMPT: float, sampling time in sec
>     |                          NSAMP: int, no. A/D samples
>     |                      }
>     |                  ]
>     |      COILCODE,   # int   Coil calib. code (1,2,3 etc.)
>     |      COILINF ,   [   # Coil configuration
>     |                      {   COILPOS: str, Coil position e.g. LEFTEAR
>     |                          ADCHX:  A/D channel number for X-position   
>     |                          ADCHY:  A/D channel number for Y-position 
>     |                          COILCOF: [
>     |                              {      COFX:  real, A/D channel number for X-position 
>     |                                     COFY:  real, A/D channel number for Y-position 
>     |                              }
>     |                          ]
>     |                      }
>     |                  ]
>     |      AVOLCCM ,   #   REAL  Voltage conversion factor for CM
>     |      AVCCCM  ,   #   Voltage conversion code for CM
>     |      ANBITSCM,   #   Bits/sample for CM (16 or 32)
>     |      ACHANCM ,   #   Channel number for CM
>     |      LEDPOS  ,   [
>     |                      {   AZIM: float, LED azimuth position (-180 to +180) 
>     |                          ELEV: float, LED elevation pos. (-90 to +90)
>     |                      }
>     |                  ]
>     |      SPKPOS  ,   [
>     |                      {   AZIM: real, Speaker azimuth pos. (-180 to +180) 
>     |                          ELEV: real, Speaker elevation pos. (-90 to +90)  
>     |                      }
>     |                  ]
>     |      DATA    ,   [
>     |                      {   UDATA: [{time: , code:}] spike time data 
>     |                          ANDATA: [
>     |                                      [int] sampled analog data
>     |                                  ]
>     |                          CMDATA: [
>     |                                      [int] sampled CM Data
>     |                                  ]
>     |                          DERV:   [
>     |                                      {   DERVNAM: str, name of derived variable
>     |                                          DERVTYP: int, variable type
>     |                                          DERVAL: list or str, value of variable 
>     |                                      }
>     |                                  ]
>     |                      }
>     |                  ]   
>     |      STATTB  ,   [    # status table
>     |                      {   STVARS: [   # status variables
>     |                                      {   STVNAM: str, name of variable
>     |                                          STVTYP: int, variable type
>     |                                          STVAL: list or str, value of variable 
>     |                                      }
>     |                                  ] 
>     |                         
>     |                      }
>     |                  ]
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data and other attributes defined here:
>     |  
>     |  SCHNAM = 'scho18'
>     |  
>     |  comment_words = 30
>     |  
>     |  scapend_words = 4
>     |  
>     |  var_name_words = 4
>     |  
>     |  ----------------------------------------------------------------------
>     |  Methods inherited from dataset:
>     |  
>     |  __init__(self, SCHNAM=None, ANID=None, DSID=None, DATE=None, TIME=None, EXTYP=None)
>     |      sets up the header for this dataset
>     |      requires:
>     |      SCHNAM # str, name of schema
>     |      ANID # str, name of subject
>     |      DSID # str, subject id
>     |      DATE # str, date in the form DDMM-YY
>     |      TIME # int, time of exp in 10ths/sec since midnight
>     |      EXTYP # str, type of Experiment i.e. COM
>     |  
>     |  assert_consistent_list_len(self, listolists)
>     |      asserts that this is a list of lists
>     |      and that all interior lists are of the same length
>     |  
>     |  assert_consistent_list_of_dicts(self, listodicts)
>     |      checks the listodicts is a list of dicts
>     |      and that each dict has the same keys
>     |      
>     |      raises AssertionError if it, else return None
>     |  
>     |  assert_list_of_type(self, lst, typ)
>     |      asserts that lst is a list with elements of typ or empty
>     |  
>     |  check_presence(self, keyword, repgrplist)
>     |      check if keyword is present in repgrplist
>     |      keyword is str
>     |      repgrplist is list of dicts
>     |      used for UDATA, ANDATA, CMDATA
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data and other attributes inherited from dataset:
>     |  
>     |  ANID_LEN = 6
>     |  
>     |  DATE_LEN = 4
>     |  
>     |  DSID_LEN = 6
>     |  
>     |  EXP_LEN = 2
>     |  
>     |  SCHNAM_LEN = 4
>     |  
>     |  ----------------------------------------------------------------------
>     |  Methods inherited from edfdat.datumobjects.datumlist:
>     |  
>     |  __getitem__(self, k)
>     |  
>     |  __str__(self)
>     |  
>     |  add(self, name, typ, value=None, num_elems=None, elem_type=None, code=None, time=None, description=None)
>     |      add a new datum to this datumlist
>     |      this constructs a datum. which can be quite an involved thing. 
>     |      
>     |      _dname__ is the name of the new datum. 
>     |      
>     |      __typ__ is the type that the datum will be. this must be a string or integer
>     |       representing a dat_type, see datum docs for more.
>     |      
>     |      _dvalue__ will be the value of the created datum. this is not neccessary to 
>     |      include. as you can set the value of the datum later. 
>     |      
>     |      
>     |      __num_elems__ can be provided for lists, vectors, and strings. if provided 
>     |      they will constrian the length of their values. however this can be overridden
>     |      in the case of vectors by reading a file.
>     |      
>     |      this can be another datum name as well. If it refers to another datum, and 
>     |      that datum is not set, updating this datum (via set) will update that datum.
>     |      however, updating that datum after this datum will not change this datum. 
>     |      If the referred datum is set. then the value of that datum will be used to 
>     |      constrain this datums value.  
>     |      
>     |      __elem_type__ required for lists and vectors. must be a string or int 
>     |      representing a dat_type. see datum docs for more. It can also be a ref to 
>     |      another datum. that datum must be able to be evaluated before creating this 
>     |      datum
>     |  
>     |  calc_size(self)
>     |  
>     |  generate_datlist(self)
>     |      for a generic datlist it simply returns self.datums. but subclasses can 
>     |      overridden this func and generate new ones to search through. basically 
>     |      in an effort to enumerate the namespace availble to individual datums if 
>     |      referance ing other datums.
>     |  
>     |  get(self, name, pos=False)
>     |      generates a datumlist to search through then returns the first datum
>     |      of the indicated name or None
>     |      if pos is True, returns byte offset from beginning of datumlist as
>     |      well as datum in dict with keys pos and datum
>     |  
>     |  get_pointer(self, datums, ret_datum=False)
>     |      returns word where specified datums are from
>     |      datums should be a list describing the hirearchical 
>     |      location of the desired location. 
>     |      e.g. to find b,1c,2d in the datum list constructed like so
>     |      a: sasd
>     |      b:
>     |          1-c:
>     |              1-d:adskhfjd
>     |              2-d:asdasdf
>     |          2-c:
>     |              1-d:asdkfasdf
>     |              2-d:sdaflsf
>     |      you would provide datums like so:
>     |      [{name:b},{name:c,index:1},{name:d,index:2}]
>     |      if any index is out of range an IndexError will be raised.
>     |      if this path can't be found. -1 will be returned
>     |      if ret_datum is true. will return datum, loc
>     |  
>     |  istypevalid(self, dtyp)
>     |      assures that dtyp is either a recognized type or
>     |      is the name of a known datum
>     |  
>     |  size_in_blocks(self)
>     |  
>     |  size_in_words(self)
>     |  
>     |  ----------------------------------------------------------------------
>     |  Data descriptors inherited from edfdat.datumobjects.datumlist:
>     |  
>     |  __dict__
>     |      dictionary for instance variables (if defined)
>     |  
>     |  __weakref__
>     |      list of weak references to the object (if defined)
>     |  
>     |  ------------------------------------

-----------

## edf.py

this file contains all the functions neccessary to parse both edf files as well as use the mapping files the user provides in order to parse them. 

**currently not implemented**

wjw

---------