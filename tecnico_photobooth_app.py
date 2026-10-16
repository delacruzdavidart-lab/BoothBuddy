import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(
    page_title="Técnico Virtual Photobooth - Soporte 24/7",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('''
    <style>
    .main-title { font-size: 2.6rem; color: #FF007F; font-weight: 800; text-align: center; }
    .sub-title { font-size: 1.2rem; color: #4A4A4A; text-align: center; margin-bottom: 25px; }
    </style>
''', unsafe_allow_html=True)

# 2. Configuración de la API Key
api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

st.sidebar.title("⚙️ Configuración")
user_key_input = st.sidebar.text_input(
    "Clave API de Gemini:",
    value=api_key,
    type="password",
    help="Consíguela gratis en Google AI Studio"
)

if user_key_input:
    api_key = user_key_input

if not api_key:
    st.sidebar.warning("⚠️ Ingresa tu API Key para activar la Inteligencia Artificial.")
else:
    st.sidebar.success("✅ API Key lista.")

st.sidebar.markdown("---")
st.sidebar.subheader("📱 Soporte Humano Directo")
whatsapp_num = st.sidebar.text_input("Número WhatsApp Técnico:", value="5210000000000")

p = "https://" + "wa.me/"
wa_url = f"{p}{whatsapp_num}?text=Hola,%20necesito%20soporte%20tecnico"

st.sidebar.markdown(f"[💬 Contactar por WhatsApp]({wa_url})")

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Cobertura Técnica")
st.sidebar.markdown('''
- **Impresoras**: DNP (RX1, DS620), Mitsubishi, Selphy.
- **Cámaras**: Canon, Nikon, Sony.
- **Software**: Snappic, Breeze Booth, DSLRBooth, LumaBooth.
- **Iluminación**: Flashes Godox.
''')

st.markdown("<h1 class='main-title'>🛠️ Técnico Virtual Photobooth</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Asistente IA de Diagnóstico y Solución Inmediata de Fallas en Eventos</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🖨️ Impresoras", "DNP / Selphy / Mitsubishi")
col2.metric("📸 Cámaras", "Canon / Nikon / Sony")
col3.metric("💻 Software", "Snappic / Breeze / DSLRBooth")
col4.metric("⚡ Sincronización", "Flashes & Triggers Godox")

st.markdown("---")

SYSTEM_PROMPT = '''
Eres el Técnico Virtual Experto en Photobooths (Cabinas de fotos, Espejos Mágicos, Plataformas 360).
Tu objetivo es ayudar a operadores de eventos a resolver fallas técnicas de forma rápida, directa, práctica y cordial.

Reglas clave de respuesta:
1. Da pasos numerados (1, 2, 3) cortos y directos porque el operador está en medio de un evento.
2. Para IMPRESORAS (DNP, Selphy, Mitsubishi):
   - Verificar encendido (LED verde), cable USB directo al PC (sin hub).
   - Para error 'Ribbon End' o Papel: recolocar consumibles, tensar cinta, limpiar sensores y reiniciar.
   - Para impresiones lentas o atascadas: vaciar cola de impresión o reiniciar Print Spooler.
3. Para CÁMARAS (Canon/Nikon/Sony):
   - Para Live View negro o 'Camera Busy': poner modo Manual (M), cerrar programas como EOS Utility, reconectar USB directo.
   - Para apagos o sobrecalentamiento: recomendar batería ficticia (dummy battery) y desactivar ahorro de energía.
4. Para SOFTWARE (Snappic, Breeze, DSLRBooth, LumaBooth):
   - Verificar si 'Photo Booth Print Server' está activo, comprobar red Wi-Fi e IP, verificar permisos en iPad/PC.
'''

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "¡Hola! Soy tu **Técnico Virtual de Photobooth**. ¿Qué problema o error estás teniendo en tu evento?"}
    ]

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

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Escribe tu falla técnica aquí...")
prompt_to_process = user_input or quick_query

if prompt_to_process:
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

    bot_reply = ""
    if api_key:
        try:
            genai.configure(api_key=api_key)
            
            # Autodetección dinámica de modelo activo
            model_name = None
            try:
                models_list = genai.list_models()
                available = [m.name for m in models_list if 'generateContent' in m.supported_generation_methods]
                if available:
                    for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-2.0-flash-exp', 'models/gemini-1.5-pro']:
                        if pref in available:
                            model_name = pref
                            break
                    if not model_name:
                        model_name = available[0]
            except Exception:
                pass

            if not model_name:
                model_name = 'gemini-1.5-flash'

            model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(prompt_to_process)
            bot_reply = response.text

        except Exception as e:
            bot_reply = f"❌ Error al consultar la API de Gemini: {str(e)}\n\n*Tip: Revisa que la API Key de Google AI Studio sea válida y esté activa.*"
    else:
        bot_reply = f"ℹ️ **Respuesta del Técnico (Modo demostración base de datos)**:\n\n"
        bot_reply += f"Para respuestas personalizadas con la IA, ingresa tu API Key en la barra lateral izquierda.\n\n"
        bot_reply += f"**Pasos recomendados para '{prompt_to_process}'**:\n"
        bot_reply += "1. **Conexiones**: Verifica que el cable USB vaya directo al equipo (sin hubs) y que la luz de estado esté en verde estable.\n"
        bot_reply += "2. **Reinicio de Spooler**: Abre la consola de Windows (`cmd`) como administrador y ejecuta `net stop spooler` y luego `net start spooler`.\n"
        bot_reply += "3. **Software**: Confirma que el *Photo Booth Print Server* esté ejecutándose y la impresora esté seleccionada como predeterminada.\n"
        bot_reply += "4. **Cámara**: Asegúrate de tener la rueda en modo Manual (M), enfoque en Manual o fijo, y cerrar programas secundarios."

    bot_reply += f"\n\n---\n🆘 **¿No se solucionó el problema?** [Contacta al Soporte Humano por WhatsApp]({wa_url})"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
