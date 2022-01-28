'''
No.
'''
from __future__ import print_function
import argparse
import json
import os
from adsputils import setup_logging, load_config
from journals import tasks
from journals import utils

proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                       level=config.get('LOGGING_LEVEL', 'INFO'),
                       attach_stdout=config.get('LOG_STDOUT', False))



def get_arguments():
    '''
    No.
    '''

    parser = argparse.ArgumentParser(description='Command line options.')

    parser.add_argument('-lm',
                        '--load-master',
                        dest='load_master',
                        action='store_true',
                        help='Load master list of bibstems')

    parser.add_argument('-la',
                        '--load-abbrevs',
                        dest='load_abbrevs',
                        action='store_true',
                        help='Load list of journal name abbreviations')

    parser.add_argument('-ch',
                        '--calculate-holdings',
                        dest='calc_holdings',
                        action='store_true',
                        help='Populate holdings from Solr data')

    parser.add_argument('-ca',
                        '--load-complete-ast',
                        dest='load_ca',
                        action='store_true',
                        help='Load spreadsheet complete_ast')

    parser.add_argument('-lr',
                        '--load-rasterconf',
                        dest='load_raster',
                        action='store_true',
                        help='Load rasterization control parameters')

    parser.add_argument('-ls',
                        '--load-refsources',
                        dest='load_refsources',
                        action='store_true',
                        help='Load refsources from citing2file.dat')

    parser.add_argument('-xi',
                        '--checkin-table',
                        dest='checkin_table',
                        action='store',
                        default=None,
                        help='Check IN table TABLE from GSheets')

    parser.add_argument('-xo',
                        '--checkout-table',
                        dest='checkout_table',
                        action='store',
                        default=None,
                        help='Check OUT table TABLE to GSheets')

    args = parser.parse_args()
    return args


def load_master_table():
    '''
    No.
    '''
    bibstems = utils.read_bibstems_list()
    recs = []
    for key, value in list(bibstems.items()):
        bibstem = key
        pubtype = value['type']
        journal_name = value['pubname']
        recs.append((bibstem, pubtype, journal_name))
    if recs:
        logger.info("Inserting %s bibstems into Master", len(recs))
        tasks.task_db_bibstems_to_master(recs)
    else:
        logger.info("No bibstems to insert")
    return


def load_rasterconfig(masterdict):
    '''
    No.
    '''
    try:
        recsr = utils.read_raster_xml(masterdict)
    except Exception as e:
        logger.warn('error in utils.read_raster_xml: %s' % e)
    else:
        logger.info("Inserting %s raster config records" % len(recsr))
        try:
            tasks.task_db_load_raster(recsr)
        except Exception as err:
            logger.warn("Could not load raster config: %s" % err)
    return


def load_abbreviations(masterdict):
    '''
    No.
    '''
    abbrevs = utils.read_abbreviations_list()
    recs = []
    for key, value in list(abbrevs.items()):
        try:
            if key in masterdict:
                logger.debug("Got masterid for bibstem %s", key)
                masterid = masterdict[key]
                for attrib in value:
                    recs.append((masterid, attrib))
            else:
                logger.debug("No masterid for bibstem %s", key)
        except Exception as err:
            logger.warn("Error with bibstem %s", key)
            logger.warn("Error: %s", err)
    if recs:
        logger.info("Inserting %s abbreviations into Abbreviations",
                     len(recs))
        try:
            tasks.task_db_load_abbrevs(recs)
        except Exception as err:
            logger.info("Could not load abbreviations: %s" % err)
    else:
        logger.info("There are no abbreviations to load.")
    return


def load_completeness(masterdict):
    '''
    No.
    '''
    pub_dict = utils.read_complete_csvs()
    recsi = []
    recsx = []
    recsp = []
    for key, value in list(pub_dict.items()):
        try:
            if key in masterdict:
                logger.debug("Got masterid for bibstem %s", key)
                mid = masterdict[key]
                c = value['startyear']
                d = value['startvol']
                e = value['endvol']
                f = value['complete']
                g = value['comporig']
                i = value['scanned']
                j = value['online']
                if value['issn'] != '':
                    recsi.append((mid, value['issn']))
                if value['xref'] != '':
                    recsx.append((mid, value['xref']))
                if value['publisher'] != '':
                    recsp.append((mid, value['publisher'], value['url']))

            else:
                logger.debug("No mid for bibstem %s", key)
        except Exception as err:
            logger.warn("Error with bibstem %s", key)
            logger.warn("Error: %s", err)
    if recsi:
        tasks.task_db_load_issn(recsi)
    if recsx:
        tasks.task_db_load_xref(recsx)
    if recsp:
        tasks.task_db_load_publisher(recsp)
    return


def calc_holdings(masterdict):
    '''
    No.
    '''
    for bibstem, masterid in list(masterdict.items()):
        try:
            tasks.task_db_load_holdings(bibstem, masterid)
        except Exception as err:
            logger.warn("Failed to load holdings for bibstem (%s): %s" % (bibstem, err))
    return

def load_refsources(masterdict):
    refsources = utils.create_refsource()
    missing_stems = []
    loaded_stems = []

    if refsources:

        for bibstem, refsource in refsources.items():
            try:
                bibstem = bibstem.rstrip('.')
                masterid = masterdict[bibstem]
            except Exception as err:
                logger.info("missing masterdict bibstem: (%s)" % bibstem)
                missing_stems.append(bibstem)
            else:
                tasks.task_db_load_refsource(masterid,refsource)
                loaded_stems.append(bibstem)

        logger.info("Loaded bibstems: %s\tMissing bibstems: %s" % (len(loaded_stems), len(missing_stems)))

    return

def checkin_table(tablename):
    try:
        result = tasks.task_checkin_table(tablename)
    except Exception as err:
        logger.warning("Unable to checkin table %s: %s" % (tablename, err))
        return
    else:
        logger.warning("Table %s successfully checked in from Sheets" % tablename)
        return result

def checkout_table(tablename):
    try:
        result = tasks.task_checkout_table(tablename)
    except Exception as err:
        logger.warning("Unable to checkout table %s: %s" % (tablename, err))
        return
    else:
        logger.warning("Table %s is available in Sheets" % tablename)
        return result

def main():
    '''
    No.
    '''

    args = get_arguments()

    # if args.load_master == True:
    # create the set of bibcode-journal name pairs and assign them UIDs;
    # these UIDs will be used as foreign keys in all other tables, so
    # if this fails, you're dead in the water.
    if args.load_master:
        load_master_table()

    # none of the other loaders will work unless you have data in
    # journals.master, so try to load it
    try:
        masterdict = tasks.task_db_get_bibstem_masterid()
        logger.info("masterdict has %s records", len(masterdict))
    except Exception as err:
        logger.warn("Error reading master table bibstem-masterid mapping: %s",
            err)
    else:
        # load bibstem-journal name abbreviation pairs
        if args.load_abbrevs:
            load_abbreviations(masterdict)

        if args.load_ca:
            # astro journal data
            load_completeness(masterdict)

        if args.calc_holdings:
            # holdings: be aware this is a big Solr query
            calc_holdings(masterdict)

        if args.load_raster:
            load_rasterconfig(masterdict)

        if args.load_refsources:
            load_refsources(masterdict)

    if args.checkin_table:
        result = checkin_table(args.checkin_table)
        
    if args.checkout_table:
        result = checkout_table(args.checkout_table)
        pprint(result)
        


if __name__ == '__main__':
    main()
