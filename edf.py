'''
	this file is filled with useful functions that deal with parsing 
	edf files. 

	instructions for use:
	1. call parse_edf
		which returns a dictionary with 'trials'and 'header'
		trials is a list of dicts

		the header is just a list of strings, 
		but the trials are a list of dictionaries. with 'dropped', 'sample' 
		& 'MSG'

		every dictionary represents a trial. 

		that's really it. the trial becomes a nice dictionary.
		one thing we must change is that the parse_edf function takes a map
		to turn messages into keywords. 

		we should get rid of that and let the mappers do the parsing of 
		messages.

'''

from os.path import join
import re

def open_edf(path=['temp.txt']):
	''' opens a asci version of an edf file and returns the pointer
		as readonly. ''' 
    return open(join(*path), 'r')



def get_trial_sets(fp,reset=True):
    ''' returns a list of lists.
        where each sublist represents all the
        statements from that trial

        if reset is True starts from byte 0 else 
        starts from current location
        returns
        [   [trial1.1, trial1.2,...],
            ...
        ]

        the first entry is the header. if there are no lines
        it will be empty. 

        moves fp to 0
        '''
    trials = [] # the initial list is the header
    if reset: fp.seek(0) # go to the head

    for statement in fp: # go line by line
        if len(trials) == 0: trials.append([]) 
        # ensure theres one there. the first 'trial' is the header
        if emptystr(statement): continue
        if matches_trial_start(statement):
           trials.append([])
        trials[-1].append(statement)
    fp.seek(0)
    return trials


def emptystr(string):
    ''' returns T/F if string is empty or no
        '''
    return len(re.findall(r"^[\s]*$", string)) > 0 # look for empty lines    

def matches_trial_start(statement):
    ''' determines if a statement (or line from an eyelink datafile )
        is the start of a new trial.
        basically if it matches this pattern
        MSG\t<TIMESTAMP> TIRALID <TIRALID>

        that's what we're calling the start of the trial. 
        ''' 
    return len(re.findall(r"^MSG\t\d+ TRIALID \d+$", statement)) > 0

def sample_parser(trial_str, 
    monocle = True, 
    velocity = False, 
    resolution = False,
    remote = True,
    CR = True,
    logger=logging,
    *args,
    **kwargs):
    ''' this parses a trial string containing a sample
        returns a dict with keys representing fields in the
        sample.

        the fields present are determined by the length and the flags
        e.g.
        string :    1 2 3 4 5 ... 6 7 8 .............
        results in ->
            timestamp = 1
            xpos = 2
            ypos = 3
            pupil = 4
            # note 5 is unkown and is being ignored
            monocle_errs = ...
            xpos_camera = 6
            ypos_camera = 7
            distance = 8
            remote_errs = .............
        '''
    def deal_with_missing_data(data):
        ''' this returns a float value always. for this data point.
            if the data is missing it will be 9998. else the correct value'''
        if data == '.': return float(9998)
        else: return float(data)

    split_tr = re.split(r'\s+', trial_str)
    logger.debug('In parse sample. split string = %s'%split_tr)
    tr_iter = split_tr.__iter__()
    ret = {}
    try:
        ret['type'] = 'sample'
        ret['timestamp']    = float(tr_iter.next())
        if monocle:
            ret['xpos']     = deal_with_missing_data(tr_iter.next())
            ret['ypos']     = deal_with_missing_data(tr_iter.next())
            ret['pupil']    = float(tr_iter.next())

            if velocity: ####################################################### this needs to be tested! I'm not sure how adding resolution/velocity will affect column structure 
                ret['xvel']     = float(tr_iter.next())
                ret['yvel']     = float(tr_iter.next())
            if resolution:
                ret['xres']     = float(tr_iter.next())
                ret['yres']     = float(tr_iter.next())

            tr_iter.next() # there is an unknown quantity. 
            if CR: ret['CR_err']     = tr_iter.next()

            if remote: # then there are some more columns
                ret['xpos_camera']  = float(tr_iter.next())
                ret['ypos_camera']  = float(tr_iter.next())
                ret['distance']     = float(tr_iter.next())
                ret['remote_errs']  = tr_iter.next()
        else: # not monoclular mode different structure. page 120 in user manual
            raise NotImplementedError('binocular mode has not been written yet'
                                        + ' dont worry. its not hard')
        
    except(StopIteration, ValueError), e:
        logger.error('Trial str (%s) did not meet expectations based on '%trial_str
                    + ' flags (mono:%s, vel:%s, res: %s, remote:%s, CR:%s).'%(monocle, 
                        velocity, resolution, remote,CR)
                    + ' Error: %s' %str(e))
        return None 
    return ret

