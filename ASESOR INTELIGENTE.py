import pandas as pd
import customtkinter
from PIL import Image
import unicodedata
import os
import random

# Leer el dataset ampliado
try:
    df = pd.read_csv("DATASET.csv", encoding='latin1')
except FileNotFoundError:
    print("❌ Error: No se encontró ningún archivo de dataset")
    exit()


# Preprocesamiento mejorado
def preprocesar_datos(df):
    # Limpieza de precios
    df["Cars Prices"] = df["Cars Prices"].astype(str).str.replace("[$,]", "", regex=True)
    df["Cars Prices"] = pd.to_numeric(df["Cars Prices"].replace('', '0'), errors='coerce')
    
    # Limpieza de caballos de fuerza
    df["HorsePower"] = df["HorsePower"].astype(str).str.extract(r'(\d+)')
    df["HorsePower"] = pd.to_numeric(df["HorsePower"], errors='coerce')
    
    # Limpieza de asientos
    df["Seats"] = df["Seats"].astype(str).str.extract(r'(\d+)')
    df["Seats"] = pd.to_numeric(df["Seats"], errors='coerce')
    
    # Limpieza de torque
    if 'Torque' in df.columns:
        df["Torque"] = df["Torque"].fillna('N/A')
    
    # Limpieza de performance
    if 'Performance(0 - 100 )KM/H' in df.columns:
        df['Performance(0 - 100 )KM/H'] = df['Performance(0 - 100 )KM/H'].fillna('N/A')
    
    # Limpieza de marcas
    df["Company Names"] = df["Company Names"].str.strip().fillna('Desconocido')
    
    return df.dropna(subset=["Company Names", "Cars Prices"])

df = preprocesar_datos(df)

# Obtener opciones disponibles para filtros
combustibles_disponibles = sorted(df["Fuel Types"].astype(str).str.strip().str.lower().dropna().unique())
marcas_disponibles = sorted(df["Company Names"].astype(str).str.strip().str.lower().dropna().unique())

# Convertir a título para mejor presentación
marcas_disponibles = [marca.title() for marca in marcas_disponibles]
combustibles_disponibles = [comb.title() for comb in combustibles_disponibles]

# Valores mínimos y máximos
min_precio, max_precio = int(df["Cars Prices"].min()), int(df["Cars Prices"].max())
min_asientos, max_asientos = int(df["Seats"].min()), int(df["Seats"].max())
min_hp, max_hp = int(df["HorsePower"].min()), int(df["HorsePower"].max())

# Sistema de ponderación
PESOS = {
    'precio': 0.35,
    'caballos_fuerza': 0.25,
    'asientos': 0.15,
    'combustible': 0.15,
    'marca': 0.10
}

# Inicializar customtkinter
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

# Normalizador mejorado
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

# Variables globales
respuestas = {
    "presupuesto_min": 0,
    "presupuesto_max": float('inf'),
    "combustible": "",
    "asientos": 0,
    "marca": "",
    "hp_min": 0,
    "hp_max": float('inf')
}

