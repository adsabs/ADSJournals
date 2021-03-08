from __future__ import print_function
from bs4 import BeautifulSoup as bs
import chardet
import config
from namedentities import named_entities, unicode_entities
import os
from glob import glob


class ReadBibstemException(Exception):
    pass


class ReadCanonicalException(Exception):
    pass


class ReadEncodingException(Exception):
    pass


def get_encoding(filename):
    try:
        encoding = chardet.detect(open(filename, 'rb').read())['encoding']
        return encoding
    except Exception as err:
        raise ReadEncodingException(err)


def read_bibstems_list():
    data = {}
    infile = config.BIBSTEMS_FILE
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
    infile = config.JOURNAL_ABBREV_FILE
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


def read_canonical_list():
    bibc = []
    infile = config.CANONICAL_BIB_FILE
    try:
        with open(infile, 'r', encoding=get_encoding(infile)) as f:
            for l in f.readlines():
                (bibcode, a, b, c) = l.rstrip().split('\t')
                bibc.append(bibcode)
    except Exception as err:
        raise ReadCanonicalException(err)
    return bibc


def read_complete_csvs():
    data = {}
    for coll in config.COLLECTIONS:
        infile = config.JDB_DATA_DIR + 'completion.' + coll + '.csv'
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


def read_raster_xml(masterdict):
    raster_dir = config.RASTER_CONFIG_DIR
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
                                        print(('volumening problem:', err))
                            if vol_param:
                                vol_range['range'] = v['range']
                                vol_range['param'] = vol_param
                                volumes.append(vol_range)
    
                    # now make a dict of the general params
                    global_param = dict()
                    for t in pub.children:
                        if t.name:
                            try:
                                global_param[t.name] = t.contents[0].strip()
                                if not global_param[t.name]:
                                    del global_param[t.name]
                            except Exception as err:
                                if t.name == 'bibstem':
                                    global_param['bibstem'] = filestem
                                else:
                                    print("Error in %s: %s\t%s"%(filestem,t.name,err))
                    try:
                        if volumes:
                            # add volume-specific params to dict as an array
                            global_param['rastervol'] = volumes
                    except Exception as err:
                        print(('ERROR:', err))
                    recs.append((masterid,global_param))
            except Exception as err:
                pass
    return recs


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
            parsed_bib = {"bibcode": bibcode, "year": year, "bibstem": stem,
                          "volume": volm, "qualifier": qual, "page": page,
                          "initial": auth}
        except Exception as err:
            # logger.warn("Nonstandard bibcode: {0}".format(bibcode))
            pass
    return parsed_bib
