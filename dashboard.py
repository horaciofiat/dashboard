from flask import Flask, request, redirect, render_template_string, flash, url_for, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
import requests
import random
import string
import time
import base64
import hmac
import hashlib
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YuPUJHFgrJUCmwwNjCZjtXGUIAiuWXEO@junction.proxy.rlwy.net:40962/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tu_secret_key'

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios_whatsapp'
    id                    = db.Column(db.Integer, primary_key=True)
    nombre                = db.Column(db.String(100), nullable=False)
    telefono              = db.Column(db.String(20), unique=True, nullable=False)
    clabe                 = db.Column(db.String(18), nullable=True)
    banco                 = db.Column(db.String(50), nullable=True)
    saldo                 = db.Column(db.Numeric, default=0.0)
    password_hash         = db.Column(db.String(512), nullable=False)
    plaid_access_token    = db.Column(db.String(256), nullable=True)
    ultima_consulta_plaid = db.Column(db.DateTime, nullable=True)
    pais                  = db.Column(db.String(20), nullable=True)
    email                 = db.Column(db.String(100), nullable=True)
    ssn_last4             = db.Column(db.String(4), nullable=True)
    address               = db.Column(db.String(255), nullable=True)
    fecha_nacimiento      = db.Column(db.Date, nullable=True)
    kyc_verificado        = db.Column(db.Boolean, default=False)
    rapyd_customer_id     = db.Column(db.String(50), nullable=True)

# ---------------- RAPYD HELPERS ----------------
ACCESS_KEY = 'rak_FC87F89BFB0D11A60157'
SECRET_KEY = 'rsk_aeb64885a09be79d41fbf8791b08857dc313356acd51896d891b6b90895e6b79d2318d9a3f46012f'

def generate_rapyd_signature(http_method, url_path, salt, timestamp, body_string):
    to_sign    = http_method.lower() + url_path + salt + timestamp + ACCESS_KEY + SECRET_KEY + body_string
    h          = hmac.new(SECRET_KEY.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha256)
    hex_digest = h.hexdigest()
    return base64.b64encode(hex_digest.encode('utf-8')).decode('utf-8')

def crear_cliente_rapyd(nombre, email):
    url_path    = '/v1/customers'
    url         = 'https://sandboxapi.rapyd.net' + url_path
    http_method = 'post'
    salt        = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    timestamp   = str(int(time.time()))

    body = {'name': nombre, 'email': email}
    body_string = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
    signature   = generate_rapyd_signature(http_method, url_path, salt, timestamp, body_string)

    headers = {
        'Content-Type': 'application/json',
        'access_key':    ACCESS_KEY,
        'salt':          salt,
        'timestamp':     timestamp,
        'signature':     signature
    }

    resp = requests.post(url, headers=headers, data=body_string)
    if resp.status_code == 200:
        return resp.json()['data']['id']
    else:
        print('Rapyd crear cliente error:', resp.status_code, resp.text)
        return None
# ----------------------------------------------

