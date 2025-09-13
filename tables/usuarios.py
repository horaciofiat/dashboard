from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YuPUJHFgrJUCmwwNjCZjtXGUIAiuWXEO@junction.proxy.rlwy.net:40962/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios_whatsapp'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    telefono = db.Column(db.String(20), unique=True)
    clabe = db.Column(db.String(18))
    banco = db.Column(db.String(50))
    saldo = db.Column(db.Numeric, default=0.0)
    password_hash = db.Column(db.String(128))
    
    plaid_access_token = db.Column(db.String(256), nullable=True)
    ultima_consulta_plaid = db.Column(db.DateTime, nullable=True)

    # Nuevos campos para KYC
    pais = db.Column(db.String(20))
    email = db.Column(db.String(100))
    ssn_last4 = db.Column(db.String(4), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    kyc_verificado = db.Column(db.Boolean, default=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tabla 'usuarios_whatsapp' actualizada (o ya existente).")
