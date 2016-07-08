from utils import make_logger, logging, truncfile

debuglog = 'debug.log'
frmt = '%(name)s:%(levelno)s:%(lineno)s:%(message)s'

truncfile(debuglog)

# for logging things in edf
edflog = make_logger('edf_log',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.WARNING
    )


# for logging things in main
mainlog = make_logger('main_log',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.WARNING
    )


# for logging things in datfiles
datflog = make_logger('datfile_log',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.WARNING
    )

# for logging things in dat_primitive
primlog = make_logger('Primitive_log',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.WARNING
    )

# for logging things in datumlist
datumlistlog = make_logger('datumlistlog',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.DEBUG)

# for logging things in datums
datumlog = make_logger('datumlog',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    # lvl=logging.WARNING,
    lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.DEBUG)

# for logging things in dataset
dsetlog = make_logger('dsetlog',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.DEBUG)

# for logging things in rep_Group
rglog = make_logger('rglog',
    frmt=frmt,
    fpath=debuglog,
    stdout=True,
    # lvl=logging.DEBUG, # use one of the following to easily set the stdout log level
    # lvl=logging.INFO,
    lvl=logging.WARNING,
    # lvl=logging.ERROR,
    # lvl=logging.CRITICAL,
    flvl = logging.DEBUG)

