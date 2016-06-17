''' 
    This file contains datums and stuff made form datums such as datum lists



    We need a way to organize the raw data into sets. 
    we'll call these datumlists in general.

    because in general they are just list of datum objects. 

    This file contains the datumlist class as well as it's subclasses. 
    e.g. groups (used by repeatgroups)
    e.g. dset headers (mandatory for all datasets in datafiles)
    e.g. directory (a special dataset at the beginning of all dat files 
        describing what dsets are in the datfile)
    e.g. specific data schemas e.g. sho18
    
    when creating a dataset you are really defining a schema. with the option of 
    filling it in. which if you want it full of data you probably should. 

    to use a dataset first declare it. 
    dset = dataset(<mandatory header stuff as python primitives>)

        if you don't include the stuff you will not be able to write it. 
        but again, you're really just defining a schema. so it doesn't have to 
        contain any actual data.

    then add datums to fit your schema
    dset.add(<datum defininition>)

        the datum defininitions are exactly the same as the datums.datum class
        With the major exception that you can provide other datum names instead of 
        values for any kwarg values including elem_type,num_elems, etc.
        but not for typ or value 

        again they don't need to be filled. a datum is a placeholder in a schema. 
        they can't be written to a file unless they can be evaluated to a value
        but they can still exist. (datums are data too!)

    e.g.
        see datum documentation for more on why 

        dset.add('Num Vars', 'int')
        dset.add('Vars', 'rg', num_elems='Num Vars') 
            # the above links the number of groups in 'Vars' to the value of 'Num Vars' 
            # i.e. 'NUM Vars has just been set to 0, because this has no groups

        dset['Vars'].add('Name', 'str', num_elems=4) # 8 characters  
        dset['Vars'].add('Type', 'short')
        dset['Vars'].add('Words', 'short')
        dset['Vars'].add('Value', 'list', elem_type='Type', num_elems='Words')
            # the above added 4 datums to the repeatGroup 'Vars'
            # which defines a single variable that we want to save.
            # the type of the variable is coded by a short 
            # the number of 4byte words in the variable is defined by the 'Words' datum
            # the value of the variable is saved in 'Value' 

            # the Value 'datum' is the most important as it's the most complex
            # When you define the type of a datum by specifying another datum  
            # the datum referred will not be set upon updating the value datum
            # i.e. once we set value, the 'Words' datum will be updated but the 'Type'
            #     datum will not. 

        dset['Vars'].add_group() # adds a group to the repeat group
            # this command created a group within the repGroup and 4 datums empty
            # within that as if these were called:
            #   datum('Name','str',num_elems=4)
            #   t = datum('Type','short')
            #   w = datum('Words','short')
            #   datum('Value','list',elem_type=t,num_elems=w) 
            # this implies that datums must be able to take datum arguments. 
            # this also updates 'Num vars' to 1

        dset['Vars'][0]['Name'].set('var1') # this gets expanded to 8 char2 (8 words)
        dset['Vars'][0]['Type'].set(1) # codes for an int array

        # BAD!!!
        dset['Vars'][0]['Value'].set('hello world') # elem_type is set to int!
            # threw error

        # Good  
        dset['Vars'][0]['Value'].set([1,2,3]) # elem_type is set to int!
            # this set num_elems to be 3, because we tried to evaluate 'Words' and 
            # it returned None. as it wasn't set

        #---------------- NEXT GROUP

        dset['Vars'].add_group() # adds a group to the repeat group
            # this also updates 'Num vars' to 2

        dset['Vars'][1]['Name'].set('var2') # this gets expanded to 8 char2 (8 words)
        dset['Vars'][1]['Type'].set(3) # codes for an str
        dset['Vars'][1]['Words'].set(2)
        dset['Vars'][1]['Value'].set('hello world') # saves 'hell'  
            # this does not update 'Words', rather it truncates the value 
            # this is the same operation as before. but now Words evaluated to 2. 


        dset.add('Extra var', 'int', value=1) # adds and sets the datum right away. 
        
        print dset
        > NUM VARS [int] : 2
          Data [rg] :
            0   -   Name [str]: 'var1    '
                    Type [short]: 1
                    Words [short]: 3
                    Value [list]: [1,2,3]
            1   -   Name [str]: 'var2    '
                    Type [short]: 3
                    Words [short]: 2
                    Value [list]: 'hell'
         Extra var [int]: 1
        dset.write(sio()) # writes to a file 
        # Num vars        [0]name                [0]type [0]Words  [0]Value[0] ...
        > 02 00 00 00 | 76 61 72 31 20 20 20 20 | 01 00 | 03 00 | 01 00 00 00 | ...


    '''


from utils import make_logger, logging, blocksize, roundup, wordsize
from dat_primitives import dat_int, dat_float, dat_char, dat_list, dat_short, dat_str, \
dat_vec, dat_uet, dat_strchunk, dat_type
from __init__ import rglog, datumlistlog, datumlog
import ipdb
from random import random



class typError(Exception):
    '''for use when typ is wrong'''
    pass
class num_elemError(Exception):
    ''' for use if num_elems is wrong'''
    pass
class elem_typeError(Exception):
    '''for use if elem_type is wrong'''
    pass
class val_func_error(Exception):
    '''for use if value is a func and it throws an error'''
    pass



# datumlist  ###################### 
# datumlist  ###################### 
# datumlist  ###################### 
# datumlist  ###################### 
# datumlist  ###################### 
# datumlist  ###################### 

