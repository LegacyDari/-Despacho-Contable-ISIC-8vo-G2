from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re
import bcrypt

userlogin = None

app = Flask(__name__)
app.secret_key = 'clave_super_secreta'

def es_rfc_valido(rfc):
    return re.match(r"^[A-Z\u00D1&]{3,4}\d{6}[A-Z0-9]{3}$", rfc, re.IGNORECASE)

def es_email_valido(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email)

def es_telefono_valido(telefono):
    return re.match(r"^\d{10}$", telefono)

def es_entero(valor):
    return valor.isdigit()

def es_float(valor):
    try:
        float(valor)
        return True
    except ValueError:
        return False

def es_fecha_valida(fecha):
    return re.match(r"^\d{4}-\d{2}-\d{2}$", fecha)

def es_hora_valida(hora):
    return re.match(r"^\d{2}:\d{2}$", hora)

def entrada_segura(texto):
    return re.sub(r"[<>\"';]", "", texto.strip())

def usuario_valido(username):
    return re.match(r"^\w{3,20}$", username)

def contrasena_segura(password):
    return re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@#$%^&+=]{8,}$", password)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registrar_nuevo_usuario():
    if request.method == 'POST':
        usuario = entrada_segura(request.form['usuario'])
        password = request.form['password']
        confirm = request.form['confirm']

        if not usuario or not password or not confirm:
            flash('Por favor, completa todos los campos.', 'warning')
            return redirect(url_for('registrar_nuevo_usuario'))

        if not usuario_valido(usuario):
            flash('El nombre de usuario debe tener entre 3 y 20 caracteres y solo usar letras, números o guiones bajos.', 'danger')
            return redirect(url_for('registrar_nuevo_usuario'))

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('registrar_nuevo_usuario'))

        if not contrasena_segura(password):
            flash('La contraseña debe tener al menos 8 caracteres, una letra y un número.', 'danger')
            return redirect(url_for('registrar_nuevo_usuario'))

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            conexion = sqlite3.connect('database.db')
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", (usuario, hashed))
            conexion.commit()
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('registrar_nuevo_usuario'))
        finally:
            conexion.close()

    return render_template('registro.html')

@app.route('/registrar-historial', methods=['GET', 'POST'])
def registrar_historial():
    if request.method == 'POST':
        id_cliente = request.form['id_cliente']
        descripcion = request.form['descripcion']
        fecha = request.form['fecha']

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        
        cursor.execute("INSERT INTO Historial (description, date) VALUES (?, ?)", (descripcion, fecha))
        id_historial = cursor.lastrowid
        cursor.execute("INSERT INTO CRyH (id_client, id_historial) VALUES (?, ?)", (id_cliente, id_historial))
        
        conexion.commit()
        conexion.close()
        flash('Historial agregado correctamente')
        return redirect(url_for('mostrar_historial'))

    return render_template('registrar_historial.html')

@app.route('/historial', methods=['GET', 'POST'])
def mostrar_historial():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyH.id_client, Historial.id_historial, Historial.description, Historial.date
        FROM Historial
        JOIN CRyH ON Historial.id_historial = CRyH.id_historial
    """)
    historiales = cursor.fetchall()
    conexion.close()
    return render_template('historial.html', historiales=historiales)


@app.route("/registrar_cita", methods=["GET", "POST"])
def registrar_cita():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        descripcion = request.form.get("descripcion")

        if not (es_entero(id_client) and es_fecha_valida(fecha) and es_hora_valida(hora)):
            flash("Datos inválidos. Verifica que el ID sea numérico, la fecha en formato YYYY-MM-DD y la hora en HH:MM.", "error")
            return redirect(url_for("registrar_cita"))

        descripcion = entrada_segura(descripcion)

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO DateManager (date, hour, description) VALUES (?, ?, ?)", (fecha, hora, descripcion))
        id_datemanager = cursor.lastrowid
        cursor.execute("INSERT INTO CRyDM (id_client, id_datemanager) VALUES (?, ?)", (int(id_client), id_datemanager))
        conexion.commit()
        conexion.close()

        flash("Cita programada correctamente.", "success")
        return redirect(url_for("mostrar_citas"))

    return render_template("registrar_cita.html")

@app.route("/citas", methods=['GET', 'POST'])
def mostrar_citas():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyDM.id_client, DateManager.id_datemanager, DateManager.date, DateManager.hour, DateManager.description
        FROM DateManager
        JOIN CRyDM ON DateManager.id_datemanager = CRyDM.id_datemanager
    """)
    citas = cursor.fetchall()
    conexion.close()
    return render_template("citas.html", citas=citas)

