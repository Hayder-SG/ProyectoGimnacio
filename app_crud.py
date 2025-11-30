from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "claveTemporalParaCRUD"

# ==============================
# Conexión a la base de datos
# ==============================
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "gimnasio"

mysql = MySQL(app)

# ==============================
# CRUD SOCIO
# ==============================
@app.route("/socios")
def socios_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM socio")
    socios = cursor.fetchall()
    return render_template("socios/lista.html", socios=socios)

@app.route("/socios/agregar", methods=["POST"])
def socios_agregar():
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO socio (nombre, apellido, email, telefono) VALUES (%s, %s, %s, %s)",
        (nombre, apellido, email, telefono)
    )
    mysql.connection.commit()
    return redirect("/socios")

@app.route("/socios/editar/<int:id>", methods=["POST"])
def socios_editar(id):
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    email = request.form["email"]
    telefono = request.form["telefono"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE socio SET nombre=%s, apellido=%s, email=%s, telefono=%s WHERE id_socio=%s",
        (nombre, apellido, email, telefono, id)
    )
    mysql.connection.commit()
    return redirect("/socios")

@app.route("/socios/eliminar/<int:id>")
def socios_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM socio WHERE id_socio=%s", (id,))
    mysql.connection.commit()
    return redirect("/socios")

# ==============================
# CRUD PLANES
# ==============================
@app.route("/planes")
def planes_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM planmembresia")
    planes = cursor.fetchall()
    return render_template("planes/lista.html", planes=planes)

@app.route("/planes/agregar", methods=["POST"])
def planes_agregar():
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    duracion_dias = request.form["duracion_dias"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO planmembresia (nombre_plan, precio, duracion_dias) VALUES (%s, %s, %s)",
        (nombre, precio, duracion_dias)
    )
    mysql.connection.commit()
    return redirect("/planes")

@app.route("/planes/editar/<int:id>", methods=["POST"])
def planes_editar(id):
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    duracion_dias = request.form["duracion_dias"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE planmembresia SET nombre_plan=%s, precio=%s, duracion_dias=%s WHERE id_plan=%s",
        (nombre, precio, duracion_dias, id)
    )
    mysql.connection.commit()
    return redirect("/planes")

@app.route("/planes/eliminar/<int:id>")
def planes_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM planmembresia WHERE id_plan=%s", (id,))
    mysql.connection.commit()
    return redirect("/planes")

# ==============================
# CRUD PAGOS
# ==============================
@app.route("/pagos")
def pagos_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.id_pago, p.id_socio, s.nombre, s.apellido, pl.nombre_plan,
               p.fecha_inicio, p.fecha_fin, p.monto
        FROM pago p
        JOIN socio s ON p.id_socio = s.id_socio
        JOIN planmembresia pl ON p.id_plan = pl.id_plan
    """)
    pagos = cursor.fetchall()
    return render_template("pagos/lista.html", pagos=pagos)

@app.route("/pagos/agregar", methods=["POST"])
def pagos_agregar():
    id_socio = request.form["id_socio"]
    id_plan = request.form["id_plan"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    monto = request.form["monto"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO pago (id_socio, id_plan, fecha_inicio, fecha_fin, monto) VALUES (%s, %s, %s, %s, %s)",
        (id_socio, id_plan, fecha_inicio, fecha_fin, monto)
    )
    mysql.connection.commit()
    return redirect("/pagos")

@app.route("/pagos/editar/<int:id>", methods=["POST"])
def pagos_editar(id):
    id_socio = request.form["id_socio"]
    id_plan = request.form["id_plan"]
    fecha_inicio = request.form["fecha_inicio"]
    fecha_fin = request.form["fecha_fin"]
    monto = request.form["monto"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE pago SET id_socio=%s, id_plan=%s, fecha_inicio=%s, fecha_fin=%s, monto=%s WHERE id_pago=%s",
        (id_socio, id_plan, fecha_inicio, fecha_fin, monto, id)
    )
    mysql.connection.commit()
    return redirect("/pagos")

@app.route("/pagos/eliminar/<int:id>")
def pagos_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pago WHERE id_pago=%s", (id,))
    mysql.connection.commit()
    return redirect("/pagos")

# ==============================
# CRUD CLASES
# ==============================
@app.route("/clases")
def clases_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM clase")
    clases = cursor.fetchall()
    return render_template("clases/lista.html", clases=clases)

@app.route("/clases/agregar", methods=["POST"])
def clases_agregar():
    nombre = request.form["nombre_clase"]
    descripcion = request.form["descripcion"]
    cupo = request.form["cupo"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO clase (nombre_clase, descripcion, cupo) VALUES (%s, %s, %s)",
        (nombre, descripcion, cupo)
    )
    mysql.connection.commit()
    return redirect("/clases")

@app.route("/clases/editar/<int:id>", methods=["POST"])
def clases_editar(id):
    nombre = request.form["nombre_clase"]
    descripcion = request.form["descripcion"]
    cupo = request.form["cupo"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE clase SET nombre_clase=%s, descripcion=%s, cupo=%s WHERE id_clase=%s",
        (nombre, descripcion, cupo, id)
    )
    mysql.connection.commit()
    return redirect("/clases")

@app.route("/clases/eliminar/<int:id>")
def clases_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM clase WHERE id_clase=%s", (id,))
    mysql.connection.commit()
    return redirect("/clases")

# ==============================
# Ejecutar la app
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
