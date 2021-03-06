#File Use python functions to update the solr index
#And delete mysql data source or import csv file

import requests
import json
from app.constants import SOLR_HOST, SOLR_CORE, SOLR_PORT

##TODO: Use constants that are imported, and test by calling in app route of guests

def delta_import():

    delta_url = "http://"+SOLR_HOST+":"+str(SOLR_PORT)+"/solr/"+SOLR_CORE+"/dataimport?command=delta-import&clean=false&optimize=false"
    r = requests.get(delta_url)
    print r.text
    return r.text


def full_import():
    #full-import
    full_url = "http://"+SOLR_HOST+":"+str(SOLR_PORT)+"/solr/"+SOLR_CORE+"/dataimport?command=full-import&clean=true&optimize=true"
    r = requests.get(full_url)
    print r.text
    return r.text


#If None then full index delete

def delete_index(index_id=None):

    delete_url = "http://"+SOLR_HOST+":"+str(SOLR_PORT)+"/solr/"+SOLR_CORE+"/update/json?wt=json"
    if index_id is None: index_id = '*'
    uuid_str = "uuid:{}".format(index_id)
    headers = {
    'content-type' : 'text/json',
    'cache-control': "no-cache"
    }
    data = {"delete": {"query":uuid_str, "commitWithin":500},"commit": {}}
    print data

    r = requests.post(delete_url,headers=headers, data=json.dumps(data))
    print r.text
    return None


def update_index(update_type,index_id=None):

    if update_type == 2: delta_import()
    elif update_type == 1: full_import()
    else: delete_index(index_id)


if __name__ == "__main__":
        delete_index()
        full_import()