# Banco de explicaciones ampliado y variado
BANCO_EXPLICACIONES = {
    'precio': [
        ("Excelente relación precio-calidad", 0.8),
        ("Oferta destacada en su rango de precios", 0.75),
        ("Buena opción económica", 0.6),
        ("Precio competitivo para sus características", 0.55),
        ("Precio algo elevado pero justificado", 0.4),
        ("Precio superior al promedio del mercado", 0.3)
    ],
    'caballos_fuerza': [
        ("Potencia excepcional para su categoría", 0.85),
        ("Alto rendimiento motor", 0.8),
        ("Potencia más que suficiente", 0.7),
        ("Balance ideal entre potencia y eficiencia", 0.6),
        ("Potencia adecuada para uso cotidiano", 0.5),
        ("Potencia modesta pero eficiente", 0.4)
    ],
    'asientos': [
        ("Amplio espacio para familias numerosas", 7),
        ("Ideal para familias grandes", 6),
        ("Buen espacio para familia", 5),
        ("Cómodo para pequeños grupos", 4),
        ("Configuración práctica", 3),
        ("Compacto pero funcional", 2)
    ],
    'combustible': [
        ("Combustible preferido ({}) - Eficiente", 1),
        ("Tecnología {} avanzada", 1),
        ("Sistema {} de última generación", 1),
        ("Motorización {} optimizada", 1),
        ("Eficiencia en consumo de {}", 1)
    ],
    'marca': [
        ("Marca preferida ({}) - Alta confiabilidad", 1),
        ("{} reconocida por su calidad", 1),
        ("Excelente reputación de {}", 1),
        ("Tecnología {} de vanguardia", 1),
        ("Servicio postventa {} destacado", 1)
    ],
    'general': [
        "Elección muy bien valorada por expertos",
        "Opción destacada en pruebas de manejo",
        "Incluye tecnología de última generación",
        "Sistema de seguridad muy completo",
        "Diseño ergonómico y funcional",
        "Bajo costo de mantenimiento",
        "Alto valor de reventa",
        "Paquete de conectividad avanzado",
        "Sistema de infoentretenimiento premium",
        "Asistencia a la conducción inteligente",
        "Materiales de alta calidad en interior",
        "Garantía extendida incluida",
        "Bajas emisiones contaminantes",
        "Suspensión optimizada para confort",
        "Sistema de frenado de alto desempeño"
    ]
}

# Función para generar explicaciones mejorada y más variada
def generar_explicacion(fila):
    explicaciones = []
    
    # Explicaciones específicas por criterio
    if 'score_precio' in fila:
        for msg, umbral in BANCO_EXPLICACIONES['precio']:
            if fila['score_precio'] >= umbral:
                explicaciones.append(msg)
                break
    
    if 'score_hp' in fila:
        for msg, umbral in BANCO_EXPLICACIONES['caballos_fuerza']:
            if fila['score_hp'] >= umbral:
                explicaciones.append(msg)
                break
    
    if 'Seats' in fila:
        for msg, umbral in BANCO_EXPLICACIONES['asientos']:
            if fila['Seats'] >= umbral:
                explicaciones.append(msg)
                break
    
    if fila.get('score_combustible', 0) == 1:
        msg = random.choice(BANCO_EXPLICACIONES['combustible'])[0]
        explicaciones.append(msg.format(fila['Fuel Types']))
    
    if fila.get('score_marca', 0) == 1:
        msg = random.choice(BANCO_EXPLICACIONES['marca'])[0]
        explicaciones.append(msg.format(fila['Company Names']))
    
    # Añadir explicaciones generales aleatorias (2-3)
    explicaciones_generales = random.sample(BANCO_EXPLICACIONES['general'], k=random.randint(2, 3))
    explicaciones.extend(explicaciones_generales)
    
    # Determinar emoji de recomendación
    puntuacion = fila.get('puntuacion_total', 0)
    if puntuacion >= 80:
        emoji = "🏆 RECOMENDACIÓN TOP"
    elif puntuacion >= 50:
        emoji = "👍 BUENA OPCIÓN"
    else:
        emoji = "⚠️ CONSIDERA OTRAS OPCIONES"
    
    return f"{emoji}\n💡 " + " | ".join(explicaciones)

