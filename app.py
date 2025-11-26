from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "miClaveSegura"


# CONFIGURACIÓN PARA MYSQL

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "gimnasio"

mysql = MySQL(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "gimnasio_app"  # Usuario específico
app.config["MYSQL_PASSWORD"] = "clave_segura_123"
app.config["MYSQL_DB"] = "gimnasio"

# LOGIN 

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        nom_usuario = request.form["usuario"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT id, username, password_hash, nombre, activo, rol FROM usuarios WHERE username = %s"
        cursor.execute(sql, (nom_usuario,))
        usuario = cursor.fetchone()
        cursor.close()

        if not usuario or not usuario["activo"]:
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for("login"))

        if not check_password_hash(usuario["password_hash"], password):
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for("login"))

        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        session['rol'] = usuario['rol']

        flash(f'Bienvenido {usuario["nombre"]}', 'success')
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for("login"))


# Página principal

@app.route("/")
@login_required
def index():
    return render_template("index.html")


# FUNCION GLOBAL: VERIFICAR VIGENCIA

def membresia_vigente(id_socio):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT fecha_fin 
        FROM pago
        WHERE id_socio = %s
        ORDER BY fecha_fin DESC
        LIMIT 1
    """, (id_socio,))
    pago = cursor.fetchone()

    if not pago:
        return False 

    return date.today() <= pago["fecha_fin"]

# SOCIOS (CRUD - COMPLETO)

@app.route("/socios")
@login_required
def socios_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM socio")
    socios = cursor.fetchall()
    return render_template("socios/lista.html", socios=socios)


@app.route("/socios/agregar", methods=["GET", "POST"])
@login_required
def socios_agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"]

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO socio (nombre, apellido, email, telefono)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido, email, telefono))
        mysql.connection.commit()

        flash('Socio agregado correctamente', 'success')
        return redirect(url_for("socios_lista"))

    return render_template("socios/agregar.html")


@app.route("/socios/editar/<int:id>", methods=["GET", "POST"])
@login_required
def socios_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        telefono = request.form["telefono"]

        cursor.execute("""
            UPDATE socio
            SET nombre=%s, apellido=%s, email=%s, telefono=%s
            WHERE id_socio=%s
        """, (nombre, apellido, email, telefono, id))
        mysql.connection.commit()

        flash('Socio actualizado correctamente', 'success')
        return redirect(url_for("socios_lista"))

    cursor.execute("SELECT * FROM socio WHERE id_socio=%s", (id,))
    socio = cursor.fetchone()

    return render_template("socios/editar.html", socio=socio)


@app.route("/socios/eliminar/<int:id>")
@login_required
def socios_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM socio WHERE id_socio=%s", (id,))
    mysql.connection.commit()
    flash('Socio eliminado correctamente', 'success')
    return redirect(url_for("socios_lista"))


# PLANES (CRUD COMPLETO)

@app.route("/planes")
@login_required
def planes_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM planmembresia")
    planes = cursor.fetchall()
    return render_template("planes/lista.html", planes=planes)


@app.route("/planes/agregar", methods=["GET", "POST"])
@login_required
def planes_agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        duracion_dias = request.form["duracion_dias"]

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO planmembresia (nombre_plan, precio, duracion_dias)
            VALUES (%s, %s, %s)
        """, (nombre, precio, duracion_dias))
        mysql.connection.commit()

        flash('Plan agregado correctamente', 'success')
        return redirect(url_for("planes_lista"))

    return render_template("planes/agregar.html")


