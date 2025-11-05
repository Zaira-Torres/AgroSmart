import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk  # Para manejar la imagen
import psycopg2
import os  # Importar el módulo os para manejar rutas
import json #para cargar datos desde archivos .JSON
import requests
import io
import random
from datetime import datetime
import re
import joblib
import pandas as pd
import numpy as np
import sklearn
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import psycopg2.extras


class Conexion:
    def __init__(self):  # Cambiado de _init a __init__
        self.conexion = None
        try:
            self.conexion = psycopg2.connect(
                host='localhost',
                port=5432,
                database='COSECHA',
                user='postgres',
                password='admin'
            )
            print('Conexión exitosa')
        except Exception as e:
            print(f'Error al conectar: {e}')
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")

def login():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    try:
        conexion = Conexion().conexion
        if not conexion:
            raise Exception("No se pudo establecer la conexión con la base de datos.")

        cursor = conexion.cursor()
        # Consulta para verificar si el usuario y la contraseña existen en la tabla login
        cursor.execute(
            "SELECT * FROM login WHERE usuario = %s AND contrasena = %s",
            (username, password)
        )
        resultado = cursor.fetchone()  # Obtiene el primer resultado de la consulta

        if resultado:
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
            show_dashboard(username)  # Pasa el nombre del usuario al dashboard
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        cursor.close()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar sesión: {e}")

global_username = "" #variable global para guardar el usuario

def validar_numeros(action, value):
    """Función para validar que solo se ingresen números."""
    if action == '1':  # Acción '1' = insertar texto
        return value.isdigit()  # Retorna True si solo contiene dígitos
    return True 

def validar_fecha(action, value):
    """Valida que la fecha tenga el formato correcto (YYYY-MM-DD)."""
    if action == "1":  # Solo validar cuando se inserta texto
        patron = r"^\d{4}-\d{2}-\d{2}$"  # Expresión regular para YYYY-MM-DD
        return bool(re.match(patron, value))
    return True  # Permitir borrar texto


def show_dashboard(username):
    #se carga el usuario que recibe en la variable global
    global global_username
    global_username = username
    
    login_frame.pack_forget()
    dashboard_frame.pack(expand=True, fill="both")
    
    
    # Mostrar el nombre del usuario en el dashboard
    user_label = tk.Label(
        dashboard_frame,
        text=f"Usuario 👤: {username}",
        font=("Arial", 12, "bold"),
        bg="#2E4053",
        fg="#FFFFFF",
        highlightbackground="#ffffff",  # Color del borde
        highlightthickness=2,  # Grosor del borde
    )
    user_label.place(x=890, y=60)  # Posición encima del botón de "Cerrar Sesión"
    
    crear_widget_clima(dashboard_frame.clima_container)
    
def go_to_prediccion():
    # Ocultar el dashboard y mostrar la pantalla de predicción
    dashboard_frame.pack_forget()  # 'dashboard_frame' debe estar definido en tu código
    prediccion_frame.pack(expand=True, fill="both")  # 'prediccion_frame' debe ser accesible

    # Limpiar el contenedor de la tabla para evitar duplicados
    for widget in prediccion_frame.tabla_container.winfo_children():
        widget.destroy()

    # Cargar la tabla de cultivos en el contenedor
    tabla_cultivos = mostrar_cultivos_usuario(prediccion_frame.tabla_container)  # 'mostrar_cultivos_usuario' debe estar definida

    # Actualizar el comando del botón de predicción
    prediccion_frame.boton_prediccion.config(command=lambda: realizar_prediccion(tabla_cultivos))  # 'realizar_prediccion' debe estar definida

def go_to_gestion():
    dashboard_frame.pack_forget()
    gestion_frame.pack(expand=True, fill="both")
        # Contenedor para la tabla
    tabla_container = tk.Frame(gestion_frame, bg="#2E4053")
    tabla_container.pack(fill="both", expand=True, padx=20, pady=10)
    mostrar_terrenos_usuario(tabla_container)
    print(f"[DEBUG] USUARIO: {global_username}")

def go_to_registro_cultivos():
    dashboard_frame.pack_forget()
    registro_cultivos_frame.pack(expand=True, fill="both")

def back_to_dashboard(frame):
    frame.pack_forget()
    dashboard_frame.pack(expand=True, fill="both")
def back_to_inicio(frame):
    frame.pack_forget()
    inicio_frame.pack(expand=True, fill="both")

def go_to_predicciones_realizadas():
    dashboard_frame.pack_forget()
    predicciones_realizadas_frame.pack(expand=True, fill="both")

    for widget in predicciones_realizadas_frame.tabla_container.winfo_children():
        widget.destroy()

    tabla_predicciones = mostrar_predicciones_usuario(predicciones_realizadas_frame.tabla_container)

    if tabla_predicciones:
        predicciones_realizadas_frame.boton_registrar_real.config(command=lambda: registrar_rendimiento_real(tabla_predicciones))
        predicciones_realizadas_frame.boton_generar_reporte.config(command=lambda: generar_reporte(tabla_predicciones))

def logout():
    global global_username
    global_username = ""  # Limpiar la variable global del nombre de usuario
    dashboard_frame.pack_forget()  # Ocultar la pantalla del dashboard
    login_frame.pack(expand=True, fill="both")  # Mostrar la pantalla de inicio de sesión
    entry_user.delete(0, tk.END)  # Borrar el contenido del campo de usuario
    entry_pass.delete(0, tk.END)  # Borrar el contenido del campo de contraseña

def show_login():
    inicio_frame.pack_forget()
    login_frame.pack(expand=True, fill="both")
    