# Función para calcular puntuación mejorada
def calcular_puntuacion(df_resultados):
    df = df_resultados.copy()
    
    # Puntuación por precio (menor precio = mayor puntuación)
    if respuestas["presupuesto_max"] < float('inf'):
        precio_max = respuestas["presupuesto_max"]
    else:
        precio_max = df["Cars Prices"].max() * 1.1
    
    df['score_precio'] = 1 - (df["Cars Prices"] / precio_max)
    
    # Puntuación por caballos de fuerza
    if respuestas["hp_max"] < float('inf'):
        hp_max = respuestas["hp_max"]
    else:
        hp_max = df["HorsePower"].max()
    
    df['score_hp'] = df["HorsePower"] / hp_max if hp_max > 0 else 0
    
    # Puntuación por asientos
    if respuestas["asientos"] > 0:
        asientos_min = respuestas["asientos"]
    else:
        asientos_min = df["Seats"].min()
    
    asientos_max = df["Seats"].max()
    df['score_asientos'] = (df["Seats"] - asientos_min) / (asientos_max - asientos_min) if (asientos_max - asientos_min) > 0 else 0
    
    # Puntuación por combustible y marca (con normalización)
    df['score_combustible'] = (df["Fuel Types"].astype(str).str.lower().str.strip() == normalizar(respuestas["combustible"])).astype(int)
    df['score_marca'] = (df["Company Names"].astype(str).str.lower().str.strip() == normalizar(respuestas["marca"])).astype(int)
    
    # Puntuación total ponderada
    df['puntuacion_total'] = (
        df['score_precio'] * PESOS['precio'] +
        df['score_hp'] * PESOS['caballos_fuerza'] +
        df['score_asientos'] * PESOS['asientos'] +
        df['score_combustible'] * PESOS['combustible'] +
        df['score_marca'] * PESOS['marca']
    ) * 100
    
    return df.round({'puntuacion_total': 2})

# Función de recomendación mejorada
def recomendar_vehiculos():
    resultados = df.copy()
    
    # Aplicar filtros con manejo de mayúsculas/minúsculas
    if respuestas["presupuesto_min"] > 0 or respuestas["presupuesto_max"] < float('inf'):
        resultados = resultados[
            (resultados["Cars Prices"] >= respuestas["presupuesto_min"]) & 
            (resultados["Cars Prices"] <= respuestas["presupuesto_max"])
        ]
    
    if respuestas["hp_min"] > 0 or respuestas["hp_max"] < float('inf'):
        resultados = resultados[
            (resultados["HorsePower"] >= respuestas["hp_min"]) & 
            (resultados["HorsePower"] <= respuestas["hp_max"])
        ]
    
    if respuestas["combustible"] != "":
        resultados = resultados[
            resultados["Fuel Types"].astype(str).str.lower().str.strip() == normalizar(respuestas["combustible"])
        ]
    
    if respuestas["asientos"] > 0:
        resultados = resultados[resultados["Seats"] >= respuestas["asientos"]]
    
    if respuestas["marca"] != "":
        resultados = resultados[
            resultados["Company Names"].astype(str).str.lower().str.strip() == normalizar(respuestas["marca"])
        ]
    
    # Calcular puntuación si hay resultados
    if not resultados.empty:
        resultados = calcular_puntuacion(resultados)
        return resultados.sort_values(by=['puntuacion_total', 'Cars Prices'], ascending=[False, True])
    
    return resultados

# Crear ventanas
ventana = customtkinter.CTk()
ventana.geometry("1100x800")  # Ventana más grande
ventana.title("Asesor Inteligente de CAR DEALER")

# Contenedor de frames
frames = {}

# ================= INICIO =================
inicio = customtkinter.CTkFrame(ventana)
frames["inicio"] = inicio

label = customtkinter.CTkLabel(inicio, text="Bienvenido al Asesor Inteligente de CAR DEALER",
                             font=("Arial", 20), justify="center")
label.pack(pady=40)

try:
    img_inicio = customtkinter.CTkImage(Image.open("assets/logo.png"), size=(300, 200))
    label_img = customtkinter.CTkLabel(inicio, image=img_inicio, text="")
    label_img.pack(pady=10)
except:
    pass

label = customtkinter.CTkLabel(inicio, text="\nTe ayudaré a encontrar el vehículo ideal según tus necesidades", 
                             font=("Arial", 20), justify="center")
label.pack(pady=40)

boton_empezar = customtkinter.CTkButton(inicio, text="🚗 Empezar", text_color=("#7AF04B"), fg_color=("#004E00"), command=lambda: mostrar_filtro("presupuesto"))
boton_empezar.pack(pady=10)

boton_salir = customtkinter.CTkButton(inicio, text="❌ Salir", text_color=("#E76969"), fg_color=("#530000"), command=ventana.destroy)
boton_salir.pack(pady=10)

