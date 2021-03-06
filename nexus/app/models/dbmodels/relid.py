from app.constants import META_TABLE_RELID, META_TABLE_RELIDLAB, META_TABLE_RELIDPROPS
from app.sqldb import MetaSQLDB


class RelIdTable:

    def __init__(self, relid, reltype='', startuuid='', enduuid=''):
        self.dbwrap = MetaSQLDB()
        self.tablename = META_TABLE_RELID
        self.relid = relid
        self.reltype = reltype
        self.startuuid = startuuid
        self.enduuid = enduuid
        return

    def create(self):
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelIdTable object] In create"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        query = "INSERT INTO " + self.tablename + " (relid, reltype, startuuid,\
                enduuid) VALUES(%d, '%s', %d, %d)" % (self.relid,
                self.reltype, self.startuuid, self.enduuid)

        print query
        numrows = 0
        try:
            numrows = cursor.execute(query)
        except Exception as e:
            import traceback
            traceback.print_exc()
            traceback.print_stack()
            print "[relid.RelIdTable.create: query execution error]"
            self.dbwrap.commitAndClose()

        else:
            self.dbwrap.commitAndClose()
        return numrows

    def delete(self):
        ##delete self object into db
        ##TODO - later
        pass

    ##Update reltable.,   Not present
    ##For the RelLabels and RelProps class
    def update(self, column='all'):
        ##update self object into db

        attr_list = ['all', 'reltype', 'startuuid', 'enduuid']
        assert(column in attr_list)

        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelIdTable] In update"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        base_query = "UPDATE " + self.tablename + " SET "
        rest_query = " WHERE relid= "+str(self.relid)
        if column == "all":
            body_query = "reltype='%s', startuuid=%d, enduuid = %d" % \
                    (self.reltype, self.startuuid, self.enduuid)

        else:
            t = type(column)
            val = getattr(self, column)
            if t == int:
                typestr = "%d"
            else: typestr = "'%s'"
            body_query = (column+"="+typestr) % (val)

        query = base_query + body_query + rest_query
        print "UPDATE query"
        print query

        numrows = 0
        try:
            numrows = cursor.execute(query)
        except Exception as e:
            print e.message
            self.dbwrap.commitAndClose()
            exit(3)
        else:
            self.dbwrap.commitAndClose()

        return numrows

    def getSelfFromDB(self):

        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[User object] In update"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        query = "SELECT relid, reltype, startuuid, enduuid \
                 FROM " + self.tablename + "  where relid=" + str(self.relid)

        cursor.execute(query)
        rows = cursor.fetchall()
        assert(len(rows) == 1)
        for r in rows:
            self.relid = r[0]
            self.reltype = r[1]
            self.startuuid = r[2]
            self.enduuid = r[3]

        self.dbwrap.commitAndClose()
        return self

    @classmethod
    def getRel(cls, relid):
        rel = RelIdTable(relid)
        return rel.getSelfFromDB()

    def __str__(self):
        print '[ Relation: relid: '+str(self.relid)+' startuuid: '\
                + str(self.startuuid)+' enduuid: '+str(self.enduuid)+' ]'
        return