#Carga la informacion de los estados de Mexico desde un archivo JSON 
def cargar_datos_json():
    try:
        with open('DATOS/estados-municipios.JSON', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo")
        return {}
    except json.JSONDecodeError:
        print("Error: El archivo JSON no tiene un formato válido")
        return {}
    
#Al seleccionar un estado se van a cagar los municipios que le corresponden     
def actualizar_municipios(event, combo_estados, combo_municipio, datos):
    estado_seleccionado = combo_estados.get()
    if estado_seleccionado in datos_estados_municipios:
        combo_municipio['values'] = datos_estados_municipios[estado_seleccionado]
        combo_municipio.set('')
    else:
        combo_municipio['values'] = []
        combo_municipio.set('')

# Cargar datos desde JSON
datos_estados_municipios = cargar_datos_json()

def crear_cuenta():
    # Verificar si ya existe una ventana de creación de cuenta
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() in ["Crear Cuenta", "Crear Cuenta 1", "Crear Cuenta 2"]:
            widget.lift()  # Traer al frente si ya existe
            return

    # Crear UNA SOLA ventana
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Crear Cuenta")
    ventana_registro.geometry("500x500")
    ventana_registro.configure(bg="#2E4053")
    ventana_registro.resizable(False, False)
    ventana_registro.grab_set()  # Hacerla modal

    # Centrar la ventana
    window_width = 500
    window_height = 500
    screen_width = ventana_registro.winfo_screenwidth()
    screen_height = ventana_registro.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    ventana_registro.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    def registrar_usuario():
        # Obtener datos del formulario
        nuevo_usuario = entry_nuevo_usuario.get()
        nueva_contrasena = entry_nueva_contrasena.get()
        telefono = entry_telefono.get()
        estado = combo_estados.get()
        municipio = combo_municipio.get()
        correo = entry_correo.get()

        # Validar campos
        if not all([nuevo_usuario, nueva_contrasena, telefono, estado, municipio, correo]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            # Conexión y registro en la base de datos
            conexion = Conexion().conexion
            cursor = conexion.cursor()

            cursor.execute(
                """INSERT INTO login (usuario, contrasena)
                VALUES (%s, %s)""",
                (nuevo_usuario, nueva_contrasena)
            )

            cursor.execute(
                """INSERT INTO agricultor (usuario, contrasena, telefono, estado, municipio, correo)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (nuevo_usuario, nueva_contrasena, telefono, estado, municipio, correo)
            )

            conexion.commit()
            messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
            ventana_registro.destroy()  # Cerrar ventana solo después de éxito
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la cuenta: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
            

    
    # Crear y configurar un nuevo estilo para el Combobox
    style = ttk.Style()
    style.configure("Custom.TCombobox", font=("Arial", 12))
    

    titulo_label = tk.Label(ventana_registro, text="Crear Cuenta", bg="#2E4053", fg="#FFFFFF", font=("Arial", 16, "bold"))
    titulo_label.pack(pady=10)

    # Marco para los campos de entrada
    form_frame = tk.Frame(ventana_registro, bg="#2E4053", relief="groove", bd=2)  # Fondo azul oscuro
    form_frame.pack(pady=20, padx=20)

    # Campos de entrada
    tk.Label(form_frame, text="Usuario", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_nuevo_usuario = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_nuevo_usuario.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Contraseña", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_nueva_contrasena = tk.Entry ( form_frame, show="*", font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1) 
    entry_nueva_contrasena.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Teléfono", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_telefono = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1  )
    entry_telefono.grid(row=2, column=1, padx=10, pady=10)

    # lista desplegable de estados
    tk.Label(form_frame, text="Estado:", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12) ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    combo_estados = ttk.Combobox(form_frame, font=("Arial", 12), state="readonly", values=list(datos_estados_municipios.keys()))
    combo_estados.grid(row=3, column=1, padx=10, pady=10)
    combo_estados.bind("<<ComboboxSelected>>", 
                  lambda e: actualizar_municipios(e, combo_estados, combo_municipio, datos_estados_municipios))
    
    #Lista despleganle de Municipios en base al estado seleccionado
    tk.Label(form_frame, text="Municipio:", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
    combo_municipio = ttk.Combobox(form_frame, font=("Arial", 12), state="readonly")
    combo_municipio.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Correo Electrónico", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
    entry_correo = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_correo.grid(row=5, column=1, padx=10, pady=10)

    # Botón de registro
    boton_registrar = tk.Button(ventana_registro, text="Registrar", command=registrar_usuario)
    estilo_boton(boton_registrar)
    boton_registrar.pack(pady=10)
    
    

# ---- Función para aplicar estilo a botones ----
def estilo_boton(boton):
    boton.configure(
        bg="#4CAF50",  # Verde moderno
        fg="white",  # Texto blanco
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#45A049",  # Verde más claro al hacer clic
        activeforeground="white",
        cursor="hand2",
        padx=10,
        pady=5
    )

# ---- Función para aplicar estilo a etiquetas ----
def estilo_etiqueta(etiqueta, font_size=14, bold=False):
    etiqueta.configure(
        font=("Arial", font_size, "bold" if bold else "normal"),
        bg="#2E4053",  # Fondo azul oscuro
        fg="#FFFFFF"  # Texto blanco
    )
    
    
    

# ---- Pantalla de Inicio ----
def crear_pantalla_inicio():
    global inicio_frame
    inicio_frame = tk.Frame(root, bg="#2E4053")  # Fondo azul oscuro
    inicio_frame.pack(expand=True, fill="both")

    try:
        # Construir la ruta absoluta de la imagen
        ruta_imagen = os.path.join(os.path.dirname(__file__), "imagenes", "cosecha1.png")
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((300, 200))  # Ajustar tamaño
        img_tk = ImageTk.PhotoImage(imagen)
        img_label = tk.Label(inicio_frame, image=img_tk, bg="#2E4053")  # Fondo azul oscuro
        img_label.image = img_tk  # Evitar que la imagen sea recolectada por el garbage collector
        img_label.pack(pady=10)
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")
        messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    # Título principal
    titulo_label = tk.Label(
        inicio_frame,
        text="Bienvenido a CosechaFarm",
        bg="#2E4053",  # Fondo azul oscuro
        fg="#FFFFFF",  # Texto blanco para contraste
        font=("Arial", 18, "bold")
    )
    titulo_label.pack(pady=10)

    # Línea decorativa
    decor_line = tk.Frame(inicio_frame, bg="#4CAF50", height=2, width=300)
    decor_line.pack(pady=10)

    # Botones de la pantalla de inicio
    boton_crear_cuenta = tk.Button(inicio_frame, text="Crear Cuenta", command=crear_cuenta, width=20)
    estilo_boton(boton_crear_cuenta)
    boton_crear_cuenta.pack(pady=10)

    boton_iniciar_sesion = tk.Button(inicio_frame, text="Iniciar Sesión", command=show_login, width=20)
    estilo_boton(boton_iniciar_sesion)
    boton_iniciar_sesion.pack(pady=10)

    # Pie de página
    footer_label = tk.Label(
        inicio_frame,
        text="© 2025 CosechaFarm - Todos los derechos reservados",
        font=("Arial", 10),
        bg="#2E4053",
        fg="#B0BEC5"  # Gris claro
    )
    footer_label.pack(side="bottom", pady=10)

# ---- Pantalla de Login ----
def crear_pantalla_login():
    login_frame = tk.Frame(root, bg="#2E4053")  # Fondo azul oscuro

    titulo_label = tk.Label(
        login_frame, 
        text="Iniciar Sesión", 
        bg="#2E4053",  # Fondo azul oscuro
        fg="#FFFFFF"  # Texto blanco para contraste
    )
    estilo_etiqueta(titulo_label, font_size=16, bold=True)
    titulo_label.pack(pady=10)

    # Línea decorativa
    decor_line = tk.Frame(login_frame, bg="#4CAF50", height=2, width=300)
    decor_line.pack(pady=10)

    # Marco para los campos de usuario y contraseña
    form_frame = tk.Frame(login_frame, bg="#2E4053", relief="groove", bd=2)  # Fondo azul oscuro
    form_frame.pack(pady=20, padx=20)

    # Campo de usuario
    tk.Label(form_frame, text="Usuario", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    global entry_user
    entry_user = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_user.grid(row=0, column=1, padx=10, pady=10)

    # Campo de contraseña
    tk.Label(form_frame, text="Contraseña", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    global entry_pass
    entry_pass = tk.Entry(form_frame, show="*", font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_pass.grid(row=1, column=1, padx=10, pady=10)

    # Botón de iniciar sesión
    boton_iniciar_sesion = tk.Button(login_frame, text="Iniciar Sesión", command=login)
    estilo_boton(boton_iniciar_sesion)
    boton_iniciar_sesion.pack(pady=10)
    
    boton_volver = tk.Button(login_frame, text="Volver", command=lambda: back_to_inicio(login_frame))
    estilo_boton(boton_volver)
    boton_volver.pack(pady=5)

    return login_frame

#En base al usuario actual se consulata su ubicacion en la BD
def obtener_ubicacion_usuario():
    if not global_username:
        print("[DEBUG] No hay usuario logueado")
        return None
        
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        
        cursor.execute(
            "SELECT municipio FROM agricultor WHERE usuario = %s AND municipio IS NOT NULL",
            (global_username,)
        )
        
        resultado = cursor.fetchone()
        if resultado:
            print(f"[DEBUG] Municipio encontrado: {resultado[0]}")
            return resultado[0]
        else:
            print(f"[DEBUG] Usuario {global_username} no tiene municipio registrado")
            return None
            
    except Exception as e:
        print(f"[ERROR] Al obtener ubicación: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()
     
#Obtiene datos del clima desde OpenWeatherMap 
#tuve que meter mi tarjeta para que me diera mil consultas
def obtener_clima_openweather(ciudad, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
        respuesta = requests.get(url)
        datos = respuesta.json()
        
        if datos.get("cod") != 200:
            print(f"Error en API: {datos.get('message', 'Error desconocido')}")
            return None
            
        return {
            "temperatura": datos["main"]["temp"],
            "humedad": datos["main"]["humidity"],
            "descripcion": datos["weather"][0]["description"].capitalize(),
            "icono": datos["weather"][0]["icon"]
        }
    except Exception as e:
        print(f"Error al obtener clima: {e}")
        return None

#Descarga el icono del clima desde OpenWeatherMap
def obtener_imagen_clima(icono_codigo):
    try:
        url = f"http://openweathermap.org/img/wn/{icono_codigo}@2x.png"
        respuesta = requests.get(url, stream=True)
        imagen = Image.open(io.BytesIO(respuesta.content))
        return ImageTk.PhotoImage(imagen)
    except Exception as e:
        print(f"Error al obtener icono: {e}")
        return None
    
def crear_widget_clima(container):
    """Crea el widget de clima con datos reales"""
    # Limpiar el contenedor primero
    for widget in container.winfo_children():
        widget.destroy()
    
    # Obtener ubicación del usuario
    municipio = obtener_ubicacion_usuario()
    
    if not municipio:
        tk.Label(container, 
                text="Ubicación no disponible\nPor favor complete su perfil",
                bg="#ffffff", fg="red", justify="center").pack()
        return
    
    # Obtener datos del clima
    API_KEY = "cdb3c60a97e6875d843c79b4d6e61bd8"
    datos_clima = obtener_clima_openweather(municipio, API_KEY)
    
    if not datos_clima:
        tk.Label(container, 
                text="Datos de clima no disponibles",
                bg="#ffffff").pack()
        return
    
    # Crear el frame del clima
    clima_frame = tk.Frame(container, bg="#ffffff", relief="groove", bd=2)
    clima_frame.pack(fill="both", expand=True)
    
    # Obtener y mostrar icono del clima
    icono_clima = obtener_imagen_clima(datos_clima["icono"])
    if icono_clima:
        label_icono = tk.Label(clima_frame, image=icono_clima, bg="#ffffff")
        label_icono.image = icono_clima
        label_icono.pack(pady=5)
    
    # Mostrar datos del clima
    tk.Label(
        clima_frame, 
        text=f"Clima en {municipio}\n"
             f"{datos_clima['temperatura']}°C | {datos_clima['descripcion']}\n"
             f"Humedad: {datos_clima['humedad']}%", 
        font=("Arial", 12, "bold"), 
        bg="#ffffff", 
        justify="center"
    ).pack(pady=5)

def obtener_noticias_agricolas():
    """Obtiene noticias sobre agricultura de NewsAPI"""
    API_KEY = "3a5619b42315405d9861bd08a870897c"
    try:
        # Usar timestamp actual para evitar caché
        import time
        timestamp = int(time.time())
        
        params = {
            'q': f'agricultura OR cultivos OR cosechas -deporte -fútbol -política&timestamp={timestamp}',
            'language': 'es',
            'sortBy': 'publishedAt',
            'pageSize': 10,
            'page': random.randint(1, 10)  # Pagina aleatoria para variedad
        }
        
        headers = {'X-Api-Key': API_KEY}
        
        respuesta = requests.get(
            "https://newsapi.org/v2/everything",
            headers=headers,
            params=params,
            timeout=10
        )
        
        datos = respuesta.json()
        
        if datos.get("status") == "ok" and datos.get("totalResults", 0) > 0:
            noticias = datos["articles"]
            # Filtrar noticias sin título
            noticias = [n for n in noticias if n.get("title")]
            # Ordenar por fecha descendente
            noticias.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
            return noticias[:3]  # Devolver las 3 más recientes
        return None
        
    except Exception as e:
        print(f"Error al obtener noticias: {e}")
        return None

def crear_widget_noticias(frame):
    """Crea widget con noticias agrícolas actuales"""
    noticias_frame = tk.Frame(frame, bg="#ffffff", relief="groove", bd=2)
    noticias_frame.place(x=400, y=150, width=300, height=200)

    # Icono y título
    header_frame = tk.Frame(noticias_frame, bg="#ffffff")
    header_frame.pack(fill="x")
    
    tk.Label(
        header_frame,
        text="📰",  # Ícono de periódico
        font=("Arial", 20),
        bg="#ffffff"
    ).pack(side="left", padx=5)
    
    tk.Label(
        header_frame,
        text="Noticias Agrícolas",
        font=("Arial", 12, "bold"),
        bg="#ffffff"
    ).pack(side="left")
    
    # Botón de actualización
    btn_actualizar = tk.Button(
        header_frame,
        text="⟳",
        font=("Arial", 10),
        command=lambda: actualizar_contenido_noticias(noticias_frame),
        bd=0,
        relief="flat",
        activebackground="#f0f0f0"
    )
    btn_actualizar.pack(side="right", padx=5)

    # Contenedor desplazable
    canvas = tk.Canvas(noticias_frame, bg="#ffffff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(noticias_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#ffffff")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
    scrollbar.pack(side="right", fill="y")

    # Cargar noticias iniciales
    actualizar_contenido_noticias(noticias_frame)
    
    return noticias_frame

def actualizar_contenido_noticias(frame):
    """Actualiza el contenido del widget de noticias"""
    # Encontrar el frame desplazable
    canvas = frame.winfo_children()[1]  # El canvas es el segundo widget
    scrollable_frame = canvas.winfo_children()[0]
    
    # Limpiar contenido anterior
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    # Mostrar indicador de carga
    tk.Label(
        scrollable_frame,
        text="Cargando noticias...",
        bg="#ffffff",
        fg="#7f8c8d"
    ).pack(pady=20)
    
    frame.update()  # Forzar actualización de la UI
    
    # Obtener noticias
    noticias = obtener_noticias_agricolas()
    
    # Limpiar el mensaje de carga
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    if not noticias:
        tk.Label(
            scrollable_frame,
            text="No se pudieron cargar las noticias\nIntenta más tarde",
            bg="#ffffff",
            fg="#e74c3c",
            justify="center"
        ).pack(pady=20)
        return
    
    # Mostrar cada noticia
    for i, noticia in enumerate(noticias):
        # Frame para cada noticia
        noticia_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=5, pady=5)
        noticia_frame.pack(fill="x", pady=(0, 5))
        
        # Título (clickable)
        titulo = tk.Label(
            noticia_frame,
            text=noticia.get("title", "Sin título"),
            bg="#ffffff",
            fg="#2c3e50",
            font=("Arial", 9, "bold"),
            wraplength=250,
            justify="left",
            cursor="hand2"
        )
        titulo.pack(anchor="w")
        titulo.bind(
            "<Button-1>", 
            lambda e, url=noticia.get("url"): abrir_en_navegador(url)
        )
        
        # Fuente y fecha
        fuente = noticia.get("source", {}).get("name", "Fuente desconocida")
        fecha = noticia.get("publishedAt", "")[:10]  # Solo la fecha
        
        tk.Label(
            noticia_frame,
            text=f"{fuente} | {fecha}",
            bg="#ffffff",
            fg="#7f8c8d",
            font=("Arial", 7),
            justify="left"
        ).pack(anchor="w")
        
        # Separador
        if i < len(noticias)-1:
            tk.Frame(
                scrollable_frame, 
                height=1, 
                bg="#ecf0f1"
            ).pack(fill="x", padx=5)

def abrir_en_navegador(url):
    """Abre la URL en el navegador predeterminado"""
    import webbrowser
    if url:
        webbrowser.open(url)

def obtener_estadisticas_usuario():
    """Obtiene estadísticas reales del usuario desde la base de datos"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        
        # Obtener ID del agricultor
        cursor.execute("SELECT \"ID\" FROM agricultor WHERE usuario = %s", (global_username,))
        id_agricultor = cursor.fetchone()[0]
        
        if not id_agricultor:
            return None, None
        
        # Contar cultivos activos
        cursor.execute(
            "SELECT COUNT(*) FROM cultivos WHERE id_agricultor = %s",
            (id_agricultor,)
        )
        cultivos_activos = cursor.fetchone()[0]
        
        # Sumar rendimiento total de predicciones
        cursor.execute(
            """SELECT COALESCE(SUM(rendimiento_total), 0) 
               FROM predicciones 
               WHERE id_agricultor = %s""",
            (id_agricultor,)
        )
        produccion_total = cursor.fetchone()[0]
        
        return cultivos_activos, produccion_total
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return None, None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def actualizar_estadisticas():
    """Actualiza el contenido del widget de estadísticas"""
    cultivos_activos, produccion_total = obtener_estadisticas_usuario()
    if cultivos_activos is not None and produccion_total is not None:
        dashboard_frame.estadisticas_label1.config(text=f"Producción Total: {produccion_total:.2f} t")
        dashboard_frame.estadisticas_label2.config(text=f"Cultivos Activos: {cultivos_activos}")
    else:
        dashboard_frame.estadisticas_label1.config(text="Error al cargar producción total")
        dashboard_frame.estadisticas_label2.config(text="Error al cargar cultivos activos")

# ---- Dashboard ----
def crear_dashboard():
    dashboard_frame = tk.Frame(root, bg="#2E4053")  # Fondo azul oscuro

    # Título principal
    titulo_label = tk.Label(
        dashboard_frame, 
        text="Bienvenido a tu Dashboard de CosechaFarm", 
        font=("Arial", 20, "bold"), 
        bg="#2E4053", 
         fg="#FFFFFF",
    )
    titulo_label.pack(pady=20)

    # Línea decorativa
    decor_line = tk.Frame(dashboard_frame, bg="#4CAF50", height=2, width=600)
    decor_line.pack(pady=10)

    # Subtítulo
    subtitulo_label = tk.Label(
        dashboard_frame, 
        text="Selecciona una opción para continuar", 
        font=("Arial", 14), 
        bg="#2E4053",
        fg="#FFFFFF",
    )
    subtitulo_label.place(x=200, y=360)

    # Widget de Clima
    dashboard_frame.clima_container = tk.Frame(dashboard_frame, bg="#2E4053")
    dashboard_frame.clima_container.place(x=50, y=150, width=300, height=200)

    # Widget de Tips
    crear_widget_noticias(dashboard_frame)
    
    
 # Widget de Estadísticas
    estadisticas_frame = tk.Frame(dashboard_frame, bg="#ffffff", relief="groove", bd=2)
    estadisticas_frame.place(x=750, y=150, width=300, height=250)
    
    estadisticas_icon = tk.Label(
        estadisticas_frame,                     
        text="📊",
        font=("Arial", 40),
        bg="#ffffff",
        fg="#3498db"
    )
    estadisticas_icon.pack(pady=10)
    
    estadisticas_title = tk.Label(
        estadisticas_frame,
        text="Estadísticas Clave",
        font=("Arial", 14, "bold"),
        bg="#ffffff",
        fg="#2E4053"
    )
    estadisticas_title.pack(pady=5)

    # Crear labels iniciales con "Cargando..." y almacenarlos como atributos
    dashboard_frame.estadisticas_label1 = tk.Label(
        estadisticas_frame,
        text="Producción Total: Cargando...",
        font=("Arial", 12),
        bg="#ffffff",
        fg="#333333"
    )
    dashboard_frame.estadisticas_label1.pack()
    
    dashboard_frame.estadisticas_label2 = tk.Label(
        estadisticas_frame,
        text="Cultivos Activos: Cargando...",
        font=("Arial", 12),
        bg="#ffffff",
        fg="#333333"
    )
    dashboard_frame.estadisticas_label2.pack()
    
    # Botón de actualización
    boton_actualizar = tk.Button(
        estadisticas_frame,
        text="⟳ Actualizar",
        command=actualizar_estadisticas,  # Usar la nueva función
        width=15,
        bg="#2E4053",
        fg="white"
    )
    boton_actualizar.pack(pady=10)
    
    # Botón de Predicción de Cosechas
    boton_prediccion = tk.Button(
        dashboard_frame, 
        text="Predicción de Cosechas", 
        command=go_to_prediccion, 
        width=20, 
        height=2, 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 12, "bold"), 
        relief="raised", 
        bd=3, 
        activebackground="#45A049", 
        activeforeground="white", 
        cursor="hand2"
    )
    boton_prediccion.place(x=50, y=400)
    
    # botón de Registro de Cultivos
    boton_Registro_datos = tk.Button(
        dashboard_frame,
        text="Registro de Cultivos",
        command=go_to_registro_cultivos,
        width=20,
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#45A049",
        activeforeground="white",
        cursor="hand2"
    )
    boton_Registro_datos.place(x=520, y=400)
    
    # Botón de Gestión de Terrenos
    boton_gestion = tk.Button(
        dashboard_frame, 
        text="Gestión de Terrenos", 
        command=go_to_gestion, 
        width=20, 
        height=2, 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 12, "bold"), 
        relief="raised", 
        bd=3, 
        activebackground="#45A049", 
        activeforeground="white", 
        cursor="hand2"
    )
    boton_gestion.place(x=285, y=400)

    # Botón de Cerrar Sesión
    boton_logout = tk.Button(
        dashboard_frame, 
        text="Cerrar Sesión", 
        command=logout, 
        width=13,  # Reducir el ancho
        height=3,  # Reducir la altura
        bg="#ff4d4d", 
        fg="white", 
        font=("Arial", 8, "bold"),  # Reducir el tamaño de la fuente
        relief="raised", 
        bd=3, 
        activebackground="#cc0000", 
        activeforeground="white", 
        cursor="hand2"
    )
    boton_logout.place(x=45, y=45)

    boton_predicciones_realizadas = tk.Button(
        dashboard_frame,
        text="Predicciones Realizadas",
        command=go_to_predicciones_realizadas,
        width=20,
        height=2,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#45A049",
        activeforeground="white",
        cursor="hand2"
    )
    boton_predicciones_realizadas.place(x=300, y=500)

    # Pie de página
    footer_label = tk.Label(
        dashboard_frame, 
        text="© 2025 CosechaFarm - Todos los derechos reservados", 
        font=("Arial", 10), 
        bg="#2E4053", 
        fg="#B0BEC5"
    )
    footer_label.pack(side="bottom", pady=10)

    return dashboard_frame

# ---- Pantalla de Predicción ----
import tkinter as tk

def crear_pantalla_prediccion():
    prediccion_frame = tk.Frame(root, bg="#2E4053")  # 'root' debe estar definido en tu código

    # Título de la pantalla
    titulo_label = tk.Label(prediccion_frame, text="Predicción de Cosechas", bg="#2E4053", fg="white", font=("Arial", 16, "bold"))
    titulo_label.pack(pady=10)

    # Contenedor para la tabla de cultivos (vacío inicialmente)
    prediccion_frame.tabla_container = tk.Frame(prediccion_frame, bg="#2E4053")
    prediccion_frame.tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

    # Botón de predicción (sin funcionalidad hasta que se cargue la tabla)
    prediccion_frame.boton_prediccion = tk.Button(
        prediccion_frame,
        text="Realizar Predicción",
        command=lambda: None,  # Sin acción por ahora
        width=20,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#45A049",
        activeforeground="white",
        cursor="hand2"
    )
    prediccion_frame.boton_prediccion.pack(pady=10)

    # Botón para volver al dashboard
    boton_volver = tk.Button(
        prediccion_frame,
        text="Volver",
        command=lambda: back_to_dashboard(prediccion_frame),  # 'back_to_dashboard' debe estar definida
        width=15,
        bg="#D32F2F",
        fg="white",
        font=("Arial", 12),
        relief="raised",
        bd=3,
        activebackground="#C62828",
        activeforeground="white",
        cursor="hand2"
    )
    boton_volver.pack(pady=5)

    return prediccion_frame

#--pantalla de monitoreo de cultivos--
def crear_pantalla_predicciones_realizadas():
    predicciones_frame = tk.Frame(root, bg="#2E4053")

    # Título de la pantalla
    titulo_label = tk.Label(predicciones_frame, text="Predicciones Realizadas", bg="#2E4053", fg="white", font=("Arial", 16, "bold"))
    titulo_label.pack(pady=10)

    # Contenedor para la tabla de predicciones
    predicciones_frame.tabla_container = tk.Frame(predicciones_frame, bg="#2E4053")
    predicciones_frame.tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

    # Botón para registrar rendimiento real
    predicciones_frame.boton_registrar_real = tk.Button(
        predicciones_frame,
        text="Registrar Rendimiento Real",
        command=lambda: None,  # Updated dynamically in go_to_predicciones_realizadas
        width=25,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#45A049",
        activeforeground="white",
        cursor="hand2"
    )
    predicciones_frame.boton_registrar_real.pack(pady=5)

    # Botón para generar reporte
    predicciones_frame.boton_generar_reporte = tk.Button(
        predicciones_frame,
        text="Generar Reporte",
        command=lambda: None,  # Updated dynamically in go_to_predicciones_realizadas
        width=25,
        bg="#2196F3",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=3,
        activebackground="#1976D2",
        activeforeground="white",
        cursor="hand2"
    )
    predicciones_frame.boton_generar_reporte.pack(pady=5)

    # Botón para volver al dashboard
    boton_volver = tk.Button(
        predicciones_frame,
        text="Volver",
        command=lambda: back_to_dashboard(predicciones_frame),
        width=15,
        bg="#D32F2F",
        fg="white",
        font=("Arial", 12),
        relief="raised",
        bd=3,
        activebackground="#C62828",
        activeforeground="white",
        cursor="hand2"
    )
    boton_volver.pack(pady=5)

    return predicciones_frame

def crear_terreno():
    # Verificar si ya existe una ventana de creación de terreno
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) :
            widget.lift()  # Traer al frente si ya existe
            return

    # Crear UNA SOLA ventana
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registrar Terreno")
    ventana_registro.geometry("600x600")
    ventana_registro.configure(bg="#2E4053")
    ventana_registro.resizable(False, False)
    ventana_registro.grab_set()  # Hacerla modal

    # Centrar la ventana
    window_width = 500
    window_height = 500
    screen_width = ventana_registro.winfo_screenwidth()
    screen_height = ventana_registro.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    ventana_registro.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    def cargar_variedades():
        try:
            conexion = Conexion().conexion
            cursor = conexion.cursor()
            cursor.execute("SELECT tipo FROM tipo_suelo ORDER BY tipo")
            variedades = [row[0] for row in cursor.fetchall()]
            return variedades
        except Exception as e:
            print(f"Error al cargar variedades: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def registrar_usuario():
        # Obtener datos del formulario
        nombre_terreno = entry_nombre_terreno.get()
        extension_terreno = entry_extension_terreno.get()
        suelo = combo_suelo.get()
        estado = combo_estados.get()
        municipio = combo_municipio.get()
        precipitacion = entry_precipitacion.get()
        temperatura = entry_temperatura.get()

        # Validar campos
        if not all([nombre_terreno, extension_terreno, suelo, estado, municipio, temperatura]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            # Conexión y registro en la base de datos
            conexion = Conexion().conexion
            cursor = conexion.cursor()

            cursor.execute(
                """SELECT "ID" FROM agricultor WHERE usuario = %s""",
                (global_username, )
            )

            ID_agricultor = cursor.fetchone()
            cursor.execute(
                """INSERT INTO terrenos (nombre, extension, suelo, estado, municipio, precipitacion, id_agricultor, temperatura)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (nombre_terreno, extension_terreno, suelo, estado, municipio, precipitacion, ID_agricultor, temperatura)
            )

            conexion.commit()
            messagebox.showinfo("Éxito", "Terreno registrado con exito")
            ventana_registro.destroy()  # Cerrar ventana solo después de éxito
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el terreno: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
            

    
    # Crear y configurar un nuevo estilo para el Combobox
    style = ttk.Style()
    style.configure("Custom.TCombobox", font=("Arial", 12))
    

    titulo_label = tk.Label(ventana_registro, text="Crear terreno", bg="#2E4053", fg="#FFFFFF", font=("Arial", 16, "bold"))
    titulo_label.pack(pady=10)

    # Marco para los campos de entrada
    form_frame = tk.Frame(ventana_registro, bg="#2E4053", relief="groove", bd=2)  # Fondo azul oscuro
    form_frame.pack(pady=20, padx=20)

    # Campos de entrada
    tk.Label(form_frame, text="Nombre del terreno", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_nombre_terreno = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_nombre_terreno.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Extensión del terreno en Hectáreas", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_extension_terreno = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1, validate="key", validatecommand=(validate_cmd, "%d", "%P"))
    entry_extension_terreno.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Tipo de suelo", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    variedades = cargar_variedades()
    combo_suelo = ttk.Combobox(
        form_frame, 
        values=variedades, 
        font=("Arial", 12), 
        state="readonly"
    )
    combo_suelo.grid(row=2, column=1, padx=10, pady=10)
    if variedades:
        combo_suelo.set(variedades[0]) 

    # lista desplegable de estados
    tk.Label(form_frame, text="Estado:", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12) ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    combo_estados = ttk.Combobox(form_frame, font=("Arial", 12), state="readonly", values=list(datos_estados_municipios.keys()))
    combo_estados.grid(row=3, column=1, padx=10, pady=10)
    combo_estados.bind("<<ComboboxSelected>>", 
                  lambda e: actualizar_municipios(e, combo_estados, combo_municipio, datos_estados_municipios))
    
    #Lista despleganle de Municipios en base al estado seleccionado
    tk.Label(form_frame, text="Municipio:", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
    combo_municipio = ttk.Combobox(form_frame, font=("Arial", 12), state="readonly")
    combo_municipio.grid(row=4, column=1, padx=10, pady=10)
    
    tk.Label(form_frame, text="Precipitacion (en mm)", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="w")
    entry_precipitacion = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_precipitacion.grid(row=5, column=1, padx=10, pady=10)
    
    tk.Label(form_frame, text="Temperatura promedio en °C", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="w")
    entry_temperatura = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_temperatura.grid(row=6, column=1, padx=10, pady=10)


    # Botón de registro
    boton_registrar = tk.Button(ventana_registro, text="Registrar", command=registrar_usuario)
    estilo_boton(boton_registrar)
    boton_registrar.pack(pady=10)

def eliminar_terreno(tabla):
    """Elimina el terreno seleccionado de la tabla y la base de datos"""
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Selecciona un terreno para eliminar")
        return
    
    # Confirmar eliminación
    if not messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este terreno?"):
        return
    
    try:
        # Obtener nombre del terreno para identificarlo
        nombre_terreno = tabla.item(seleccionado)['values'][0]
        
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        
        cursor.execute(
            "DELETE FROM terrenos WHERE nombre = %s AND id_agricultor = (SELECT \"ID\" FROM agricultor WHERE usuario = %s)",
            (nombre_terreno, global_username)
        )
        
        if cursor.rowcount > 0:
            messagebox.showinfo("Éxito", "Terreno eliminado correctamente")
            tabla.delete(seleccionado)
        else:
            messagebox.showerror("Error", "No se pudo eliminar el terreno")
        
        conexion.commit()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar el terreno: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def obtener_id_agricultor():
    """Obtiene el ID del agricultor basado en el nombre de usuario"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        
        cursor.execute( "SELECT \"ID\" FROM agricultor WHERE usuario = %s", 
            (global_username,))
        
        
        resultado = cursor.fetchone()
        print(f"[DEBUG] ID encontrado: {resultado[0]}")
        return resultado[0] if resultado[0] else None
        
    except Exception as e:
        print(f"Error al obtener ID agricultor: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def obtener_terrenos_agricultor(id_agricultor):
    """Obtiene los terrenos de un agricultor específico"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        
        cursor.execute(
            """SELECT id_terreno, nombre, extension, suelo, estado, municipio 
               FROM terrenos 
               WHERE id_agricultor = %s
               ORDER BY nombre""",
            (id_agricultor,)
        )
        
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Error al obtener terrenos: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def mostrar_terrenos_usuario(container):
    """Muestra los terrenos del usuario en una tabla"""
    # Obtener ID del agricultor
    id_agricultor = obtener_id_agricultor()
    
    if not id_agricultor:
        tk.Label(
            container,
            text="No se pudo obtener la información del agricultor",
            bg="#2E4053",
            fg="white"
        ).pack()
        return
    
    # Obtener terrenos
    terrenos = obtener_terrenos_agricultor(id_agricultor)
    
    if not terrenos:
        tk.Label(
            container,
            text="No tienes terrenos registrados",
            bg="#2E4053",
            fg="white"
        ).pack()
        return
    
    # Crear Treeview (tabla)
    frame_tabla = tk.Frame(container, bg="#2E4053")
    frame_tabla.pack(fill="both", expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla)
    scrollbar.pack(side="right", fill="y")
    
    # Configurar la tabla
    tabla = ttk.Treeview(
        frame_tabla,
        columns=("id", "nombre", "extension", "suelo", "estado", "municipio"),
        yscrollcommand=scrollbar.set,
        selectmode="browse",
        height=8
    )
    scrollbar.config(command=tabla.yview)
    
    # Estilo
    estilo = ttk.Style()
    estilo.configure("Treeview", 
                   background="#f0f0f0",
                   foreground="black",
                   rowheight=25,
                   fieldbackground="#f0f0f0")
    estilo.map('Treeview', background=[('selected', '#4CAF50')])
    
    # Columnas
    tabla.heading("#0", text="ID")
    tabla.column("#0", width=0, stretch=tk.NO)  # Ocultar columna ID
    
    tabla.heading("id", text="ID")
    tabla.column("id", width=50, anchor="center")
    
    tabla.heading("nombre", text="Nombre")
    tabla.column("nombre", width=120, anchor="w")
    
    tabla.heading("extension", text="Extensión (ha)")
    tabla.column("extension", width=90, anchor="center")
    
    tabla.heading("suelo", text="Tipo de Suelo")
    tabla.column("suelo", width=100, anchor="w")
    
    tabla.heading("estado", text="Estado")
    tabla.column("estado", width=100, anchor="w")
    
    tabla.heading("municipio", text="Municipio")
    tabla.column("municipio", width=100, anchor="w")
    
    # Insertar datos
    for i, terreno in enumerate(terrenos, start=1):
        tabla.insert("", "end", iid=i, values=terreno)
    
    tabla.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Botones de acción
    frame_botones = tk.Frame(container, bg="#2E4053")
    frame_botones.pack(fill="x", pady=(10, 0))
    
    boton_eliminar = tk.Button(
        frame_botones,
        text="Eliminar Terreno",
        command=lambda: eliminar_terreno(tabla),
        width=20,
        bg="#e74c3c",
        fg="white"
    )
    boton_eliminar.pack(side="left", padx=5)
    
    boton_actualizar = tk.Button(
        frame_botones,
        text="⟳ Actualizar",
        command=lambda: actualizar_tabla_terrenos(container, tabla),
        width=15,
        bg="#2E4053",
        fg="white"
    )
    boton_actualizar.pack(side="right", padx=5)

def actualizar_tabla_terrenos(container, tabla):
    """Actualiza los datos de la tabla de terrenos"""
    # Limpiar tabla
    for item in tabla.get_children():
        tabla.delete(item)
    
    # Obtener nuevos datos
    id_agricultor = obtener_id_agricultor()
    if id_agricultor:
        terrenos = obtener_terrenos_agricultor(id_agricultor)
        for i, terreno in enumerate(terrenos, start=1):
            tabla.insert("", "end", iid=i, values=terreno)

def mostrar_cultivos_usuario(container):
    """Muestra los cultivos del usuario en una tabla"""
    id_agricultor = obtener_id_agricultor()
    if not id_agricultor:
        tk.Label(
            container,
            text="No se pudo obtener la información del agricultor",
            bg="#2E4053",
            fg="white"
        ).pack()
        return None

    cultivos = obtener_cultivos_agricultor(id_agricultor)
    if not cultivos:
        tk.Label(
            container,
            text="No tienes cultivos registrados",
            bg="#2E4053",
            fg="white"
        ).pack()
        return None

    frame_tabla = tk.Frame(container, bg="#2E4053")
    frame_tabla.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tabla)
    scrollbar.pack(side="right", fill="y")

    tabla = ttk.Treeview(
        frame_tabla,
        columns=("id", "nombre", "tipo", "fecha_siembra", "riego", "id_terreno"),
        yscrollcommand=scrollbar.set,
        selectmode="browse",
        height=8
    )
    scrollbar.config(command=tabla.yview)

    estilo = ttk.Style()
    estilo.configure("Treeview", 
                     background="#f0f0f0",
                     foreground="black",
                     rowheight=25,
                     fieldbackground="#f0f0f0")
    estilo.map('Treeview', background=[('selected', '#4CAF50')])

    tabla.heading("#0", text="ID")
    tabla.column("#0", width=0, stretch=tk.NO)  # Ocultar columna ID
    tabla.heading("id", text="ID")
    tabla.column("id", width=50, anchor="center")
    tabla.heading("nombre", text="Nombre")
    tabla.column("nombre", width=120, anchor="w")
    tabla.heading("tipo", text="Tipo")
    tabla.column("tipo", width=100, anchor="w")
    tabla.heading("fecha_siembra", text="Fecha Siembra")
    tabla.column("fecha_siembra", width=100, anchor="center")
    tabla.heading("riego", text="Riego")
    tabla.column("riego", width=50, anchor="center")
    tabla.heading("id_terreno", text="ID Terreno")
    tabla.column("id_terreno", width=80, anchor="center")

    for i, cultivo in enumerate(cultivos, start=1):
        tabla.insert("", "end", iid=i, values=cultivo)

    tabla.pack(fill="both", expand=True, padx=5, pady=5)

    return tabla

def obtener_cultivos_agricultor(id_agricultor):
    """Obtiene los cultivos de un agricultor específico"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()

        cursor.execute(
            """SELECT id_cultivo, nombre, tipo, fecha_siembra, riego, id_terreno
               FROM cultivos
               WHERE id_agricultor = %s
               ORDER BY nombre""",
            (id_agricultor,)
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener cultivos: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def obtener_datos_terreno(id_terreno):
    """Obtiene la precipitación, temperatura y extensión del terreno"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        cursor.execute("SELECT precipitacion, temperatura, extension FROM terrenos WHERE id_terreno = %s", (id_terreno,))
        resultado = cursor.fetchone()
        if resultado:
            precipitacion = float(resultado[0]) if resultado[0] is not None else None
            temperatura = float(resultado[1]) if resultado[1] is not None else None
            extension = float(resultado[2]) if resultado[2] is not None else None
            return precipitacion, temperatura, extension
        return None, None, None
    except Exception as e:
        print(f"Error al obtener datos del terreno: {e}")
        return None, None, None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def obtener_days_to_harvest(tipo_cultivo):
    """Obtiene los días para cosechar basado en el tipo de cultivo"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()
        cursor.execute("SELECT dias_cosecha FROM variedad_cultivo WHERE tipo = %s", (tipo_cultivo,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Error al obtener days_to_harvest: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def guardar_prediccion(id_agricultor, id_cultivo, rendimiento_hectarea, rendimiento_total, uso_fertilizante):
    """Guarda las predicciones en la base de datos"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()

        cursor.execute(
            """INSERT INTO predicciones 
               (rendimiento_hectarea, rendimiento_total, uso_fertilizante, id_cultivo, id_agricultor)
               VALUES (%s, %s, %s, %s, %s)""",
            (rendimiento_hectarea, rendimiento_total, uso_fertilizante, id_cultivo, id_agricultor)
        )

        conexion.commit()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la predicción: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def realizar_prediccion(tabla):
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Selecciona un cultivo para predecir")
        return

    # Obtener datos del cultivo seleccionado
    valores = tabla.item(seleccionado)['values']
    id_cultivo = valores[0]
    tipo_cultivo = valores[2]  # 'tipo' está en la posición 2
    id_terreno = valores[5]  # 'id_terreno' está en la posición 5

    # Obtener datos del terreno
    rainfall, temperature, extension = obtener_datos_terreno(id_terreno)
    if rainfall is None or temperature is None or extension is None:
        messagebox.showerror("Error", "No se pudieron obtener los datos del terreno")
        return

    # Obtener days_to_harvest basado en el tipo de cultivo
    days_to_harvest = obtener_days_to_harvest(tipo_cultivo)
    if days_to_harvest is None:
        messagebox.showerror("Error", "No se pudo obtener los días para cosechar")
        return

    # Cargar modelos
    try:
        import sklearn  # Verificar si sklearn está instalado
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_rf = joblib.load(os.path.join(BASE_DIR, 'modelos', 'random_forest_model.pkl'))
        model_lr = joblib.load(os.path.join(BASE_DIR, 'modelos', 'linear_regresion_model.pkl'))
    except ModuleNotFoundError:
        messagebox.showerror("Error", "Falta la biblioteca scikit-learn. Instálala con: pip install scikit-learn")
        return
    except FileNotFoundError:
        messagebox.showerror("Error", "No se encontraron los archivos de los modelos en la carpeta 'modelos/'")
        return
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los modelos: {e}")
        return

    # Predicción con Regresión Lineal (solo usa rainfall)
    input_lr = np.array([[rainfall]])
    rendimiento_hectarea = model_lr.predict(input_lr)[0]

    # Predicción con Random Forest (usa rainfall, temperature, days_to_harvest, rendimiento_hectarea)
    input_rf = pd.DataFrame(
        [[rainfall, temperature, days_to_harvest, rendimiento_hectarea]],
        columns=['Rainfall_mm', 'Temperature_Celsius', 'Days_to_Harvest', 'Yield_tons_per_hectare']
    )
    uso_fertilizante = bool(model_rf.predict(input_rf)[0])
    print(f"Tipo de uso_fertilizante: {type(uso_fertilizante)}, Valor: {uso_fertilizante}")
    # Calcular rendimiento_total
    try:
        rendimiento_total = rendimiento_hectarea * extension
    except TypeError as e:
        messagebox.showerror("Error", f"Error al calcular rendimiento total: {e}")
        return

    # Obtener id_agricultor
    id_agricultor = obtener_id_agricultor()
    if id_agricultor is None:
        messagebox.showerror("Error", "No se pudo obtener el ID del agricultor")
        return

    # Guardar predicciones en la base de datos
    guardar_prediccion(
        id_agricultor,
        id_cultivo,
        rendimiento_hectarea,
        rendimiento_total,
        uso_fertilizante
    )

    messagebox.showinfo("Éxito", f"Predicción realizada y guardada:\nRendimiento por hectárea: {rendimiento_hectarea:.2f} t/ha\nRendimiento total: {rendimiento_total:.2f} t\nUso de fertilizante: {'Sí' if uso_fertilizante else 'No'}")

# ---- Pantalla de Gestión ----
def crear_pantalla_gestion():
    gestion_frame = tk.Frame(root, bg="#2E4053")  # Fondo azul oscuro

    # Título
    titulo_label = tk.Label(gestion_frame, text="Gestión de Terrenos")
    estilo_etiqueta(titulo_label, font_size=16, bold=True)
    titulo_label.pack(pady=10)
    
    # Botón para crear nuevo terreno
    boton_crear_terreno = tk.Button(gestion_frame, text="Crear Terreno", command=crear_terreno, width=20)
    estilo_boton(boton_crear_terreno)
    boton_crear_terreno.pack(pady=10)

    # Botón para volver
    boton_volver = tk.Button(gestion_frame, text="Volver", command=lambda: back_to_dashboard(gestion_frame))
    estilo_boton(boton_volver)
    boton_volver.pack(pady=5)

    return gestion_frame

def registrar_cultivo():
    # Verificar si ya existe una ventana de creación de terreno
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.lift()  # Traer al frente si ya existe
            return

    # Crear ventana
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registrar Cultivo")
    ventana_registro.geometry("500x500")
    ventana_registro.configure(bg="#2E4053")
    ventana_registro.resizable(False, False)
    ventana_registro.grab_set()

    # Centrar la ventana
    window_width = 500
    window_height = 500
    screen_width = ventana_registro.winfo_screenwidth()
    screen_height = ventana_registro.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    ventana_registro.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
    
    def cargar_variedades():
        try:
            conexion = Conexion().conexion
            cursor = conexion.cursor()
            cursor.execute("SELECT tipo FROM variedad_cultivo ORDER BY tipo")
            variedades = [row[0] for row in cursor.fetchall()]
            return variedades
        except Exception as e:
            print(f"Error al cargar variedades: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
    
    def guardar_cultivo():
        nombre_cultivo = entry_cultivo.get().strip()
        tipo_cultivo = combo_tipo.get().strip()  # Cambiado a get() del Combobox
        fecha = entry_fecha.get().strip()
        terreno = entry_terreno.get().strip()
        riego = entry_riego.get().strip().lower()
        
        # Validar campos vacíos
        if not all([nombre_cultivo, tipo_cultivo, fecha, terreno, riego]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            if riego in ('1', 'si', 'sí', 'true', 'verdadero', 'yes'):
                riego_bool = True
            elif riego in ('0', 'no', 'false', 'falso'):
                riego_bool = False
            else:
                raise ValueError("Valor no válido para riego")
            
            # Conexión a la base de datos
            conexion = Conexion().conexion
            cursor = conexion.cursor()

            # Obtener ID del agricultor
            cursor.execute(
                """SELECT "ID" FROM agricultor WHERE usuario = %s""",
                (global_username,)
            )
            resultado_agricultor = cursor.fetchone()
            
            if not resultado_agricultor:
                messagebox.showerror("Error", "Agricultor no encontrado")
                return
                
            ID_agricultor = resultado_agricultor[0]

            # Validar terreno
            cursor.execute(
                """SELECT id_terreno FROM terrenos 
                WHERE id_terreno = %s AND id_agricultor = %s""",
                (terreno, ID_agricultor)
            )
            terreno_valido = cursor.fetchone()
            
            if not terreno_valido:
                messagebox.showerror("Error", 
                    "El terreno no existe o no pertenece a este agricultor")
                return

            # Registrar el cultivo
            cursor.execute(
                """INSERT INTO cultivos 
                (nombre, tipo, fecha_siembra, riego, id_terreno, id_agricultor)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (nombre_cultivo, tipo_cultivo, fecha, riego_bool, terreno, ID_agricultor)
            )

            conexion.commit()
            messagebox.showinfo("Éxito", "Cultivo registrado con éxito")
            ventana_registro.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cultivo: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
    
    # Marco para los campos de entrada
    form_frame = tk.Frame(ventana_registro, bg="#2E4053", relief="groove", bd=2)
    form_frame.pack(pady=20, padx=20)

    # Campos de entrada
    tk.Label(form_frame, text="Nombre del Cultivo", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_cultivo = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_cultivo.grid(row=0, column=1, padx=10, pady=10)

    # Cambio: Combobox para tipos de cultivo
    tk.Label(form_frame, text="Tipo o Variedad de cultivo", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    variedades = cargar_variedades()
    combo_tipo = ttk.Combobox(
        form_frame, 
        values=variedades, 
        font=("Arial", 12), 
        state="readonly"
    )
    combo_tipo.grid(row=1, column=1, padx=10, pady=10)
    if variedades:
        combo_tipo.set(variedades[0])  # Seleccionar el primer valor por defecto

    tk.Label(form_frame, text="Fecha de siembra (YYYY-MM-DD)", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_fecha = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_fecha.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="Uso de riego (1-si 0-no)", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    entry_riego = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_riego.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(form_frame, text="ID de terreno a sembrar", bg="#2E4053", fg="#FFFFFF", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
    entry_terreno = tk.Entry(form_frame, font=("Arial", 12), relief="flat", highlightbackground="#4CAF50", highlightthickness=1)
    entry_terreno.grid(row=4, column=1, padx=10, pady=10)
    
    # Botón para guardar los datos
    boton_guardar = tk.Button(
        ventana_registro, 
        text="Guardar Datos", 
        command=guardar_cultivo,
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 12, "bold"), 
        relief="raised", 
        bd=3, 
        activebackground="#45A049", 
        activeforeground="white", 
        cursor="hand2"
    )
    boton_guardar.pack(pady=10)

def crear_pantalla_registro_cultivos():
    registro_datos_frame = tk.Frame(root, bg="#2E4053")  # Fondo azul oscuro

    # Título principal
    titulo_label = tk.Label(
        registro_datos_frame, 
        text="Registro de cultivos", 
        font=("Arial", 20, "bold"), 
        bg="#2E4053", 
        fg="#FFFFFF"
    )
    titulo_label.pack(pady=20)

    boton_crear_cultivo = tk.Button(registro_datos_frame, text="Crear cultivo", command=registrar_cultivo, width=20)
    estilo_boton(boton_crear_cultivo)
    boton_crear_cultivo.pack(pady=10)

    # Botón para volver al Dashboard
    boton_volver = tk.Button(
        registro_datos_frame, 
        text="Volver", 
        command=lambda: back_to_dashboard(registro_datos_frame), 
        width=20, 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 12, "bold"), 
        relief="raised", 
        bd=3, 
        activebackground="#45A049", 
        activeforeground="white", 
        cursor="hand2"
    )
    boton_volver.pack(pady=10)

    return registro_datos_frame


# ---- generacion de Reporte ---- #

def obtener_predicciones_agricultor(id_agricultor):
    """Obtiene las predicciones realizadas por un agricultor específico"""
    try:
        conexion = Conexion().conexion
        cursor = conexion.cursor()

        cursor.execute(
            """SELECT p.id_prediccion, c.nombre AS cultivo, p.fecha, p.rendimiento_hectarea, 
                      p.rendimiento_total, p.uso_fertilizante, p.rendimiento_real
               FROM predicciones p
               JOIN cultivos c ON p.id_cultivo = c.id_cultivo
               WHERE p.id_agricultor = %s
               ORDER BY p.fecha DESC""",
            (id_agricultor,)
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"Error al obtener predicciones: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def mostrar_predicciones_usuario(container):
    """Muestra las predicciones del usuario en una tabla"""
    id_agricultor = obtener_id_agricultor()
    if not id_agricultor:
        tk.Label(
            container,
            text="No se pudo obtener la información del agricultor",
            bg="#2E4053",
            fg="white"
        ).pack()
        return None

    predicciones = obtener_predicciones_agricultor(id_agricultor)
    if not predicciones:
        tk.Label(
            container,
            text="No tienes predicciones realizadas",
            bg="#2E4053",
            fg="white"
        ).pack()
        return None

    frame_tabla = tk.Frame(container, bg="#2E4053")
    frame_tabla.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_tabla)
    scrollbar.pack(side="right", fill="y")

    tabla = ttk.Treeview(
        frame_tabla,
        columns=("id", "cultivo", "fecha", "rendimiento_hectarea", "rendimiento_total", "uso_fertilizante", "rendimiento_real"),
        yscrollcommand=scrollbar.set,
        selectmode="browse",
        height=8
    )
    scrollbar.config(command=tabla.yview)

    estilo = ttk.Style()
    estilo.configure("Treeview", 
                     background="#f0f0f0",
                     foreground="black",
                     rowheight=25,
                     fieldbackground="#f0f0f0")
    estilo.map('Treeview', background=[('selected', '#4CAF50')])

    tabla.heading("id", text="ID")
    tabla.column("id", width=50, anchor="center")
    tabla.heading("cultivo", text="Cultivo")
    tabla.column("cultivo", width=120, anchor="w")
    tabla.heading("fecha", text="Fecha")
    tabla.column("fecha", width=100, anchor="center")
    tabla.heading("rendimiento_hectarea", text="Rend. Hectárea (t/ha)")
    tabla.column("rendimiento_hectarea", width=120, anchor="center")
    tabla.heading("rendimiento_total", text="Rend. Total (t)")
    tabla.column("rendimiento_total", width=100, anchor="center")
    tabla.heading("uso_fertilizante", text="Fertilizante")
    tabla.column("uso_fertilizante", width=80, anchor="center")
    tabla.heading("rendimiento_real", text="Rend. Real (t)")
    tabla.column("rendimiento_real", width=100, anchor="center")

    for i, prediccion in enumerate(predicciones, start=1):
        tabla.insert("", "end", iid=i, values=prediccion)

    tabla.pack(fill="both", expand=True, padx=5, pady=5)

    return tabla

def registrar_rendimiento_real(tabla):
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Selecciona una predicción para registrar el rendimiento real")
        return

    valores = tabla.item(seleccionado)['values']
    id_prediccion = valores[0]

    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registrar Rendimiento Real")
    ventana_registro.geometry("300x150")
    ventana_registro.configure(bg="#2E4053")

    tk.Label(ventana_registro, text="Rendimiento Real (t):", bg="#2E4053", fg="white", font=("Arial", 12)).pack(pady=10)
    entry_rendimiento_real = tk.Entry(ventana_registro, font=("Arial", 12))
    entry_rendimiento_real.pack(pady=5)

    def guardar_rendimiento():
        rendimiento_real = entry_rendimiento_real.get().strip()
        if not rendimiento_real:
            messagebox.showerror("Error", "Ingresa un valor para el rendimiento real")
            return
        try:
            rendimiento_real = float(rendimiento_real)
            conexion = Conexion().conexion
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE predicciones SET rendimiento_real = %s WHERE id_prediccion = %s",
                (rendimiento_real, id_prediccion)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Rendimiento real registrado correctamente")
            ventana_registro.destroy()
            for widget in predicciones_realizadas_frame.tabla_container.winfo_children():
                widget.destroy()
            tabla_predicciones = mostrar_predicciones_usuario(predicciones_realizadas_frame.tabla_container)
            predicciones_realizadas_frame.boton_registrar_real.config(command=lambda: registrar_rendimiento_real(tabla_predicciones))
            predicciones_realizadas_frame.boton_generar_reporte.config(command=lambda: generar_reporte(tabla_predicciones))
        except ValueError:
            messagebox.showerror("Error", "Ingresa un valor numérico válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el rendimiento real: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    boton_guardar = tk.Button(ventana_registro, text="Guardar", command=guardar_rendimiento, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    boton_guardar.pack(pady=10)

def generar_reporte(tabla):
    seleccionado = tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Selecciona una predicción para generar el reporte")
        return

    valores = tabla.item(seleccionado)['values']
    id_prediccion = valores[0]

    try:
        conexion = Conexion().conexion
        # Use DictCursor to return results as dictionaries
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute(
            """SELECT p.*, c.nombre AS cultivo, c.tipo, c.fecha_siembra, c.riego, 
                      t.nombre AS terreno, t.extension, t.suelo, t.estado, t.municipio
               FROM predicciones p
               JOIN cultivos c ON p.id_cultivo = c.id_cultivo
               JOIN terrenos t ON c.id_terreno = t.id_terreno
               WHERE p.id_prediccion = %s""",
            (id_prediccion,)
        )
        datos = cursor.fetchone()

        if not datos:
            messagebox.showerror("Error", "No se encontró la información para la predicción seleccionada")
            return

        # Generate PDF
        nombre_archivo = f"reporte_prediccion_{id_prediccion}.pdf"
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elements = []

        # Title
        elements.append(Table([["Reporte de Predicción"]], colWidths=[500], rowHeights=30))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#2E4053")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
        ]))

        # Cultivo Section
        elements.append(Table([["Información del Cultivo"]], colWidths=[500], rowHeights=25))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        cultivo_data = [
            ["Nombre", datos['cultivo']],
            ["Tipo", datos['tipo']],
            ["Fecha de Siembra", datos['fecha_siembra'].strftime('%Y-%m-%d')],
            ["Riego", "Sí" if datos['riego'] else "No"]
        ]
        elements.append(Table(cultivo_data, colWidths=[250, 250]))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Terreno Section
        elements.append(Table([["Información del Terreno"]], colWidths=[500], rowHeights=25))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#2196F3")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        terreno_data = [
            ["Nombre", datos['terreno']],
            ["Extensión (ha)", str(datos['extension'])],
            ["Tipo de Suelo", datos['suelo']],
            ["Estado", datos['estado']],
            ["Municipio", datos['municipio']]
        ]
        elements.append(Table(terreno_data, colWidths=[250, 250]))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Predicción Section
        elements.append(Table([["Información de la Predicción"]], colWidths=[500], rowHeights=25))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FF9800")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        prediccion_data = [
            ["Fecha", datos['fecha'].strftime('%Y-%m-%d %H:%M:%S')],
            ["Rendimiento por Hectárea (t/ha)", f"{datos['rendimiento_hectarea']:.2f}"],
            ["Rendimiento Total (t)", f"{datos['rendimiento_total']:.2f}"],
            ["Uso de Fertilizante", "Sí" if datos['uso_fertilizante'] else "No"],
            ["Rendimiento Real (t)", f"{datos['rendimiento_real']:.2f}" if datos['rendimiento_real'] else "No registrado"]
        ]
        elements.append(Table(prediccion_data, colWidths=[250, 250]))
        elements[-1].setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        doc.build(elements)
        messagebox.showinfo("Éxito", f"Reporte generado: {nombre_archivo}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

# ---- Configuración de la ventana principal ----
root = tk.Tk()
root.title("Predicción de Cosechas")
root.geometry("1100x850")
validate_cmd = root.register(validar_numeros)
validate_fecha_cmd = root.register(validar_fecha)


# Crear las pantallas
crear_pantalla_inicio()
login_frame = crear_pantalla_login()
dashboard_frame = crear_dashboard()
prediccion_frame = crear_pantalla_prediccion()
gestion_frame = crear_pantalla_gestion()
registro_cultivos_frame = crear_pantalla_registro_cultivos()
predicciones_realizadas_frame = crear_pantalla_predicciones_realizadas()
root.mainloop()