#!/usr/bin/python3
'''
sqllite3 wrapper for Search Engine Lab Sequence (Richard Wicentowski, Doug Turnbull, 2010-2015)
CS490: Search Engine and Recommender Systems
http://jimi.ithaca.edu/CourseWiki/index.php/CS490_S15_Schedule
'''

import sqlite3
import re

class WebDB:

    def __init__(self, dbfile):
        """
        Connect to the database specified by dbfile.  Assumes that this
        dbfile already contains the tables specified by the schema.
        """
        self.dbfile = dbfile
        self.cxn = sqlite3.connect(dbfile)
        self.cur = self.cxn.cursor()
        
        
        self.execute("""CREATE TABLE IF NOT EXISTS CachedURL (
                                 id  INTEGER PRIMARY KEY,
                                 url VARCHAR,
                                 title VARCHAR,
                                 docType VARCHAR
                            );""")
                            
        self.execute("""CREATE TABLE IF NOT EXISTS URLToItem (
                                 id  INTEGER PRIMARY KEY,
                                 urlID INTEGER,
                                 itemID INTEGER
                            );""")
        
        self.execute("""CREATE TABLE IF NOT EXISTS Item (
                                 id  INTEGER PRIMARY KEY,
                                 name VARCHAR,
                                 type VARCHAR
                            );""")

    def _quote(self, text):
        """
        Properly adjusts quotation marks for insertion into the database.
        """

        text = re.sub("'", "''", text)
        return text

    def _unquote(self, text):
        """
        Properly adjusts quotations marks for extraction from the database.
        """

        text = re.sub("''", "'", text)
        return text

    def execute(self, sql):
        """
        Execute an arbitrary SQL command on the underlying database.
        """
        #print(sql)
        res = self.cur.execute(sql)
        self.cxn.commit()

        return res


    ####----------####
    #### CachedURL ####

    def lookupCachedURL_byURL(self, url):
        """
        Returns the id of the row matching url in CachedURL.

        If there is no matching url, returns an None.
        """
        sql = "SELECT id FROM CachedURL WHERE URL='%s'" % (self._quote(url))
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        elif len(reslist) > 1:
            raise RuntimeError('DB: constraint failure on CachedURL.')
        else:
            return reslist[0][0]


    def lookupCachedURL_byID(self, cache_url_id):
        """
        Returns a (url, docType, title) tuple for the row
        matching cache_url_id in CachedURL.

        If there is no matching cache_url_id, returns an None.
        """
        sql = "SELECT url, docType, title FROM CachedURL WHERE id=%d"\
              % (cache_url_id)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]

    def lookupURLs_byItemID(self,itemID):
        #gets list of URLs associated with item
        sql = "SELECT url, CachedURL.id FROM CachedURL JOIN UrlToItem on CachedURL.id = UrlToItem.urlID WHERE UrlToItem.itemID='%s'"\
            % (itemID)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            out = []
            for i in reslist:
                out.append(i)
            return out#[0]

    def lookupItem(self, name, itemType):
        """
        Returns a Item ID for the row
        matching name and itemType in the Item table.

        If there is no match, returns an None.
        """
        sql = "SELECT id FROM Item WHERE name='%s' AND type='%s'"\
              % (self._quote(name), self._quote(itemType))
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0][0]

    def ItemIDfromUrlID(self,urlID):
        #gets list of itemIDs associated with urlID
        sql = "SELECT name, type FROM Item JOIN UrlToItem on Item.id =UrlToItem.itemID WHERE UrlToItem.urlID = {}".format(urlID)
        res = self.execute(sql)
        reslist= res.fetchall()
        if reslist == []:
            return None
        else:
            out = []
            for i in reslist:
                itemTitle = i[0].rstrip("\n")+"("+i[1]+")"
                out.append(itemTitle)
            return out[0]
    def getURLsfromItemID(self,itemID):
        pass
        sql = "SELECT url, id FROM CachedURL JOIN UrlToItem on Item.id = UrlWHERE id=%d"

    def getItems(self):
        pass
        sql = "SELECT * from Item"
        res = self.execute(sql)
        reslist = res.fetchall()
        return reslist
    def lookupURLToItem(self, urlID, itemID):
        """
        Returns a urlToItem.id for the row
        matching name and itemType in the Item table.

        If there is no match, returns an None.
        """
        sql = "SELECT id FROM UrlToItem WHERE urlID=%d AND itemID=%d"\
              % (urlID, itemID)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]

    def deleteCachedURL_byID(self, cache_url_id):
        """
        Delete a CachedURL row by specifying the cache_url_id.

        Returns the previously associated URL if the integer ID was in
        the database; returns None otherwise.
        """
        result = self.lookupCachedURL_byID(cache_url_id)
        if result == None:
            return None

        (url, download_time, docType) = result

        sql = "DELETE FROM CachedURL WHERE id=%d" % (cache_url_id)
        self.execute(sql)
        return self._unquote(url)

    

    def insertCachedURL(self, url, docType=None, title=None):

        #print("in insertCachedURL")
        """
        Inserts a url into the CachedURL table, returning the id of the
        row.
        
        Enforces the constraint that url is unique.
        """        
        if docType is None:
            docType = ""

        cache_url_id = self.lookupCachedURL_byURL(url)
        if cache_url_id is not None:
            return cache_url_id

        sql = """INSERT INTO CachedURL (url, docType, title)
                 VALUES ('%s', '%s','%s')""" % (self._quote(url), docType, self._quote(title))
        #print(sql)
        res = self.execute(sql)
        return self.cur.lastrowid
        

    def insertItem(self, name, itemType):
        """
        Inserts a item into the Item table, returning the id of the
        row. 
        itemType should be something like "music", "book", "movie"
        
        Enforces the constraint that name is unique.
        """        


        item_id = self.lookupItem(name, itemType)
        if item_id is not None:
            return item_id

        sql = """INSERT INTO Item (name, type)
                 VALUES (\'%s\', \'%s\')""" % (self._quote(name), self._quote(itemType))

        res = self.execute(sql)
        return self.cur.lastrowid

    def insertURLToItem(self, urlID, itemID):
        """
        Inserts a item into the URLToItem table, returning the id of the
        row.         
        Enforces the constraint that (urlID,itemID) is unique.
        """        


        u2i_id = self.lookupURLToItem(urlID, itemID)
        if u2i_id is not None:
            return u2i_id

        sql = """INSERT INTO URLToItem (urlID, itemID)
                 VALUES ('%s', '%s')""" % (urlID, itemID)

        res = self.execute(sql)
        return self.cur.lastrowid

if __name__=='__main__':
    db = WebDB('test.db')
    urlID  = db.insertCachedURL("http://jimi.ithaca.edu/", "text/html", "JimiLab :: Ithaca College")
    itemID = db.insertItem("JimiLab", "Research Lab")
    u2iID  = db.insertURLToItem(urlID, itemID)

    (url, docType, title) =  db.lookupCachedURL_byID(urlID);

    print("Page Info: ",url,"\t" , docType,"\t", title)

    
