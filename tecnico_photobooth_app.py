import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. Configuración de la página
st.set_page_config(
    page_title="Técnico Virtual Photobooth - Soporte 24/7",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado en CSS
st.markdown("""
    <style>
    .main-title { font-size: 2.6rem; color: #FF007F; font-weight: 800; text-align: center; }
    .sub-title { font-size: 1.2rem; color: #4A4A4A; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# 2. Barra lateral - Configuración y accesos
st.sidebar.title("⚙️ Configuración del Técnico")
api_key = st.sidebar.text_input("Clave API de Gemini:", type="password", help="Consíguela gratis en Google AI Studio")

st.sidebar.markdown("---")
st.sidebar.subheader("📱 Soporte Humano Directo")
whatsapp_num = st.sidebar.text_input("Número WhatsApp Técnico (con código de país):", value="5210000000000", help="Ejemplo: 521XXXXXXXXXX")

wa_custom_msg = urllib.parse.quote("¡Hola! Necesito soporte técnico humano urgente para mi evento de Photobooth.")
base_wa = "https://" + "wa.me/"
wa_url = f"{base_wa}{whatsapp_num}?text={wa_custom_msg}"

st.sidebar.markdown(f'''
<a href="{wa_url}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold;">
        💬 Contactar Técnico Humano por WhatsApp
    </div>
</a>
''', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Cobertura Técnica")
st.sidebar.markdown("""
- **Impresoras**: DNP (RX1, DS620), Mitsubishi, Selphy (Ribbon, Spooler, Cortes 2").
- **Cámaras**: Canon, Nikon, Sony (Live View, Error 70/80, Camera Busy).
- **Software**: Snappic, Breeze Booth, DSLRBooth, LumaBooth, LA Photo Party.
- **Iluminación**: Flashes Godox, Triggers e Iluminación LED.
- **Redes e iPad**: AirPrint, Print Server, Hotspots de eventos.
""")

st.sidebar.info("💡 **Tip rápido**: Si la impresora no reacciona en Windows, reinicia el *Print Spooler* ejecutando `net stop spooler` y `net start spooler` en CMD.")

# 3. Encabezado principal
st.markdown("<h1 class='main-title'>🛠️ Técnico Virtual Photobooth</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Asistente IA de Diagnóstico y Solución Inmediata de Fallas en Eventos</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🖨️ Impresoras", "DNP / Selphy / Mitsubishi")
col2.metric("📸 Cámaras", "Canon / Nikon / Sony")
col3.metric("💻 Software", "Snappic / Breeze / DSLRBooth")
col4.metric("⚡ Sincronización", "Flashes & Triggers Godox")

st.markdown("---")

# 4. Prompt de Sistema de la Base de Datos
SYSTEM_PROMPT = """
Eres el Técnico Virtual Experto en Photobooths (Cabinas de fotos, Espejos Mágicos, Plataformas 360).
Tu objetivo es ayudar a operadores de eventos a resolver fallas técnicas de forma rápida, directa, práctica y cordial.

Reglas clave de respuesta:
1. Da pasos numerados (1, 2, 3) cortos y directos porque el operador está en medio de un evento.
2. Para IMPRESORAS (DNP, Selphy, Mitsubishi):
   - Verificar encendido (LED verde), cable USB directo al PC (sin hub).
   - Para error 'Ribbon End' o Papel: recolocar consumibles, tensar cinta, limpiar sensores y reiniciar.
   - Para impresiones lentas o atascadas: vaciar cola de impresión o reiniciar Print Spooler (`net stop spooler` / `net start spooler`).
3. Para CÁMARAS (Canon/Nikon/Sony):
   - Para Live View negro o 'Camera Busy': poner modo Manual (M), cerrar programas como EOS Utility, reconectar USB directo.
   - Para apagos o sobrecalentamiento: recomendar batería ficticia (dummy battery) y desactivar ahorro de energía.
4. Para SOFTWARE (Snappic, Breeze, DSLRBooth, LumaBooth):
   - Verificar si 'Photo Booth Print Server' está activo, comprobar red Wi-Fi e IP, verificar permisos en iPad/PC.
"""

# 5. Historial de Chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "¡Hola! Soy tu **Técnico Virtual de Photobooth**. ¿Qué problema o error estás teniendo en tu evento? (Ej: *'Mi DNP RX1 no imprime'*, *'Live View negro en DSLRBooth'*, *'Error Ribbon End'*)."}
    ]

# Botones de consulta rápida
st.subheader("⚡ Accesos Rápidos de Diagnóstico")
q1, q2, q3, q4 = st.columns(4)

quick_query = None
if q1.button("🖨️ DNP RX1 no imprime"):
    quick_query = "La impresora DNP RX1 no imprime desde mi software de photobooth, ¿qué hago?"
if q2.button("📷 Live View congelado / negro"):
    quick_query = "La cámara Canon muestra pantalla negra en el Live View del software, ¿cómo lo soluciono?"
if q3.button("🎗️ Error 'Ribbon End'"):
    quick_query = "Tengo error Ribbon End en la impresora de sublimación pero la cinta es nueva, ¿cómo se arregla?"
if q4.button("📶 iPad no conecta al servidor"):
    quick_query = "El iPad con Snappic / Breeze no detecta el servidor de impresión en la red del evento."

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada de usuario
user_input = st.chat_input("Escribe tu falla técnica aquí...")
prompt_to_process = user_input or quick_query

if prompt_to_process:
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

    if api_key:
        genai.configure(api_key=api_key)
        # Bucle con fallback de modelos para evitar errores 404 de versión
        model_candidates = ["gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        bot_reply = None
        last_err = None

        for model_name in model_candidates:
            try:
                model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
                response = model.generate_content(prompt_to_process)
                if response and response.text:
                    bot_reply = response.text
                    break
            except Exception as e:
                last_err = e

        if not bot_reply:
            bot_reply = f"❌ Error de conexión con Gemini API: {str(last_err)}\n\n*Tip*: Verifica que tu API Key sea válida y esté activa en Google AI Studio."
    else:
        bot_reply = f"ℹ️ **Respuesta del Técnico (Modo demostración base de datos)**:\n\n"
        bot_reply += f"Para consultas libres con la IA, ingresa tu API Key en la barra izquierda.\n\n"
        bot_reply += f"**Pasos recomendados para '{prompt_to_process}'**:\n"
        bot_reply += "1. **Conexiones**: Verifica que el cable USB vaya directo al equipo (sin hubs) y que la luz de estado esté en verde estable.\n"
        bot_reply += "2. **Reinicio de Spooler**: Abre la consola de Windows (`cmd`) como administrador y ejecuta `net stop spooler` y luego `net start spooler`.\n"
        bot_reply += "3. **Software**: Confirma que el *Photo Booth Print Server* esté ejecutándose y la impresora esté seleccionada como predeterminada.\n"
        bot_reply += "4. **Cámara**: Asegúrate de tener la rueda en modo Manual (M), enfoque en Manual o fijo, y cerrar programas secundarios."

    # Opción de escalar a WhatsApp al final de la respuesta
    bot_reply += f"\n\n---\n🆘 **¿No se solucionó el problema?** [Contacta al Soporte Humano por WhatsApp]({wa_url})"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
