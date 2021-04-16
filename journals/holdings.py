from builtins import str
from builtins import object
import os
import json
import requests
import journals.utils as utils
from journals import app as app_module
from adsputils import load_config

proj_home = os.path.realpath(os.path.dirname(__file__)) + '/../'
config = load_config(proj_home=proj_home)
app = app_module.ADSJournalsCelery('journals', proj_home=proj_home, config=globals().get('config', {}), local_config=globals().get('local_config', {}))
logger = app.logger

INDEXER_HOST = config.get('_INDEXER_HOST','localhost')
INDEXER_PORT = config.get('_INDEXER_PORT','9983')


class HoldingsQueryException(Exception):
    pass


class BadBibstemException(Exception):
    pass


class Holdings(object):

    def __init__(self):
        self.base_url = 'http://%s:%s/solr/collection1/' % (INDEXER_HOST,INDEXER_PORT)
        self.query = ['select?fq=bibstem:',
                     '&fl=year,volume,page,esources&cursorMark=',
                     '&q=*%3A*&rows=5000&sort=bibcode%20asc%2Cid%20asc&wt=json']
        self.results = {}

    def fetch(self, bibstem):
        cursormark_token = '*'
        last_token = ''
        output_list = list()

        # make sure query params are URL encoded (esp. bibstems w/ampersand)
        if isinstance(bibstem, str):
            bibstem = requests.utils.quote(bibstem)
            while cursormark_token != last_token:
                q_arr = self.query
                query = q_arr[0] + bibstem + q_arr[1] + cursormark_token + q_arr[2]
                q_url = self.base_url + query
                resp = utils.return_query(q_url, method='get')
                last_token = cursormark_token
                try:
                    cursormark_token = resp['nextCursorMark']
                except Exception as err:
                    raise HoldingsQueryException('Bad result from solr: %s' % err)
                else:
                    output_list.extend(resp['response']['docs'])
            self.results = {'bibstem': bibstem, 'docs': output_list}
        else:
            # bibstem must be a string
            raise BadBibstemException('Bad type for bibstem: %s' % type(bibstem))

    def process_output(self):
        holdings_list = dict()
        try:
            if self.results:
                bs = self.results['bibstem']
                for paper in self.results['docs']:
                    try:
                        vol = paper['volume']
                        pg = paper['page'][0]
                        yr = int(paper['year'])
                        try:
                            eso = self.convert_esources_to_int(paper['esources'])
                        except Exception as pass_err:
                            eso = 0
                        outdict = {'page': pg, 'esources': eso}
                        if vol in holdings_list:
                            holdings_list[vol].append(outdict)
                        else:
                            holdings_list[vol] = [outdict]
                    except Exception as pass_err:
                        logger.debug("Invalid record in holdings search: %s, %s" % (bs,paper))
        except Exception as err:
            logger.warning("Error in Holdings.process_output: %s" % err)
        holdings_all = list()
        for k, v in holdings_list.items():
            volume = k
            bibstem = bs
            vol_list = v
            outrec = {'bibstem': bibstem, 'volume': volume, 'holdings': vol_list}
            holdings_all.append(outrec)

        return holdings_all

    def convert_esources_to_int(self, esource_array):
        try:
            bin_int_string = ''
            ESOURCE_LIST = config.get('ESOURCE_LIST', [])
            for p in ESOURCE_LIST:
                if p in esource_array:
                    bin_int_string = bin_int_string + '1'
                else:
                    bin_int_string = bin_int_string + '0'
            bin_int_string = '0b' + bin_int_string
            esources_out = int(bin_int_string, 2)
        except Exception as pass_err:
            esources_out = 0
        return esources_out
