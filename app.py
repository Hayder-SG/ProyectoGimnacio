from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "miClaveSegura"

# ===========================================================
# CONFIGURACIÓN MYSQL
# ===========================================================
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "gimnasio"

mysql = MySQL(app)


# ============================================================
# Página principal
# ============================================================
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ============================================================
# Ejecutar la app
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
