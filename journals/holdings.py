from builtins import str
from builtins import object
import os
import json
import requests
import config
import journals.utils as utils


class HoldingsQueryException(Exception):
    pass


class Holdings(object):

    def __init__(self):
        self.base_url = "http://localhost:9983/solr/collection1/"
        self.query = "select?fq=bibstem:%s" \
                     "&fl=year,volume,page,esources&cursorMark=%s" \
                     "&rows=5000&sort=bibcode%20asc&wt=json"
        self.results = {}

    def fetch(self, bibstem):
        cursormark_token = '*'
        last_token = ''
        output_list = list()

        # make sure query params are URL encoded (esp. bibstems w/ampersand)
        if isinstance(bibstem, str):
            bibstem = requests.utils.quote(bibstem)
            while cursormark_token != last_token:
                query = self.query % (bibstem, cursormark_token)
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
            # bibstem must be a string -- if it's not, just return
            logger.warn('Bad type for bibstem: %s' % type(bibstem))

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
                        except Exception as err:
                            eso = 0
                        outdict = {'page': pg, 'volume': vol, 'year': yr, 'esources': eso}
                        if bs in holdings_list:
                            holdings_list[bs].append(outdict)
                        else:
                            holdings_list[bs] = [outdict]
                    except Exception as err:
                        print('Holdings wut? %s' % err)
                        pass
        except Exception as err:
            logger.warn("Error in Holdings.process_output: %s" % err)
        return holdings_list

    def convert_esources_to_int(self, esource_array):
        try:
            bin_int_string = ''
            for p in config.ESOURCE_LIST:
                if p in esource_array:
                    bin_int_string = bin_int_string + '1'
                else:
                    bin_int_string = bin_int_string + '0'
            bin_int_string = '0b' + bin_int_string
            esources_out = int(bin_int_string, 2)
        except Exception as err:
            esources_out = 0
        return esources_out