# ================= FILTROS =================
def mostrar_filtro(filtro):
    frame = customtkinter.CTkFrame(ventana)
    frames[f"filtro_{filtro}"] = frame
    for f in frames.values():
        f.pack_forget()
    frame.pack(fill="both", expand=True)

    # Diccionario de preguntas
    pregunta = {
        "presupuesto": "¿Deseas establecer un rango de presupuesto?",
        "combustible": "¿Deseas elegir un tipo de combustible?",
        "asientos": "¿Deseas establecer un número mínimo de asientos?",
        "marca": "¿Deseas filtrar por marca?",
        "hp": "¿Deseas establecer un rango de caballos de fuerza?"
    }[filtro]

    # Diccionario de imágenes (rutas a los archivos)
    imagenes = {
        "presupuesto": "assets/presupuesto.png",
        "combustible": "assets/combustible.png",
        "asientos": "assets/asientos.png",
        "marca": "assets/marca.png",
        "hp": "assets/hp.png"
    }

    customtkinter.CTkLabel(frame, text=pregunta, font=("Arial", 18)).pack(pady=40)

    try:
        # Cargar la imagen específica para el filtro actual
        img_path = imagenes[filtro]
        img = customtkinter.CTkImage(Image.open(img_path), size=(250, 180))
        customtkinter.CTkLabel(frame, image=img, text="").pack(pady=10)
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")
        # Opcional: cargar una imagen por defecto si la específica falla
        try:
            img = customtkinter.CTkImage(Image.open("assets/filtro.png"), size=(250, 180))
            customtkinter.CTkLabel(frame, image=img, text="").pack(pady=10)
        except:
            pass

    customtkinter.CTkButton(frame, text="Sí", text_color=("#7AF04B"), fg_color=("#004E00"), command=lambda: mostrar_pregunta(filtro)).pack(pady=10)
    customtkinter.CTkButton(frame, text="No", text_color=("#E76969"), fg_color=("#530000"), command=lambda: siguiente_filtro(filtro)).pack(pady=10)