html_form = """<!DOCTYPE html>
<html lang='es'>
<head>
<meta charset='UTF-8'>
<title>Fiatransfer — Registro</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<script src='https://cdn.tailwindcss.com'></script>
<script>
function toggleFields() {
  const pais = document.getElementById('pais').value;
  document.getElementById('form-mexico').style.display = pais === 'mexico' ? 'block' : 'none';
  document.getElementById('usa-fields').style.display  = pais === 'usa'   ? 'block' : 'none';
}
window.onload = toggleFields;
</script>
</head>
<body class='min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-white'>
  <!-- Header / Branding -->
  <header class='w-full py-8'>
    <div class='max-w-4xl mx-auto px-4 text-center'>
      <!-- Logo colocado arriba del título -->
      <img src="{{ url_for('static', filename='fiatransfer_logo.jpg') }}"
           alt="Logo Fiatransfer"
           class="mx-auto w-28 h-28 mb-4 rounded-full shadow-sm">

      <h1 class='text-4xl md:text-5xl font-extrabold tracking-tight text-blue-700'>Fiatransfer</h1>
      <p class='mt-2 text-sm md:text-base text-blue-700/80'>manda tu dinero rápido y lo más barato del mercado</p>
    </div>
  </header>

  <!-- Card -->
  <main class='max-w-4xl mx-auto px-4 pb-16'>
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="mb-4 space-y-2">
          {% for category, message in messages %}
            <div class="px-4 py-3 rounded-lg border
                        {% if category == 'success' %} bg-green-50 border-green-200 text-green-800
                        {% elif category == 'error' %} bg-red-50 border-red-200 text-red-800
                        {% else %} bg-blue-50 border-blue-200 text-blue-800 {% endif %}">
              {{ message }}
            </div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    <div class='bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-blue-100'>
      <div class='p-6 md:p-8'>
        <h2 class='text-2xl font-semibold text-slate-800 mb-2'>Registra tu cuenta</h2>
        <p class='text-slate-500 mb-6'>Selecciona tu país y completa los datos para empezar a enviar dinero.</p>

        <div class='grid md:grid-cols-2 gap-4 items-end mb-6'>
          <div>
            <label class='block mb-1 text-slate-700 font-medium'>País</label>
            <select id='pais' name='pais' onchange='toggleFields()'
                    class='w-full border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 rounded-lg px-4 py-2 bg-white'>
              <option value='mexico'>México</option>
              <option value='usa'>Estados Unidos</option>
            </select>
          </div>
          <div class='hidden md:block'></div>
        </div>

        <!-- MÉXICO -->
        <form method='POST' id='form-mexico' action='/' class='space-y-5'>
          <input type='hidden' name='pais' value='mexico'>

          <div>
            <label class='block text-slate-700 font-medium mb-1'>Nombre</label>
            <input type='text' name='nombre' required
                   class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200'>
          </div>

          <div>
            <label class='block text-slate-700 font-medium mb-1'>Teléfono</label>
            <input type='text' name='telefono' required
                   placeholder='10 dígitos'
                   class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
          </div>

          <div class='grid md:grid-cols-2 gap-4'>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Email</label>
              <input type='email' name='email' required
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Contraseña</label>
              <input type='password' name='password' required
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
          </div>

          <div class='grid md:grid-cols-2 gap-4'>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>CLABE</label>
              <input type='text' name='clabe' placeholder='18 dígitos'
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Banco</label>
              <input type='text' name='banco'
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
          </div>

          <button type='submit'
                  class='w-full bg-blue-600 hover:bg-blue-700 transition text-white py-3 px-4 rounded-xl font-semibold shadow-md'>
            Guardar
          </button>
        </form>

        <!-- USA -->
        <form method='POST' id='usa-fields' action='/' class='space-y-5' style='display:none;'>
          <input type='hidden' name='pais' value='usa'>

          <div>
            <label class='block text-slate-700 font-medium mb-1'>Nombre</label>
            <input type='text' name='nombre_usa' required
                   class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
          </div>

          <div>
            <label class='block text-slate-700 font-medium mb-1'>Teléfono</label>
            <input type='text' name='telefono_usa' required
                   class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
          </div>

          <div class='grid md:grid-cols-2 gap-4'>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Email</label>
              <input type='email' name='email_usa' required
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Contraseña</label>
              <input type='password' name='password_usa' required
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
          </div>

          <div class='grid md:grid-cols-2 gap-4'>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>SSN (4 últimos)</label>
              <input type='text' name='ssn_usa' maxlength='4'
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
            <div>
              <label class='block text-slate-700 font-medium mb-1'>Fecha de nacimiento</label>
              <input type='date' name='dob_usa'
                     class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
            </div>
          </div>

          <div>
            <label class='block text-slate-700 font-medium mb-1'>Dirección</label>
            <input type='text' name='address_usa'
                   class='w-full border border-blue-200 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-200'>
          </div>

          <button type='submit'
                  class='w-full bg-blue-600 hover:bg-blue-700 transition text-white py-3 px-4 rounded-xl font-semibold shadow-md'>
            Registrar
          </button>
        </form>
      </div>
    </div>

    <p class='text-center text-xs text-slate-400 mt-6'>© <span id="y"></span> Fiatransfer. Todos los derechos reservados.</p>
  </main>

  <script>
    document.getElementById('y').textContent = new Date().getFullYear();
  </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pais = request.form.get('pais')

        if pais == 'mexico':
            nombre   = request.form['nombre']
            telefono = request.form['telefono']
            email    = request.form['email']
            clabe    = request.form.get('clabe')
            banco    = request.form.get('banco')
            pwd      = request.form['password']
            pwd_hash = generate_password_hash(pwd)

            usuario = Usuario(
                nombre = nombre,
                telefono = telefono,
                email = email,
                clabe = clabe,
                banco = banco,
                pais = 'mexico',
                password_hash = pwd_hash
            )
            db.session.add(usuario)
            db.session.commit()

            customer_id = crear_cliente_rapyd(nombre, email)
            if customer_id:
                usuario.rapyd_customer_id = customer_id
                db.session.commit()
            else:
                flash('Error al crear cliente en Rapyd.', 'error')

            # número de WhatsApp (dejé el que pusiste)
            return redirect("https://wa.me/5213318202679?text=Hola,%20quiero%20conectar%20mi%20banco%20de%20México")

        elif pais == 'usa':
            nombre   = request.form['nombre_usa']
            telefono = request.form['telefono_usa']
            email    = request.form['email_usa']
            ssn      = request.form.get('ssn_usa')
            address  = request.form.get('address_usa')
            dob      = request.form.get('dob_usa')
            pwd      = request.form['password_usa']
            pwd_hash = generate_password_hash(pwd)

            usuario = Usuario(
                nombre = nombre,
                telefono = telefono,
                email = email,
                ssn_last4 = ssn,
                address = address,
                fecha_nacimiento = dob,
                pais = 'usa',
                password_hash = pwd_hash
            )
            db.session.add(usuario)
            db.session.commit()

            customer_id = crear_cliente_rapyd(nombre, email)
            if customer_id:
                usuario.rapyd_customer_id = customer_id
                db.session.commit()
            else:
                flash('Error al crear cliente en Rapyd.', 'error')

            # mismo número, cambia aquí si necesitas otro
            return redirect("https://wa.me/5213318202679?text=Hola,%20quiero%20conectar%20mi%20banco%20de%20USA")

    return render_template_string(html_form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)

