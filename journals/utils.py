from __future__ import print_function
import chardet
import os
import requests
import string
import urllib3
from adsputils import load_config
from bs4 import BeautifulSoup as bs
from glob import glob
from journals.exceptions import *
from journals.refsource import RefCount, RefVolume, RefSource

proj_home = os.path.realpath(os.path.dirname(__file__)+ '/../')
config = load_config(proj_home=proj_home)


def parse_bibcodes(bibcode):
    parsed_bib = {}
    if not isinstance(bibcode, str):
        pass
    else:
        try:
            year = bibcode[0:4]
            stem = bibcode[4:9]
            volm = bibcode[9:13]
            qual = bibcode[13]
            page = bibcode[14:18]
            auth = bibcode[18]
            if volm in config.get('BIBSTEM_VOLUMES'):
                stem = year + stem + volm
                volm = None
            parsed_bib = {"bibcode": bibcode, "year": year, "bibstem": stem,
                          "volume": volm, "qualifier": qual, "page": page,
                          "initial": auth}
        except Exception as err:
            # logger.warn("Nonstandard bibcode: {0}".format(bibcode))
            pass
    return parsed_bib


def return_query(url, method='get', data='', headers='', verify=False):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        if method.lower() == 'get':
            rQuery = requests.get(url)
        elif method.lower() == 'post':
            rQuery = requests.post(url, data=data, headers=headers, verify=False)
        if rQuery.status_code != 200:
            raise RequestsException('Return code error: %s' % rQuery.status_code)
        else:
            return rQuery.json()
    except Exception as err:
        raise RequestsException('Error in return_query: %s' % err)


def get_encoding(filename):
    try:
        encoding = chardet.detect(open(filename, 'rb').read())['encoding']
        return encoding
    except Exception as err:
        raise ReadEncodingException(err)


def read_bibstems_list():
    data = {}
    infile = config.get('BIBSTEMS_FILE')
    try:
        with open(infile, 'r', encoding=get_encoding(infile)) as f:
            nbibstem = f.readline()
            for l in f.readlines():
                (bibstem, bstype, bspubname) = l.rstrip().split('\t')
                bibstem = bibstem.rstrip('.').lstrip('.')
                if bibstem in data:
                    # logger.warn("Duplicate in bibstems list: {0}"
                    #             .format(bibstem))
                    pass
                data[bibstem] = {'type': bstype, 'pubname': bspubname}
    except Exception as err:
        raise ReadBibstemException(err)
    return data


def read_abbreviations_list():
    datadict = {}
    infile = config.get('JOURNAL_ABBREV_FILE')
    try:
        with open(infile, 'r', encoding=get_encoding(infile)) as f:
            for l in f.readlines():
                (bibstem_abbrev, abbrev) = l.rstrip().split('\t')
                bibstem_abbrev = bibstem_abbrev.rstrip('.').lstrip('.')
                abbrev = abbrev.lstrip().rstrip()
                if bibstem_abbrev in datadict:
                    if abbrev not in datadict[bibstem_abbrev]:
                        datadict[bibstem_abbrev].append(abbrev)
                    else:
                        # logger.warn("Duplicate abbreviation: {0}".format(abbrev))
                        pass
                else:
                    datadict[bibstem_abbrev] = [abbrev]
    except Exception as err:
        # logger.warn("Problem reading abbreviations file: %s" % err)
        pass
    return datadict


def read_complete_csvs():
    data = {}
    for coll in config.get('COLLECTIONS'):
        infile = config.get('JDB_DATA_DIR') + 'completion.' + coll + '.csv'
        try:
            with open(infile, 'r', encoding=get_encoding(infile)) as f:
                f.readline()
                f.readline()
                for l in f.readlines():
                    try:
                        (journal, bibstem, issn, xref, startyear, startvol,
                         endvol, complete, complete_origin, publisher, scanned,
                         online, url, notes) = l.strip().split('|')
                    except Exception as err:
                        # logger.warn("Unparseable csv: {0}".format(l.strip()))
                        pass
                    else:
                        if bibstem in data:
                            # logger.info("skipping duplicate bibstem: %s" %
                            #             bibstem)
                            pass
                        else:
                            for a in [complete, scanned, online]:
                                if (a != '' and (a[0] == 'Y' or a[0] == 'y')):
                                    a = True
                                else:
                                    a = False
                            data[bibstem] = {u'issn': issn,
                                             u'xref': xref,
                                             u'startyear': startyear,
                                             u'startvol': startvol,
                                             u'endvol': endvol,
                                             u'complete': complete,
                                             u'comporig': complete_origin,
                                             u'publisher': publisher,
                                             u'scanned': scanned,
                                             u'online': online,
                                             u'url': url,
                                             u'notes': notes}
        except Exception as err:
            # logger.warn('Cant load collection {0}:'.format(coll))
            pass
    return data


