from flask import Flask, request, session, redirect, render_template

app = Flask(__name__, template_folder='html', static_folder='static')
app.secret_key = 'clave_secreta'

USUARIOS = {
    'admin': '1234',
    'usuario1': 'password1'
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username in USUARIOS and USUARIOS[username] == password:
        session['usuario'] = username
        return redirect('/')
    
    return "Credenciales incorrectas", 401

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
