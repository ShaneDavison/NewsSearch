from flask import Flask, request, Response
from flask import render_template
from pymongo import MongoClient
import json
import urllib2

client = MongoClient('localhost', 27017)
db = client['stream2_project']
coll = db.word


def search_nytimes(word):
    collection = db.get_collection(word)
    collection.remove({"source": "nytimes"})

    for year in range(1951, 2016):
        url = "http://api.nytimes.com/svc/search/v2/articlesearch.json?q=" + str(word) + "&begin_date=%s0101&end_date=%s0101&api-key=9edec79d0d0ab43243de45857ebdb1a6:13:74877917" % (year, year + 1)
        response = urllib2.urlopen(url)
        data = json.load(response)
        year_hits = {"year": str(year), "hits": str(data['response']['meta']['hits']), "source": 'nytimes'}
        collection.insert(year_hits)


app = Flask(__name__)



MONGODB_HOST='127.0.0.1'
MONGODB_PORT=27017
DBS_NAME='stream2_project'
COLLECTION_NAME= "war"
FIELDS ={
    "_id":False,
    "source":True,
    "hits" : True,
    "year":True

}





@app.route('/')
def index():
    return render_template("index.html")

@app.route('/searchForm')
def searchForm():
    return render_template("searchForm.html")

@app.route('/search/<term>')
def search(term):
    wordsearch = request.args.get('wordSearch')
    if term in db.collection_names(False):
        return donor_projects(term)


    else:

        search_nytimes(str(term))
        return donor_projects(str(term))





def donor_projects(term):

    searchConn = request.args.get('wordSearch')
    connection= MongoClient(MONGODB_HOST,MONGODB_PORT)
    collection=connection[DBS_NAME][term]
    projects=collection.find(projection=FIELDS,limit=55000)
    json_projects=[]
    for project in projects:
        json_projects.append(project)
        # json_projects.append(project)
        # json_projects = json.dumps(json_projects)
    connection.close()
    json_projects = json.dumps(json_projects)
    # return render_template('searchresults.html', data=json_projects)

    # dat = dumps(data)

    resp = Response(response=json_projects, status=200)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Access-Control_Origin'] = '*'

    return resp

if __name__ == '__main__':
    app.run(debug=True)
