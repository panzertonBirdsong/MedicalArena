from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
	return render_template("index.html")

@app.route('/leaderboard/')
def leaderboard():
	return render_template("leaderboard.html")

@app.route('/introduction/')
def introduction():
	return render_template("introduction.html")

@app.route('/compete/')
def compete():
	return render_template("compete.html")




if __name__ == "__main__":
	app.run(debug=True, threaded=True)