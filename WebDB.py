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

        
        
        self.execute("""CREATE TABLE IF NOT EXISTS Documents (
                                 id  INTEGER PRIMARY KEY,
                                 fimficID INTEGER,

                                 author TEXT,
                                 chapter_count INTEGER,
                                 comments INTEGER,
                                 content_rating INTEGER,
                                 content_rating_text TEXT,
                                 date_modified TEXT,
                                 description TEXT,
                                 dislikes INTEGER,
                                 full_image TEXT,
                                 image TEXT,
                                 likes INTEGER,
                                 path TEXT,
                                 short_description TEXT,
                                 status TEXT,
                                 title TEXT,
                                 total_views INTEGER,
                                 url TEXT,
                                 views INTEGER,
                                 words INTEGER
                            );""")

        self.execute("""CREATE TABLE IF NOT EXISTS Authors (
                                id  INTEGER PRIMARY KEY,
                                fimficID INTEGER,
                                name TEXT
                            );""")
        self.execute("""CREATE TABLE IF NOT EXISTS DocumentToTags (
                                 id  INTEGER PRIMARY KEY,
                                 docfimficID INTEGER,
                                 nd_Person BOOLEAN,
                                 Adventure BOOLEAN,
                                 Alternate_Universe BOOLEAN,
                                 Anthro BOOLEAN,
                                 Comedy BOOLEAN,
                                 Crossover BOOLEAN,
                                 Dark BOOLEAN,
                                 Drama BOOLEAN,
                                 Equestria_Girls BOOLEAN,
                                 Horror BOOLEAN,
                                 Human BOOLEAN,
                                 Mystery BOOLEAN,
                                 Random BOOLEAN,
                                 Romance BOOLEAN,
                                 Sad BOOLEAN,
                                 Sci_Fi BOOLEAN,

                                 Slice_of_Life BOOLEAN,
                                 Thriller BOOLEAN,
                                 Tragedy BOOLEAN

                            );""")
        
        self.execute("""CREATE TABLE IF NOT EXISTS AuthorToDocument (
                                 id  INTEGER PRIMARY KEY,
                                 authorfimficID INTEGER,
                                 docfimficID INTEGER
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
        res = self.cur.execute(sql)
        self.cxn.commit()

        return res

    def execute(self, sql, params=None):
        """
        Execute an arbitrary SQL command on the underlying database.
        """
        #print(sql, flush=True)
        if params == None:
            res = self.cur.execute(sql)
        else:
            res = self.cur.execute(sql,params)
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
    def insert_document(self,fimficID, dic):
        native_doc_id = self.lookup_doc_by_fimficID(fimficID)
        if native_doc_id is not None:
            return native_doc_id
        sql = """INSERT INTO Documents """

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
#### my stuff here####
    def lookup_author_by_authorID(self,fimficid):
        sql = "select id from Authors where fimficID={}".format(fimficid)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]
    def lookup_doc_by_doc_ID(self,doc_id):
        sql = "select * from Documents where fimficID={}".format(doc_id)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]
    def get_any_by_doc_ID(self,column_name, doc_id):
        sql = "select {} from Documents where fimficID={}".format(column_name,doc_id)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0][0]
    def get_docIDs_by_top_trait(self, column_name):
        sql = "SELECT fimficID from Documents ORDER BY {} DESC".format(column_name)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            z = [i[0] for i in reslist]
            return z
    def get_all_docIDs(self):
        sql = "select fimficID from Documents"
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            z = [i[0] for i in reslist]
            return z
    def lookup_tags_by_doc_ID(self,doc_ID ):
        sql = "select * from DocumentToTags where docfimficID={}".format(doc_ID)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            return reslist[0]
    def get_docs_by_tag(self,tagname):
        sql = "SELECT docfimficID from DocumentToTags where {} = 1".format(tagname)
        res = self.execute(sql)
        reslist = res.fetchall()
        if reslist == []:
            return None
        else:
            z = [i[0] for i in reslist]
            return z
    def docID_has_tag(self,docID,tag):
        sql = "SELECT * from DocumentToTags where docfimficID = {} and {} = 1".format(docID,tag)
        res = self.execute()
        reslist = res.fetchall()
        if reslist == []:
            return False
        else:
            return True
'''
if __name__=='__main__':
    db = WebDB('test.db')
    urlID  = db.insertCachedURL("http://jimi.ithaca.edu/", "text/html", "JimiLab :: Ithaca College")
    itemID = db.insertItem("JimiLab", "Research Lab")
    u2iID  = db.insertURLToItem(urlID, itemID)

    (url, docType, title) =  db.lookupCachedURL_byID(urlID);

    print("Page Info: ",url,"\t" , docType,"\t", title)
'''