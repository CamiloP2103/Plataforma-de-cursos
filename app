from flask import Flask, request, session, redirect, render_template

app = Flask(__name__, template_folder='html', static_folder='css')
app.secret_key = 'clave_secreta'

USUARIOS = {
    'admin': '1234',
    'usuario1': 'password1'
}

#Encuentra el index principal al iniciar la pagina
@app.route('/')
def home():
    return render_template('index.html')

#Toma las credenciales que se le estan pidiendo al usuario en el index
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    #Si encuentra las credenciales en la base de datos entonces va a redirigirse al home con el usuario dado
    if username in USUARIOS and USUARIOS[username] == password:
        session['usuario'] = username
        return redirect('/home')
    
    #Si no encuentra las credenciales estan incorrectas mostrara el siguiente error
    error = "Usuario o contraseña inválida. Intente de nuevo."
    return render_template('index.html', error=error)

#Funcion para cerrar sesion y volver al index.html
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

#Funcion para establecer la ruta /home, si el usuario no esta en session lo va a mandar al index para que intente de nuevo
@app.route('/home')
def homepage():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('home.html', usuario=session['usuario'])

if __name__ == '__main__':
    app.run(debug=True)