class RelLabels:

    def __init__(self, changeid='', relid='', label='', changetype=''):
        self.changeid = changeid
        self.relid = relid
        self.label = label
        self.changetype = changetype
        self.dbwrap = MetaSQLDB()
        self.tablename = META_TABLE_RELIDLAB

        return

    def create(self):
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[Taskusers object] In create"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        query = "INSERT INTO " + self.tablename + " (changeid, relid,\
                label, changetype) VALUES(%d, %d, '%s', %d)" %\
                (int(self.changeid), int(self.relid), self.label, int(self.changetype))

        print query
        numrows = 0
        try:
            numrows = cursor.execute(query)
        except Exception as e:
            import traceback
            traceback.print_exc()
            traceback.print_stack()
            print "[relid.RelLabels.create: query execution error]"
            self.dbwrap.commitAndClose()
        else:
            self.dbwrap.commitAndClose()
        return numrows

    def getListFromDB(self, by):

        assert(by in ['relid', 'changeid'])
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelLabels object] In SELECT"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        if by == 'changeid':
            bystr = " where changeid=" + str(self.changeid)
        else:
            bystr = " where relid=" + str(self.relid)

        rest_str = ' ORDER by changeid DESC'
        query = "SELECT changeid, relid, label, changetype FROM "\
                + self.tablename + bystr + rest_str

        cursor.execute(query)
        rows = cursor.fetchall()
        assert(len(rows) >= 1)
        print len(rows)
        results_list = []
        rlabel = RelLabels()
        for r in rows:
            rlabel.changeid = r[0]
            rlabel.relid = r[1]
            rlabel.label = r[2]
            rlabel.changetype = r[3]
            results_list.append(rlabel.__dict__.copy())

        self.dbwrap.commitAndClose()
        for r in results_list: 
            del r['dbwrap']
            del r['tablename']
        return results_list
    
    def getListFromDBMultiple(self, by_list=['']):

        #TODO - verify the by_list
        for by in by_list: assert(by in self.__dict__.keys())

        #TODO - connect to db
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelLabels object] In SELECT"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        #TODO - create a list of all strings 
        bystr_list = []
        for by in by_list:
            paramstr = ' ' + str(by) + '='
            if (type(self.__dict__[by]) == int): fieldstr = "%d"
            else: fieldstr = "'%s'"
            fields = fieldstr % self.__dict__[by]
            bystr_list.append(paramstr + fields)

        #TODO - join all sources by ' AND '
        bystr = ' AND '.join(bystr_list)
        #TODO - append to select query and run it as usual
        rest_str = ' ORDER by  changeid DESC'
        query = "SELECT changeid, relid, label, changetype FROM "\
                + self.tablename + " WHERE " + bystr + rest_str
        print query

        cursor.execute(query)
        rows = cursor.fetchall()
        assert(len(rows) >= 1)
        print len(rows)
        results_list = []
        rlabel = RelLabels()
        for r in rows:
            rlabel.changeid = r[0]
            rlabel.relid = r[1]
            rlabel.label = r[2]
            rlabel.changetype = r[3]
            results_list.append(rlabel.__dict__.copy())

        self.dbwrap.commitAndClose()

        #TODO - return the list
        return results_list


    def __str__(self):
        s = '[ RelIDLabels -- relid: %s   label: %s  changeid: %s  changetype: %s]' %(str(self.relid), self.label, str(self.changeid), str(self.changetype))
        return s


    @classmethod
    def getRelLabelsRelId(cls, relid):
        r = RelLabels(relid=relid)
        return r.getListFromDB(by='relid')

    @classmethod
    def getRelLabelsChangeId(cls, changeid):
        r = RelLabels(changeid=changeid)
        return r.getListFromDB(by='changeid')

    @classmethod
    def getRelLabelsBothIds(cls, changeid, relid):
        rp = RelLabels(changeid=changeid, relid=relid)
        return rp.getListFromDBMultiple(['changeid', 'relid'])

    @classmethod
    def getRelByLabelRelId(cls, label, relid):
        u = RelLabels(relid=relid)
        u.label = label
        return u.getListFromDBMultiple(['label', 'relid'])

