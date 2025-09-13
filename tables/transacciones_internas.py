from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YuPUJHFgrJUCmwwNjCZjtXGUIAiuWXEO@junction.proxy.rlwy.net:40962/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ Debes volver a declarar este modelo aquí
class Usuario(db.Model):
    __tablename__ = 'usuarios_whatsapp'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    telefono = db.Column(db.String(20), unique=True)
    clabe = db.Column(db.String(18))
    banco = db.Column(db.String(50))
    saldo = db.Column(db.Numeric, default=0.0)

# ✅ Nueva tabla
class TransaccionInterna(db.Model):
    __tablename__ = 'transacciones_internas'
    id = db.Column(db.Integer, primary_key=True)
    emisor_id = db.Column(db.Integer, db.ForeignKey('usuarios_whatsapp.id'))
    receptor_id = db.Column(db.Integer, db.ForeignKey('usuarios_whatsapp.id'))
    cantidad_btc = db.Column(db.Numeric)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tabla 'transacciones_internas' creada (o ya existente).")
