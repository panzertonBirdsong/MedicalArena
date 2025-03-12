from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from openai import OpenAI
import random
import os
import openai
import string
import logging
# from wtforms import Textfield



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///llms.db'
app.config['SQLALCHEMY_BINDS'] = {
	'chats': 'sqlite:///chats_db.sqlite',
}
app.config['SECRET_KEY'] = '123'

db = SQLAlchemy(app)

# two_models_selected = []
compete_initiated = False


# openai.api_key = os.getenv("OPENAI_API_KEY")
OpenAI_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

logging.basicConfig(level=logging.INFO)

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

	# Generate Unique ID
	new_id_0 = None
	count = 0
	while True:
		new_id_0 = ''.join(random.choices(string.digits, k=6))
		existed = ChatsDB.query.filter_by(chat_id=new_id_0).first()
		if not existed:
			break
		if count > 99999:
			return render_template("Failed to direct to compete")
		count = count + 1



	new_id_1 = None
	count = 0
	while True:
		new_id_1 = ''.join(random.choices(string.digits, k=6))
		existed = ChatsDB.query.filter_by(chat_id=new_id_1).first()
		if not existed:
			break
		if count > 99999:
			return render_template("Failed to direct to compete")
		count = count + 1

	selected_models = []

	llm_model_collection = LLMDB.query.order_by(LLMDB.db_id).all()
	selected_first = llm_model_collection[0] if llm_model_collection else None
	selected_second = llm_model_collection[0] if llm_model_collection else None

	assert selected_first and selected_second

	selected_models.append(selected_first.db_id)
	selected_models.append(selected_second.db_id)

	new_chat_0 = ChatsDB(new_id_0, selected_first.name)
	new_chat_1 = ChatsDB(new_id_1, selected_second.name)
	db.session.add(new_chat_0)
	db.session.add(new_chat_1)
	db.session.commit()

	return render_template("compete.html", llm_model_collection=llm_model_collection, chat_id=[new_id_0, new_id_1])

@app.route('/add_model/')
def add_model():
	return render_template("add_model.html")

@app.route('/add', methods=['POST'])
def add():



	new_id_0 = None
	count = 0
	while True:
		new_id_0 = ''.join(random.choices(string.digits, k=6))
		existed = LLMDB.query.filter_by(db_id=new_id_0).first()
		if not existed:
			break
		if count > 99999:
			return render_template("Failed to direct to generate a new id.")
		count = count + 1


	# db_id = request.form['db_id']
	db_id = new_id_0
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


@app.route('/submit_user_input', methods=['POST'])
def submit_user_input():

	# get info from html
	data = request.get_json()
	chat_id = data.get("chat_id")
	input_text = data.get("input_text")



	# get response from the first model
	chat_0 = ChatsDB.query.filter_by(chat_id=int(chat_id[0])).first()

	chat_0.add_user_input(input_text)
	db.session.commit()

	reply_0 = get_reply_from_agent(chat_0.model, chat_0.chat_history, chat_0.developer_instruction)

	chat_0.add_agent_reply(reply_0)
	db.session.commit()



	# get response from the second model
	chat_1 = ChatsDB.query.filter_by(chat_id=int(chat_id[1])).first()

	chat_1.add_user_input(input_text)
	db.session.commit()

	reply_1 = get_reply_from_agent(chat_1.model, chat_1.chat_history, chat_1.developer_instruction)

	chat_1.add_agent_reply(reply_1)
	db.session.commit()



	return jsonify({"answer_1": reply_0, "answer_2": reply_1})

def get_reply_from_agent(model_name, chat_history, developer_instruction):
	
	if model_name == "gpt-4o":

		modified_history = []

		for msg in chat_history:
			modified_msg = msg.copy()
			if modified_msg["role"] == "agent":
				modified_msg["role"] = "assistant"

			modified_history.append(modified_msg)

		modified_history = [{"role": "developer", "content": developer_instruction}] + modified_history

		logging.info(modified_history)

		response = OpenAI_client.chat.completions.create(
			model=model_name,
			messages=modified_history
		)
		reply = response.choices[0].message.content
		return reply
	elif model_name == "gemini-2.0-flash":
		...
	else:
		logging.info(f"Error: {model_name} not found.")
		return f"Error: {model_name} not found."


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


@app.route('/update_first_model/<int:db_id>/<int:chat_id>')
def update_first_model(db_id, chat_id):
	selected_model = LLMDB.query.get(db_id)
	chat = ChatsDB.query.get(chat_id)
	if selected_model and chat:
		if len(chat.chat_history) == 0:
			chat.model = selected_model.name
		return str(chat.model)
	return "Error: Model does not exist.", 404

# @app.route('/update_second_model/<int:db_id>')
# def update_second_model(db_id):
# 	second_selected = LLMDB.query.get(db_id)
# 	if second_selected:
# 		two_models_selected[1] = second_selected.db_id
# 		return str(second_selected.db_id)
# 	return "Error: Model does not exist.", 404




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

class ChatsDB(db.Model):
	__bind_key__ = "chats"
	__tablename__ = "chats_db"
	chat_id = db.Column(db.Integer, primary_key=True)
	model = db.Column(db.String(50))
	chat_history = db.Column(db.JSON, default=[])
	developer_instruction = db.Column(db.String(50))

	def __init__(self, chat_id, model):
		self.chat_id = chat_id
		self.model = model
		self.developer_instruction = "Please provide assistance as a BioMedical expert."

	def __repr__(self):
		return f"<ChatsDB chat_id={self.chat_id}>"

	def add_user_input(self, input_text):
		self.chat_history = self.chat_history + [{"role": "user", "content": input_text}]

	def add_agent_reply(self, reply):
		self.chat_history = self.chat_history + [{"role": "agent", "content": reply}]

with app.app_context():
	db.create_all()



if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)