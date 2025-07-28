from flask import Flask, render_template, request
from backend import authenticate, generate_unique_portfolios

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    investment = float(request.form['investment'])
    risk_level = request.form['risk']
    time_goal = request.form['goal']
    token = authenticate()
    portfolios = generate_unique_portfolios(token, investment, risk_level, time_goal)
    return render_template('results.html', portfolios=portfolios)

if __name__ == '__main__':
    app.run(debug=True)