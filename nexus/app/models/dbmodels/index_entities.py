from app.constants import INDEX_TABLE_ENTITIES
from app.sqldb import IndexSQLDB


class Entity:

    def __init__(self, uuid="", name="", labels="", aliases="", keywords="", lastmodified=None):
        self.uuid = uuid
        self.name = name
        self.labels = labels
        self.aliases = aliases
        self.keywords = keywords
        self.tablename = INDEX_TABLE_ENTITIES
        self.dbwrap = IndexSQLDB()
        self.lastmodified = lastmodified

    @classmethod
    def del_all_entities(cls):
        dbwrap = IndexSQLDB()
        dbwrap.connect()
        cursor = dbwrap.cursor()
        query = 'TRUNCATE TABLE entities'
        cursor.execute(query)
        dbwrap.commitAndClose()

    def insertEntity(self):
        self.dbwrap.connect()
        print (self.dbwrap.cursor)
        try:
            cursor = self.dbwrap.cursor()
        except:
            print "In insertEntity"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()
        query = "INSERT INTO entities(uuid, name, labels, aliases, keywords) VALUES\
                ('%s','%s','%s','%s','%s')"\
                % (self.uuid, self.name, self.labels, self.aliases, self.keywords)
        print query
        numrows = cursor.execute(query)
        self.dbwrap.commitAndClose()
        return numrows

    def updateEntity(self):
        self.dbwrap.connect()
        print (self.dbwrap.cursor)
        try:
            cursor = self.dbwrap.cursor()
        except:
            print "In updateEntity"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        query = ("UPDATE entities SET name='%s', labels='%s', aliases='%s', keywords='%s'\
                 WHERE uuid ='" + str(self.uuid) + "'")\
                % (self.name, self.labels, self.aliases, self.keywords)
        print query
        numrows = cursor.execute(query)
        self.dbwrap.commitAndClose()
        return numrows

    def getEntity(self, uuid):
        self.dbwrap.connect()
        cursor = self.dbwrap.cursor()
        query = ("SELECT uuid, name, labels, aliases, keywords FROM entities WHERE uuid = '{}'".format(uuid))
        print query
        cursor.execute(query)
        results = cursor.fetchall()
        for r in results:
            self.uuid = r[0]
            self.name = r[1]
            self.labels = r[2]
            self.aliases = r[3]
            self.keywords = r[4]

        self.dbwrap.commitAndClose()
        return
