LOGGING_LEVEL = 'WARNING'
LOG_STDOUT = True
'''
    configuration file for ADSJournals system
'''
# COLLECTIONS is a list of which collections/databases are stored
COLLECTIONS = ['ast', 'phy', 'gen']

# DATA_DIRECTORY:
JDB_DATA_DIR = '/proj/ads/abstracts/config/journalsdb/PIPELINE/data/'

# BIBSTEMS has bibstem, R/J/C/etc, and canonical name
BIBSTEMS_FILE = JDB_DATA_DIR + 'bibstems.dat'

# JOURNAL_ABBREV has bibstem and multiple title abbreviations (e.g.
# A&A, AA, Astron. & Astrophys.)
JOURNAL_ABBREV_FILE = JDB_DATA_DIR + 'journals_abbrev.dat'

JOURNAL_ISSN_FILE = JDB_DATA_DIR + 'journal_issn'
ISSN_JOURNAL_FILE = JDB_DATA_DIR + 'issn2journal'
CANONICAL_BIB_FILE = JDB_DATA_DIR + 'bib2accno.dat'

# RASTERIZING.xml directory
RASTER_CONFIG_DIR = JDB_DATA_DIR + 'raster_config/'

# REFSOURCE_FILE
BIB_TO_REFS_FILE = JDB_DATA_DIR + 'citing2file.dat'

# ESOURCES: for holdings table
# Any new esources must be **prepended** to this list
ESOURCE_LIST = ['PUB_HTML', 'PUB_PDF', 'EPRINT_HTML', 'EPRINT_PDF',
                'ADS_SCAN', 'ADS_PDF']

BIBSTEM_VOLUMES = ['book', 'conf', 'work', 'proc', 'rept', 'symp', 'prop']
