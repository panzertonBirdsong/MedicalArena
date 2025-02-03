from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
# from wtforms import Textfield



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///llms.db'
app.config['SECRET_KEY'] = '123'

db = SQLAlchemy(app)

two_models_selected = []
compete_initiated = False




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
	llm_model_collection = LLMDB.query.order_by(LLMDB.db_id).all()
	selected_first = llm_model_collection[0] if llm_model_collection else None
	selected_second = llm_model_collection[1] if llm_model_collection else None

	assert selected_first and selected_second

	two_models_selected.append(selected_first.db_id)
	two_models_selected.append(selected_second.db_id)

	# compete_initiated = True
	return render_template("compete.html", llm_model_collection=llm_model_collection, two_models_selected=two_models_selected)

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


@app.route('/submit_user_input', methods=['GET', 'POST'])
def submit_user_input():
	new_user_input = request.form['user_input']

	# TBD


	return redirect(url_for('compete'))


@app.route('/vote_first', methods=['POST'])
def vote_first():
	model = LLMDB.query.get(two_models_selected[0])
	model.vote_score = model.vote_score + 2
	db.session.commit()
	return redirect(url_for('compete'))


@app.route('/vote_second', methods=['POST'])
def vote_second():
	model = LLMDB.query.get(two_models_selected[1])
	model.vote_score = model.vote_score + 2
	db.session.commit()
	return redirect(url_for('compete'))


@app.route('/vote_tie', methods=['POST'])
def vote_tie():
	model_1 = LLMDB.query.get(two_models_selected[0])
	model_2 = LLMDB.query.get(two_models_selected[1])
	model_1.vote_score = model.vote_score + 1
	model_2.vote_score = model.vote_score + 1
	db.session.commit()
	return redirect(url_for('compete'))

@app.route('/restart')
def restart():
	compete_initiated = False

	return compete()


@app.route('/update_first_model/<int:db_id>')
def update_first_model(db_id):
	first_selected = LLMDB.query.get(db_id)
	if first_selected:
		two_models_selected[0] = first_selected.db_id
		return str(first_selected.db_id)
	return "Error: Model does not exist.", 404

@app.route('/update_second_model/<int:db_id>')
def update_second_model(db_id):
	second_selected = LLMDB.query.get(db_id)
	if second_selected:
		two_models_selected[1] = second_selected.db_id
		return str(second_selected.db_id)
	return "Error: Model does not exist.", 404




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