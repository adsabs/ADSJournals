from adsputils import get_date, UTCDateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, Numeric, String, TIMESTAMP,
                        ForeignKey, Boolean, Float, Text, UniqueConstraint)
from sqlalchemy.dialects.postgresql import ENUM

Base = declarative_base()


class JournalsMaster(Base):
    __tablename__ = 'master'

    pub_type = ENUM('Journal', 'Conf. Proc.', 'Monograph', 'Book',
                    'Software', 'Other', name='pub_type')
    ref_status = ENUM('yes', 'no', 'partial', 'na', name='ref_status')

    masterid = Column(Integer, primary_key=True, unique=True)
    bibstem = Column(String, unique=True, nullable=False)
    journal_name = Column(String, nullable=False)
    primary_language = Column(String)
    multilingual = Column(Boolean, default=False)
    defunct = Column(Boolean, default=False)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    pubtype = Column(pub_type, nullable=False)
    refereed = Column(ref_status, nullable=False)

    def __repr__(self):
        return "master.masterid='{self.masterid}'".format(self=self)


class JournalsMasterHistory(Base):
    __tablename__ = 'master_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    masterid = Column(Integer)
    bibstem = Column(String)
    journal_name = Column(String)
    primary_language = Column(String)
    multilingual = Column(Boolean)
    defunct = Column(Boolean)
    updated = Column(UTCDateTime)
    created = Column(UTCDateTime)
    superseded = Column(UTCDateTime, default=get_date)

    pubtype = Column(String)
    refereed = Column(String)

    def __repr__(self):
        return "master_hist.masterid='{self.masterid}'".format(self=self)


class JournalsNames(Base):
    __tablename__ = 'names'

    nameid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    name_english_translated = Column(String)
    title_language = Column(String)
    name_native_language = Column(String)
    name_normalized = Column(String)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "names.masterid='{self.masterid}'".format(self=self)


class JournalsNamesHistory(Base):
    __tablename__ = 'names_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    nameid = Column(Integer)
    masterid = Column(Integer)
    name_english_translated = Column(String)
    title_language = Column(String)
    name_native_language = Column(String)
    name_normalized = Column(String)
    updated = Column(UTCDateTime)
    created = Column(UTCDateTime)
    superseded = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "names_hist.masterid='{self.masterid}'".format(self=self)


class JournalsAbbreviations(Base):
    __tablename__ = 'abbrevs'

    abbrevid = Column(Integer, primary_key=True, autoincrement=True,
                      unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    abbreviation = Column(String)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "abbrevs.abbrevid='{self.abbrevid}'".format(self=self)


class JournalsAbbreviationsHistory(Base):
    __tablename__ = 'abbrevs_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    abbrevid = Column(Integer)
    masterid = Column(Integer)
    abbreviation = Column(String)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)
    superseded = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "abbrevs.abbrevid='{self.abbrevid}'".format(self=self)


