#! /usr/bin/python2.6

# originally from http://wiki.apache.org/couchdb/Getting_started_with_Python

# Modified heavily to support custom couchdb migration for Adlibre DMS

# This is used when we need to do some hacky migrations or raw manipulations to the couchdb schema

import httplib, json, datetime

MIGRATION_DATE_PATTERN = '%Y-%m-%d' # <<< MIGRATE FROM THIS PATTERN

def prettyPrint(s):
    """Prettyprints the json response of an HTTPResponse object"""

    # HTTPResponse instance -> Python object -> str
    return json.dumps(json.loads(s.read()), sort_keys=True, indent=4)

class Couch:
    """Basic wrapper class for operations on a couchDB"""

    def __init__(self, host, port=5984, options=None):
        self.host = host
        self.port = port

    def connect(self):
        return httplib.HTTPConnection(self.host, self.port) # No close()

    # Database operations

    def createDb(self, dbName):
        """Creates a new database on the server"""

        r = self.put(''.join(['/',dbName,'/']), "")
        prettyPrint(r)

    def deleteDb(self, dbName):
        """Deletes the database on the server"""

        r = self.delete(''.join(['/',dbName,'/']))
        prettyPrint(r)

    def listDb(self):
        """List the databases on the server"""

        prettyPrint(self.get('/_all_dbs'))

    def infoDb(self, dbName):
        """Returns info about the couchDB"""
        r = self.get(''.join(['/', dbName, '/']))
        prettyPrint(r)

    # Document operations

    def listDoc(self, dbName):
        """List all documents in a given database"""

        r = self.get(''.join(['/', dbName, '/_design/', dbName, '/_view/all']))
        return prettyPrint(r)

    def openDoc(self, dbName, docId):
        """Open a document in a given database"""
        r = self.get(''.join(['/', dbName, '/', docId,]))
        return prettyPrint(r)

    def saveDoc(self, dbName, body, docId=None):
        """Save/create a document to/in a given database"""
        if docId:
            r = self.put(''.join(['/', dbName, '/', docId]), body)
        else:
            r = self.post(''.join(['/', dbName, '/']), body)
        return prettyPrint(r)

    def deleteDoc(self, dbName, docId):
        # XXX Crashed if resource is non-existent; not so for DELETE on db. Bug?
        # XXX Does not work any more, on has to specify an revid
        #     Either do html head to get the recten revid or provide it as parameter
        r = self.delete(''.join(['/', dbName, '/', docId, '?revid=', rev_id]))
        prettyPrint(r)

    # Basic http methods

    def get(self, uri):
        c = self.connect()
        headers = {"Accept": "application/json"}
        c.request("GET", uri, None, headers)
        return c.getresponse()

    def post(self, uri, body):
        c = self.connect()
        headers = {"Content-type": "application/json"}
        c.request('POST', uri, body, headers)
        return c.getresponse()

    def put(self, uri, body):
        c = self.connect()
        if len(body) > 0:
            headers = {"Content-type": "application/json"}
            c.request("PUT", uri, body, headers)
        else:
            c.request("PUT", uri, body)
        return c.getresponse()

    def delete(self, uri):
        c = self.connect()
        c.request("DELETE", uri)
        return c.getresponse()

def unify_index_info_couch_dates_fmt(index_info):
    """
    Applies standardization to secondary keys 'date' type keys.
    """
    clean_info = {}
    index_keys = [key for key in index_info.iterkeys()]
    for index_key in index_keys:
        if not index_key=='date':
            try:
                value = index_info[index_key]
                index_date = datetime.datetime.strptime(value, MIGRATION_DATE_PATTERN)
                clean_info[index_key] = str_date_to_couch(value)
            except ValueError:
                clean_info[index_key] = index_info[index_key]
                pass
        else:
            clean_info[index_key] = index_info[index_key]
    return clean_info

def str_date_to_couch(from_date):
    """
    Converts date from form date widget generated format

    e.g.:
    date '2012-03-02' or whatever format specified in settings.py
    to CouchDocument stored date. E.g.: '2012-03-02T00:00:00Z'
    """
    # HACK: left here to debug improper date calls
    converted_date = ''
    try:
        couch_date = datetime.datetime.strptime(from_date, MIGRATION_DATE_PATTERN)
        converted_date = str(couch_date.strftime("%Y-%m-%dT00:00:00Z"))
    except ValueError:
        print 'adlibre.date_convertor time conversion error. String received: %s' % from_date
        pass
    return converted_date

def reformatDates():
    """
    This will increment the doc_type_rule_id by 1.
    Used for JTG migration 20120613
    """
    db = Couch('localhost', '5984')
    dbName = 'dmscouch'

    print "\nList all documents in database %s updated" % dbName
    docs_js = db.listDoc(dbName)

    docs_decoded = json.loads(docs_js)

    for doc in docs_decoded['rows']:
        bar_code = doc['id']

        d_js = db.openDoc(dbName, bar_code)
        d = json.loads(d_js)

        d['mdt_indexes'] = unify_index_info_couch_dates_fmt(d['mdt_indexes'])

        d_enc = json.dumps(d)
        print db.saveDoc(dbName, d_enc, docId=bar_code)

if __name__ == "__main__":
    reformatDates()