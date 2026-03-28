from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ======================
# DB
# ======================
def get_db():
    return sqlite3.connect("clientes.db")

# ======================
# ESTADO + FORMATOS
# ======================
def parse_fecha(fecha):
    try:
        return datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        return datetime.strptime(fecha, "%Y/%m/%d").date()

def calcular_estado(vence):
    hoy = datetime.now().date()
    fecha_v = parse_fecha(vence)

    if fecha_v < hoy:
        return "Vencido"
    elif (fecha_v - hoy).days <= 2:
        return "Por vencer"
    else:
        return "Activo"

# ======================
# ROUTES
# ======================
@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM clientes")
    data = cursor.fetchall()

    clientes = []
    alertas = []

    for c in data:
        estado = calcular_estado(c[5])

        if estado != "Activo":
            alertas.append(f"{c[1]} → {estado}")

        clientes.append({
            "id": c[0],
            "nombre": c[1],
            "whatsapp": c[2],
            "servicio": c[3],
            "inicio": c[4],
            "vence": c[5],
            "estado": estado
        })

    return render_template("index.html", clientes=clientes, alertas=alertas)

@app.route("/add", methods=["POST"])
def add():
    nombre = request.form["nombre"]
    whatsapp = request.form["whatsapp"]
    servicio = request.form["servicio"]
    inicio = request.form["inicio"]
    vence = request.form["vence"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO clientes (nombre, whatsapp, servicio, inicio, vence)
    VALUES (?, ?, ?, ?, ?)
    """, (nombre, whatsapp, servicio, inicio, vence))

    db.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (id,))
    db.commit()
    return redirect("/")

# ======================
# INIT
# ======================
if __name__ == "__main__":
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        whatsapp TEXT,
        servicio TEXT,
        inicio TEXT,
        vence TEXT
    )
    """)
    db.close()

    app.run(host="0.0.0.0", port=5000)