class JournalsIdentifiers(Base):
    __tablename__ = 'idents'

    identid = Column(Integer, primary_key=True, autoincrement=True,
                     unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    id_type = Column(String)
    id_value = Column(String)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "idents.identid='{self.identid}'".format(self=self)


class JournalsIdentifiersHistory(Base):
    __tablename__ = 'idents_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    identid = Column(Integer)
    masterid = Column(Integer)
    id_type = Column(String)
    id_value = Column(String)
    updated = Column(UTCDateTime)
    created = Column(UTCDateTime)
    superseded = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "idents_histidentid='{self.identid}')".format(self=self)


class JournalsPublisher(Base):
    __tablename__ = 'publisher'

    publisherid = Column(Integer, primary_key=True, autoincrement=True,
                         unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    pubname = Column(String)
    pubaddress = Column(String)
    pubcontact = Column(Text)
    puburl = Column(String)
    year_start = Column(Integer)
    year_end = Column(Integer)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "publisher.publisherid='{self.publisherid}'".format(self=self)


class JournalsPublisherHistory(Base):
    __tablename__ = 'publisher_hist'

    histid = Column(Integer, primary_key=True, unique=True)
    publisherid = Column(Integer)
    masterid = Column(Integer)
    pubname = Column(String)
    pubaddress = Column(String)
    pubcontact = Column(Text)
    puburl = Column(String)
    year_start = Column(Integer)
    year_end = Column(Integer)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "publisher_hist.publisherid='{self.publisherid}'"\
               .format(self=self)


class JournalsStatus(Base):
    __tablename__ = 'status'

    statusid = Column(Integer, primary_key=True, autoincrement=True,
                       unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    year_start = Column(Integer)
    year_end = Column(Integer)
    complete = Column(String)
    predecessor_id = Column(Integer, ForeignKey('publisher.publisherid'))
    successor_id = Column(Integer, ForeignKey('publisher.publisherid'))
    orgid = Column(String)
    notes = Column(String)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "pubhist.pubhistid='{self.pubhistid}'".format(self=self)


class JournalsStatusHistory(Base):
    __tablename__ = 'status_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    statusid = Column(Integer)
    masterid = Column(Integer)
    year_start = Column(Integer)
    year_end = Column(Integer)
    predecessor_id = Column(Integer)
    successor_id = Column(Integer)
    orgid = Column(String)
    notes = Column(String)
    updated = Column(UTCDateTime)
    created = Column(UTCDateTime)
    superseded = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "pubhist_hist.pubhistid='{self.pubhistid}')".format(self=self)


class JournalsHoldings(Base):
    __tablename__ = 'holdings'

    holdingsid = Column(Integer, primary_key=True, autoincrement=True,
                        unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    volume = Column(String)
    volumes_list = Column(Text)
    complete = Column(Boolean, default=False)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "holdings.holdingsid='{self.holdingsid}'".format(self=self)


class JournalsRaster(Base):
    __tablename__ = 'raster'

    masterid = Column(Integer, ForeignKey('master.masterid'),
                       primary_key=True, nullable=False)
    rasterid = Column(Integer, primary_key=True, autoincrement=True,
                      unique=True, nullable=False)
    copyrt_file = Column(String, nullable=True)
    pubtype = Column(String, nullable=True)
    bibstem = Column(String, nullable=True)
    abbrev = Column(String, nullable=True)
    width = Column(String, nullable=True)
    height = Column(String, nullable=True)
    embargo = Column(String, nullable=True)
    options = Column(String, nullable=True)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr(self):
        return "raster.rasterid='{self.rasterid}'".format(self=self)


class JournalsRasterHistory(Base):
    __tablename__ = 'raster_hist'

    histid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    masterid = Column(Integer, nullable=False)
    rasterid = Column(Integer, nullable=False)
    copyrt_file = Column(String, nullable=True)
    pubtype = Column(String, nullable=True)
    bibstem = Column(String, nullable=True)
    abbrev = Column(String, nullable=True)
    width = Column(String, nullable=True)
    height = Column(String, nullable=True)
    embargo = Column(String, nullable=True)
    options = Column(String, nullable=True)
    updated = Column(UTCDateTime)
    created = Column(UTCDateTime)
    superseded = Column(UTCDateTime, default=get_date)

    def __repr(self):
        return "raster.rasterid='{self.rasterid}'".format(self=self)


class JournalsRasterVolume(Base):
    __tablename__ = 'rastervolume'
    rasterid = Column(Integer, ForeignKey('raster.rasterid'),
                      primary_key=True, nullable=False)
    rvolid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    volume_number = Column(String, nullable=False)
    volume_properties = Column(Text)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr(self):
        return "rastervolume.rvolid='{self.rasterid}'".format(self=self)


class JournalsRefSource(Base):
    __tablename__ = 'refsource'

    refsourceid = Column(Integer, primary_key=True, autoincrement=True,
                         unique=True, nullable=False)
    masterid = Column(Integer, ForeignKey('master.masterid'),
                      primary_key=True, nullable=False)
    refsource_list = Column(Text)
    updated = Column(UTCDateTime, onupdate=get_date)
    created = Column(UTCDateTime, default=get_date)

    def __repr__(self):
        return "refsource.refsourceid='{self.refsourceid}'".format(self=self)


class JournalsEditControl(Base):
    __tablename__ = 'editcontrol'

    editid = Column(Integer, primary_key=True, autoincrement=True,
                    unique=True, nullable=False)
    tablename = Column(String, nullable=False)
    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime, onupdate=get_date)
    editstatus = Column(String, nullable=False)
    editfileid = Column(String, nullable=False)

    def __repr__(self):
        return "editcontrol.editid='{self.editid}'".format(self=self)
