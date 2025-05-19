import sqlite3
import tkinter as tk
#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
import bcrypt
import re
#---------------------------------------------------------------------------------------------------------------------------------------------------
from tkinter import messagebox
from ttkbootstrap import Style, ttk

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
userlogin = None

def es_rfc_valido(rfc):
    return re.match(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", rfc, re.IGNORECASE)

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
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def agregar_historial(id_client, descripcion, fecha):
    if not es_entero(id_client):
        messagebox.showerror("Error", "El ID del cliente debe ser un número entero.")
        return

    if not es_fecha_valida(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
        return

    descripcion = entrada_segura(descripcion)

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO Historial (description, date) VALUES (?, ?)", (descripcion, fecha))
    id_historial = cursor.lastrowid
    cursor.execute("INSERT INTO CRyH (id_client, id_historial) VALUES (?, ?)", (int(id_client), id_historial))
    conexion.commit()
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_agregar_historial():
    ventana = tk.Toplevel()
    ventana.title("Agregar Historial")
    ventana.geometry("400x300")
    
    tk.Label(ventana, text="ID Cliente:").pack()
    entry_id_client = tk.Entry(ventana)
    entry_id_client.pack()
    
    tk.Label(ventana, text="Descripción:").pack()
    entry_descripcion = tk.Entry(ventana)
    entry_descripcion.pack()
    
    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").pack()
    entry_fecha = tk.Entry(ventana)
    entry_fecha.pack()
    
    def guardar():
        agregar_historial(entry_id_client.get(), entry_descripcion.get(), entry_fecha.get())
        messagebox.showinfo("Éxito", "Historial agregado correctamente")
        ventana.destroy()
    
    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_historial():
    ventana = tk.Toplevel()
    ventana.title("Historiales de Clientes")
    ventana.geometry("700x400")

    tree = ttk.Treeview(ventana, columns=("ID Cliente", "ID Historial", "Descripción", "Fecha"), show="headings")
    
    tree.heading("ID Cliente", text="ID Cliente")
    tree.heading("ID Historial", text="ID Historial")
    tree.heading("Descripción", text="Descripción")
    tree.heading("Fecha", text="Fecha")

    for col in ("ID Cliente", "ID Historial", "Descripción", "Fecha"):
        tree.column(col, width=150)

    tree.pack(expand=True, fill='both')

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyH.id_client, Historial.id_historial, Historial.description, Historial.date
        FROM Historial
        JOIN CRyH ON Historial.id_historial = CRyH.id_historial
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def programar_cita(id_client, fecha, hora, descripcion):
    if not es_entero(id_client) or not es_fecha_valida(fecha) or not es_hora_valida(hora):
        messagebox.showerror("Error", "Datos inválidos.")
        return

    descripcion = entrada_segura(descripcion)

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO DateManager (date, hour, description) VALUES (?, ?, ?)", (fecha, hora, descripcion))
    id_datemanager = cursor.lastrowid
    cursor.execute("INSERT INTO CRyDM (id_client, id_datemanager) VALUES (?, ?)", (int(id_client), id_datemanager))
    conexion.commit()
    conexion.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_programar_cita():
    ventana = tk.Toplevel()
    ventana.title("Programar Cita")
    ventana.geometry("400x300")
    
    tk.Label(ventana, text="ID Cliente:").pack()
    entry_id_client = tk.Entry(ventana)
    entry_id_client.pack()
    
    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").pack()
    entry_fecha = tk.Entry(ventana)
    entry_fecha.pack()
    
    tk.Label(ventana, text="Hora (HH:MM):").pack()
    entry_hora = tk.Entry(ventana)
    entry_hora.pack()
    
    tk.Label(ventana, text="Descripción:").pack()
    entry_descripcion = tk.Entry(ventana)
    entry_descripcion.pack()
    
    def guardar():
        programar_cita(entry_id_client.get(), entry_fecha.get(), entry_hora.get(), entry_descripcion.get())
        messagebox.showinfo("Éxito", "Cita programada correctamente")
        ventana.destroy()
    
    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_citas():
    ventana = tk.Toplevel()
    ventana.title("Citas Programadas")
    ventana.geometry("700x400")

    tree = ttk.Treeview(ventana, columns=("ID Cliente", "ID Cita", "Fecha", "Hora", "Descripción"), show="headings")

    tree.heading("ID Cliente", text="ID Cliente")
    tree.heading("ID Cita", text="ID Cita")
    tree.heading("Fecha", text="Fecha")
    tree.heading("Hora", text="Hora")
    tree.heading("Descripción", text="Descripción")

    for col in ("ID Cliente", "ID Cita", "Fecha", "Hora", "Descripción"):
        tree.column(col, width=120)

    tree.pack(expand=True, fill='both')

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyDM.id_client, DateManager.id_datemanager, DateManager.date, DateManager.hour, DateManager.description
        FROM DateManager
        JOIN CRyDM ON DateManager.id_datemanager = CRyDM.id_datemanager
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def agregar_estado_financiero(id_client, balance, income, expenses, fecha):
    if not es_entero(id_client):
        messagebox.showerror("Error", "ID de cliente inválido.")
        return

    if not es_float(balance) or not es_float(income) or not es_float(expenses):
        messagebox.showerror("Error", "Balance, ingresos y egresos deben ser números.")
        return

    if not es_fecha_valida(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
        return

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO FinancialStatus (id_client, balance, income, expenses, date) VALUES (?, ?, ?, ?, ?)",
                   (int(id_client), float(balance), float(income), float(expenses), fecha))
    id_financialstatus = cursor.lastrowid
    cursor.execute("INSERT INTO CRyFS (id_client, id_financialstatus) VALUES (?, ?)", (int(id_client), id_financialstatus))
    conexion.commit()
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_gestion_financiera():
    ventana = tk.Toplevel()
    ventana.title("Gestión Financiera")
    ventana.geometry("500x400")

    tk.Label(ventana, text="ID Cliente:").pack()
    entry_cliente_id = tk.Entry(ventana)
    entry_cliente_id.pack()

    tk.Label(ventana, text="Balance:").pack()
    entry_balance = tk.Entry(ventana)
    entry_balance.pack()

    tk.Label(ventana, text="Ingresos:").pack()
    entry_ingresos = tk.Entry(ventana)
    entry_ingresos.pack()

    tk.Label(ventana, text="Egresos:").pack()
    entry_egresos = tk.Entry(ventana)
    entry_egresos.pack()

    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").pack()
    entry_fecha = tk.Entry(ventana)
    entry_fecha.pack()

    def guardar():
        agregar_estado_financiero(entry_cliente_id.get(), entry_balance.get(), entry_ingresos.get(),
                                  entry_egresos.get(), entry_fecha.get())
        messagebox.showinfo("Éxito", "Estado financiero agregado correctamente")
        ventana.destroy()

    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_estados_financieros():
    ventana = tk.Toplevel()
    ventana.title("Estados Financieros")
    ventana.geometry("800x400")

    columnas = ("ID Cliente", "ID Estado", "Balance", "Ingresos", "Egresos", "Fecha")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(expand=True, fill='both')

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyFS.id_client, FinancialStatus.id_financialstatus, FinancialStatus.balance, 
               FinancialStatus.income, FinancialStatus.expenses, FinancialStatus.date
        FROM FinancialStatus
        JOIN CRyFS ON FinancialStatus.id_financialstatus = CRyFS.id_financialstatus
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def agregar_nomina(id_client, employees, total_salary, fecha):
    if not es_entero(id_client) or not es_entero(employees):
        messagebox.showerror("Error", "ID de cliente y número de empleados deben ser enteros.")
        return

    if not es_float(total_salary):
        messagebox.showerror("Error", "El salario total debe ser un número.")
        return

    if not es_fecha_valida(fecha):
        messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
        return

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO Payroll (id_client, employees, total_salary, date) VALUES (?, ?, ?, ?)",
                   (int(id_client), int(employees), float(total_salary), fecha))
    id_payroll = cursor.lastrowid
    cursor.execute("INSERT INTO CRyP (id_client, id_payroll) VALUES (?, ?)", (int(id_client), id_payroll))
    conexion.commit()
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_nomina():
    ventana = tk.Toplevel()
    ventana.title("Agregar Nómina")
    ventana.geometry("400x300")

    tk.Label(ventana, text="ID Cliente:").pack()
    entry_id_client = tk.Entry(ventana)
    entry_id_client.pack()

    tk.Label(ventana, text="Empleados:").pack()
    entry_employees = tk.Entry(ventana)
    entry_employees.pack()

    tk.Label(ventana, text="Salario Total:").pack()
    entry_total_salary = tk.Entry(ventana)
    entry_total_salary.pack()

    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").pack()
    entry_fecha = tk.Entry(ventana)
    entry_fecha.pack()

    def guardar():
        agregar_nomina(entry_id_client.get(), entry_employees.get(), entry_total_salary.get(), entry_fecha.get())
        messagebox.showinfo("Éxito", "Nómina agregada correctamente")
        ventana.destroy()
    
    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_nominas():
    ventana = tk.Toplevel()
    ventana.title("Lista de Nóminas")
    ventana.geometry("700x400")

    columnas = ("ID Cliente", "ID Nómina", "Empleados", "Salario Total", "Fecha")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=130)

    tree.pack(expand=True, fill='both')

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyP.id_client, Payroll.id_payroll, Payroll.employees, Payroll.total_salary, Payroll.date
        FROM Payroll
        JOIN CRyP ON Payroll.id_payroll = CRyP.id_payroll
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def registrar_plan_fiscal(id_client, total_tax, submission_date):
    if not es_entero(id_client):
        messagebox.showerror("Error", "ID de cliente debe ser un número entero.")
        return

    if not es_float(total_tax):
        messagebox.showerror("Error", "El monto de impuestos debe ser numérico.")
        return

    if not es_fecha_valida(submission_date):
        messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
        return

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO TaxPlanning (id_client, total_tax, submission_date) VALUES (?, ?, ?)",
                   (int(id_client), float(total_tax), submission_date))
    id_taxplanning = cursor.lastrowid
    cursor.execute("INSERT INTO CRyTP (id_client, id_taxplanning) VALUES (?, ?)", (int(id_client), id_taxplanning))
    conexion.commit()
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_plan_fiscal():
    ventana = tk.Toplevel()
    ventana.title("Registrar Plan Fiscal")
    ventana.geometry("400x250")

    tk.Label(ventana, text="ID Cliente:").pack()
    entry_id_client = tk.Entry(ventana)
    entry_id_client.pack()

    tk.Label(ventana, text="Impuesto Total:").pack()
    entry_total_tax = tk.Entry(ventana)
    entry_total_tax.pack()

    tk.Label(ventana, text="Fecha de Presentación (YYYY-MM-DD):").pack()
    entry_submission_date = tk.Entry(ventana)
    entry_submission_date.pack()

    def guardar():
        registrar_plan_fiscal(entry_id_client.get(), entry_total_tax.get(), entry_submission_date.get())
        messagebox.showinfo("Éxito", "Plan fiscal registrado correctamente")
        ventana.destroy()
    
    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_plan_fiscal():
    ventana = tk.Toplevel()
    ventana.title("Lista de Planes Fiscales")
    ventana.geometry("700x400")

    columnas = ("ID Cliente", "ID Plan Fiscal", "Impuesto Total", "Fecha de Presentación")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(expand=True, fill='both')

    # Conexión y consulta a la base de datos
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyTP.id_client, TaxPlanning.id_taxplanning, TaxPlanning.total_tax, TaxPlanning.submission_date
        FROM TaxPlanning
        JOIN CRyTP ON TaxPlanning.id_taxplanning = CRyTP.id_taxplanning
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()