class RelProps:

    def __init__(self, changeid='', relid='', propname='',
            oldpropvalue='', newpropvalue='', changetype=''):

        import MySQLdb
        ##makes sense to change propname to None, this way nothing will be inserted, error!

        self.changeid = changeid
        self.relid = relid
        self.propname = propname
        ##TODO: add constarint in programming or db, if both none, non need of anything here
        self.oldpropvalue = MySQLdb.escape_string(oldpropvalue)
        self.newpropvalue = MySQLdb.escape_string(newpropvalue)
        self.changetype = changetype
        self.dbwrap = MetaSQLDB()
        self.tablename = META_TABLE_RELIDPROPS

    def create(self):

        ##TODO: can put a check here that some strings cannot be empty
        ##or in __init__
        ##TODO: check numrows on insert!

        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelProps object] In create"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        ##TODO: will insert empty strings for oldpropvalue!

        query = "INSERT INTO " + self.tablename + " (changeid, relid, propname,\
                oldpropvalue, newpropvalue, changetype) VALUES(%d, %d, '%s',\
                '%s', '%s', %d)" % (int(self.changeid), int(self.relid), self.propname,
                self.oldpropvalue, self.newpropvalue, int(self.changetype))

        print query
        numrows = 0
        try:
            numrows = cursor.execute(query)
        except Exception as e:
            import traceback
            traceback.print_exc()
            traceback.print_stack()
            print "[relid.RelProps.create: query execution error]"
            self.dbwrap.commitAndClose()
        else:
            self.dbwrap.commitAndClose()

        return numrows

    def getListFromDB(self, by):

        assert(by in ['relid', 'changeid'])
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except:
            print "[RelProps object] In update"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        if by == 'changeid':
            bystr = " where changeid=" + str(self.changeid)
        else:
            bystr = " where relid=" + str(self.relid)

        rest_str = ' ORDER by changeid DESC'
        query = "SELECT changeid, relid, propname, oldpropvalue, newpropvalue,\
                 changetype FROM " + self.tablename + bystr + rest_str

        print query
        cursor.execute(query)
        rows = cursor.fetchall()
        assert(len(rows) >= 1)
        results_list = []
        rprops = RelProps()
        for r in rows:
            rprops.changeid = r[0]
            rprops.relid = r[1]
            rprops.propname = r[2]
            rprops.oldpropvalue = r[3]
            rprops.newpropvalue = r[4]
            rprops.changetype = r[5]

            results_list.append(rprops.__dict__.copy())

        self.dbwrap.commitAndClose()
        for r in results_list:
            del r['dbwrap']
            del r['tablename']
        return results_list

    def getListFromDBMultiple(self, by_list=['']):

        #TODO - verify the by_list
        for by in by_list: assert(by in self.__dict__.keys())

        #TODO - connect to db
        self.dbwrap.connect()
        try:
            cursor = self.dbwrap.cursor()
        except Exception as e:
            print e.message
            print "[RelProps object] In SELECT"
            print "Cannot get cursor"
            self.dbwrap.commitAndClose()

        #TODO - create a list of all strings 
        bystr_list = []
        for by in by_list:
            paramstr = ' ' + str(by) + '='
            if (type(self.__dict__[by]) == int): fieldstr = "%d"
            else: fieldstr = "'%s'"
            fields = fieldstr % self.__dict__[by]
            bystr_list.append(paramstr + fields)
            
        #TODO - join all sources by ' AND '
        bystr = ' AND '.join(bystr_list)
        #TODO - append to select query and run it as usual
        rest_str = ' ORDER by changeid DESC'
        query = "SELECT changeid, relid, propname, oldpropvalue, newpropvalue,\
                 changetype FROM " + self.tablename + " WHERE " + bystr + rest_str
        print query

        cursor.execute(query)
        rows = cursor.fetchall()
        assert(len(rows) >= 1)
        print len(rows)
        results_list = []
        rprop = RelProps()
        for r in rows:
            rprop.changeid = r[0]
            rprop.relid = r[1]
            rprop.propname = r[2]
            rprop.oldpropvalue = r[3]
            rprop.newpropvalue = r[4]
            rprop.changetype = r[5]
            results_list.append(rprop.__dict__.copy())

        self.dbwrap.commitAndClose()

        #TODO - return the list
        return results_list


    def __str__(self):
        s = '[ RelIDprops -- relid: %s   propname: %s  changeid: %s  changetype: %s oldpropvalue: %s newpropvalue: %s]'
        s = s %(str(self.relid), self.propname, str(self.changeid), str(self.changetype), self.oldpropvalue, self.newpropvalue)
        return s

    @classmethod
    def getRelPropsChangeId(cls, changeid):
        rp = RelProps(changeid=changeid)
        return rp.getListFromDB(by='changeid')

    @classmethod
    def getRelPropsRelId(cls, relid):
        rp = RelProps(relid=relid)
        return rp.getListFromDB(by='relid')

    @classmethod
    def getRelPropsBothIds(cls, changeid, relid):
        rp = RelProps(changeid=changeid, relid=relid)
        return rp.getListFromDBMultiple(['changeid', 'relid'])

    @classmethod
    def getRelByPropRelId(cls, propname, relid):
        u = RelProps(relid=relid)
        u.propname = propname
        return u.getListFromDBMultiple(['relid', 'propname'])