@app.route("/planes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def planes_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        duracion_dias = request.form["duracion_dias"]

        cursor.execute("""
            UPDATE planmembresia
            SET nombre_plan=%s, precio=%s, duracion_dias=%s
            WHERE id_plan=%s
        """, (nombre, precio, duracion_dias, id))
        mysql.connection.commit()

        flash('Plan actualizado correctamente', 'success')
        return redirect(url_for("planes_lista"))

    cursor.execute("SELECT * FROM planmembresia WHERE id_plan=%s", (id,))
    plan = cursor.fetchone()

    return render_template("planes/editar.html", plan=plan)


@app.route("/planes/eliminar/<int:id>")
@login_required
def planes_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM planmembresia WHERE id_plan=%s", (id,))
    mysql.connection.commit()
    flash('Plan eliminado correctamente', 'success')
    return redirect(url_for("planes_lista"))

# PAGOS (CRUD)

@app.route("/pagos")
@login_required
def pagos_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT 
            p.id_pago,
            p.id_socio,
            s.nombre,
            s.apellido,
            pl.nombre_plan,
            p.fecha_inicio,
            p.fecha_fin,
            p.monto
        FROM pago p
        JOIN socio s ON p.id_socio = s.id_socio
        JOIN planmembresia pl ON p.id_plan = pl.id_plan
    """)

    pagos = cursor.fetchall()
    return render_template("pagos/lista.html", pagos=pagos)



@app.route("/pagos/agregar", methods=["GET", "POST"])
@login_required
def pagos_agregar():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT id_socio, nombre, apellido FROM socio")
    socios = cursor.fetchall()

    cursor.execute("SELECT id_plan, nombre_plan, duracion_dias, precio FROM planmembresia")
    planes = cursor.fetchall()

    if request.method == "POST":
        id_socio = request.form["id_socio"]
        id_plan = request.form["id_plan"]
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]
        monto = request.form["monto"]

        cursor.execute("""
            INSERT INTO pago (id_socio, id_plan, fecha_inicio, fecha_fin, monto)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_socio, id_plan, fecha_inicio, fecha_fin, monto))

        mysql.connection.commit()
        flash('Pago registrado correctamente', 'success')
        return redirect(url_for("pagos_lista"))

    return render_template("pagos/agregar.html", socios=socios, planes=planes)


@app.route("/pagos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def pagos_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        id_socio = request.form["id_socio"]
        id_plan = request.form["id_plan"]
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]
        monto = request.form["monto"]

        cursor.execute("""
            UPDATE pago
            SET id_socio=%s, id_plan=%s, fecha_inicio=%s, fecha_fin=%s, monto=%s
            WHERE id_pago=%s
        """, (id_socio, id_plan, fecha_inicio, fecha_fin, monto, id))

        mysql.connection.commit()
        flash('Pago actualizado correctamente', 'success')
        return redirect(url_for("pagos_lista"))

    cursor.execute("SELECT * FROM pago WHERE id_pago=%s", (id,))
    pago = cursor.fetchone()

    cursor.execute("SELECT * FROM socio")
    socios = cursor.fetchall()

    cursor.execute("SELECT * FROM planmembresia")
    planes = cursor.fetchall()

    return render_template("pagos/editar.html", pago=pago, socios=socios, planes=planes)


@app.route("/pagos/eliminar/<int:id>")
@login_required
def pagos_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pago WHERE id_pago=%s", (id,))
    mysql.connection.commit()
    flash('Pago eliminado correctamente', 'success')
    return redirect(url_for("pagos_lista"))


# CLASES (CRUD)

@app.route("/clases")
@login_required
def clases_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM clase")
    clases = cursor.fetchall()
    return render_template("clases/lista.html", clases=clases)