def parse_trial(trial_str, logger=logging, **kwargs):
    ''' This takes a trial string
        i.e. 
        {TIMESTAMP}{X}{Y}{ps}{UNKOWN}{MONOCLE ERRORS CHARS}\
                            {X camera}{y camera}{distance}{remote ERRORS}
        returns a dictionary or None if it can be ignored
        dict will defintly have type = sample\message
        if type= sample
            it will have all the keys as a sample line

        if type = MSG
            it will have key string & TIMESTAMP.

        kwargs can contain flags for parsing. things like 
        CR  # Corneal reflection mode
        remote # remote mode
        velocity, resolution etc. flags set when creating asci file. 

        if they are not provided defaults will be used

        '''
    def err(): # we call the same error message a few times here. 
        logger.debug('in parse_trial:{%s} is neither a sample nor a MSG.'%trial_str)
        return None

    timestamp = None
    matchfloat = r"[-]?\d*\.*\d+" # e.g. -13.5
    matchfirstval = r"^[0-9a-zA-Z]*" # e.g. MSG\TIMESTAMP\EFIX\SSACC
    stype = None
    try:
        stype = re.findall(matchfirstval,trial_str)[0]
    except IndexError: return err() # not found
        
    typeparsers = {
        'MSG':msg_parser,
        'sample':sample_parser
    }
     
    try: # see if it's a sample. everything else begins with a string of type
        timestamp = float(stype)
        stype = 'sample'
    except ValueError: pass # it's not a sample
            
    if stype in typeparsers:
        try:
            return typeparsers[stype](trial_str, logger=logger, **kwargs) ########## NEED TO UPDATE monocle should reflect whether theres a monocle or not as set by global variable or something...
        except NotImplementedError: return err() 
    else:
        return err()

def parse_trial_set(tr_list, 
    org = 'single',
    logger=logging,
    **kwargs):
    ''' this take a list of trial strings and parses them using parse trial.
        returns a list of dicts.. pretty simple really.

        Oh! this drops trials that aren't either message or sample

        also you notice the org kwarg. that accepts single, multi 
        single returns an array with both samples and messages
        multi returns a dict with two array based on type.
            e.g. {msg:[....], samples:[...]}

        kwargs should be flags such as monocle
        '''
    ret = None
    if org == 'single': ret = []
    else: ret = {} 
    for trial in tr_list:
        parsed_trial = parse_trial(trial, logger=logger, **kwargs)
        # if this fails it will just print error message to stdout
        # and return None
        if parsed_trial is None: 
            if org != 'single': 
                if 'dropped' not in ret: ret['dropped'] = []
                ret['dropped'].append(trial)
            continue
        if org == 'single': ret.append(parsed_trial)
        else:
            tr_type = parsed_trial['type'] 
            if tr_type not in ret: ret[tr_type] = []
            ret[tr_type].append(parsed_trial)
    return ret 

def parse_edf(edfpath, logger=logging):
    ''' this takes a file path to an edf file and 
        parses it. this does not attempt to parse the messages in the trials
        that will be the callee's responsibility

        the idea being the controller will call this and pass the result to 
        a mapper which will turn it into a dictionary suitable for 
        the schemas populate function. 
    '''
    f = open_edf(edfpath)
    sets = get_trial_sets(f) # breaks edf into trial sets.
    hdr = sets[0] # grab the header as it's special
    sets = sets[1:] # grab the trial sets. which have not been parsed yet
    parsed_trs = [] # prepare to save parsed trials
    for i,tr_set in enumerate(sets): # parse each trial
        logger.info('processing trial %s of %s'%(i+1,len(sets)))
        parsed_tr = parse_trial_set(tr_set, # parse the trial. i.e. break into 
                    org='multi',            # samples, messages, 
                    logger=logger)          # and unkown stuff
        
        dropped = []
        if 'dropped' in parsed_tr: dropped = parsed_tr['dropped']
        samples = []
        if 'sample' in parsed_tr: samples = parsed_tr['sample']
        messages = []
        if 'MSG' in parsed_tr: messages = parsed_tr['MSG']


        logger.debug('\tfound %s samples'%len(samples))
        logger.debug('\tfound %s messages '%len(messages))
        logger.debug('\tcould not parse %s samples'%len(dropped)) 
        tr_dict = {
            'samples':samples,
            'dropped': dropped,
            'messages': messages
        }
        parsed_trs.append(tr_dict)

    return {'header':hdr,
            'trials':parsed_trs}