class datumlist(object):
    ''' this is a list of datums. 

        you can add datums to this list one by one. by calling datumlist.add
        this func will construct a new datum. just as if you constructed a new datum
        manually. however this has the added advantage of being aware of other datums.
        Due to this you can avoid passing values to datums directly.

        you can instead refer to other datums by name for certain kwargs. 
        When it comes time to create the new datum the referred datums will be evaluated
        and the value in those datums will be passed to the newly constructed datum. 

        if the datum referred is not set at the time, the behavior varies depending 
        on the kwarg indicated. 

        see the add foo docs for specifics. but an example is if you use a datum 
        to define num_elems, and don't set the referred datum
        then after setting the new datum the referred datum will be updated 
        '''
    datums = []
    def __init__(self):
        self.size = 0
        self.datums = [] # reinitilialize datums so they don't hold over
    def add(self, name, typ, 
        value=None, # value passed to new datum 
        num_elems=None, # number of elements within datum, used for lists and repGroups
        elem_type=None, # type of elements within daum, used for lists
        code=None, # used for UETs
        time=None, # used for UETs
        description=None, # description of what this datum is for
        ):
        ''' add a new datum to this datumlist
            this constructs a datum. which can be quite an involved thing. 

            _dname__ is the name of the new datum. 

            __typ__ is the type that the datum will be. this must be a string or integer
             representing a dat_type, see datum docs for more.

            _dvalue__ will be the value of the created datum. this is not neccessary to 
            include. as you can set the value of the datum later. 


            __num_elems__ can be provided for lists, vectors, and strings. if provided 
            they will constrian the length of their values. however this can be overridden
            in the case of vectors by reading a file.

            this can be another datum name as well. If it refers to another datum, and 
            that datum is not set, updating this datum (via set) will update that datum.
            however, updating that datum after this datum will not change this datum. 
            If the referred datum is set. then the value of that datum will be used to 
            constrain this datums value.  

            __elem_type__ required for lists and vectors. must be a string or int 
            representing a dat_type. see datum docs for more. It can also be a ref to 
            another datum. that datum must be able to be evaluated before creating this 
            datum  
            '''
        datumlistlog.debug(('Adding new datum given name %s. typ %s.'
            ' value %s. num_elems %s. elem_type %s. code %s. time %s.'
            ' description %s')%(name, typ, value, num_elems, elem_type,
             code, time, description))
        # there can be no duplicate names of datums
        assert self.get(name) == None, 'there can be no duplicate names of datums %s'%name

        # dtyp must be valid in datums.recognized_types
        assert typ in datum.recognized_types, 'typ %s not recognized'%typ

        # allow num_elems to be a ref to another existing datum
        # num_elems must be an integer. 
        try: 
            if num_elems != None: num_elems = int(num_elems)
        except: # could not be cast to an int. it must be a datum name 
            datumlistlog.debug(('checking validity of num_elems (%s) when adding new '
                'datum to datumlist')%num_elems)
            num_elems = self.get(num_elems)
            # if we can't find a datum will be None
            if num_elems == None: raise num_elemError(('num_elems provided %s '
                                'could not be determined')%num_elems)
            # it must be a dat_int type 
            assert issubclass(num_elems.typ, dat_int), ('num_elems provided %s '
                                'must be a number not %s')%(num_elems, num_elems.typ)
            
        # allow elem_type to be a ref to another existing datum
        # elem_type must be an integer or a string found in datum.recognized_types
        try: 
            # if it's not in recognized_types it might be a string of an integer.
            if elem_type != None:
                datumlistlog.debug(('checking validity of elem_type (%s) when adding new '
                    'datum to datumlist')%elem_type)
                if elem_type not in datum.recognized_types: 
                    elem_type = int(elem_type)
                # at this point it needs to be a str unless it's a datum ref
                datumlistlog.debug('elem_type decided to be (%s)'%elem_type)
                    
        except: # that means it threw an error, 
            # either casting a string to an int or wasn't in recognized_types
            # either way, it must be a datum name at this point
            elem_type = self.get(elem_type)
            if elem_type == None: raise elem_typeError(('elem_type provided %s '
                                'could not be determined')%elem_type)
            # it must be a dat_int type 
            assert issubclass(num_elems.typ, dat_int), ('elem_type provided %s '
                                'must be a number not %s')%(elem_type, elem_type.typ)
        
        # at this point we have ensured that num_elems are either datums or codes for 
        # known dat_types it should be safe to make a datum

        # create the datum
        newdat = datum(name, typ, value,
            num_elems=num_elems, 
            elem_type=elem_type, 
            code=code,
            time=time,
            description=description,
            parent_datumlist=self,)
        self.datums.append(newdat)
        datumlistlog.info('Created Datum %s : %s'%(newdat.name, newdat.__dict__))
        self.calc_size()
        return newdat
    def __getitem__(self,k):
        if isinstance(k, (dat_int, int)): return self.datums[k]
        dat = self.get(k)
        if dat is None: raise KeyError('%s not found in %s'%(k, self))
        return dat 
    def istypevalid(self, dtyp):
        ''' assures that dtyp is either a recognized type or
            is the name of a known datum '''
        if dtyp in datum.recognized_types: return True
        # else it should be the name of a number 
        for dat in self.generate_datlist(): # generate list of datums we know about
            if dtyp == dat.name:
                assert issubclass(dat.typ, dat_int), ('datum %s found, but  is of '
                    'typ %s, not an int')%(dat.typ) # 
                # if it's a datum, then it has to be a number datum
                return True
        # searched through all known datums no match found
        return False
    def get(self, name, pos=False):
        ''' generates a datumlist to search through then returns the first datum
                of the indicated name or None
                if pos is True, returns byte offset from beginning of datumlist as
                well as datum in dict with keys pos and datum'''
        position = 0
        datumlistlog.debug('Trying to find datum with name %s in %s'%(name, self))
        datumlistlog.debug('generating datlist for %s'%(type(self)))
        datlist = self.generate_datlist()
        for dat in datlist:
            if dat.name == name: 
                datumlistlog.debug('Found datum matching %s : %s (did: %s)'%(name, dat,
                    dat.did))
                if not pos:return dat
                else: return {'pos':position, 'datum':dat} 
            datumlistlog.debug(('loking for %s at datum %s with position '
                '%s and dict %s')%(name, dat, position, dat.__dict__))
            datumlistlog.debug('adding size of %s : %s to position'%(dat, dat.__dict__))
            if pos: position += dat.size
        datumlistlog.debug('No match Found. returning None')
        return None
    def generate_datlist(self):
        ''' for a generic datlist it simply returns self.datums. but subclasses can 
            overridden this func and generate new ones to search through. basically 
            in an effort to enumerate the namespace availble to individual datums if 
            referance ing other datums.'''
        return self.datums
    def __str__(self):
        ret = '\n'
        for dat in self.datums: 
            ret += str(dat) + '\n'
        return ret
    def size_in_blocks(self): 
        self.calc_size()
        return roundup(self.size / blocksize)
    def size_in_words(self): 
        self.calc_size()
        return roundup(self.size / wordsize)
    def calc_size(self):
        self.size = 0
        for dat in self.datums:
            try:
                self.size += dat.size
            except Exception,e: 
                datumlistlog.debug(('Error raised while getting size '
                    'of %s. ERROR %s')%(dat, e))
    def get_pointer(self, datums,ret_datum=False):
        ''' returns word where specified datums are from
            datums should be a list describing the hirearchical 
            location of the desired location. 
            e.g. to find b,1c,2d in the datum list constructed like so
            a: sasd
            b:
                1-c:
                    1-d:adskhfjd
                    2-d:asdasdf
                2-c:
                    1-d:asdkfasdf
                    2-d:sdaflsf
            you would provide datums like so:
            [{name:b},{name:c,index:1},{name:d,index:2}]
            if any index is out of range an IndexError will be raised.
            if this path can't be found. -1 will be returned
            if ret_datum is true. will return datum, loc 
                '''
        #if they pass in a single datum_name, set it to the correct format
        try:
            datumlistlog.critical('######## getting %s'%datums)
            if isinstance(datums, str): datums = [{'name':datums}]
            assert len(datums)>0, ('must pass in a list of datum def dicts '
                '{name:_, index:_} not %s'%datums)
            
            loc = 0
            cur_iterable = self # start iterating at top level of self
            # go through all the definitions they provide. should be path through self
            ipdb.set_trace()
            for dat_def in datums: 
                datumlistlog.critical('iterating and trying to find %s'%dat_def)
                assert 'name' in dat_def, 'datum definition %s must have name key'%dat_def
                # it should either be datlist or repGroup datum. implementing datlist
                if isinstance(cur_iterable, datumlist): 
                    datumlistlog.critical('looking for %s in datumlist'%dat_def['name'])
                    # go through datlist
                    for d in cur_iterable: 
                        datumlistlog.critical('%s == %s? %s @ %s'%(dat_def['name'], 
                            d.name, loc, d.name == dat_def['name']))
                        # did we find the right one? based on name alone, no index needed
                        if d.name == dat_def['name']: 
                            datumlistlog.critical('Found %s'%d)
                            cur_iterable = d
                            break # go to next dat_def
                        loc += d.size # else increment the pointer position
                # it should either be a datlist or a repGroup datum. implementing repGroup
                elif (isinstance(cur_iterable, datum)            # if it's a datum 
                                and issubclass(cur_iterable.typ, repGroup)): # then it must be a repGroup
                    # repgroups require index to specify what index to go through
                    assert 'index' in dat_def, '%s leads to a repGroup needs index'%datums
                    datumlistlog.critical('looking for %s(%s) in repGroup'%(dat_def['name'], dat_def['index']))
                    #iterate through the group
                    try:
                        for i,grp in enumerate(cur_iterable.value): # iterate through groups
                            # iterate through the datums in group
                            datumlistlog.critical('looking in group %s'%i)
                            for d in grp:
                                datumlistlog.critical('%s == %s(%s) @ %s? %s'%(dat_def['name'],
                                    d.name,i, loc, 
                                    dat_def['name'] == d.name and dat_def['index'] == i))
                                # check if it's got the right name and grp index
                                if dat_def['name'] == d.name and dat_def['index'] == i:
                                    # if so set the iteration of the next loop to be this
                                    # should be repeatGroup or they screwed something up
                                    cur_iterable = d
                                    raise StopIteration # go to next dat_def
                                loc += d.size
                    except StopIteration, e: pass
            
            # return values datum or None and pointer value
            if isinstance(cur_iterable, datum) and cur_iterable.name == datums[-1]['name']:
                datumlistlog.critical('Found %s at pos %s'%(cur_iterable, loc))
                if ret_datum: return cur_iterable, loc
                else: return loc
            else: 
                datumlistlog.critical(('looked thorugh everything unable to find %s. '
                    'size of self is %s')%(datums[-1]['name'], loc))
                if ret_datum: return None, loc  
                else: return -1 
        except Exception,e: 
            datumlistlog.critical('\n#########\n#####\n##### ERROR(%s): %s'%(type(e),e))

