'''
No.
'''
from __future__ import print_function
import argparse
from adsputils import setup_logging
from journals import tasks
from journals import utils



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
                        action='store',
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
        print("Inserting %s bibstems into Master", len(recs))
        tasks.task_db_bibstems_to_master(recs)
    else:
        print("No bibstems to insert")
    return


def load_rasterconfig(masterdict):
    '''
    No.
    '''
    try:
        recsr = utils.read_raster_xml(masterdict)
    except Exception as e:
        print('error in utils.read_raster_xml:',e)
    else:
        # LOGGER.debug("Inserting %s raster config records", len(recsr))
        print('lol %s recs' % len(recsr))
        # try:
        tasks.task_db_load_raster(recsr)
        # except Exception as err:
        #     LOGGER.error("Could not load raster config: %s", err)
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
                print("Got masterid for bibstem %s", key)
                masterid = masterdict[key]
                for attrib in value:
                    recs.append((masterid, attrib))
            else:
                print("No masterid for bibstem %s", key)
        except Exception as err:
            print("Error with bibstem %s", key)
            print("Error: %s", err)
    if recs:
        print("Inserting %s abbreviations into Abbreviations",
                     len(recs))
        try:
            tasks.task_db_load_abbrevs(recs)
        except Exception as err:
            print("Could not load abbreviations: %s", err)
    else:
        print("There are no abbreviations to load.")
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
                print("Got masterid for bibstem %s", key)
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
                print("No mid for bibstem %s", key)
        except Exception as err:
            print("Error with bibstem %s", key)
            print("Error: %s", err)
    if recsi:
        tasks.task_db_load_issn(recsi)
    if recsx:
        tasks.task_db_load_xref(recsx)
    if recsp:
        tasks.task_db_load_publisher(recsp)
    return


def calc_holdings(masterdict, json_file):
    '''
    No.
    '''
    try:
        tasks.task_db_load_holdings(masterdict, json_file)
    except Exception as err:
        print("Failed to load holdings: %s", err)
    return


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
        print("masterdict has %s records", len(masterdict))
    except Exception as err:
        print("Error reading master table bibstem-masterid mapping: %s",
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
            calc_holdings(masterdict, args.calc_holdings)

        if args.load_raster:
            load_rasterconfig(masterdict)


if __name__ == '__main__':
    main()
