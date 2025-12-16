import os
from datetime import date, time

import streamlit as st
from dotenv import load_dotenv
from google import genai  # SDK nueva

# 1) Cargar variables de entorno del archivo .env
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

client = None
if gemini_api_key:
    # La SDK nueva usa un Client central
    client = genai.Client(api_key=gemini_api_key)

# 2) Configuración de la página
st.set_page_config(
    page_title="SesiónSimple IA (Gemini)",
    page_icon="🧠",
    layout="centered"
)

# 3) Título
st.title("🧠 SesiónSimple IA – Generador de recodatorios de turnos (Gemini)")

# 4) Descripción
st.write(
    """
Esta aplicación web, desarrollada con **Streamlit**, genera mensajes de recordatorio de turnos
para pacientes o clientes usando **Gemini (Google)**.

Completá los datos del turno, elegí el tono del mensaje y hacé clic en el botón para obtener un texto
listo para copiar y pegar en WhatsApp o email.
"""
)

st.markdown("---")

# 5) Formulario de entrada de datos del turno
st.subheader("Datos del turno")

col1, col2 = st.columns(2)

with col1:
    nombre_profesional = st.text_input("Nombre del profesional", value="")
    nombre_paciente = st.text_input("Nombre del paciente/cliente", value="")
    fecha_turno = st.date_input("Fecha del turno", value=date.today())

with col2:
    hora_turno = st.time_input("Hora del turno", value=time(10, 0))
    modalidad = st.selectbox("Modalidad", ["Presencial", "Online"])
    canal = st.selectbox("Canal de envío", ["WhatsApp", "Email"])

tono = st.selectbox(
    "Tono del mensaje",
    ["Formal", "Cálido", "Breve", "Detallado"]
)

instrucciones_adicionales = st.text_area(
    "Instrucciones adicionales (opcional)",
    placeholder="Ej: mencionar que traiga estudios, recordar llegar 10 minutos antes, etc."
)

st.markdown("---")

# 6) Botón de acción (tarea específica)
generar = st.button("✨ Generar recordatorio con IA (Gemini)")

if generar:
    # Validaciones básicas
    if not gemini_api_key:
        st.error("No se encontró la GEMINI_API_KEY. Asegurate de tener un archivo .env con tu clave de Gemini.")
    elif client is None:
        st.error("No se pudo inicializar el cliente de Gemini. Revisá la API key.")
    elif not nombre_profesional or not nombre_paciente:
        st.error("Por favor completá al menos el nombre del profesional y del paciente.")
    else:
        # 7) Prompt que se envía a la IA (Gemini)
        prompt = f"""
Sos un asistente especializado en redactar mensajes de recordatorio de turnos
para profesionales de la salud y bienestar (psicología, nutrición, kinesiología, etc.).

Escribí un único mensaje claro y amable en español neutro, listo para copiar y pegar por {canal}.

Datos del turno:
- Profesional: {nombre_profesional}
- Paciente/cliente: {nombre_paciente}
- Fecha: {fecha_turno.strftime('%d/%m/%Y')}
- Hora: {hora_turno.strftime('%H:%M')}
- Modalidad: {modalidad}
- Tono deseado: {tono}
- Instrucciones adicionales: {instrucciones_adicionales or 'Ninguna'}

El mensaje debe:
- Saludar al paciente por su nombre.
- Recordar fecha, hora y modalidad del turno.
- Mencionar el lugar si es presencial o indicar que se enviará enlace si es online, si corresponde.
- Incluir una frase amable de cierre.
- Ser corto y directo, respetando el tono indicado.

No expliques lo que estás haciendo, solo devolvé el texto final del mensaje.
"""

        with st.spinner("Generando mensaje con IA (Gemini)..."):
            try:
                # SDK nueva: se usa client.models.generate_content
                response = client.models.generate_content(
                    model="gemini-2.0-flash",  # modelo recomendado en la SDK nueva
                    contents=prompt,
                )

                mensaje = (response.text or "").strip()

                if not mensaje:
                    st.error("La respuesta de Gemini vino vacía. Probá de nuevo o revisá el prompt.")
                else:
                    st.success("Mensaje generado:")
                    st.text_area(
                        "Mensaje listo para copiar",
                        value=mensaje,
                        height=200
                    )
            except Exception as e:
                st.error(f"Ocurrió un error al llamar a Gemini: {e}")

st.markdown("---")

# 10) Sección "Cómo funciona"
st.subheader("🧩 ¿Cómo funciona este producto?")

st.markdown(
    """
### Características clave
- Genera mensajes personalizados de recordatorio de turno usando **IA de Gemini**.
- Permite elegir el tono del mensaje (formal, cálido, breve, detallado).
- Adapta el contenido al canal elegido (WhatsApp o Email).

### Cómo realizar solicitudes
1. Ingresá los datos del turno (profesional, paciente, fecha, hora, modalidad y canal).  
2. Elegí el tono que querés para el mensaje.  
3. (Opcional) Escribí instrucciones adicionales.  
4. Hacé clic en **“✨ Generar recordatorio con IA (Gemini)”**.

### Qué podés esperar como resultado
- Un mensaje en español neutro, listo para copiar y pegar.  
- Un texto claro, amable y enfocado en recordar la cita.  
- Un estilo consistente, que podés reutilizar para todos tus pacientes.

> Recomendación: revisá siempre el mensaje antes de enviarlo, especialmente si trabajás con
> información sensible o necesitás cumplir requisitos legales específicos.
"""
)