@app.route("/clases/agregar", methods=["GET", "POST"])
@login_required
def clases_agregar():
    if request.method == "POST":
        nombre = request.form["nombre_clase"]
        descripcion = request.form["descripcion"]
        cupo = request.form["cupo"]

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO clase (nombre_clase, descripcion, cupo)
            VALUES (%s, %s, %s)
        """, (nombre, descripcion, cupo))

        mysql.connection.commit()
        flash('Clase agregada correctamente', 'success')
        return redirect(url_for("clases_lista"))

    return render_template("clases/agregar.html")


@app.route("/clases/editar/<int:id>", methods=["GET", "POST"])
@login_required
def clases_editar(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        nombre = request.form["nombre_clase"]
        descripcion = request.form["descripcion"]
        cupo = request.form["cupo"]

        cursor.execute("""
            UPDATE clase
            SET nombre_clase=%s, descripcion=%s, cupo=%s
            WHERE id_clase=%s
        """, (nombre, descripcion, cupo, id))

        mysql.connection.commit()
        flash('Clase actualizada correctamente', 'success')
        return redirect(url_for("clases_lista"))

    cursor.execute("SELECT * FROM clase WHERE id_clase=%s", (id,))
    clase = cursor.fetchone()

    return render_template("clases/editar.html", clase=clase)


@app.route("/clases/eliminar/<int:id>")
@login_required
def clases_eliminar(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM clase WHERE id_clase=%s", (id,))
    mysql.connection.commit()
    flash('Clase eliminada correctamente', 'success')
    return redirect(url_for("clases_lista"))


# RENOVAR MEMBRESÍA DEL GIMNASIO

@app.route('/renovar_membresia', methods=['GET', 'POST'])
@login_required
def renovar_membresia():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Obtener SOCIOS
    cursor.execute("SELECT id_socio, nombre, apellido, email FROM socio")
    socios = cursor.fetchall()

    # Obtener PLANES DE MEMBRESÍA
    cursor.execute("SELECT * FROM planmembresia")
    planes = cursor.fetchall()

    if request.method == 'POST':
        # Obtenemos datos del formulario
        id_socio = request.form['id_socio']
        id_plan = request.form['id_plan']

        # Validar si exiaste el socio
        cursor.execute("SELECT * FROM socio WHERE id_socio = %s", (id_socio,))
        socio = cursor.fetchone()
        
        if not socio:
            flash('El socio seleccionado no existe', 'error')
            return render_template('renovar_membresia.html', socios=socios, planes=planes)

        # Obtener información del plan
        cursor.execute("SELECT duracion_dias, precio, nombre_plan FROM planmembresia WHERE id_plan = %s", (id_plan,))
        plan = cursor.fetchone()

        if not plan:
            flash('El plan seleccionado no existe', 'error')
            return render_template('renovar_membresia.html', socios=socios, planes=planes)

        # Calcular fechas
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=plan['duracion_dias'])

        try:
            # Insertar el pago O renovación
            cursor.execute("""
                INSERT INTO pago (id_socio, id_plan, fecha_inicio, fecha_fin, monto)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_socio, id_plan, fecha_inicio, fecha_fin, plan['precio']))

            mysql.connection.commit()
            flash(f'Membresía renovada exitosamente para {socio["nombre"]} {socio["apellido"]}. Plan: {plan["nombre_plan"]}', 'success')
            return redirect(url_for('pagos_lista'))

        except Exception as e:
            mysql.connection.rollback()
            flash('Error al renovar la membresía: ' + str(e), 'error')
            return render_template('renovar_membresia.html', socios=socios, planes=planes)

    return render_template('renovar_membresia.html', socios=socios, planes=planes)


# RESERVA DE CLASES 

@app.route('/reservar_clase', methods=['GET', 'POST'])
@login_required
def reservar_clase():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Obtener SOCIOS
    cursor.execute("SELECT id_socio, nombre, apellido FROM socio")
    socios = cursor.fetchall()

    # Obtener CLASES QUE EXISTEN
    cursor.execute("SELECT id_clase, nombre_clase, descripcion, cupo FROM clase")
    clases = cursor.fetchall()

    if request.method == 'POST':
        id_socio = request.form['id_socio']
        id_clase = request.form['id_clase']

        try:
            fecha_actual = date.today()
            cursor.execute("""
                INSERT INTO reservaclase (id_socio, id_clase, fecha_reserva)
                VALUES (%s, %s, %s)
            """, (id_socio, id_clase, fecha_actual))

            mysql.connection.commit()
            flash('¡Clase reservada correctamente!', 'success')
            return redirect(url_for('reservas_lista'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al reservar la clase: {str(e)}', 'error')

    return render_template('reservar_clase.html', socios=socios, clases=clases)

@app.route('/reservas')
@login_required
def reservas_lista():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT r.id_reserva, s.nombre, s.apellido, c.nombre_clase, r.fecha_reserva
        FROM reservaclase r
        JOIN socio s ON r.id_socio = s.id_socio
        JOIN clase c ON r.id_clase = c.id_clase
    """)
    reservas = cursor.fetchall()

    return render_template('reservas_lista.html', reservas=reservas)


# CONTROL DE ACCESO POR VIGENCIA

@app.route("/acceso/<int:id_socio>")
@login_required
def acceso(id_socio):
    if not membresia_vigente(id_socio):
        return render_template("acceso_denegado.html")
    return render_template("acceso_ok.html")


# Ejecutar la app

if __name__ == "__main__":
    app.run(debug=True)