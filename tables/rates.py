from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:YuPUJHFgrJUCmwwNjCZjtXGUIAiuWXEO@junction.proxy.rlwy.net:40962/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Rate(db.Model):
    __tablename__ = 'rates'

    id = db.Column(db.Integer, primary_key=True)

    # Nota: el nombre de la columna en la BD será "timestamp" (como la usas en tus SELECTs)
    timestamp = db.Column('timestamp', db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    taptap_rate          = db.Column(db.Numeric(10, 4), nullable=True)
    binance_rate         = db.Column(db.Numeric(10, 4), nullable=False)  # la usas seguro en el webhook
    wise_rate            = db.Column(db.Numeric(10, 4), nullable=True)
    diff_cheapest        = db.Column(db.Numeric(10, 4), nullable=True)
    tipo_cambio_cliente  = db.Column(db.Numeric(10, 4), nullable=True)
    tipo_cambio_stripe   = db.Column(db.Numeric(10, 4), nullable=True)

    def __repr__(self):
        return f"<Rate {self.id} {self.timestamp} binance={self.binance_rate}>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Índice útil para ORDER BY "timestamp" DESC
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_rates_timestamp_desc ON rates ("timestamp" DESC);'))
        db.session.commit()

        # Semilla opcional para evitar None al primer SELECT
        if not db.session.execute(db.text('SELECT 1 FROM rates LIMIT 1')).first():
            db.session.add(Rate(
                taptap_rate=18.50,
                binance_rate=18.70,
                wise_rate=18.60,
                diff_cheapest=0.10,
                tipo_cambio_cliente=18.56,
                tipo_cambio_stripe=18.50
            ))
            db.session.commit()

        print("✅ Tabla 'rates' lista (creada o ya existente).")
