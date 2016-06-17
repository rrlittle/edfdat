from __init__ import dsetlog
from datumobjects import datumlist
import IPython
import ipdb

class dataset(datumlist):
    ''' 
        A dataset is a special datumlist
        where the first set of datums are always the same. 
        SCHNAM TYPE STRING LENGTH 8
        RECLNT                        /* in blocks */
        ANID TYPE STRING LENGTH 12
        DSID TYPE STRING LENGTH 12
        DATE TYPE STRING LENGTH 8
        TIME                          /* in 10ths of seconds since midnight */
        EXTYP TYPE STRING LENGTH 4

        after that it's just a normal datumlist an you're free to 
        set up whatever schema you'd like.
        '''
    SCHNAM_LEN = 4  # str size in words
    ANID_LEN = 6    # str size in words
    DSID_LEN = 6    # str size in words
    DATE_LEN = 4    # str size in words
    EXP_LEN = 2     # str size in words
    def __init__(self,SCHNAM=None,
        ANID=None,
        DSID=None,
        DATE=None,
        TIME=None,
        EXTYP=None):
        ''' sets up the header for this dataset
            requires:
            SCHNAM # str, name of schema
            ANID # str, name of subject
            DSID # str, subject id
            DATE # str, date in the form DDMM-YY
            TIME # int, time of exp in 10ths/sec since midnight
            EXTYP # str, type of Experiment i.e. COM
            '''
        datumlist.__init__(self) # do the super to set this up

        # add all the standard things to form the header
        if not hasattr(self, 'SCHNAM'):
            self.add('SCHNAM', 'str', str(SCHNAM), 
                num_elems=self.SCHNAM_LEN,
                description='Name of Schema')
        else: 
            self.add('SCHNAM', 'str', str(self.SCHNAM), # precreated schemas should have 
                num_elems=self.SCHNAM_LEN,                   # this defined already
                description='Name of Schema')
        
        self.add('RECLNT', 'int', self.size_in_blocks, 
            description='Record length')
        

        self.add('ANID', 'str', str(ANID), 
            num_elems=self.ANID_LEN, 
            description='subject ID')

        self.add('DSID', 'str', str(DSID), 
            num_elems=self.DSID_LEN, 
            description='dataset ID')

        self.add('DATE', 'str', str(DATE), 
            num_elems=self.DATE_LEN,
            description='Date of Experiment DDMM-YY')

        self.add('TIME', 'int', int(TIME), 
            description='Time of Experiment in 10ths of a second from midnight')
        
        self.add('EXTYP', 'str', str(EXTYP),
            num_elems=self.EXP_LEN, 
            description='Name of Experiment type. i.e. COM')
    def check_presence(self, keyword, repgrplist):
        ''' check if keyword is present in repgrplist
            keyword is str
            repgrplist is list of dicts
            used for UDATA, ANDATA, CMDATA
            '''
        assert isinstance(repgrplist, list) # repgrplist must be a list 
        presence = [(keyword in d) for d in repgrplist] # full of True/False
        if True in presence: return 1
        else: return 0
    def assert_consistent_list_of_dicts(self, listodicts):
        ''' checks the listodicts is a list of dicts
            and that each dict has the same keys

            raises AssertionError if it, else return None
            '''
        self.assert_list_of_type(listodicts, dict)
        
        if len(listodicts) == 0: return
        keys = listodicts[0].keys()
        # listodicts of full of one type
        for d in listodicts:
            for key in keys:
                assert key in d
        # no errors raised return
    def assert_consistent_list_len(self, listolists):
        ''' asserts that this is a list of list
            and that all interior lists are of the same length'''
        self.assert_list_of_type(listolists, list)
        lengths = set([len(l) for l in listolists])
        assert len(lengths) <= 1, 'lengths in %s are not all same'%(lengths)
    def assert_list_of_type(self, lst,typ):
        ''' asserts that lst is a list with elements of typ or empty'''
        assert isinstance(lst, list), 'its not a list'
        types = set([type(d) for d in lst])
        assert len(types) <= 1, 'multiple types in list'
        if len(lst) > 0:
            assert isinstance(lst[0], typ), 'not of type %s instead %s'%(typ, lst[0])