class group(datumlist):
    ''' these are the things that get held in a repeat group
        we need to 
        '''
    parent_datumlist = None # start with empty datumlist
    def __init__(self, parent_datumlist, parent_repGroup):
        self.parent_datumlist = None
        self.parent_repGroup = None
        self.size = 0
        self.datums = []
        rglog.debug('New group being created parent datumlist is %s'%parent_datumlist)
        assert isinstance(parent_datumlist, datumlist), ('Group objects require a '
            'datumlist object to be their parent.')
        self.parent_datumlist = parent_datumlist
        assert isinstance(parent_repGroup, repGroup), ('Group objects require a repGroup',
            'to be their parent')
        self.parent_repGroup = parent_repGroup
    def generate_datlist(self):
        ''' overrides datumlist.generate_datlist this includes parents datums 
            as well as self's datums.  '''
        rglog.debug(('generating datlist'
            ' including self.datums : %s and parent_datumlist : %s')%(self.datums, 
            self.parent_datumlist.generate_datlist()))
        return self.datums + self.parent_datumlist.generate_datlist()
    def add(self, name, typ, 
        value=None, # value passed to new datum 
        num_elems=None, # number of elements within datum, used for lists and repGroups
        elem_type=None, # type of elements within daum, used for lists
        code=None, # used for UETs
        time=None, # used for UETs
        description=None, # description of what this datum is for
        ):
        ''' wrapper for super add. we need to update self.parent_datumlist.size '''
        super(group, self).add(name, typ, 
            value = value,
            num_elems = num_elems,
            elem_type = elem_type,
            code = code,
            time = time,
            description = description,)
        self.parent_repGroup.calc_size()


