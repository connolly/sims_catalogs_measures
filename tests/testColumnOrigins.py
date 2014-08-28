import os
import numpy
import unittest
from lsst.sims.catalogs.measures.instance import InstanceCatalog, cached
from lsst.sims.catalogs.generation.db import DBObject

def makeTestDB(size=10, **kwargs):
    """
    Make a test database to serve information to the mflarTest object
    """
    conn = sqlite3.connect('testDatabase.db')
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE testTable
                     (id int, aa float, bb float, ra float, decl float)''')
        conn.commit()
    except:
        raise RuntimeError("Error creating database.")
    
    for i in xrange(size):
        
        ra = numpy.random.sample()*360.0
        dec = (numpy.random.sample()-0.5)*180.0
        
        #insert the row into the data base
        qstr = '''INSERT INTO testTable VALUES (%i, '%f', '%f', '%f', '%f')''' % (i, 2.0*i,3.0*i,ra,dec)
        c.execute(qstr)
        
    conn.commit()
    conn.close()

class testDBobject(DBObject):
    objid = 'testDBobject'
    tableid = 'testTable'
    idColKey = 'id'
    #Make this implausibly large?  
    appendint = 1023
    dbAddress = 'sqlite:///testDatabase.db'
    raColName = 'ra'
    decColName = 'decl'
    columns = [('objid', 'id', int),
               ('raJ2000', 'ra*%f'%(numpy.pi/180.)),
               ('decJ2000', 'decl*%f'%(numpy.pi/180.)),
               ('aa', None),
               ('bb', None)]

class mixin1(object):
    @cached
    def get_cc(self):
        aa = self.column_by_name('aa')
        bb = self.column_by_name('bb')
        
        return numpy.array(aa-bb)

    @cached
    def get_dd(self):
        aa = self.column_by_name('aa')
        bb = self.column_by_name('bb')
        
        return numpy.array(aa+bb)

class mixin2(object):
    @compound('cc','dd')
    def get_both(self):
        aa = self.column_by_name(aa)
        bb = self.column_by_name(bb)
        
        return numpy.array([aa-bb,aa+bb])

class mixin3(object):
    @cached
    def get_cc(self):
        aa = self.column_by_name('aa')
        bb = self.column_by_name('bb')
        
        return numpy.array(aa-bb)
    
class testCatalogDefaults(InstanceCatalog):
    column_outputs = ['objid','aa','bb','cc','dd','raJ2000','decJ2000']
    default_columns = [('cc',0.0,float),('dd',1.0,float)]

class testCatalogMixin1(InstanceCatalog,mixin1):
    column_outputs = ['objid','aa','bb','cc','dd','raJ2000','decJ2000']
    default_columns = [('cc',0.0,float),('dd',1.0,float)]

class testCatalogMixin2(InstanceCatalog,mixin2):
    column_outputs = ['objid','aa','bb','cc','dd','raJ2000','decJ2000']
    default_columns = [('cc',0.0,float),('dd',1.0,float)]

class testCatalogMixin3(InstanceCatalog,mixin3):
    column_outputs = ['objid','aa','bb','cc','dd','raJ2000','decJ2000']
    default_columns = [('cc',0.0,float),('dd',1.0,float)]
    
class testCatalogMixin3Mixin1(InstanceCatalog,Mixin3,Mixin1):
    column_outputs = ['objid','aa','bb','cc','dd','raJ2000','decJ2000']
    default_columns = [('cc',0.0,float),('dd',1.0,float)]

class testColumnOrigins(unittest.TestCase):

if os.path.exists('testDatabase.db'):
    os.unlink('testDatabase.db')

makeTestDB()
myDBobject = testDBobject()
myCatalog = testCatalog(myDBobject)
myCatalog.print_column_origins()
print myCatalog._column_origins
myCatalog.write_catalog('catOutput.sav')