# ================= PREGUNTAS =================
def mostrar_pregunta(filtro):
    frame = customtkinter.CTkFrame(ventana)
    frames[f"pregunta_{filtro}"] = frame
    for f in frames.values():
        f.pack_forget()
    frame.pack(fill="both", expand=True)

    if filtro == "presupuesto":
        customtkinter.CTkLabel(frame, text=f"Establece tu rango de presupuesto (USD {min_precio:,} - {max_precio:,})", 
                             font=("Arial", 18)).pack(pady=20)
        
        input_frame = customtkinter.CTkFrame(frame)
        input_frame.pack(pady=10)
        
        customtkinter.CTkLabel(input_frame, text="Mínimo:", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
        min_entry = customtkinter.CTkEntry(input_frame, placeholder_text=f" {min_precio:,}")
        min_entry.grid(row=0, column=1, padx=5, pady=5)
        customtkinter.CTkLabel(input_frame, text="USD", font=("Arial", 14)).grid(row=0, column=2, padx=5, pady=5)
        
        customtkinter.CTkLabel(input_frame, text="Máximo:", font=("Arial", 14)).grid(row=1, column=0, padx=5, pady=5)
        max_entry = customtkinter.CTkEntry(input_frame, placeholder_text=f" {max_precio:,}")
        max_entry.grid(row=1, column=1, padx=5, pady=5)
        customtkinter.CTkLabel(input_frame, text="USD", font=("Arial", 14)).grid(row=1, column=2, padx=5, pady=5)
        
        def guardar_presupuesto():
            try:
                min_val = float(min_entry.get()) if min_entry.get() else 0
                max_val = float(max_entry.get()) if max_entry.get() else float('inf')
                
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                
                respuestas["presupuesto_min"] = max(min_val, 0)
                respuestas["presupuesto_max"] = max_val
                siguiente_filtro(filtro)
            except ValueError:
                respuestas["presupuesto_min"] = 0
                respuestas["presupuesto_max"] = float('inf')
                siguiente_filtro(filtro)
                
        customtkinter.CTkButton(frame, text="Siguiente", text_color=("#7AF04B"), fg_color=("#004E00"), command=guardar_presupuesto).pack(pady=20)
        
    elif filtro == "asientos":
        customtkinter.CTkLabel(frame, text=f"Selecciona el número mínimo de asientos ({min_asientos}-{max_asientos})", 
                             font=("Arial", 16)).pack(pady=20)
        
        slider = customtkinter.CTkSlider(
            frame, 
            from_=min_asientos, 
            to=max_asientos,
            number_of_steps=max_asientos-min_asientos,
            command=lambda value: slider_label.configure(text=f"Asientos: {int(value)}")
        )
        slider.set(min_asientos)
        slider.pack(pady=10)
        
        slider_label = customtkinter.CTkLabel(frame, text=f"Asientos: {min_asientos}")
        slider_label.pack()
        
        def guardar_asientos():
            respuestas["asientos"] = int(slider.get())
            siguiente_filtro(filtro)
            
        customtkinter.CTkButton(frame, text="Siguiente", text_color=("#7AF04B"), fg_color=("#004E00"), command=guardar_asientos).pack(pady=20)
        
    elif filtro == "hp":
        customtkinter.CTkLabel(frame, text=f"Establece tu rango de caballos de fuerza ({min_hp}-{max_hp} hp)", 
                             font=("Arial", 18)).pack(pady=20)
        
        input_frame = customtkinter.CTkFrame(frame)
        input_frame.pack(pady=10)
        
        customtkinter.CTkLabel(input_frame, text="Mínimo:", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
        min_entry = customtkinter.CTkEntry(input_frame, placeholder_text=f" {min_hp}")
        min_entry.grid(row=0, column=1, padx=5, pady=5)
        customtkinter.CTkLabel(input_frame, text="hp", font=("Arial", 14)).grid(row=0, column=2, padx=5, pady=5)
        
        customtkinter.CTkLabel(input_frame, text="Máximo:", font=("Arial", 14)).grid(row=1, column=0, padx=5, pady=5)
        max_entry = customtkinter.CTkEntry(input_frame, placeholder_text=f" {max_hp}")
        max_entry.grid(row=1, column=1, padx=5, pady=5)
        customtkinter.CTkLabel(input_frame, text="hp", font=("Arial", 14)).grid(row=1, column=2, padx=5, pady=5)
        
        def guardar_hp():
            try:
                min_val = float(min_entry.get()) if min_entry.get() else 0
                max_val = float(max_entry.get()) if max_entry.get() else float('inf')
                
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                
                respuestas["hp_min"] = max(min_val, 0)
                respuestas["hp_max"] = max_val
                siguiente_filtro(filtro)
            except ValueError:
                respuestas["hp_min"] = 0
                respuestas["hp_max"] = float('inf')
                siguiente_filtro(filtro)
                
        customtkinter.CTkButton(frame, text="Siguiente", text_color=("#7AF04B"), fg_color=("#004E00"), command=guardar_hp).pack(pady=20)
        
    elif filtro == "combustible":
        customtkinter.CTkLabel(frame, text="Selecciona el tipo de combustible:", font=("Arial", 16)).pack(pady=20)
        
        combobox = customtkinter.CTkComboBox(
            frame,
            values=combustibles_disponibles,
            state="readonly"
        )
        combobox.pack(pady=10)
        
        def guardar_combustible():
            respuestas[filtro] = combobox.get().lower()  # Guardar en minúsculas para comparación
            siguiente_filtro(filtro)
            
        customtkinter.CTkButton(frame, text="Siguiente", text_color=("#7AF04B"), fg_color=("#004E00"), command=guardar_combustible).pack(pady=20)
        
    elif filtro == "marca":
        customtkinter.CTkLabel(frame, text="Selecciona la marca:", font=("Arial", 16)).pack(pady=20)
        
        combobox = customtkinter.CTkComboBox(
            frame,
            values=marcas_disponibles,
            state="readonly"
        )
        combobox.pack(pady=10)
        
        def guardar_marca():
            respuestas[filtro] = combobox.get().lower()  # Guardar en minúsculas para comparación
            siguiente_filtro(filtro)
            
        customtkinter.CTkButton(frame, text="Siguiente", text_color=("#7AF04B"), fg_color=("#004E00"), command=guardar_marca).pack(pady=20)

# ================= SUGERENCIAS =================
def mostrar_sugerencias():
    frame = customtkinter.CTkFrame(ventana)
    frames["sugerencias"] = frame
    for f in frames.values():
        f.pack_forget()
    frame.pack(fill="both", expand=True)

    # Botón de volver al inicio EN LA PARTE SUPERIOR (fijo)
    boton_volver = customtkinter.CTkButton(frame, text="← Volver al inicio", 
                                         command=lambda: [resetear_filtros(), mostrar_ventana("inicio")],
                                         fg_color="#ff7b00", hover_color="#3a3a3a",
                                         font=("Arial", 14, "bold"))
    boton_volver.pack(pady=10, padx=20, anchor="w")

    resultados = recomendar_vehiculos()
    num_resultados = len(resultados)
    
    # Mostrar resumen de filtros aplicados
    filtros_aplicados = []
    if respuestas["presupuesto_min"] > 0 or respuestas["presupuesto_max"] < float('inf'):
        min_str = f"${respuestas['presupuesto_min']:,.0f}" if respuestas["presupuesto_min"] > 0 else "sin mínimo"
        max_str = f"${respuestas['presupuesto_max']:,.0f}" if respuestas["presupuesto_max"] < float('inf') else "sin máximo"
        filtros_aplicados.append(f"Presupuesto: {min_str} - {max_str}")
    if respuestas["combustible"]:
        filtros_aplicados.append(f"Combustible: {respuestas['combustible'].title()}")
    if respuestas["asientos"] > 0:
        filtros_aplicados.append(f"Asientos: ≥ {respuestas['asientos']}")
    if respuestas["marca"]:
        filtros_aplicados.append(f"Marca: {respuestas['marca'].title()}")
    if respuestas["hp_min"] > 0 or respuestas["hp_max"] < float('inf'):
        min_str = f"{respuestas['hp_min']}" if respuestas["hp_min"] > 0 else "sin mínimo"
        max_str = f"{respuestas['hp_max']}" if respuestas["hp_max"] < float('inf') else "sin máximo"
        filtros_aplicados.append(f"Caballos de fuerza: {min_str} - {max_str} hp")
    
    if filtros_aplicados:
        lbl_filtros = customtkinter.CTkLabel(frame, text="Filtros aplicados: " + ", ".join(filtros_aplicados), 
                                           font=("Arial", 14))
        lbl_filtros.pack(pady=(0, 10), padx=20, anchor="w")

    lbl_titulo = customtkinter.CTkLabel(frame, 
                                      text=f"Vehículos Sugeridos ({min(num_resultados, 10)} de {num_resultados} resultados)", 
                                      font=("Arial", 22, "bold"))
    lbl_titulo.pack(pady=(0, 20), padx=20, anchor="w")

    if num_resultados == 0:
        lbl_error = customtkinter.CTkLabel(frame, 
                                         text="❌ No se encontraron autos que coincidan con tus preferencias.", 
                                         font=("Arial", 16))
        lbl_error.pack(pady=20, padx=20)
        
        # Sugerir relajar filtros
        sugerencia_frame = customtkinter.CTkFrame(frame)
        sugerencia_frame.pack(pady=10, padx=20, fill="x")
        
        lbl_sugerencia = customtkinter.CTkLabel(sugerencia_frame, text="Prueba:", 
                                              font=("Arial", 14, "bold"))
        lbl_sugerencia.pack(anchor="w")
        
        consejos = customtkinter.CTkLabel(sugerencia_frame, 
                                        text="• Aumentar tu presupuesto máximo\n• Considerar otros tipos de combustible\n• Reducir los caballos de fuerza requeridos\n• Flexibilizar la marca preferida", 
                                        justify="left")
        consejos.pack(anchor="w")
    else:
        scroll_frame = customtkinter.CTkScrollableFrame(frame, width=1000, height=550)
        scroll_frame.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        # Limitar a 10 sugerencias como máximo
        for _, fila in resultados.head(10).iterrows():
            explicacion = generar_explicacion(fila)
            
            # Obtener todos los campos con manejo seguro de valores faltantes
            company = fila.get('Company Names', 'N/A')
            car_name = fila.get('Cars Names', 'N/A')
            engine = fila.get('Engines', 'N/A')
            cc_battery = fila.get('CC/Battery Capacity', 'N/A')
            horsepower = fila.get('HorsePower', 'N/A')
            total_speed = fila.get('Total Speed', 'N/A')
            performance = fila.get('Performance(0 - 100 )KM/H', 'N/A')
            price = fila.get('Cars Prices', 'N/A')
            fuel = fila.get('Fuel Types', 'N/A')
            seats = fila.get('Seats', 'N/A')
            torque = fila.get('Torque', 'N/A')
            
            # Formatear valores numéricos
            try:
                price_str = f"${float(price):,.0f}" if str(price).replace('.','').isdigit() else str(price)
                horsepower_str = f"{int(horsepower)} hp" if str(horsepower).isdigit() else str(horsepower)
                seats_str = str(int(seats)) if str(seats).replace('.','').isdigit() else str(seats)
            except:
                price_str = str(price)
                horsepower_str = str(horsepower)
                seats_str = str(seats)
            
            auto_info = (
                f"🔹 {company} {car_name}\n"
                f"⭐ Puntuación total: {fila.get('puntuacion_total', 'N/A')}%\n"
                f"{explicacion}\n\n"
                f"📌 ESPECIFICACIONES TÉCNICAS:\n"
                f"⚙️ Motor: {engine}\n"
                f"🔋 CC/Capacidad Batería: {cc_battery}\n"
                f"🏇 Caballos de fuerza: {horsepower_str}\n"
                f"🚀 Velocidad máxima: {total_speed}\n"
                f"⏱️ Aceleración (0-100 km/h): {performance}\n"
                f"🔧 Torque: {torque}\n\n"
                f"💵 INFORMACIÓN GENERAL:\n"
                f"💲 Precio: {price_str}\n"
                f"⛽ Combustible: {fuel}\n"
                f"🪑 Asientos: {seats_str}\n"
                + "─" * 100
            )
            
            etiqueta = customtkinter.CTkLabel(scroll_frame, text=auto_info, anchor="w", justify="left", 
                                            font=("Arial", 14))
            etiqueta.pack(pady=10, anchor="w", padx=10, fill="x")

    # Botón de volver al inicio también en la parte inferior
    boton_volver_abajo = customtkinter.CTkButton(frame, text="← Volver al inicio", 
                                               command=lambda: [resetear_filtros(), mostrar_ventana("inicio")],
                                               fg_color="#ff7b00", hover_color="#3a3a3a",
                                               font=("Arial", 14, "bold"))
    boton_volver_abajo.pack(pady=20, side="bottom")

# Función para resetear los filtros
def resetear_filtros():
    respuestas.update({
        "presupuesto_min": 0,
        "presupuesto_max": float('inf'),
        "combustible": "",
        "asientos": 0,
        "marca": "",
        "hp_min": 0,
        "hp_max": float('inf')
    })

# ================= FLUJO =================
def siguiente_filtro(actual):
    orden = ["presupuesto", "combustible", "asientos", "marca", "hp"]
    idx = orden.index(actual)
    if idx + 1 < len(orden):
        mostrar_filtro(orden[idx + 1])
    else:
        mostrar_sugerencias()

def mostrar_ventana(nombre):
    for f in frames.values():
        f.pack_forget()
    frames[nombre].pack(fill="both", expand=True)

# Iniciar app
resetear_filtros()
mostrar_ventana("inicio")
ventana.mainloop()