#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def registrar_auditoria(id_client, audit_type, result, date):
    if not es_entero(id_client):
        messagebox.showerror("Error", "ID de cliente inválido.")
        return

    if not es_fecha_valida(date):
        messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
        return

    audit_type = entrada_segura(audit_type)
    result = entrada_segura(result)

    if not audit_type or not result:
        messagebox.showwarning("Advertencia", "Tipo de auditoría y resultado no deben estar vacíos.")
        return

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO Audit (id_client, audit_type, result, date) VALUES (?, ?, ?, ?)",
                   (int(id_client), audit_type, result, date))
    id_audit = cursor.lastrowid
    cursor.execute("INSERT INTO CRyA (id_client, id_audit) VALUES (?, ?)", (int(id_client), id_audit))
    conexion.commit()
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_auditoria():
    ventana = tk.Toplevel()
    ventana.title("Registrar Auditoría")
    ventana.geometry("400x300")

    tk.Label(ventana, text="ID Cliente:").pack()
    entry_id_client = tk.Entry(ventana)
    entry_id_client.pack()

    tk.Label(ventana, text="Tipo de Auditoría:").pack()
    entry_audit_type = tk.Entry(ventana)
    entry_audit_type.pack()

    tk.Label(ventana, text="Resultado:").pack()
    entry_result = tk.Entry(ventana)
    entry_result.pack()

    tk.Label(ventana, text="Fecha (YYYY-MM-DD):").pack()
    entry_date = tk.Entry(ventana)
    entry_date.pack()

    def guardar():
        registrar_auditoria(entry_id_client.get(), entry_audit_type.get(), entry_result.get(), entry_date.get())
        messagebox.showinfo("Éxito", "Auditoría registrada correctamente")
        ventana.destroy()
    
    ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    ventana.mainloop()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_auditorias():
    ventana = tk.Toplevel()
    ventana.title("Lista de Auditorías")
    ventana.geometry("700x400")

    columnas = ("ID Cliente", "ID Auditoría", "Tipo de Auditoría", "Resultado", "Fecha")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=130)

    tree.pack(expand=True, fill='both')

    # Conexión a la base de datos y consulta
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT CRyA.id_client, Audit.id_audit, Audit.audit_type, Audit.result, Audit.date
        FROM Audit
        JOIN CRyA ON Audit.id_audit = CRyA.id_audit
    """)
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def verificar_credenciales():
    global userlogin

    usuario = entrada_segura(entry_usuario.get())
    contrasena = entry_contrasena.get()

    if not usuario or not contrasena:
        messagebox.showwarning("Campos vacíos", "Por favor, ingresa usuario y contraseña.")
        return

    if not usuario_valido(usuario):
        messagebox.showerror("Usuario inválido", "El nombre de usuario es inválido.")
        return

    try:
        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT Password FROM Users WHERE Username = ?", (usuario,))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado and bcrypt.checkpw(contrasena.encode('utf-8'), resultado[0]):
            userlogin = usuario
            messagebox.showinfo("Éxito", "Acceso concedido")
            ventana_inicio.destroy()
            abrir_menu_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    except Exception as e:
        messagebox.showerror("Error de conexión", f"Ocurrió un error: {e}")
#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------

def abrir_menu_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Despacho Contable")
    ventana_principal.geometry("500x400")
    frame_horizontal = tk.Frame(ventana_principal)
    frame_horizontal.pack(pady=20)
    tk.Label(ventana_principal, text="Bienvenido al Despacho Contable").pack(pady=20)
    frame_tabular = tk.Frame(ventana_principal)
    frame_tabular.pack(pady=20)

    tk.Label(frame_horizontal, text="Versión: 2.0").grid(row=0, column=0, padx=10)
    ttk.Button(frame_horizontal, text="Detalles del usuario", command=lambda: mostrar_datos_usuario(userlogin)).grid(row=0, column=1, padx=10)
    ttk.Button(frame_horizontal, text="Cerrar sesión", command=lambda: cerrar_sesion(ventana_principal)).grid(row=0, column=2, padx=10)

    ttk.Button(frame_tabular, text="Gestión financiera", command=abrir_gestion_financiera).grid(row=0, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora financiera", command=mostrar_estados_financieros).grid(row=0, column=1, padx=10)
    ttk.Button(frame_tabular, text="Gestión de clientes", command=abrir_gestion_clientes).grid(row=1, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora de clientes", command=mostrar_clientes).grid(row=1, column=1, padx=10)
    ttk.Button(frame_tabular, text="Registrar una cita", command=abrir_programar_cita).grid(row=2, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora de citas", command=mostrar_citas).grid(row=2, column=1, padx=10)
    ttk.Button(frame_tabular, text="Gestión del Historial", command=abrir_agregar_historial).grid(row=3, column=0, padx=10)
    ttk.Button(frame_tabular, text="Historial de casos atendidos", command=mostrar_historial).grid(row=3, column=1, padx=10)
    ttk.Button(frame_tabular, text="Registrar una nomina", command=abrir_nomina).grid(row=4, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora de nominas", command=mostrar_nominas).grid(row=4, column=1, padx=10)
    ttk.Button(frame_tabular, text="Registrar un plan Fiscal", command=abrir_plan_fiscal).grid(row=5, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora planes Fiscales", command=mostrar_plan_fiscal).grid(row=5, column=1, padx=10)
    ttk.Button(frame_tabular, text="Registrar una auditoria", command=abrir_auditoria).grid(row=6, column=0, padx=10)
    ttk.Button(frame_tabular, text="Bitácora de auditorias", command=mostrar_auditorias).grid(row=6, column=1, padx=10)
    ventana_principal.mainloop()
    

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------
def abrir_gestion_clientes():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Clientes")
    ventana.geometry("400x400")

    campos = [("Nombre", ""), ("RFC", ""), ("Teléfono", ""), ("Email", ""), ("Dirección", "")]
    entradas = {}

    for texto, _ in campos:
        tk.Label(ventana, text=texto).pack()
        entrada = tk.Entry(ventana)
        entrada.pack()
        entradas[texto] = entrada

    def registrar_cliente():
        nombre = entrada_segura(entradas["Nombre"].get())
        rfc = entrada_segura(entradas["RFC"].get())
        telefono = entradas["Teléfono"].get().strip()
        email = entrada_segura(entradas["Email"].get())
        direccion = entrada_segura(entradas["Dirección"].get())

        # Validaciones
        if not all([nombre, rfc, telefono, email, direccion]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not es_rfc_valido(rfc):
            messagebox.showerror("Error", "El RFC no tiene un formato válido.")
            return

        if not es_email_valido(email):
            messagebox.showerror("Error", "El correo electrónico no es válido.")
            return

        if not es_telefono_valido(telefono):
            messagebox.showerror("Error", "El teléfono debe contener exactamente 10 dígitos.")
            return

        # Guardar en la base de datos
        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO ClientRegister (name, rfc, numberphone, email, address) VALUES (?, ?, ?, ?, ?)",
            (nombre, rfc.upper(), telefono, email, direccion)
        )
        conexion.commit()
        conexion.close()
        messagebox.showinfo("Éxito", "Cliente registrado correctamente")
        ventana.destroy()

    ttk.Button(ventana, text="Registrar Cliente", command=registrar_cliente).pack(pady=10)
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def registrar_nuevo_usuario():
    ventana = tk.Toplevel()
    ventana.title("Registro de Usuario")
    ventana.geometry("300x250")

    tk.Label(ventana, text="Nuevo Usuario").pack(pady=10)

    tk.Label(ventana, text="Nombre de usuario:").pack()
    entry_user = tk.Entry(ventana)
    entry_user.pack()

    tk.Label(ventana, text="Contraseña:").pack()
    entry_pass = tk.Entry(ventana, show="*")
    entry_pass.pack()

    tk.Label(ventana, text="Confirmar contraseña:").pack()
    entry_confirm = tk.Entry(ventana, show="*")
    entry_confirm.pack()

    def guardar_usuario():
        usuario = entrada_segura(entry_user.get())
        password = entry_pass.get()
        confirm = entry_confirm.get()

        if not usuario or not password or not confirm:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return

        if not usuario_valido(usuario):
            messagebox.showerror("Usuario inválido", "El nombre de usuario debe tener entre 3 y 20 caracteres y solo usar letras, números o guiones bajos.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        if not contrasena_segura(password):
            messagebox.showerror("Contraseña insegura", "La contraseña debe tener al menos 8 caracteres, una letra y un número.")
            return

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conexion = sqlite3.connect('database.db')
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", (usuario, hashed))
            conexion.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            ventana.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")
        finally:
            conexion.close()

    ttk.Button(ventana, text="Registrar", command=guardar_usuario).pack(pady=10)
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Modificado
#---------------------------------------------------------------------------------------------------------------------------------------------------

def mostrar_clientes():
    ventana = tk.Toplevel()
    ventana.title("Lista de Clientes")
    ventana.geometry("600x400")

    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Teléfono", "Email", "Dirección"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(expand=True, fill='both')

    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM ClientRegister")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conexion.close()
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_datos_usuario(usuario):
    conexion = sqlite3.connect('database.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id, username, password FROM Users WHERE Username = ?", (usuario,))
    datos = cursor.fetchone()
    conexion.close()

    if datos:
        ventana_datos = tk.Toplevel()
        ventana_datos.title("Datos del Usuario")
        ventana_datos.geometry("500x150")

        tk.Label(ventana_datos, text="Datos del Usuario", font=('Arial', 14, 'bold')).pack(pady=10)
        tk.Label(ventana_datos, text=f"ID: {datos[0]}").pack()
        tk.Label(ventana_datos, text=f"Usuario: {datos[1]}").pack()
        tk.Label(ventana_datos, text=f"Contraseña: {datos[2]}").pack()

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------
def cerrar_sesion(ventana_actual):
    global userlogin
    respuesta = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que deseas cerrar sesión?")
    if respuesta:
        userlogin = None
        ventana_actual.destroy()
        iniciar_aplicacion()
#---------------------------------------------------------------------------------------------------------------------------------------------------

#Nuevo
#---------------------------------------------------------------------------------------------------------------------------------------------------

def iniciar_aplicacion():
    global entry_usuario, entry_contrasena, ventana_inicio

    ventana_inicio = tk.Tk()
    ventana_inicio.title("Inicio de sesión")
    ventana_inicio.geometry("300x270")

    tk.Label(ventana_inicio, text="Usuario:").pack(pady=5)
    entry_usuario = tk.Entry(ventana_inicio)
    entry_usuario.pack()

    tk.Label(ventana_inicio, text="Contraseña:").pack(pady=5)
    entry_contrasena = tk.Entry(ventana_inicio, show='*')
    entry_contrasena.pack()

    ttk.Button(ventana_inicio, text="Iniciar Sesión", command=verificar_credenciales).pack(pady=10)
    ttk.Button(ventana_inicio, text="Registrarse", command=registrar_nuevo_usuario).pack(pady=10)
    tk.Label(ventana_inicio, text="Despacho Contable Versión: 2.0").pack(pady=10)

    ventana_inicio.mainloop()

#---------------------------------------------------------------------------------------------------------------------------------------------------

iniciar_aplicacion()