class sho18(dataset):
    SCHNAM = 'scho18'
    scapend_words = 4 # each word is 2 character
    comment_words = 30
    var_name_words = 4
    def populate(self, 
        SP1CH   =None,  # int       Spikes UET channel number
        STRTCH  =None,  # int       Start sync. UET channel number
        TERMCH  =None,  # int       Terminate UET channel number
        INWCH   =None,  # int       Enter Window UET channel number
        REWCH   =None,  # int       Reward start UET channel number
        ENDCH   =None,  # int       End Trial UET channel number
        TBASE   =None,  # float     UET times base in seconds
        STFORM  =None,  # int       Status table format code
        RNSEED  =None,  # int       Seed used for random number generator
        TGRACL1 =None,  # float     Grace time for LED-1 ? (secs)
        TSPOTL1 =None,  # float     Time to spot LED-1 ? (secs)
        TGRACL2 =None,  # float     Grace time for LED-2 ? (secs)
        TSPOTL2 =None,  # float     Time to spot LED-2 ? (secs)
        SPONTIM =None,  # float     Spontaneous time ? (secs)
        ISDREW  =None,  # float     Inter-seq delay after reward (secs)
        ISDNOREW=None,  # float     Inter-seq delay after no-reward (secs)
        ATTLOW  =None,  # float     Attenuator low value (dB)
        ATTHIGH =None,  # float     Attenuator High value (dB)
        ATTINC  =None,  # float     Attn. Step size (dB)
        SCAPEND =None,  # STR  8    Schema name for appended data
        FXPAR   =None,  # rg        fill in beforehand. checked here.
        #    FXPARV RG OCCURS NFXPAR TIMES
        #        FXVNAM TYPE STRING 8    Fixed Variable name
        #        FXVTYP TYPE I*2         Fixed Var type 1=int,2=fp,3=char
        #        FXVLEN TYPE I*2         Length in 32-bit words
        #        FXVVAL LENGTH SUBTVLEN  Fixed variable value
        COMENT  =None,  # STRING LENGTH 60   Subjective comment
        SUBTPAR =None,  # TYPE RG OCCURS NSUBTASK TIMES
        #    SUBTPARV TYPE RG OCCURS NSUBTPAR TIMES
        #        SUBTVNAM TYPE STRING 8  Sub-Task Variable name
        #        SUBTVTYP TYPE I*2       Sub-Task Var type 1=int,2=fp,3=char
        #        SUBTVLEN TYPE I*2       Length in 32-bit words
        #        SUBTVVAL LENGTH SUBTVLEN   Sub-Task variable value
        AVOLC=None, # TYPE REAL     Voltage conversion factor
        AVCC=None,  #               Voltage Conversion Code
        ANBITS=None,#               No. of bits per sample 16/32
        ADCH=None,  # TYPE RG OCCURS NACH TIMES
        #    02  ACHAN                      A/D Channel number
        #    02  SRATE TYPE REAL            Sampling rate (samples/sec)
        #    02  ASAMPT TYPE REAL           Analog sampling time in secs
        #    02  NSAMP                      Number of A/D samples
        COILCODE=None,  #                       Coil calib. code (1,2,3 etc.)
        COILINF=None,   # TYPE RG OCCURS NCOIL TIMES
        #    COILPOS STR 8      Coil position (e.g. LEFTEAR,RITEAR)
        #    ADCHX                      A/D channel number for X-position
        #    ADCHY                      A/D channel number for Y-position
        #    COILCOF RG OCCURS NCOILCOF TIMES
        #       COFX REAL         Coefficient for X-direction
        #       COFY REAL         Coefficient for Y-direction
        AVOLCCM=None,   # REAL  Voltage conversion factor for CM
        AVCCCM=None,    #               Voltage conversion code for CM
        ANBITSCM=None,  #               Bits/sample for CM (16 or 32)
        ACHANCM=None,   #               Channel number for CM
        LEDPOS=None,    # RG OCCURS NUMLED TIMES
        #    LEDPAZIM REAL         LED azimuth position (-180 to +180)
        #    LEDPELEV REAL         LED elevation pos. (-90 to +90)
        SPKPOS=None,    # RG OCCURS NUMSPK TIMES
        #    SPKPAZIM REAL         Speaker azimuth pos. (-180 to +180)
        #    SPKPELEV REAL         Speaker elevation pos. (-90 to +90)
        DATA=None,      # TYPE RG OCCURS NSEQ TIMES
        #    TSDATA VECTOR INTEGER                 spike time data
        #    ANDATA TYPE RG OCCURS NACH TIMES   sampled analog data
        #       ANDATA_VECTOR TYPE VECTOR I*2
        #    CMDATA TYPE RG OCCURS NUMCM TIMES  sampled CM data
        #       CMDATA_VECTOR TYPE VECTOR I*2
        #    DERV  RG OCCURS NDERV TIMES
        #        DERVNAM TYPE STRING 8      name of derived var
        #        DERVTYP TYPE I*2           variable type
        #        DERVAL LENGTH DERVLEN      val of derived var
        STATTB=None,    # TYPE RG               Type-3 Status Table
        #   STVARS TYPE RG OCCURS NVSTAT TIMES
        #        STVNAM TYPE STRING 8       name of table var
        #        STVTYP TYPE I*2            variable type
        #        STVAL LENGTH STVLEN                 val of Stat Tab. var.
        #   The user can put lambda functions to point to addresses. 
        #   unless you're reading from a file. these should NOT be hardcoded
        ):
        '''
            this function takes the following:
            SP1CH   ,  # int       Spikes UET channel number
            STRTCH  ,  # int       Start sync. UET channel number
            TERMCH  ,  # int       Terminate UET channel number
            INWCH   ,  # int       Enter Window UET channel number
            REWCH   ,  # int       Reward start UET channel number
            ENDCH   ,  # int       End Trial UET channel number
            TBASE   ,  # float     UET times base in seconds
            STFORM  ,  # int       Status table format code
            LSTAT   ,  # int       Location of Status table
            RNSEED  ,  # int       Seed used for random number generator
            TGRACL1 ,  # float     Grace time for LED-1 ? (secs)
            TSPOTL1 ,  # float     Time to spot LED-1 ? (secs)
            TGRACL2 ,  # float     Grace time for LED-2 ? (secs)
            TSPOTL2 ,  # float     Time to spot LED-2 ? (secs)
            SPONTIM ,  # float     Spontaneous time ? (secs)
            ISDREW  ,  # float     Inter-seq delay after reward (secs)
            ISDNOREW,  # float     Inter-seq delay after no-reward (secs)
            ATTLOW  ,  # float     Attenuator low value (dB)
            ATTHIGH ,  # float     Attenuator High value (dB)
            ATTINC  ,  # float     Attn. Step size (dB)
            SCAPEND ,  # str  8    Schema name for appended data
            FXPAR   ,  [    # Fixed parameter variables give like so...
                            {   'NAM' :  Variable name
                                'TYP' :  Var type 1=int,2=fp,3=char
                                'VAL' :  Variable value pass as array or str
                            }
                        ]
            COMENT  ,  # STRING LENGTH 60   Subjective comment
            SUBTPAR ,   [   # SUBTPAR
                            [  # SUBTPARV
                                {   'NAM': Sub-Task Variable name
                                    'TYP': Var type 1=int,2=fp,3=char
                                    'VAL': variable value
                                }
                            ]
                        ]
            AVOLC   ,   # TYPE REAL     Voltage conversion factor
            AVCC    ,   #               Voltage Conversion Code
            ANBITS  ,   #               No. of bits per sample 16/32
            ADCH    ,   [    #           A/D channels
                            {   ACHAN: int, A/D channel no.
                                SRATE: float, sampling rate Hz
                                ASAMPT: float, sampling time in sec
                                NSAMP: int, no. A/D samples
                            }
                        ]
            COILCODE,   # int   Coil calib. code (1,2,3 etc.)
            COILINF ,   [   # Coil configuration
                            {   COILPOS: str, Coil position e.g. LEFTEAR
                                ADCHX:  A/D channel number for X-position   
                                ADCHY:  A/D channel number for Y-position 
                                COILCOF: [
                                    {      COFX:  real, A/D channel number for X-position 
                                           COFY:  real, A/D channel number for Y-position 
                                    }
                                ]
                            }
                        ]
            AVOLCCM ,   #   REAL  Voltage conversion factor for CM
            AVCCCM  ,   #   Voltage conversion code for CM
            ANBITSCM,   #   Bits/sample for CM (16 or 32)
            ACHANCM ,   #   Channel number for CM
            LEDPOS  ,   [
                            {   AZIM: float, LED azimuth position (-180 to +180) 
                                ELEV: float, LED elevation pos. (-90 to +90)
                            }
                        ]
            SPKPOS  ,   [
                            {   AZIM: real, Speaker azimuth pos. (-180 to +180) 
                                ELEV: real, Speaker elevation pos. (-90 to +90)  
                            }
                        ]
            DATA    ,   [
                            {   UDATA: [{time: , code:}] spike time data 
                                ANDATA: [
                                            [int] sampled analog data
                                        ]
                                CMDATA: [
                                            [int] sampled CM Data
                                        ]
                                DERV:   [
                                            {   DERVNAM: str, name of derived variable
                                                DERVTYP: int, variable type
                                                DERVAL: list or str, value of variable 
                                            }
                                        ]
                            }
                        ]   
            STATTB  ,   [    # status table
                            {   STVARS: [   # status variables
                                            {   STVNAM: str, name of variable
                                                STVTYP: int, variable type
                                                STVAL: list or str, value of variable 
                                            }
                                        ] 
                               
                            }
                        ]           
            '''
        # assert that the repgroups are of the correct form
        self.check_repgroups_form(FXPAR, SUBTPAR, ADCH, 
            COILINF, LEDPOS, SPKPOS, DATA, STATTB)
        
        # check consitent NSEQ
        assert len(DATA) == len(STATTB), 'STATTB and DATA must have the same no trials'
        # check consitent NACH
        try:
            andatas= []
            if len(DATA) > 0 and 'ANDATA' in DATA[0]: 
                andatas = [d['ANDATA'] for d in DATA]
                self.assert_consistent_list_len(andatas)
                # assert len(andatas) == len(ADCH)
            elif len(DATA) == 0: assert len(ADCH) == 0 
        except AssertionError,e: 
            raise AssertionError(('%s DATA[ANDATA](len %s) must have '
                'same length as ADCH (len %s)')%(e,len(andatas), len(ADCH)))

        # UET Data
        try:
            udata = self.check_presence('UDATA', DATA) # return 1/0/error if DATA is bad
            self.add('UDATAPresent', 'int', udata, description='0 No UET data, 1 Yes UET data') 
        except AssertionError,e: raise AssertionError('DATA Must be be a list of dicts')

        # ANDATA
        try:
            adata = self.check_presence('ANDATA',DATA) 
            self.add('ANDATAPresent', 'int', adata, description='0 No A/D data, 1 Yes A/D data')
        except AssertionError,e: raise AssertionError('DATA Must be be a list of dicts')

        # CMDATA
        try:
            cmdata = self.check_presence('CMDATA',DATA)
            self.add('CMDATAPresent', 'int', cmdata, description='0 No CM data, 1 Yes CM data')
        except AssertionError,e: raise AssertionError('DATA Must be be a list of dicts')
 
        self.add('STRTCH','int', STRTCH, description='Start sync. UET channel number')
        self.add('TERMCH','int', TERMCH, description='Terminate UET channel number')
        self.add('INWCH','int', INWCH, description='Enter Window UET channel number')
        self.add('REWCH','int', REWCH, description='Reward start UET channel number')
        self.add('ENDCH','int', ENDCH, description='End Trial UET channel number')
        self.add('TBASE','int', TBASE, description='UET times base in seconds')

        # scho18 always has a stat table type 3. see basement documentation for more.
        # althought the schema is included in this
        self.add('STFORM', 'int', 3, 
            description='Status table format code. always 3 for scho18')
        
        # NUMPT = number of ADDRPTs in STATTB
        # filled in automatically as num_elems in STATTB
        self.add('NUMPT', 'int', description='Number of pointers per trial in STATTB') 

        # LSTAT
        stattb_pointer = lambda: self.get_pointer('STATTB')
        self.add('LSTAT','int',stattb_pointer, description='Location of Status table')

        # NSEQ link this to STATTB and DATA
        # filled in automatically as num_elems in DATA and STATTB
        self.add('NSEQ','int', description='No of trials. i.e. rows in STATTB and DATA') 

        self.add('RNSEED', 'int', RNSEED, description='seed used for RNG')
        self.add('TGRACL1', 'float', TGRACL1, 
                            description=  'Grace time for LED-1 ? (secs)')
        self.add('TSPOTL1', 'float', TSPOTL1, 
                            description=  'Time to spot LED-1 ? (secs)')
        self.add('TGRACL2', 'float', TGRACL2, 
                            description=  'Grace time for LED-2 ? (secs)')
        self.add('TSPOTL2', 'float', TSPOTL2, 
                            description=  'Time to spot LED-2 ? (secs)')
        self.add('SPONTIM', 'float', SPONTIM, 
                            description=  'Spontaneous time ? (secs)')
        self.add('ISDREW', 'float', ISDREW, 
                            description=   'Inter-seq delay after reward (secs)')
        self.add('ISDNOREW', 'float', ISDNOREW, 
                            description= 'Inter-seq delay after no-reward (secs)')
        self.add('ATTLOW', 'float', ATTLOW, 
                            description=   'Attenuator low value (dB)')
        self.add('ATTHIGH', 'float', ATTHIGH, 
                            description=  'Attenuator High value (dB)')
        self.add('ATTINC', 'float', ATTINC, 
                            description=   'Attn. Step size (dB)')
        
        app_data_loc = lambda: self.get_pointer('STATTB')
        self.add('LAPEND', 'int', app_data_loc, description='Loc of "appended data"')


        self.add('SCAPEND', 'str', SCAPEND, num_elems=self.scapend_words, 
            description='schema name for appended data')

        def len_fxpar_words(self):
            if hasattr(self.get('FXPAR'), 'size'): return self.get('FXPAR').size
            else: return -1
        len_fxpar_words_ref = lambda: len_fxpar_words(self)
        self.add('LFXPAR', 'int', len_fxpar_words_ref, description='Length of FXPAR in words')
        self.add('NFXPAR', 'int', description='No vars in FXPAR') 
        # gets filled automatically

        # FXPAR
        self.add('FXPAR','rg', num_elems='NFXPAR', 
            description='Fixed variables for subject')

        self['FXPAR'].add('FXVNAM', 'str', num_elems=self.var_name_words, 
            description='Fixed variable name')
        self['FXPAR'].add('FXVTYP', 'short', 
            description='Fixed Var type 1=int,2=fp,3=char')
        self['FXPAR'].add('FXVLEN', 'short', description='No. words in variable list')
        self['FXPAR'].add('FXVVAL','list', elem_type='FXVTYP', num_elems='FXVLEN', 
            description='Value of fixed variable')

        for i,grp in enumerate(FXPAR):
            self['FXPAR'].add_group()
            self['FXPAR'][i]['FXVNAM'].set(grp['NAME'])
            self['FXPAR'][i]['FXVTYP'].set(grp['TYPE'])
            self['FXPAR'][i]['FXVVAL'].set(grp['VAL']) # automatically sets FXVLEN

        self.add('COMENT', 'str', COMENT, num_elems=self.comment_words, 
            description='Subjective comment')

        # SUBTASK PARAMS 

        self.add('NSUBTASK', 'int', description='No subtasks in experiment')
        # filled automatically by linking to SUBTPAR
        self.add('SUBTPAR', 'rg', num_elems='NSUBTASK', description='Subtask parameters')

        self['SUBTPAR'].add('LSUBTPARV', 'int', description='Lenth of SUBTPARV in words')
        self['SUBTPAR'].add('NSUBTPARV', 'int', description='no of SUBTPARV in words')
        self['SUBTPAR'].add('SUBTPARV', 'rg', num_elems='NSUBTPARV',
            description='Variables for this subtask')

        for i,grp in enumerate(SUBTPAR):
            self['SUBTPAR'].add_group()
            def len_subtparv_words(self):
                subtpar = self.get('SUBTPAR')
                if hasattr(subtpar[i], 'size'): return subtpar[i].size
                else: return -1 
            len_subtparv_words_ref = lambda: len_subtparv_words(self)
            self['SUBTPAR'][i]['LSUBTPARV'].set(len_subtparv_words_ref)

            # set up internal rep group 
            subtparv = self['SUBTPAR'][i]['SUBTPARV']
            subtparv.add('SUBTVNAM', 'str', 
                num_elems=self.var_name_words, description='name of subtask variable')
            subtparv.add('SUBTVTYP', 'short', 
                description='Sub-Task Var type 1=int,2=fp,3=char')
            subtparv.add('SUBTVLEN', 'short', description='no. words in variable list')
            subtparv.add('SUBTVVAL', 'list', num_elems='SUBTVLEN', elem_type='SUBTVTYP',
                description='value of subtask variable')

            for j,var in enumerate(grp):
                subtparv.add_group()
                subtparv[j]['SUBTVNAM'].set(var['NAME'])
                subtparv[j]['SUBTVTYP'].set(var['TYPE'])
                subtparv[j]['SUBTVVAL'].set(var['VAL']) # automatically sets SUBTVLEN

            
        self.add('AVOLC', 'float', AVOLC, description='Voltage conversion factor')
        self.add('AVCC', 'int', AVCC, description='Voltage Conversion Code')
        self.add('ANBITS', 'int', ANBITS, description='No. of bits per sample 16/32')

        # analog channels
        self.add('NACH', 'int', description='No. of A/D channels') # filled automatically
        self.add('ADCH', 'rg',num_elems='NACH', 
            description='Analog channel configuration')

        # set up repgroup
        self['ADCH'].add('ACHAN', 'int', description=' A/D channel no.')
        self['ADCH'].add('SRATE', 'float', description='Sampling rate (hz)')
        self['ADCH'].add('ASAMPT', 'float', description='Analog sampling time in sec')
        self['ADCH'].add('NSAMP', 'int', description='Number of A/D samples')

        for i,grp in enumerate(ADCH):
            self['ADCH'].add_group()
            self['ADCH'][i]['ACHAN'].set(grp['ACHAN'])
            self['ADCH'][i]['SRATE'].set(grp['SRATE'])
            self['ADCH'][i]['ASAMPT'].set(grp['ASAMPT'])
            self['ADCH'][i]['NSAMP'].set(grp['NSAMP'])


        self.add('COILCODE', 'int', COILCODE, description='Coil calib. code (1,2,3 etc.)')
        self.add('NCOILCOF', 'int', description='No of coil calibration coefs')
        self.add('NCOIL', 'int', description='No. of coils')
        self.add('COILINF', 'rg', num_elems='NCOIL', description='Coil configurations')

        self['COILINF'].add('COILPOS','str', num_elems=self.var_name_words, 
            description='Coil position name')
        self['COILINF'].add('ADCHX', 'int', description='A/D chan no. for X-position')
        self['COILINF'].add('ADCHY', 'int', description='A/D chan no. for Y-position')
        self['COILINF'].add('COILCOF', 'rg', num_elems='NCOILCOF', 
            description='Coil coefficients')

        for i,coil in enumerate(COILINF):
            self['COILINF'].add_group()
            
            coilinf = self['COILINF'][i]

            coilinf['COILPOS'].set(coil['COILPOS'])
            coilinf['ADCHX'].set(coil['ADCHX'])
            coilinf['ADCHY'].set(coil['ADCHY'])
            coilinf['COILCOF'].add('COFX', 'float', description='coil coefficients for x')
            coilinf['COILCOF'].add('COFY', 'float', description='coil coefficients for y')

            for j,coef in enumerate(coil['COILCOF']):
                coilinf['COILCOF'].add_group()
                coilcof = coilinf['COILCOF'][j]
                coilcof['COFX'].set(coef['COFX'])
                coilcof['COFY'].set(coef['COFY'])

        self.add('AVOLCCM', 'float', AVOLCCM, description='Volt conversion factor for CM')
        self.add('AVCCCM', 'int', AVCCCM, description='Voltage conversion code for CM')
        self.add('ANBITSCM', 'int', ANBITSCM, description='Bits/sample for CM (16 or 32)')
        self.add('ACHANCM', 'int', ACHANCM, description='Channel number for CM')
        self.add('NUMCM', 'int', description='Number of CM recordings per trial')
        # filled in automatically during DATA
        self.add('NUMLED', 'int', description='Total number of LEDs')
        # filled in automatically during LEDPOS

        self.add('LEDPOS', 'rg', num_elems='NUMLED', 
            description='LED positions')
        self['LEDPOS'].add('LEDPAZIM', 'float', 
            description='LED azimuth position (-180 to +180)')
        self['LEDPOS'].add('LEDPELEV', 'float',
         description='LED elevation position (-90 to +90)')

        for i, led in enumerate(LEDPOS):
            self['LEDPOS'].add_group()
            ledpos = self['LEDPOS'][i]
            ledpos['LEDPAZIM'].set(led['AZIM'])
            ledpos['LEDPELEV'].set(led['ELEV'])

        self.add('NUMSPK', 'int', description='Total nunmber of Speakers')
        self.add('SPKPOS', 'rg', num_elems='NUMSPK', description='Speaker positions')

        self['SPKPOS'].add('SPKPAZIM', 'float', 
            description='Speaker azimuth pos. (-180 to +180)')
        self['SPKPOS'].add('SPKPELEV', 'float', 
            description='Speaker elevation pos. (-90 to +90)')

        for i,spk in enumerate(SPKPOS):
            self['SPKPOS'].add_group()
            spkpos = self['SPKPOS'][i]
            spkpos['SPKPAZIM'].set(spk['AZIM'])
            spkpos['SPKPELEV'].set(spk['ELEV'])


        self.add('LDUMMY', 'int', 1, description='Length of DUMMY in words')
        self.add('DUMMY', 'str', '', num_elems='LDUMMY', description='Nothing useful')

        self.add('DATA', 'rg', num_elems='NSEQ', description='Data, organized by trials')
        
        self['DATA'].add('UDATA', 'vec', elem_type='uet', 
            description='UET events in this trial')
        self['DATA'].add('ANDATA', 'rg', num_elems='NACH', 
            description='sampled analog data')
        self['DATA'].add('CMDATA', 'rg', num_elems='NUMCM',  
            description='sampled cm data')
        self['DATA'].add('NDERV', 'int', description='No Derived variables')
        self['DATA'].add('DERV', 'rg', num_elems='NDERV', description='Derived variables')


        for i,trial in enumerate(DATA):
            self['DATA'].add_group()
            
            data = self['DATA'][i]
            # ipdb.set_trace()
            if 'UDATA' in trial: data['UDATA'].set(trial['UDATA'])
            else: data['UDATA'].set([])


            dsetlog.warn(str(type(data['ANDATA'])) + ':' + str(data['ANDATA'].__dict__))

            # ipdb.set_trace()
            data['ANDATA'].add('ANDATA_VECTOR', 'vec', elem_type='short')
            if 'ANDATA' in trial: 
                for j,adch in enumerate(trial['ANDATA']):
                    data['ANDATA'].add_group() 
                    data['ANDATA'][j]['ANDATA_VECTOR'].set(adch)

            data['CMDATA'].add('CMDATA_VECTOR', 'vec',  elem_type='short')
            if 'CMDATA' in trial: 
                for j,adch in enumerate(trial['CMDATA']):
                    data['CMDATA'].add_group() 
                    data['CMDATA'][j]['CMDATA_VECTOR'].set(adch)

            data['DERV'].add('DERVNAM','str', num_elems=self.var_name_words, 
                description='name of derived var')
            data['DERV'].add('DERVTYP','short', description='variable type')
            data['DERV'].add('DERVLEN', 'short', description='length in 32 bit wrds')
            data['DERV'].add('DERVAL', 'list', elem_type='DERVTYP', num_elems='DERVLEN', 
                description='val of derived var')

            for j,var in enumerate(trial['DERV']):
                data['DERV'].add_group()
                derv = data['DERV'][j]
                derv['DERVNAM'].set(var['NAME'])
                derv['DERVTYP'].set(var['TYPE'])
                derv['DERVAL'].set(var['VAL'])


        self.add('STATTB', 'rg', num_elems='NSEQ', description='Type 3 status table')
        
        self['STATTB'].add('NVSTAT', 'int', description='No. of vars in this row')
        self['STATTB'].add('STVARS', 'rg', num_elems='NVSTAT', 
            description='Status table variables')
        self['STATTB'].add('ADDRPT', 'list', num_elems='NUMPT', elem_type='int')

        
        for i,trial in enumerate(STATTB):
            self['STATTB'].add_group()
            entry = self['STATTB'][i]

            entry['STVARS'].add('STVNAM', 'str', num_elems=self.var_name_words, 
                description='name of status variable')
            entry['STVARS'].add('STVTYP', 'short', description= 'type of status var')
            entry['STVARS'].add('STVLEN', 'short', 
                description='Len of status var in words')
            entry['STVARS'].add('STVAL', 'list', elem_type='STVTYP', num_elems='STVLEN', 
                description='status table variable value')

            for j,vardef in enumerate(trial['STVARS']):
                entry['STVARS'].add_group()
                print '\n\n\n###############'
                var = entry['STVARS'][j]            
                var['STVNAM'].set(vardef['NAME'])
                var['STVTYP'].set(vardef['TYPE'])
                var['STVAL'].set(vardef['VAL'])

            uetandandata_locs = lambda: [
                self['DATA'][i].get_pointer('UDATA') \
                    + self.get_pointer([{'name':'DATA'},{'name':'UDATA','index':i}]),
                self['DATA'][i].get_pointer('ANDATA') \
                    + self.get_pointer([{'name':'DATA'},{'name':'UDATA','index':i}])
            ]
            entry['ADDRPT'].set(uetandandata_locs)

        self['LSTAT'].set(self['LSTAT'].eval())
        self['LAPEND'].set(self['LAPEND'].eval())
        self['LFXPAR'].set(self['LFXPAR'].eval())
        ipdb.set_trace()

    def check_repgroups_form(self, FXPAR, SUBTPAR, ADCH, 
        COILINF, LEDPOS, SPKPOS, DATA, STATTB):
        ''' checks that all the rep groups passed in are of the correct form'''
        self.checkVars(FXPAR, 'FXPAR')
        self.checkSUBTPAR(SUBTPAR)
        self.checkADCH(ADCH)
        self.checkCOILINF(COILINF)
        self.checkPOS(LEDPOS,'LEDPOS')
        self.checkPOS(SPKPOS,'SPKPOS')
        self.checkDATA(DATA)
        self.checkSTATTB(STATTB)
    def checkVars(self, VARSRG, name):
        ''' asserts that VARSRG has the std variable repgroup layout
            [{  NAME: 
                TYPE:
                VAL:
            }]'''
        try: 
            self.assert_list_of_type(VARSRG, dict)
            for d in VARSRG:
                assert 'NAME' in d, 'NAME not in d'
                assert 'TYPE' in d, 'TYPE not in d'
                assert 'VAL' in d, 'VAL not in d'
        except AssertionError, e: raise AssertionError(('%s %s is a Variable rep group '
            'it must have NAME, TYPE and VALUE keys in all dicts')%(e,name))
    def checkSUBTPAR(self, SUBTPAR):
        ''' checks SUBTPAR is in the proper format
            SUBTPAR ,   [   # Subtasks
                            [  # subtask parameters
                                {   'NAM': Sub-Task Variable name
                                    'TYP': Var type 1=int,2=fp,3=char
                                    'VAL': variable value
                                }
                            ]
                        ]
            '''
        try:
            self.assert_list_of_type(SUBTPAR, list)
            for l in SUBTPAR:
                self.checkVars(l, 'Subtask parameters')
        except AssertionError,e:
            raise AssertionError(('''%s SUBTPAR must be of the form:
            SUBTPAR ,   [   # Subtasks
                            [  # subtask parameters
                                {   'NAME': Sub-Task Variable name
                                    'TYPE': Var type 1=int,2=fp,3=char
                                    'VAL': variable value
                                }
                            ]
                        ]
             '''%e))
    def checkADCH(self, ADCH):
        ''' checks that ADCH is of the form:
            ADCH    ,   [    #           A/D channels
                            {   ACHAN: int, A/D channel no.
                                SRATE: float, sampling rate Hz
                                ASAMPT: float, sampling time in sec
                                NSAMP: int, no. A/D samples
                            }
                        ]
            '''
        try: 
            self.assert_list_of_type(ADCH, dict)
            for d in ADCH:
                assert 'ACHAN' in d
                assert 'SRATE' in d
                assert 'ASAMPT' in d
                assert 'NSAMP' in d
        except AssertionError:
            raise AssertionError(''' ADCH must be of the form:
                ADCH    ,   [    #           A/D channels
                                {   ACHAN: int, A/D channel no.
                                    SRATE: float, sampling rate Hz
                                    ASAMPT: float, sampling time in sec
                                    NSAMP: int, no. A/D samples
                                }
                            ]
          ''')
    def checkCOILINF(self, COILINF):
        '''   checks COILINF is in the form:
            COILINF ,   [   # Coil configuration
                            {   COILPOS: str, Coil position e.g. LEFTEAR
                                ADCHX:  A/D channel number for X-position   
                                ADCHY:  A/D channel number for Y-position 
                                COILCOF: [
                                    {      COFX:  real, A/D channel number for X-position 
                                           COFY:  real, A/D channel number for Y-position 
                                    }
                                ]
                            }
                        ]
            '''
        try:
            self.assert_list_of_type(COILINF, dict)
            for d in COILINF:
                assert 'COILPOS' in d
                assert 'ADCHX' in d
                assert 'ADCHY' in d
                assert 'COILCOF' in d
                self.assert_list_of_type(d['COILCOF'], dict)
                self.checkCOF(d['COILCOF'])
        except AssertionError:
            raise AssertionError(''' COILINF must be of the form:
                            COILINF ,   [   # Coil configuration
                            {   COILPOS: str, Coil position e.g. LEFTEAR
                                ADCHX:  A/D channel number for X-position   
                                ADCHY:  A/D channel number for Y-position 
                                COILCOF: [
                                    {      COFX:  real, A/D channel number for X-position 
                                           COFY:  real, A/D channel number for Y-position 
                                    }
                                ]
                            }
                        ]''') 
    def checkCOF(self, COFS):
        ''' asserts COFS is of the form:
            COILCOF: [
                {      COFX:  real, A/D channel number for X-position 
                       COFY:  real, A/D channel number for Y-position 
                }
            ] '''
        try:
            self.assert_list_of_type(COFS, dict)
            for d in COFS:
                assert 'COFX' in d
                assert 'COFY' in d
        except AssertionError:
            raise AssertionError(''' COFS must be in the form:
                        COILCOF: [
                            {      COFX:  real, A/D channel number for X-position 
                                   COFY:  real, A/D channel number for Y-position 
                            }
                        ]''')
    def checkPOS(self, POS, name):
        ''' checks that POS is of the form:
            POS     ,   [
                            {   AZIM: float, LED azimuth position (-180 to +180) 
                                ELEV: float, LED elevation pos. (-90 to +90)
                            }
                        ] '''
        try:
            self.assert_list_of_type(POS, dict)
            for d in POS:
                dsetlog.debug('Checking %s dict: %s'%(name, d))
                assert 'AZIM' in d, 'AZIM not in d'
                assert 'ELEV' in d, 'ELEV not in d'
        except AssertionError,e:
            raise AssertionError('''%s %s must be in the form:
                %s  ,   [
                            {   AZIM: float, azimuth position (-180 to +180) 
                                ELEV: float, elevation pos. (-90 to +90)
                            }
                        ]
            '''%(e,name, name))
    def checkDATA(self, DATA):
        ''' checks DATA is of the form:
            DATA    ,   [
                            {   UDATA: [{time: , code:}] spike time data 
                                ANDATA: [
                                            [int] sampled analog data
                                        ]
                                CMDATA: [
                                            [int] sampled CM Data
                                        ]
                                DERV:   [
                                            {   DERVNAM: str, name of derived variable
                                                DERVTYP: int, variable type
                                                DERVAL: list or str, value of variable 
                                            }
                                        ]
                            }
                        ]   '''
        try:
            dsetlog.debug('checking DATA given %s'%DATA)
            self.assert_list_of_type(DATA, dict)
            dsetlog.debug('checking DATA is list of dicts')
            
            # assert that all dicts have the same keys
            self.assert_consistent_list_of_dicts(DATA) 
            for d in DATA:
                if 'UDATA' in d: # a list of {code, time}
                    self.checkUET(d['UDATA'])
                    dsetlog.debug('DATA[UDATA] and is correctly formatted')
                if 'ANDATA' in d:
                    self.assert_list_of_type(d['ANDATA'], list)
                    dsetlog.debug('DATA[ANDATA] exists and is correctly formatted')
                if 'CMDATA' in d:
                    self.assert_list_of_type(d['CMDATA'], list)
                    dsetlog.debug('DATA[CMDATA] exists and is correctly formatted')

                self.checkVars(d['DERV'], 'DERV')
                dsetlog.debug('DATA[DERV] exisits and is correctly formatted')
        except AssertionError,e:
            raise AssertionError('''%s DATA must be of the form:
                DATA    ,   [
                            {   UDATA: [{time: , code:}] spike time data 
                                ANDATA: [
                                            [int] sampled analog data
                                        ]
                                CMDATA: [
                                            [int] sampled CM Data
                                        ]
                                DERV:   [
                                            {   NAME: str, name of derived variable
                                                TYPE: int, variable type
                                                VAL: list or str, value of variable 
                                            }
                                        ]
                            }
                            ]   '''%e)
    def checkUET(self, UDATA):
        ''' Checks UDATA is of the form
            UDATA:  [
                {   code:
                    time: 
                }
            ]
            '''
        try:
            self.assert_list_of_type(UDATA, dict)
            for d in UDATA:
                assert 'code' in d, 'code not in d'
                assert 'time' in d, 'time not in d'
        except AssertionError,e:
            raise AssertionError('''%s Checks UDATA is of the form
                        UDATA:  [
                            {   code:
                                time: 
                            }
                        ]   '''%e)
    def checkSTATTB(self, STATTB):
        ''' checks STATTB is of the form:
             STATTB  ,   [    # status table
                            {   STVARS: [   # status variables
                                            {   NAME: str, name of variable
                                                TYPE: int, variable type
                                                VAL: list or str, value of variable 
                                            }
                                        ] 
                            }
                        ]   '''

        try:
            self.assert_list_of_type(STATTB, dict)
            for d in STATTB:
                assert 'STVARS' in d
                self.checkVars(d['STVARS'], 'STVARS')
        except AssertionError: raise AssertionError(''' STATTB must be of the form:
             STATTB  ,   [    # status table
                            {   STVARS: [   # status variables
                                            {   NAME: str, name of variable
                                                TYPE: int, variable type
                                                VAL: list or str, value of variable 
                                            }
                                        ] 
                            }
                        ]   ''')