@app.route("/registrar_estado_financiero", methods=["GET", "POST"])
def registrar_estado_financiero():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        balance = request.form.get("balance")
        income = request.form.get("income")
        expenses = request.form.get("expenses")
        fecha = request.form.get("fecha")

        if not es_entero(id_client):
            flash("ID de cliente inválido.", "error")
            return redirect(url_for("registrar_estado_financiero"))

        if not (es_float(balance) and es_float(income) and es_float(expenses)):
            flash("Balance, ingresos y egresos deben ser números.", "error")
            return redirect(url_for("registrar_estado_financiero"))

        if not es_fecha_valida(fecha):
            flash("La fecha debe tener el formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_estado_financiero"))

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO FinancialStatus (id_client, balance, income, expenses, date) 
                          VALUES (?, ?, ?, ?, ?)""",
                       (int(id_client), float(balance), float(income), float(expenses), fecha))
        id_financialstatus = cursor.lastrowid
        cursor.execute("INSERT INTO CRyFS (id_client, id_financialstatus) VALUES (?, ?)",
                       (int(id_client), id_financialstatus))
        conexion.commit()
        conexion.close()

        flash("Estado financiero agregado correctamente.", "success")
        return redirect(url_for("mostrar_estados_financieros"))

    return render_template("registrar_estado_financiero.html")

@app.route("/estados_financieros", methods=['GET', 'POST'])
def mostrar_estados_financieros():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyFS.id_client, FinancialStatus.id_financialstatus, FinancialStatus.balance, 
               FinancialStatus.income, FinancialStatus.expenses, FinancialStatus.date
        FROM FinancialStatus
        JOIN CRyFS ON FinancialStatus.id_financialstatus = CRyFS.id_financialstatus
    """)
    estados = cursor.fetchall()
    conexion.close()
    return render_template("estados_financieros.html", estados=estados)

@app.route("/registrar_nomina", methods=["GET", "POST"])
def registrar_nomina():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        employees = request.form.get("employees")
        total_salary = request.form.get("total_salary")
        fecha = request.form.get("fecha")

        if not (es_entero(id_client) and es_entero(employees)):
            flash("ID de cliente y número de empleados deben ser enteros.", "error")
            return redirect(url_for("registrar_nomina"))

        if not es_float(total_salary):
            flash("El salario total debe ser un número.", "error")
            return redirect(url_for("registrar_nomina"))

        if not es_fecha_valida(fecha):
            flash("La fecha debe tener el formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_nomina"))

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO Payroll (id_client, employees, total_salary, date)
                          VALUES (?, ?, ?, ?)""",
                       (int(id_client), int(employees), float(total_salary), fecha))
        id_payroll = cursor.lastrowid
        cursor.execute("INSERT INTO CRyP (id_client, id_payroll) VALUES (?, ?)", (int(id_client), id_payroll))
        conexion.commit()
        conexion.close()

        flash("Nómina agregada correctamente.", "success")
        return redirect(url_for("mostrar_nominas"))

    return render_template("registrar_nomina.html")

@app.route("/nominas", methods=['GET', 'POST'])
def mostrar_nominas():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyP.id_client, Payroll.id_payroll, Payroll.employees, Payroll.total_salary, Payroll.date
        FROM Payroll
        JOIN CRyP ON Payroll.id_payroll = CRyP.id_payroll
    """)
    nominas = cursor.fetchall()
    conexion.close()
    return render_template("nominas.html", nominas=nominas)

@app.route("/registrar_plan_fiscal", methods=["GET", "POST"])
def registrar_plan_fiscal():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        total_tax = request.form.get("total_tax")
        submission_date = request.form.get("submission_date")

        if not es_entero(id_client):
            flash("ID de cliente debe ser un número entero.", "error")
            return redirect(url_for("registrar_plan_fiscal"))

        if not es_float(total_tax):
            flash("El monto de impuestos debe ser numérico.", "error")
            return redirect(url_for("registrar_plan_fiscal"))

        if not es_fecha_valida(submission_date):
            flash("La fecha debe tener el formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_plan_fiscal"))

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO TaxPlanning (id_client, total_tax, submission_date)
            VALUES (?, ?, ?)""", (int(id_client), float(total_tax), submission_date))
        id_taxplanning = cursor.lastrowid
        cursor.execute("INSERT INTO CRyTP (id_client, id_taxplanning) VALUES (?, ?)",
                       (int(id_client), id_taxplanning))
        conexion.commit()
        conexion.close()

        flash("Plan fiscal registrado correctamente.", "success")
        return redirect(url_for("mostrar_planes_fiscales"))

    return render_template("registrar_plan_fiscal.html")

@app.route("/planes_fiscales", methods=['GET', 'POST'])
def mostrar_planes_fiscales():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyTP.id_client, TaxPlanning.id_taxplanning, TaxPlanning.total_tax, TaxPlanning.submission_date
        FROM TaxPlanning
        JOIN CRyTP ON TaxPlanning.id_taxplanning = CRyTP.id_taxplanning
    """)
    planes = cursor.fetchall()
    conexion.close()
    return render_template("planes_fiscales.html", planes=planes)

