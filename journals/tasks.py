from __future__ import absolute_import, unicode_literals
from builtins import str
import json
import os
from kombu import Queue
from journals import app as app_module
from journals.models import *
#import journals.utils as utils
from journals.exceptions import *
from journals.sheetmanager import SpreadsheetManager
import journals.refsource as refsource

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))

app = app_module.ADSJournalsCelery('journals', proj_home=proj_home, config=globals().get('config', {}), local_config=globals().get('local_config', {}))
logger = app.logger

app.conf.CELERY_QUEUES = (
    Queue('load-datafiles', app.exchange, routing_key='load-datafiles')
)

@app.task(queue='load-datafiles')
def task_db_bibstems_to_master(recs):
    pubtypes = {'C': 'Conf. Proc.', 'J': 'Journal', 'R': 'Journal'}
    reftypes = {'C': 'na', 'J': 'no', 'R': 'yes'}
    with app.session_scope() as session:
        extant_bibstems = [x[0] for x in session.query(JournalsMaster.bibstem)]
        if recs:
            for r in recs:
                if r[0] not in extant_bibstems:
                    if r[1] in pubtypes:
                        ptype = pubtypes[r[1]]
                    else:
                        ptype = 'Other'
                    if r[1] in reftypes:
                        rtype = reftypes[r[1]]
                    else:
                        rtype = 'na'
                    session.add(JournalsMaster(bibstem=r[0], journal_name=r[2],
                                               pubtype=ptype, refereed=rtype,
                                               defunct=False))
                else:
                    logger.debug("task_db_bibstems_to_master: Bibstem %s already in master", r[0])
            try:
                session.commit()
            except Exception as err:
                logger.error("Problem with database commit: %s", err)
                raise DBCommitException("Could not commit to db, stopping now.")


@app.task(queue='load-datafiles')
def task_db_load_abbrevs(recs):
    with app.session_scope() as session:
        if recs:
            for r in recs:
                try:
                    session.add(JournalsAbbreviations(masterid=r[0],
                                                      abbreviation=r[1]))
                    session.commit()
                except Exception as err:
                    logger.debug("Problem with abbreviation: %s,%s" %
                                (r[0], r[1]))
        else:
            logger.info("There were no abbreviations to load!")


@app.task(queue='load-datafiles')
def task_db_load_issn(recs):
    with app.session_scope() as session:
        if recs:
            for r in recs:
                try:
                    session.add(JournalsIdentifiers(masterid=r[0],
                                                    id_type='ISSN',
                                                    id_value=r[1]))
                    session.commit()
                except Exception as err:
                    logger.debug("Duplicate ISSN ident skipped: %s,%s" %
                                (r[0], r[1]))
                    session.rollback()
                    session.flush()
        else:
            logger.info("There were no ISSNs to load!")


@app.task(queue='load-datafiles')
def task_db_load_xref(recs):
    with app.session_scope() as session:
        if recs:
            for r in recs:
                try:
                    session.add(JournalsIdentifiers(masterid=r[0],
                                                    id_type='CROSSREF',
                                                    id_value=r[1]))
                    session.commit()
                except Exception as err:
                    logger.debug("Duplicate XREF ident skipped: %s,%s" %
                                (r[0], r[1]))
                    session.rollback()
                    session.flush()
        else:
            logger.info("There were no XREF IDs to load!")


@app.task(queue='load-datafiles')
def task_db_load_publisher(recs):
    with app.session_scope() as session:
        if recs:
            for r in recs:
                try:
                    session.add(JournalsPublisher(masterid=r[0], pubname=r[1],
                                                  puburl=r[2]))
                    session.commit()
                except Exception as err:
                    logger.debug("Duplicate XREF ident skipped: %s,%s" %
                                (r[0], r[1]))
                    session.rollback()
                    session.flush()
        else:
            logger.info("There were no publishers to load!")


@app.task(queue='load-datafiles')
def task_db_load_raster(recs):
    with app.session_scope() as session:
        if recs:
            for r in recs:
                if 'label' in r[1]:
                    copyrt_file = r[1]['label']
                else:
                    copyrt_file = ''
                if 'pubtype' in r[1]:
                    pubtype = r[1]['pubtype']
                else:
                    pubtype = ''
                if 'bibstem' in r[1]:
                    bibstem = r[1]['bibstem']
                else:
                    bibstem = ''
                if 'abbrev' in r[1]:
                    abbrev = r[1]['abbrev']
                else:
                    abbrev = ''
                if 'width' in r[1]:
                    width = r[1]['width']
                else:
                    width = ''
                if 'height' in r[1]:
                    height = r[1]['height']
                else:
                    height = ''
                if 'embargo' in r[1]:
                    embargo = r[1]['embargo']
                else:
                    embargo = ''
                if 'options' in r[1]:
                    options = 'oops'
                else:
                    options = ''

                try:
                    session.add(JournalsRaster(masterid=r[0],
                                               copyrt_file=copyrt_file,
                                               pubtype=pubtype,
                                               bibstem=bibstem,
                                               abbrev=abbrev,
                                               width=width,
                                               height=height,
                                               embargo=embargo,
                                               options=options))
                    session.commit()
                except Exception as err:
                    logger.debug("Cant load raster data for (%s, %s): %s" %
                                (r[0], bibstem, err))
                    session.rollback()
                    session.flush()
        else:
            logger.info("There were no raster configs to load!")



@app.task(queue='load-datafiles')
def task_db_get_bibstem_masterid():
    dictionary = {}
    with app.session_scope() as session:
        try:
            for record in session.query(JournalsMaster.masterid,
                                        JournalsMaster.bibstem):
                dictionary[record.bibstem] = record.masterid
        except Exception as err:
            logger.error("Error: failed to read bibstem-masterid dict from table master")
            raise DBReadException("Could not read from database!")
    return dictionary


@app.task(queue='load-datafiles')
def task_db_load_refsource(masterid, refsource):
    with app.session_scope() as session:
        if masterid and refsource:
            try:
                refsource = json.dumps(refsource.toJSON())
                session.add(JournalsRefSource(masterid=masterid,
                                              refsource_list=refsource))
                session.commit()
            except Exception as err:
                logger.debug("Error adding refsources for %s: %s" %
                               (masterid, err))
                session.rollback()
                session.commit()
        else:
            logger.error("No refsource data to load!")
    return


def task_checkout_table(tablename):
    if tablename.lower() not in app.conf.EDITABLE_TABLES:
        raise InvalidTableException("Tablename %s is not valid" % tablename)
    try:
        with app.session_scope() as session:
            table_record = session.query(JournalsEditControl).filter(JournalsEditControl.tablename.ilike(tablename), JournalsEditControl.editstatus=='active').first()
            if table_record:
                sheet = SpreadsheetManager(table=table_record.tablename, sheetid=table_record.editfileid)
                result = sheet.get_sheet_prop()
                logger.debug("Table %s is already checked out: Time: %s, ID: %s" % (tablename, table_record.created, table_record.editfileid))
            else:
                sheet = SpreadsheetManager(table=tablename)
                result = sheet.get_sheet_prop()
                session.add(JournalsEditControl(tablename=tablename, editstatus='active', editfileid=sheet.sheetid))
                session.commit()
    except Exception as err:
        raise TableCheckoutException("Error checking out table %s: %s" % (tablename, err))
    else:
        return result
