from flask import Flask, jsonify, render_template, request,url_for,redirect
from newsapi import NewsApiClient
import db
from db import ibm_db

# init flask app
app = Flask(__name__)

# Init news api
newsapi = NewsApiClient(api_key='dbd7a6dece8f43faa88d9a976c066a13')
# helper function
@app.route('/',methods=['GET'])
def loginPage():
    return render_template("login.html")
@app.route("/login" ,methods = ['GET'])
def login():
	global userid
	msg = ''
	if request.method == 'GET':
		email = request.args.get("email")
		password = request.args.get("password")

		sql = "SELECT * FROM USERDETAILS WHERE email = ? AND password = ?"
		stmt = ibm_db.prepare(db.conn,sql)

		ibm_db.bind_param(stmt,1,email)
		ibm_db.bind_param(stmt,2,password)
		ibm_db.execute(stmt)
		account = ibm_db.fetch_assoc(stmt)
		print(account)
		
		if account:
			return jsonify({"code":200}) 
			
		else:
			return jsonify({"code":307})

@app.route('/signup',methods=['GET'])
def signup():
	email = request.args.get("email")
	password = request.args.get("password")
	name=request.args.get("name")
	name = request.args.get("name")
	email = request.args.get("email")
	password = request.args.get("password")
	sql = "INSERT INTO USERDETAILS (NAME,EMAIL,PASSWORD) VALUES('"+name+"','"+email+"','"+password+"')"
	stmt = ibm_db.prepare(db.conn,sql)
	ibm_db.execute(stmt)
	return jsonify({"code":200}) 


def get_sources_and_domains():
	all_sources = newsapi.get_sources()['sources']
	sources = []
	domains = []
	for e in all_sources:
		id = e['id']
		domain = e['url'].replace("http://", "")
		domain = domain.replace("https://", "")
		domain = domain.replace("www.", "")
		slash = domain.find('/')
		if slash != -1:
			domain = domain[:slash]
		sources.append(id)
		domains.append(domain)
	sources = ", ".join(sources)
	domains = ", ".join(domains)
	return sources, domains

@app.route("/home", methods=['GET', 'POST'])
def home():
	if request.method == "POST":
		sources, domains = get_sources_and_domains()
		keyword = request.form["keyword"]
		related_news = newsapi.get_everything(q=keyword,
									sources=sources,
									domains=domains,
									language='en',
									sort_by='relevancy')
		no_of_articles = related_news['totalResults']
		if no_of_articles > 100:
			no_of_articles = 100
		all_articles = newsapi.get_everything(q=keyword,
									sources=sources,
									domains=domains,
									language='en',
									sort_by='relevancy',
									page_size = no_of_articles)['articles']
		return render_template("home.html", all_articles = all_articles,
							keyword=keyword)
	else:
		top_headlines = newsapi.get_top_headlines(country="in", language="en")
		total_results = top_headlines['totalResults']
		if total_results > 100:
			total_results = 100
		all_headlines = newsapi.get_top_headlines(country="in",
													language="en",
													page_size=total_results)['articles']
		return render_template("home.html", all_headlines = all_headlines)
	return render_template("home.html")

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True)
    