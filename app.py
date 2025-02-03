from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# from wtforms import Textfield



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///llms.db'
app.config['SECRET_KEY'] = '123'

db = SQLAlchemy(app)




@app.route('/')
def home():
	return render_template("index.html")

@app.route('/leaderboard/')
def leaderboard():
	llm_model_collection = LLMDB.query.order_by(LLMDB.overall_score.desc()).all()
	return render_template("leaderboard.html", llm_model_collection=llm_model_collection)

@app.route('/introduction/')
def introduction():
	return render_template("introduction.html")

@app.route('/compete/')
def compete():
	return render_template("compete.html")

@app.route('/add_model/')
def add_model():
	return render_template("add_model.html")

@app.route('/add', methods=['POST'])
def add():
	db_id = request.form['db_id']
	name = request.form['name']
	company = request.form['company']
	vote_score = request.form['vote_score']
	test_score = request.form['test_score']
	overall_score = request.form['overall_score']
	license = request.form['license']
	new_llm = LLMDB(db_id=db_id, name=name, company=company, vote_score=vote_score, test_score=test_score, overall_score=overall_score, license=license)
	
	db.session.add(new_llm)
	db.session.commit()

	return redirect(url_for('home'))





class LLMDB(db.Model):
	db_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	company = db.Column(db.String(50))
	vote_score = db.Column(db.Integer)
	test_score = db.Column(db.Integer)
	overall_score = db.Column(db.Float)
	license = db.Column(db.String(50))

	def __init__(self, db_id, name, company, vote_score, test_score, overall_score, license):
		self.db_id = db_id
		self.name = name
		self.company = company
		self.vote_score = vote_score
		self.test_score = test_score
		self.overall_score = overall_score
		self.license = license

with app.app_context():
	db.create_all()



if __name__ == "__main__":
	app.run(debug=True, threaded=True)