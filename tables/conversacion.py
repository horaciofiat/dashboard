from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YuPUJHFgrJUCmwwNjCZjtXGUIAiuWXEO@junction.proxy.rlwy.net:40962/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SolicitudTransferencia(db.Model):
    __tablename__ = 'solicitudes_transferencia'
    id = db.Column(db.Integer, primary_key=True)
    telefono = db.Column(db.String(20))
    monto = db.Column(db.Numeric)
    clabe_destino = db.Column(db.String(256))
    nombre_destino = db.Column(db.String(100))  # <-- Esta es la columna nueva
    referencia = db.Column(db.String(20))
    estatus = db.Column(db.String(20), default='pendiente')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    mensaje_enviado = db.Column(db.Boolean, default=False)
    routing_destino = db.Column(db.String(20))
    account_destino = db.Column(db.String(20))
    monto_mxn = db.Column(db.Numeric, nullable=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Tabla 'solicitudes_transferencia' creada (o ya existente).")