class unittests():
    def __init__(self):
        dsetlog.warn('\n\n\n###RUNNING DATFILE UNIT TESTS')
        # IPython.embed(local_ns = locals())
        # self.testrepgroupsofrepgroupsofvecs()
        self.testsho18forpythonicdisplay()
        # self.testcalcsize()
        dsetlog.warn('\n\n\n###DATFILE UNIT TESTS PASSED!!!')
    
    def testrepgroupsofrepgroupsofvecs(self):
        dsetlog.warn('\n\n\n###CREATING simple sch for creation or complex repgroups')
        data =  [
                            {   'ANDATA': [
                                            [5],[4],[1,2,3] # sampled analog data
                                        ],
                             },
                             {   'ANDATA': [
                                            [9],[8],[6,7] # sampled analog data
                                        ],
                             },
                             {   'ANDATA': [
                                            [9],[8],[6,7] # sampled analog data
                                        ],
                             }
                        ]

        sch = dataset(ANID='testsubj',
                    DSID='first',
                    DATE='0116-16',
                    TIME=0,
                    EXTYP='PYTH',)
        sch.add('NSEQ', 'int')
        sch.add('NACH', 'int')
        
        DATA = sch.add('DATA', 'rg', num_elems='NSEQ', description='Data, organized by trials')

        dsetlog.warn('\n\n\ncreated DATA \n\n\n\n')

        DATA.add('ANDATA', 'rg', num_elems='NACH', 
            description='sampled analog data')

        dsetlog.warn('\n\n\ncreated ANDATA \n\n\n\n')

        
        # IPython.embed(local_ns = locals())
        # ipdb.set_trace()
        for i,andatas in enumerate(data): # go through outter list stop at each entry

            dsetlog.warn('\n\n\nABOUT TO ADD GROUP TO DATA \n\n\n\n')

            DATA.add_group()
            dsetlog.warn('\n\n\nADDED GROUP TO DATA \n\n\n\n')
            ANDATA = DATA[i]['ANDATA'] # grab the ANDATA datum in the ith group of DATA
            
            dsetlog.warn('\n\n\nSELECTED ANDATA at %s '%i)
            dsetlog.warn('\n\n\n\n ANDATA has the following attributes :%s'%ANDATA.__dict__)

            ANDATA.add('ANDATA_VECTOR', 'vec', elem_type='short') # inside each ANDATA is a vector that occurs NACH times
            dsetlog.warn('\n\n\nADDED VECTOR DATUM TO ANDATA at %s \n\n\n\n'%i)

            v_list = andatas['ANDATA'] # open the ANDATA dic
            for k,v in enumerate(v_list): # go through vectors inside ANDATA vec
                dsetlog.warn('####\t\tadding group %s to ANDATA[%s]'%(k,i))
                print sch
                ANDATA.add_group()
                VECTOR = ANDATA[k]
                VECTOR = VECTOR['ANDATA_VECTOR'] 
                VECTOR.set(v)



            print sch
        dsetlog.warn('\n\n\n###DONE CREATING simple sch for creation or complex repgroups')
    def testsho18forpythonicdisplay(self):
        dsetlog.warn('\n\n\n###CREATING scho18 for pythonic display')
        sch = sho18(ANID='testsubj',
                    DSID='first',
                    DATE='0116-16',
                    TIME=0,
                    EXTYP='PYTH',)
        sch.populate(
            SP1CH=3   ,  # int       Spikes UET channel number
            STRTCH=4  ,  # int       Start sync. UET channel number
            TERMCH=5  ,  # int       Terminate UET channel number
            INWCH=6   ,  # int       Enter Window UET channel number
            REWCH=7   ,  # int       Reward start UET channel number
            ENDCH=8   ,  # int       End Trial UET channel number
            TBASE=9   ,  # float     UET times base in seconds
            STFORM=10  ,  # int       Status table format code
            RNSEED=13  ,  # int       Seed used for random number generator
            TGRACL1=14 ,  # float     Grace time for LED-1 ? (secs)
            TSPOTL1=15 ,  # float     Time to spot LED-1 ? (secs)
            TGRACL2=16 ,  # float     Grace time for LED-2 ? (secs)
            TSPOTL2=17 ,  # float     Time to spot LED-2 ? (secs)
            SPONTIM=18 ,  # float     Spontaneous time ? (secs)
            ISDREW=19  ,  # float     Inter-seq delay after reward (secs)
            ISDNOREW=20,  # float     Inter-seq delay after no-reward (secs)
            ATTLOW=21  ,  # float     Attenuator low value (dB)
            ATTHIGH=22 ,  # float     Attenuator High value (dB)
            ATTINC=23  ,  # float     Attn. Step size (dB)
            SCAPEND='24' ,  # str  8    Schema name for appended data
            FXPAR=  [    # Fixed parameter variables give like so...
                            {   'NAME' :  'fxvar1',
                                'TYPE' :  3,
                                'VAL' :  'Variable value pass as array or str',
                            },
                            {'NAME':'fxvar2',
                            'TYPE': 2,
                            'VAL':4}
                        ],
            COMENT = 'boo' ,  # STRING LENGTH 60   Subjective comment
            SUBTPAR =   [   # SUBTPAR
                            [  # SUBTPARV
                                {   'NAME': 'subtparv1',
                                    'TYPE': 1,
                                    'VAL': [1,2,3,4],
                                }
                            ],
                            [    {   'NAME': 'subtparv2',
                                    'TYPE': 1,
                                    'VAL': [1,2,3,4],
                                }
                            ]
                        ],
            AVOLC  = 0 ,   # TYPE REAL     Voltage conversion factor
            AVCC   = 0 ,   #               Voltage Conversion Code
            ANBITS = 0 ,   #               No. of bits per sample 16/32
            ADCH   =    [    #           A/D channels
                            {   'ACHAN': 3, # int, A/D channel no.
                                'SRATE': 4, #float, sampling rate Hz
                                'ASAMPT': 5,    #float, sampling time in sec
                                'NSAMP': 6, #int, no. A/D samples
                            }
                        ],
            COILCODE = 1,   # int   Coil calib. code (1,2,3 etc.)
            COILINF =   [   # Coil configuration
                            {   'COILPOS': 'str, Coil position e.g. LEFTEAR',
                                'ADCHX':  3,   
                                'ADCHY':  4, 
                                'COILCOF': [
                                    {      'COFX':  5, 
                                           'COFY':  6, 
                                    }
                                ]
                            }
                        ],
            AVOLCCM=0 ,   #   REAL  Voltage conversion factor for CM
            AVCCCM=1  ,   #   Voltage conversion code for CM
            ANBITSCM=2,   #   Bits/sample for CM (16 or 32)
            ACHANCM=3 ,   #   Channel number for CM
            LEDPOS=    [
                            {   'AZIM': 1,#float, LED azimuth position (-180 to +180) 
                                'ELEV': 1,#float, LED elevation pos. (-90 to +90)
                            }
                        ],
            SPKPOS  =   [
                            {   'AZIM': 0, # real, Speaker azimuth pos. (-180 to +180) 
                                'ELEV': 0, # real, Speaker elevation pos. (-90 to +90)  
                            }
                        ],
            DATA    =   [
                            {   'UDATA': [{'time': 1, 'code':1}], # spike time data 
                                'ANDATA': [
                                            [2] # sampled analog data occur nach times
                                        ],
                                'CMDATA': [
                                            [3] # sampled CM Data
                                        ],
                                'DERV':   [
                                            {   'NAME': 'derv1', # str, name of derived variable
                                                'TYPE': 1, # int, variable type
                                                'VAL': [1,2,3], # list or str, value of variable 
                                            }
                                        ],
                            },
                            {   'UDATA': [{'time': 1, 'code':1}], # spike time data 
                                'ANDATA': [
                                            [2] # sampled analog data occur nach times
                                        ],
                                'CMDATA': [
                                            [3] # sampled CM Data
                                        ],
                                'DERV':   [
                                            {   'NAME': 'derv2', # str, name of derived variable
                                                'TYPE': 1, # int, variable type
                                                'VAL': [4,5,6], # list or str, value of variable 
                                            }
                                        ],
                            }
                        ],   
            STATTB  =   [    # status table
                            {   'STVARS': [   # status variables
                                            {   'NAME': 'stvar1', # str, name of variable
                                                'TYPE': 3, # int, variable type
                                                'VAL': 'sdflasjl', # list or str, value of variable 
                                            }
                                        ] 
                               
                            },
                            {   'STVARS': [   # status variables
                                            {   'NAME': 'stvar2', # str, name of variable
                                                'TYPE': 3, # int, variable type
                                                'VAL': 'sdflasjl', # list or str, value of variable 
                                            }
                                        ] 
                               
                            }
                        ]
                )
        dsetlog.warn(str(sch))   
    def testcalcsize(self):
        ds = datumlist()
        sizeofstuff = lambda: ds['stuff'].size
        lenofstuff = ds.add('len of stuff', 'int', sizeofstuff)
        dsetlog.warn('len of stuff: %s'%lenofstuff.size)
        stuff = ds.add('stuff', 'rg')
        stuff.add_group()
        stuff[0].add('foo', 'int', 1)
        dsetlog.warn('len of stuff: %s'%lenofstuff.size)
        ipdb.set_trace()
        stuff[0].add('foo1', 'int', 2  )
        dsetlog.warn('len of stuff: %s'%lenofstuff.size)
        
        lenofstuff.set(lenofstuff.eval())
        dsetlog.warn('%s'%ds)

        
unittests()