# datum  ######################## 
# datum  ######################## 
# datum  ######################## 
# datum  ######################## 
# datum  ######################## 

class datum(object):
    ''' this is the holder for all data objects in 
        a data file. 
        every one must have a name. 
        and a type. 

        some types require or can accept different kwargs. 
        for instance.
        type 'str' can accept num_elem = # which forces it to be # chars long. 
        type 'list' requires elem_type = simple_type, which forces all elems to be type

        num_elems and elem_type can also be Number datum objects. 
        the value contained by the datum will be evaluated and use in place. 
        a referance to the datum itself will also be saved as self.num_elems_datum 
        and self.elem_type_datum.

        num_elems_datum, if its not set when this is set (and this is an applicable type)
        num_elems_datum will be updated when this is set. 

        elem_type_datum ,ust be set before this is set. 
        '''
    did = None # datum id random number set during init to differentiate them
    name = None # the name of this datum
    value = None # the dat_type this thing holds
    func = None # a 0 arg function we will try and evaluate when this is queried
    typ = None # type of the held value, always need to know that
    num_elems = None # how many repititions in this. only used for lists and repGroups
    elem_type = None # what does this contain. only used for lists
    code = None # used for UETs
    time = None # used for UETs
    description = None # holds the descriptiopn of this datum
    parent_datumlist = None # used for casting repgroups
    isset = False # if the data in this is set

    attrs_to_update = [     # when self.update is called update these attributes 
            'num_elems',    # from self.value
            'size',
            'isset',
            'add_group',
            'add',
        ]
    recognized_types = {} # defined at bottom of file, before unittests
    def __init__(self, name, typ, 
        val=None, # the value to hold. can be a 0-argument func, or None
        num_elems=None, # how many repititions in this. only used for lists and repGroups
        elem_type=None, # what does this contain. only used for lists 
        code=None, # used to set UETs
        time=None, # used to set UETs
        description='no description', # used to decribe this datum,
        parent_datumlist=None, # used to make repGroups
        ):
        '''
            we need to parse these slightly differently for each of the 
            different types. also we need to allow for functions'''
        self.did = random()
        self.name = name # can be whatever you want
        self.description = description # can be whatever you want
        self.size = 0
        datumlog.debug('creating datum %s : %s'%(name, description))
        datumlog.debug(('args passed: '
                            '\n\tval : %s'
                            '\n\tnum_elems : %s'
                            '\n\telem_type : %s'
                            '\n\tcode : %s'
                            '\n\ttime : %s'
                            '\n\tdescription : %s'
                            '\n\tparent_datumlist : %s')%(val,num_elems,elem_type,code,
                            time,description,parent_datumlist))
        # set self.typ
        datumlog.debug('setting type of datum')
        try: self.typ = self.get_type(typ) # can raise AssertionError
        except AssertionError, e: raise TypeError(e) 

        if parent_datumlist != None: 
            assert isinstance(parent_datumlist, datumlist), ('If you provide '
                'parent_datumlist to a datum it must be a datumlist instance'
                ' not %s')%parent_datumlist
            self.parent_datumlist = parent_datumlist
            datumlog.debug('%s: parent_datumlist set'%name)

        datumlog.debug('%s: setting num_elems given %s'%(name,num_elems))
        self.checkset_num_elems(num_elems)
        try:self.checkset_elem_type(elem_type)
        except elem_typeError,e: datumlog.debug(('elem_type not set. '
            'cannot set value yet. ERROR %s')%e)

        datumlog.debug('%s: setting time (%s) and code (%s)'%(name,time, code))
        self.time = time
        self.code = code

        try:
            datumlog.debug('%s: setting val (%s) '%(name, val))
            datumlog.debug(('\n\nbefore set WHILE INITING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
            self.set(val)
        except elem_typeError, e: 
            datumlog.debug('Was not able to set value. val is current;y %s'%self.value)
        datumlog.debug('Created datum %s : %s'%(self.name, self.__dict__))
        datumlog.debug(('\n\nCREATED DATUM %s: '
            'has add? %s\n\n')%(name, hasattr(self, 'add')))
    def get_type(self,typ):
        ''' asserts all the conditions for a datum type or elem_type
            and returns the actual class referance to the dat_primitive'''
        datumlog.debug('Trying to find type equivalent to %s'%typ)
        assert isinstance(typ, (str,int, dat_int)), ('Typ to datum must be '
            'either a str, int or dat_int: %s')%typ
        assert typ in self.recognized_types, 'Typ provided %s not recognized'%typ
        return self.recognized_types[typ]
    def set(self, value):
        ''' sets the value of this datum. if we have a function call it, then'''
        datumlog.debug('Setting Value of %s before %s'%(self, self.__dict__))
        if hasattr(self, 'elem_type_datum'):
            if not self.elem_type_datum.isset:
                raise elem_typeError('When using a datum for elemtype, it must be'
                    ' set before setting this. datum for elem_type (%s) '
                    'is not set'%self.elem_type_datum)
            try:self.checkset_elem_type(self.elem_type_datum) 
            except: datumlog.debug('Type was not set. cannot set value yet') 

        datumlog.debug(('\n\nbefore eval WHILE SETTING DATUM %'
            's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
        if hasattr(value, '__call__'): self.func = value
        else: self.value = value
        self.value = self.eval()

        datumlog.debug(('\n\nafter eval WHILE SETTING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))


        self.update() # update self attributes from new value.  
        datumlog.debug(('\n\n after update WHILE SETTING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
        datumlog.debug('Value of %s set. after %s'%(self, self.__dict__))
    def eval(self):
        ''' returns the value of this datum. that is if this contains a function
            it will update the value and return it. '''
        datumlog.debug('Evaluating %s'%self)
        value = self.value
        if self.func is not None: 
            try: value = self.func()
            except Exception,e: datumlog.error(val_func_error(e))
        datumlog.debug(('\n\nbefore cast WHILE EVAL DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
        datumlog.warn('Evaluating %s. where class(value) is repGroup  = %s'%(self, isinstance(value, repGroup)))
        value = self.cast(value) 
        datumlog.debug(('\n\nafter cast WHILE EVAL DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))

        datumlog.debug('Evaluation found value to be %s'%value)
        return  value
    def cast(self, value):
        ''' casts value to self.elem_type, uses various kwargs this knows about'''
        code = self.code
        time = self.time
        num_elems = self.num_elems
        elem_type = self.elem_type
        typ = self.typ

        # return the cast value or raise an error
        datumlog.debug(('Casting value %s, num_elems %s, elem_type %s, '
            'code %s, time %s to %s')%(value, num_elems, elem_type, code, time, typ))
        try:
            datumlog.debug(('\n\inside cast 1 WHILE CASTING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))

            ret = typ(value = value, 
                num_elems=num_elems,  
                elem_type=elem_type,
                code=code,time=time,
                parent_datum=self, 
                parent_datumlist=self.parent_datumlist )
    
            # keep num_elems_datum up to date
            datumlog.debug(('\n\inside cast 4 WHILE CASTING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
            if hasattr(self, 'num_elems_datum'): self.num_elems_datum.set(ret.num_elems)
            datumlog.debug(('\n\inside cast 2 WHILE CASTING DATUM %'
                's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))
            return ret
        except Exception,e:
            datumlog.debug(('\n\inside cast 3 WHILE CASTING DATUM %'
            's: has add? %s\n\n')%(self.name, hasattr(self, 'add')))

            datumlog.debug(('Error (%s) casting to %s. self.value could '
                'not be cast. left None')%(e, typ))
            return None
    def __repr__(self): return self.__str__()
    def __str__(self):
        ret = '%s (%s)'%(self.name, self.typ.__name__)
        if self.elem_type != None and issubclass(self.elem_type, dat_type):
            ret += '[%s]'%self.elem_type.__name__
        if self.value is None and self.func is not None:
            ret +=  ': %s'%(self.func)
        else:
            ret +=  ': %s'%(self.value) 
        if self.description: ret += '\t# %s'%self.description
        return ret
    def checkset_num_elems(self, num_elems):
        '''checks that num_elems is decent 
            and sets things appropritatley for the set call'''
        # check num_elems
        if num_elems is not None: 
            try:  # eval can throw errors, as can casting to dat_int
                if isinstance(num_elems, datum):
                    # if it's a datum save the referance
                    self.num_elems_datum = num_elems
                    num_elems = num_elems.eval()
                # cast it to a dat_int
                self.num_elems = dat_int(num_elems)
            except ValueError,e: raise num_elemError(e)
    def checkset_elem_type(self, elem_type):
        # check elem_type
        #   elem_type can be either a datum or 
        if elem_type is not None: 
            try: 
                if isinstance(elem_type, datum):
                    self.elem_type_datum = elem_type
                    assert issubclass(elem_type.typ, dat_int), ('When passing a datum to'
                        ' elem_type it must be an int not %s'%elem_type.typ)
                    elem_type = elem_type.eval()
                self.elem_type = self.get_type(elem_type) # can raise AssertionError
            except AssertionError,e: raise elem_typeError(e)
    def update(self):
        ''' updates self.__dict__
            from self.value. used when value is a repeat group 
            and changes without interfacing with this datum at all. 
            so the repgroup will get updated and change it's num_elems
            '''
        datumlistlog.debug('About to update %s: %s'%(self, self.__dict__))
        # update selected attributes self to be those of new value
        if self.value is None: return 
        datumlistlog.debug('Updating from value %s:%s'%(self.value, self.value.__dict__))
        val_dic = self.value.__dict__

        for k in self.attrs_to_update: 
            try:
                datumlistlog.debug('attempting to add %s to %s'%(k, self.name))
                setattr(self, k, val_dic[k])
            except KeyError,e: datumlistlog.debug('val_dic did not have key %s'%k)
        if hasattr(self, 'num_elems_datum'): self.num_elems_datum.set(self.num_elems)
        datumlistlog.debug('updated %s : %s'%(self, self.__dict__))
    def calc_size(self):
        if self.value == None:
            self.size = 0
        else: self.size = self.value.size
    def __getitem__(self, k):
        datumlog.debug('attempting to get item in datum %s (%s) at %s.'%(
            self.name, self.typ, k))
        if self.typ is not repGroup: 
            raise TypeError ('Only Datums of repGroup support indexing;: %s'%self)
        else: return self.value[k]



# repGroup  ##################### 
# repGroup  ##################### 
# repGroup  ##################### 
# repGroup  ##################### 
# repGroup  ##################### 
# repGroup  ##################### 

class repGroup():
    ''' a repgroup is a possible value for a datum. 
        
        defined by datum(NAME, 'rg', num_elems=None) num_elems can be either a datum or
            integer 

        and filled via two methods. add, which overrides datumlists, and adds a new datum 
        archetype
        and add_group. which adds a group. all groups will have the same datums in them
        and adding a datum will add it to all of them. 

        these also support numeric indexing to access group objects. which are simply 
        further datumlists. 
        '''
    datums_arglist = None # holds arguments to create new datums
    groups = None # a list of groups in this repGroup 
    parent_datumlist = None # an empty datumlist by default
    parent_datum = None # the datum holding this value. update it when this gets updated

    def __init__(self, 
        parent_datum=None, 
        parent_datumlist=None, 
        num_elems=None, **kwargs):
        ''' initializing a repeat group doesn't do much. it will assign 
            self.parent_datumlist to be the provided parent_datumlist 
            and assert that it is in fact a datumlist. 

            __parent_datum__ is the datum containing this. 
                we need it in order to keep 
            __parent_datumlist__ passed a datumlist. this will be used to append 
            parent_datumlist to searches when looking for matching datums because
            we are allowed to search on this level as well as on higher levels up to 
            the root datumlist

            __num_elems__ passed a dat_int or None. corresponds to the number of groups 
                in this. keep self.num_elems updated with the current number of datums in 
                this. 
            '''
        self.parent_datum= None
        self.datums_arglist = []
        self.groups = []
        self.parent_datumlist = datumlist()
        self.num_elems = dat_int(0)

        rglog.debug(('Creating new Rg Value. passed pdat: %s. pdlist:'
            ' %s, num_elems: %s, kwargs %s')%(parent_datum, 
            parent_datumlist, num_elems, kwargs))

        assert isinstance(parent_datum, datum), ('repGroups must know about their '
            'parent_datum. provide it instead of %s')%parent_datum
        self.parent_datum = parent_datum
        
        if parent_datumlist != None: 
            rglog.debug('passed in a parent datumlist')
            assert isinstance(parent_datumlist, datumlist), (''
            'parent_datumlist to repGroup must be instance of datumlist '
            'not %s'%parent_datumlist)
            self.parent_datumlist = parent_datumlist
        rglog.debug('new repGroups parent datumlist is %s'%self.parent_datumlist)
        # else leave it none. 

        rglog.debug('after adding any groups if neccessary num_elems is %s'%num_elems)
        self.num_elems = dat_int(len(self.groups)) 

        # give parent datum repGroup functions
        rglog.warn('\n=============\n GIVING Parent datum %s repgroup functions!'%(
            self.parent_datum.name))
        self.parent_datum.add_group = self.add_group
        self.parent_datum.add = self.add
        rglog.debug('after giving parent_datum (%s) repGroup functions check'
            ' if they exist'%self.parent_datum.name)
        rglog.debug(('\nparent_datum has add %s, \nparent_datum has '
                    'add_group %s,  \n__getitem__ %s')%(hasattr(self.parent_datum, 'add'), 
                                        hasattr(self.parent_datum, 'add_group'),
                                        hasattr(self.parent_datum, '__getitem__')))
        self.calc_size()
    def add_group(self):
        rglog.debug(('Creating new group in %s. \n\tself has these '
                    'datums%s')%(self.parent_datum.name,self.datums_arglist))
        grp = group(self.parent_datumlist, self)
        for dat in self.datums_arglist:
            rglog.debug('Creating datum %s within grp %s[%s] given %s'%(dat['name'],
                self.parent_datum.name, len(self.groups)-1, dat))
            grp.add(dat['name'],dat['typ'],
                value=dat['value'],
                num_elems=dat['num_elems'],
                elem_type=dat['elem_type'],
                code=dat['code'],
                time=dat['time'],
                description=dat['description'],)
        
        self.groups.append(grp)
        self.num_elems += 1
        self.parent_datum.update()
        rglog.debug('Just added a group. updated parent datum %s'%self.parent_datum)
    def add(self, 
        name, 
        typ, 
        value=None, # value passed to new datum 
        num_elems=None, # number of elements within datum, used for lists and repGroups
        elem_type=None, # type of elements within daum, used for lists
        code=None, # used for UETs
        time=None, # used for UETs
        description=None, # description of what this datum is for
        ):
        ''' this overrides datumlist.add because it must add the datum to every 
            group as well as self.datums
            '''
        rglog.debug(('adding new datum given '
            'name = %s. typ = %s. value = %s. num_elems = %s. elem_type = %s '
            'code = %s. time = %s. description = %s')%(name,typ,value,num_elems,elem_type,
            code,time,description))

        # add new datum to self.datums
        # recall that num_elems and elem_type can be datum names. 
        # datumlist.add calls self.get to get datum referances. 
        # self.get calls self.generate_datlist 
        datumargs = {
            'name' : name, 
            'typ':typ,
            'value':value,
            'num_elems':num_elems,
            'elem_type':elem_type,
            'code':code,
            'time':time,
            'description':description, 
        }
        self.datums_arglist.append(datumargs)
        # add new datum to all exisitng groups
        for grp in self.groups: 
            grp.add(name, typ, 
                value=value, 
                num_elems=num_elems, 
                elem_type=elem_type, 
                code=code, 
                time=time, 
                description=description)
        self.parent_datum.update()
        self.parent_datum.calc_size()
        rglog.debug('Just added a %s datums. updated parent datum %s'%(len(self.groups),self.parent_datum))
        rglog.debug('rg now contains \n%s'%self)        
        # ipdb.set_trace()
        self.calc_size()
    def __str__(self):
        ret = '\n\t'
        for i, grp in enumerate(self.groups):
            ret += '%s-\t\t'%(i) + str(grp).replace('\n','\n\t') 
        return ret
    def __getitem__(self, k):
        assert isinstance(k, int), 'repgroups Only supports integer indexing'
        return self.groups[k]
    def calc_size(self):
        self.size = 0
        for grp in self.groups:
            self.size += grp.size
        self.parent_datum.calc_size()


# Final setup of datum ##############
# Final setup of datum ##############
# Final setup of datum ##############
# Final setup of datum ##############
# Final setup of datum ##############

'''
    repGroup inherits datum, so it must come after datum
    but datum refers to repGroup in it's class instantiation. 
    so that needs to be moved after repGroup is defined. 
    i.e. down here. 
'''
datum.recognized_types = {
        1: dat_int,
        2: dat_float,
        3: dat_strchunk,
        'int':dat_int,
        'float':dat_float,
        'char':dat_char,
        'list':dat_list,
        'short':dat_short,
        'str':dat_str,
        'vec':dat_vec,
        'uet':dat_uet,
        'rg':repGroup,
            }

########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS
########################################### UNIT TESTS


class datmlistunittests():
    def __init__(self):
        datumlistlog.warn('### dataset Unit tests\n')
        self.testdatumlist()
        # self.testdatumlistwithrepgroup()
        datumlistlog.warn('### dataset Unit Tests Passed!\n#####################\n\n\n')
    def testdatumlist(self):
        datumlistlog.warn('\n\n\n### creating a simple datumlist for a test')
        d = datumlist()
        n1 = d.add('NAME1','str',value='aaaaaaaaa',num_elems=4,
            description='8 character name2 started with 9 as')
        datumlistlog.warn('### created %s'%n1)
        n2 = d.add('NAME2','str',value='aaaa',num_elems=4,
            description='8 character name1 started with 4 as')
        datumlistlog.warn('### created %s'%n2)
        t = d.add('TYPE','short',3,description='going to contain a string')
        datumlistlog.warn('### created %s'%t)
        l = d.add('LEN','short',description='length of str in words')
        datumlistlog.warn('### created %s'%l)
        li = d.add('VALUE','list','Hello World', num_elems='LEN', elem_type='TYPE')
        datumlistlog.warn('### created %s'%li)

        v = d.add('testvec','vec',[1,2,3],elem_type='short')
        datumlistlog.warn('### dlist printed: %s'%d)

        datumlistlog.warn('### PASSED a simple datumlist TEst\n')
    def testdatumlistwithrepgroup(self):
        datumlistlog.warn('\n\n\n### creating a datumlist for with a repGroup test')
        d = datumlist()
        datumlistlog.warn('### Created the datumlist')
        datumlistlog.warn('### added int for num reps of rg')
        n = d.add('NUM VARS', 'int')
        datumlistlog.warn('### added rg to hoold variables')
        vs = d.add('VARS','rg', num_elems='NUM VARS')
        
        datumlistlog.warn('### Adding a group')
        vs.add_group()

        datumlistlog.warn('### adding datums to repgroup directly and via indexing')
        datumlistlog.warn('\n### adding NAME str 8')
        vs.add('NAME','str', num_elems=4)
        datumlistlog.warn('\n### adding DEFAULT INT int, 1')
        vs.add('DEFAULT INT','int', 1)
        datumlistlog.warn('\n### adding TYPE short not set')
        vs.add('TYPE','short')
        datumlistlog.warn('\n### adding LEN short not set')
        d['VARS'].add('LEN','short')
        datumlistlog.warn('\n### adding VALUES elem_type = TYPE, num_elems=LEN')
        vs.add('VALUE','list', elem_type='TYPE', num_elems='LEN')

        datumlistlog.warn('\n\n### added a second group')
        d['VARS'].add_group()

        datumlistlog.warn('\n\n### Setting group 0:NAME')
        d['VARS'][0]['NAME'].set('var1')
        datumlistlog.warn('\n\n### Setting group 0:TYPE')
        d['VARS'][0]['TYPE'].set(1)
        datumlistlog.warn('\n\n### Setting group 0:LEN')
        d['VARS'][0]['LEN'].set(3)
        datumlistlog.warn('\n\n### Setting group 0: VAL')
        vs[0]['VALUE'].set([1,2,3,4])        

        datumlistlog.warn('\n\n### Setting group 1')
        d['VARS'][1]['NAME'].set('var1')
        d['VARS'][1]['TYPE'].set(3)
        vs[1]['VALUE'].set("[1,2,3,4]")        

        datumlistlog.warn('%s'%d)
        datumlistlog.warn('%s'%d['VARS'].num_elems)
        datumlistlog.warn('### PASSED a datumlist with repGroup TEst\n')
        

        
class datumunittests():
    def __init__(self):
        datumlog.warn('\n\n\n###RUNNING DATUM UNIT TESTS')
        self.simple_datum()
        self.set_simple_datums_later()
        self.pass_datums_to_datums()
        datumlog.warn('###DATUM UNIT TESTS PASSED!!!\n\n\n')
    def simple_datum(self):
        datumlog.warn('###Testing Creation of a simple datum')
        datumlog.warn('###datum("TEST", "int", 1)')
        d = datum('TEST','int', 1)
        datumlog.warn('### Printing %s\n'%d)

        datumlog.warn('#---------\n')
        datumlog.warn('###datum("TEST", "uet", code=1,time=800)')
        d = datum('TEST','uet', time=800, code=1)
        datumlog.warn('### Printing %s\n'%d)
        
        datumlog.warn('#---------\n')
        datumlog.warn('###datum("TEST", "list", [1,2,3])')
        d = datum('TEST','list',[1,2,3],elem_type='int')
        datumlog.warn('### Printing %s\n'%d)

        datumlog.warn('#---------\n')
        datumlog.warn('###datum("TEST", "list", [1,2,3], num_elems=6,elem_type="int")')
        d = datum('TEST','list',[1,2,3],elem_type='int',num_elems=6)
        datumlog.warn('### Printing %s\n'%d)

        datumlog.warn('#---------\n')
        datumlog.warn(('###datum("TEST", "list", '
            'lambda: [1,2,3], num_elems=6,elem_type="int")'))
        d = datum('TEST','list',lambda:[1,2,3],elem_type='int',num_elems=6)
        datumlog.warn('### Printing %s\n'%d)
        datumlog.warn('PASSED simple_datum tests\n----------\n\n\n')
    def set_simple_datums_later(self):
        datumlog.warn('###Testing Creation of a simple datum and setting them later')
        datumlog.warn('###datum("TEST", "int") & .set(1)')
        d = datum('TEST','int')
        d.set(1)
        datumlog.warn('### Printing %s\n'%d)
        
        datumlog.warn('#---------\n')
        datumlog.warn('###datum("TEST", "list", num_elems=6,elem_type="int")')
        datumlog.warn('###d.set([1,2,3])')
        d = datum('TEST','list',elem_type='int',num_elems=6)
        d.set([1,2,3])
        datumlog.warn('### Printing %s\n'%d)
                
        datumlog.warn('PASSED simple datums set later tests\n----------\n\n\n')
    def pass_datums_to_datums(self):
        datumlog.warn('###Testing Creation of a Complex datums')
        datumlog.warn('###datum(TYPE, short, 1)')
        datumlog.warn('###datum(LEN, short)')
        datumlog.warn('###datum(VALUE, list, [1,2,3], elem_type=TYPE, num_elems=LEN)')
        t = datum('TYPE', 'short', 1)
        l = datum('LEN', 'short')
        v = datum('VALUE', 'list', [1,2,3], num_elems=l,elem_type=t)

        datumlog.warn('###TYPE : %s'%t)
        datumlog.warn('###LEN : %s'%l)
        datumlog.warn('###VAL : %s'%v)
        
        datumlog.warn('PASSED passing datums to datums test\n----------\n\n\n')
    def repGroup(self):
        datumlog.warn('Creating Repeating group datums')
        datumlog.warn('# d=datum("RGTest", "rg")')
        d = datum('RGTest','rg')

        datumlog.warn(('# d.add("INTTEST", "int"),1 # default this datum to '
            '1 in all groups'))
        d.add('INTTEST','int',1)
        datumlog.warn('# adding group')
        d.add_group()
        datumlog.warn('### Printing %s\n'%d)
        



# datumunittests()
# datmlistunittests()