@app.route("/registrar_auditoria", methods=["GET", "POST"])
def registrar_auditoria():
    if request.method == "POST":
        id_client = request.form.get("id_client")
        audit_type = entrada_segura(request.form.get("audit_type"))
        result = entrada_segura(request.form.get("result"))
        date = request.form.get("date")

        if not es_entero(id_client):
            flash("ID de cliente inválido.", "error")
            return redirect(url_for("registrar_auditoria"))

        if not es_fecha_valida(date):
            flash("La fecha debe tener el formato YYYY-MM-DD.", "error")
            return redirect(url_for("registrar_auditoria"))

        if not audit_type or not result:
            flash("Tipo de auditoría y resultado no deben estar vacíos.", "warning")
            return redirect(url_for("registrar_auditoria"))

        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Audit (id_client, audit_type, result, date)
            VALUES (?, ?, ?, ?)
        """, (int(id_client), audit_type, result, date))
        id_audit = cursor.lastrowid
        cursor.execute("INSERT INTO CRyA (id_client, id_audit) VALUES (?, ?)",
                       (int(id_client), id_audit))
        conexion.commit()
        conexion.close()

        flash("Auditoría registrada correctamente.", "success")
        return redirect(url_for("mostrar_auditorias"))

    return render_template("registrar_auditoria.html")

@app.route("/auditorias", methods=['GET', 'POST'])
def mostrar_auditorias():
    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyA.id_client, Audit.id_audit, Audit.audit_type, Audit.result, Audit.date
        FROM Audit
        JOIN CRyA ON Audit.id_audit = CRyA.id_audit
    """)
    auditorias = cursor.fetchall()
    conexion.close()
    return render_template("auditorias.html", auditorias=auditorias)

@app.route("/", methods=["GET", "POST"])
def login():
    global userlogin
    if request.method == "POST":
        usuario = entrada_segura(request.form.get("username"))
        contrasena = request.form.get("password")

        if not usuario or not contrasena:
            flash("Por favor, ingresa usuario y contraseña.", "warning")
            return redirect(url_for("login"))

        if not usuario_valido(usuario):
            flash("El nombre de usuario es inválido.", "error")
            return redirect(url_for("login"))

        try:
            conexion = sqlite3.connect("database.db")
            cursor = conexion.cursor()
            cursor.execute("SELECT Password FROM Users WHERE Username = ?", (usuario,))
            resultado = cursor.fetchone()
            conexion.close()

            if resultado and bcrypt.checkpw(contrasena.encode("utf-8"), resultado[0]):
                session["usuario"] = usuario
                userlogin = usuario
                flash("Acceso concedido", "success")
                return redirect(url_for("menu_principal"))
            else:
                flash("Usuario o contraseña incorrectos", "error")
        except Exception as e:
            flash(f"Ocurrió un error: {e}", "error")

    return render_template("login.html")

@app.route("/menu", methods=['GET', 'POST'])
def menu_principal():
    if "usuario" not in session:
        flash("Debes iniciar sesión primero", "error")
        return redirect(url_for("login"))

    usuario = session["usuario"]
    return render_template("menu.html", usuario=usuario)

@app.route('/registrar_cliente', methods=['GET', 'POST'])
def registrar_cliente():
    if request.method == 'POST':
        nombre = entrada_segura(request.form['nombre'])
        rfc = entrada_segura(request.form['rfc'])
        telefono = request.form['telefono'].strip()
        email = entrada_segura(request.form['email'])
        direccion = entrada_segura(request.form['direccion'])

        # Validaciones
        if not all([nombre, rfc, telefono, email, direccion]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('registrar_cliente'))

        if not es_rfc_valido(rfc):
            flash("El RFC no tiene un formato válido.", "error")
            return redirect(url_for('registrar_cliente'))

        if not es_email_valido(email):
            flash("El correo electrónico ingresado no es válido.", "error")
            return redirect(url_for('registrar_cliente'))

        if not es_telefono_valido(telefono):
            flash("El teléfono debe contener exactamente 10 dígitos numéricos.", "error")
            return redirect(url_for('registrar_cliente'))

        try:
            conexion = sqlite3.connect('database.db')
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO ClientRegister (name, rfc, numberphone, email, address) VALUES (?, ?, ?, ?, ?)",
                (nombre, rfc.upper(), telefono, email, direccion)
            )
            conexion.commit()
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for('registrar_cliente'))
        except Exception as e:
            flash(f"Ocurrió un error al registrar: {e}", "error")
        finally:
            conexion.close()

    return render_template('registrar_cliente.html')

@app.route('/clientes', methods=['GET', 'POST'])
def mostrar_clientes():
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ClientRegister")
    clientes = cursor.fetchall()
    conexion.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/perfil/<usuario>', methods=['GET', 'POST'])
def mostrar_datos_usuario(usuario):
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id, username, password FROM Users WHERE Username = ?", (usuario,))
    datos = cursor.fetchone()
    conexion.close()

    if datos:
        return render_template('perfil.html', datos=datos)
    else:
        flash("Usuario no encontrado", "error")
        return redirect(url_for('login'))

@app.route('/cerrar_sesion', methods=['GET', 'POST'])
def cerrar_sesion():
    session.pop('usuario', None)
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)