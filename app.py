from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_cliente')
def login_cliente():
    return render_template('login_cliente.html')

@app.route('/login_funcionario')
def login_funcionario():
    return render_template('login_funcionario.html')

if __name__ == '__main__':
    app.run(debug=True)