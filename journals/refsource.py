'''
RefSource objects used to parse and keep track of the classic list of ref
sources per bibcode.  Used to create refsource records for ADSJournals.
'''


class RefCount(object):

    def __init__(self, source=None):
        self.source = source
        self.count = 1

    def update_count(self):
        self.count += 1

    def toJSON(self):
        return {self.source: self.count}


class RefVolume(object):

    def __init__(self, volume=None, year=None, source=None):
        self.volume = volume
        self.year = year
        self.refsources = [RefCount(source)]

    def update_volume(self, source):
        found = False
        for r in self.refsources:
            if r.source == source:
                r.update_count()
                found = True
        if not found:
            rc = RefCount(source)
            self.refsources.append(rc)

    def toJSON(self):
        rs = dict()
        for r in self.refsources:
            rs.update(r.toJSON())
        return {'volume': self.volume, 'year': self.year, 'refsources': rs}


class RefSource(object):

    def __init__(self, bibstem=None, volume=None, year=None, source=None):
        self.bibstem = bibstem
        self.refvolumes = [RefVolume(volume, year, source)]

    def increment_source(self, volume, year, source):
        if self.refvolumes:
            found = False
            for v in self.refvolumes:
                if v.volume == volume:
                    v.update_volume(source)
                    found = True
            if not found:
                self.refvolumes.append(RefVolume(volume, year, source))

    def toJSON(self):
        return {'bibstem': self.bibstem, 'volumes': [x.toJSON() for x in self.refvolumes]}