def parse_raster_volume_data(pubsoup):
    volume_specific = pub.find_all('volumes')
    volumes = []
    if volume_specific:
        for v in volume_specific:
            vol_param = dict()
            vol_range = dict()
            for t in v.children:
                if t.name:
                    try:
                        vol_param[t.name] = t.contents[0].strip()
                        if not vol_param[t.name]:
                            del vol_param[t.name]
                    except Exception as err:
                        pass
                        # print(('volumening problem:', err))
            if vol_param:
                vol_range['range'] = v['range']
                vol_range['param'] = vol_param
                volumes.append(vol_range)

    return volumes


def parse_raster_pub_data(pubsoup):
    global_param = dict()
    for t in pubsoup.children:
        if t.name:
            try:
                global_param[t.name] = t.contents[0].strip()
                if not global_param[t.name]:
                    del global_param[t.name]
            except Exception as err:
                if t.name == 'bibstem':
                    global_param['bibstem'] = filestem

    return global_param


def read_raster_xml(masterdict):
    raster_dir = config.get('RASTER_CONFIG_DIR')
    xml_files = glob(raster_dir+"*.xml")
    recs = []
    for raster_file in xml_files:
        bibstem = raster_file.replace(raster_dir,'').replace('.xml','')
        if bibstem in masterdict.keys():
            masterid = masterdict[bibstem]
            try:
                with open(raster_file, 'r', encoding=get_encoding(raster_file)) as fx:
                    filestem = raster_file.split('/')[-1].rstrip('.xml')
                    data = fx.read().rstrip()
                    soup = bs(data, 'html5lib')
                    pub = soup.find('publication')
    
                    # get volume specific parameters
                    volumes = list()
                    try:
                        volumes = parse_raster_volume_data(pub)
                    except Exception as err:
                        pass
    
                    # now make a dict of the general params
                    try:
                        global_param = parse_raster_pub_data(pub)
                    except Exception as err:
                        pass

                    # add volume-specific params to dict as an array
                    try:
                        if volumes:
                            global_param['rastervol'] = volumes
                    except Exception as err:
                        pass

                    recs.append((masterid,global_param))

            except Exception as err:
                pass

    return recs

def parse_refsource_str(srcstr):
    try:
        src = srcstr.split('/')
        if src[0] == 'AUTHOR' or src[0] == 'OTHER':
            s = src[0]
        elif '.isi.pairs' in src[-1]:
            s = 'ISI'
        elif '.xref.' in src[-1]:
            s = 'CROSSREF'
        elif '.ocr.' in src[-1]:
            s = 'OCR'
        else:
            s = 'PUBLISHER'
        return s
    except Exception as err:
        print('Error in parse_refsource_str: %s' % err)
        return

def update_refsources(refsources, bibstem, year, volume, source):
    try:
        rs = refsources[bibstem]
    except Exception as noop:
        try:
            rs = RefSource(bibstem=bibstem, volume=volume, year=year, source=source)
        except Exception as err:
            print('create new failed: %s' % err)
        else:
            refsources[bibstem] = rs
    else:
        try:
            rs.increment_source(volume, year, source)
            refsources[bibstem] = rs
        except Exception as err:
            print('update existing failed: %s' % err)
    return refsources

def create_refsource():
    '''
    Takes the input file from classic and outputs a json object
    containing source counts for each bibstem/volume pair.
    The JSON format is:
    {'bibstem': bibstem,
     'volumes': [
                 {
                  'volume': volume,
                  'year': year,
                  'refsources': {
                                 'source': source,
                                 'count': count
                                }
                 }
                ]
    }

    Depending on your needs, you can write the entire JSON object
    to database, or make each bibstem a row, or make each bibstem /
    volume pair a row.
    '''
    refsources = {}
    infile = config.get('BIB_TO_REFS_FILE')
    with open(infile, 'r') as fin:
        for l in fin.readlines():
            try:
                (bibcode, srcfile) = l.strip().split('\t')
            except Exception as err:
                pass
                # print('Malformed line in source file: "%s"' % l.strip())
            else:
                try:
                    parsed_bib = parse_bibcodes(bibcode)
                    year = parsed_bib['year']
                    bibstem = parsed_bib['bibstem']
                    volume = parsed_bib['volume']
                    source = parse_refsource_str(srcfile)
                    refsources = update_refsources(refsources, bibstem, year, volume, source)
                except Exception as err:
                    pass
                    # print('failed update_refsources: %s' % err)
    return refsources
