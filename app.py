"""
Ejecutar localmente:  streamlit run app.py
"""
import base64
from pathlib import Path

import streamlit as st
import sympy as sp

import motor
from motor import ErrorEntrada

st.set_page_config(
    page_title="Análisis de funciones racionales",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)
UNIVERSIDAD = "Benemérita Universidad Autónoma de Chiapas"
MATERIA = "Cálculo Diferencial"
DOCENTE = "Mtro. Andrade"
SEMESTRE = "Semestre: Segundo"
INTEGRANTES = "·Juan Vázquez Simá ·Eduardo Jiménez Pérez ·Hugo Martinez López ·Kael Yurem Alegría Morales"
CARPETA_IMAGENES = Path(__file__).parent / "assets"
LOGO_IZQUIERDO = "logo_universidad.png" 
LOGO_DERECHO = "logo_facultad.png"
MAX_BYTES_LOGO = 1_500_000      
ORDEN = ["portada", "presentacion", "ingresa_datos", "confirmar_funcion",
         "introducir_funcion", "confirmar_datos", "resultados", "otro_calculo",
         "despedida"]
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@300;400;600&family=Figtree:wght@300;400;500;600&display=swap');
:root{
  --noche:#050A18; --abismo:#0A1230; --verde:#46FFB2; --turquesa:#22D3EE;
  --violeta:#9B6BFF; --magenta:#FF6BD6; --texto:#EAF2FF; --suave:#A9B9D6;
}
html, body, .stApp{ background:var(--noche) !important; color:var(--texto); font-family:'Figtree',sans-serif; }
[data-testid="stAppViewContainer"], [data-testid="stMain"]{ background:transparent !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu{ display:none !important; }

/* Aurora: tres capas de luz que derivan lentamente */
.stApp::before{
  content:""; position:fixed; inset:-25% -15%; z-index:0; pointer-events:none;
  background:
    radial-gradient(40% 35% at 20% 25%, rgba(70,255,178,.55), transparent 70%),
    radial-gradient(38% 40% at 80% 20%, rgba(155,107,255,.50), transparent 70%),
    radial-gradient(45% 40% at 60% 85%, rgba(34,211,238,.42), transparent 70%),
    radial-gradient(30% 30% at 10% 90%, rgba(255,107,214,.35), transparent 70%);
  filter:blur(40px) saturate(120%);
  animation:deriva 26s ease-in-out infinite alternate;
}
.stApp::after{
  content:""; position:fixed; left:0; right:0; top:0; height:75vh; z-index:0; pointer-events:none;
  background:repeating-linear-gradient(90deg, transparent 0 38px, rgba(70,255,178,.10) 60px, rgba(34,211,238,.17) 90px, transparent 130px);
  -webkit-mask-image:linear-gradient(to bottom,#000 0%,transparent 100%);
          mask-image:linear-gradient(to bottom,#000 0%,transparent 100%);
  filter:blur(14px); mix-blend-mode:screen;
  animation:cortina 14s ease-in-out infinite alternate;
}
@keyframes deriva{ from{transform:translate3d(-3%,-2%,0) rotate(0) scale(1)} to{transform:translate3d(4%,3%,0) rotate(6deg) scale(1.12)} }
@keyframes cortina{ from{transform:translateX(-30px) skewX(-6deg);opacity:.7} to{transform:translateX(30px) skewX(6deg);opacity:1} }
@keyframes brillo{ to{background-position:200% center} }
@media (prefers-reduced-motion:reduce){ .stApp::before,.stApp::after,.hero h1{animation:none !important} }
.block-container{ max-width:760px; padding-top:2rem; padding-bottom:3rem; position:relative; z-index:2; }
/* Encabezados */
.ruta{ display:flex; gap:6px; margin:0 0 1.8rem; }
.ruta i{ flex:1; height:4px; border-radius:4px; background:rgba(255,255,255,.14); }
.ruta i.on{ background:linear-gradient(90deg,var(--verde),var(--turquesa)); box-shadow:0 0 12px rgba(70,255,178,.6); }
.cab h1{
  font-family:'Unbounded',sans-serif; font-weight:600; font-size:clamp(1.6rem,5.2vw,2.5rem);
  line-height:1.15; margin:0 0 .6rem; letter-spacing:-.01em;
  background:linear-gradient(100deg,#fff 0%,var(--verde) 38%,var(--turquesa) 62%,var(--magenta) 100%);
  background-size:200% auto; -webkit-background-clip:text; background-clip:text; color:transparent;
}
.hero h1{ font-size:clamp(2rem,7.5vw,3.6rem); animation:brillo 14s linear infinite; }
.cab p.sub{ color:var(--suave); font-size:1.05rem; line-height:1.55; margin:0 0 1.4rem; max-width:60ch; }
.inst{ color:var(--suave); font-size:1rem; margin:0 0 1rem; }
.logos{ display:flex; justify-content:space-between; align-items:center; gap:1rem; margin:0 0 1.4rem; }
.logo{ display:inline-flex; align-items:center; justify-content:center; padding:.55rem .8rem;
  border-radius:18px; background:rgba(255,255,255,.94);
  box-shadow:0 8px 30px rgba(0,0,0,.35), inset 0 0 0 1px rgba(255,255,255,.4); }
.logo img{ display:block; height:clamp(44px,9vw,72px); width:auto; max-width:38vw; object-fit:contain; }
.formula{ font-family:'Unbounded',sans-serif; font-weight:300; font-size:clamp(1.2rem,4vw,1.8rem);
  color:var(--turquesa); text-shadow:0 0 24px rgba(34,211,238,.7); margin:.4rem 0 1.6rem; }
.ficha{ color:var(--texto); line-height:1.8; font-size:1.02rem; margin-bottom:1.6rem; }
.chips{ display:flex; flex-wrap:wrap; gap:.6rem; margin:.8rem 0 0; }
.chips span{ padding:.5rem 1rem; border-radius:999px; border:1px solid rgba(255,255,255,.2);
  background:rgba(255,255,255,.06); font-size:.95rem; }
.rt{ font-family:'Unbounded',sans-serif; font-weight:400; font-size:1.05rem; margin:0 0 .6rem; color:var(--verde); }
.cifra{ font-family:'Unbounded',sans-serif; font-weight:600; font-size:2.6rem; color:#fff; line-height:1; }
.cifra small{ display:block; font-family:'Figtree',sans-serif; font-weight:400; font-size:.95rem; color:var(--suave); margin-top:.5rem; }
/* Vidrio */
[class*="st-key-vidrio"]{
  background:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.03));
  border:1px solid rgba(255,255,255,.18); border-radius:28px; padding:1.6rem 1.7rem;
  -webkit-backdrop-filter:blur(22px) saturate(140%); backdrop-filter:blur(22px) saturate(140%);
  box-shadow:0 20px 60px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.25);
  margin-bottom:1rem;
}
.stMarkdown, .stMarkdown p, label, [data-testid="stWidgetLabel"] p{ color:var(--texto) !important; }
.katex{ color:#fff; font-size:1.2em; }
.katex-display{ overflow-x:auto; overflow-y:hidden; padding:.2rem 0; }
/* Botones */
.stButton>button{
  border-radius:16px; border:1px solid rgba(255,255,255,.22); background:rgba(255,255,255,.07);
  color:var(--texto); font-weight:500; padding:.7rem 1rem; transition:all .2s ease;
  -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
}
.stButton>button:hover{ border-color:var(--verde); box-shadow:0 0 22px rgba(70,255,178,.35); color:#fff; }
.stButton>button:focus-visible{ outline:2px solid var(--turquesa); outline-offset:2px; }
.stButton>button[kind="primary"], .stButton>button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(100deg,rgba(70,255,178,.95),rgba(34,211,238,.95)); color:#031018; border:0; font-weight:600;
}
.stButton>button:disabled{ opacity:.35; }
/* Calculadora */
.st-key-calc button{ height:3.2rem; font-family:'Unbounded',sans-serif; font-size:1.05rem; border-radius:14px; padding:0; }
[class*="st-key-calc_op"] button{ color:var(--turquesa); }
[class*="st-key-calc_v"] button{ color:var(--verde); }
[class*="st-key-calc_c"] button{ color:var(--magenta); }
.st-key-calc [data-testid="stHorizontalBlock"]{ flex-direction:row !important; flex-wrap:nowrap !important; gap:.5rem; }
.st-key-calc [data-testid="stColumn"], .st-key-calc [data-testid="column"]{ min-width:0 !important; flex:1 1 0 !important; width:auto !important; }
/* Campos */
.stTextInput input, .stNumberInput input{
  background:rgba(5,10,24,.55) !important; color:#fff !important; border:1px solid rgba(255,255,255,.22) !important;
  border-radius:14px !important; font-size:1.15rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus{ border-color:var(--verde) !important; box-shadow:0 0 0 2px rgba(70,255,178,.25) !important; }
[data-testid="stNumberInput"] > div > div{ background:transparent !important; border:0 !important; }
[data-testid="stNumberInput"] button{ background:rgba(255,255,255,.08) !important; color:#fff !important; }

div[role="radiogroup"]{ gap:.6rem; }
div[role="radiogroup"] label{ background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.2);
  padding:.4rem 1.2rem; border-radius:999px; transition:all .2s ease; }
div[role="radiogroup"] label:has(input:checked){ border-color:var(--verde); background:rgba(70,255,178,.15); box-shadow:0 0 18px rgba(70,255,178,.3); }

[data-testid="stExpander"]{ background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.14) !important; border-radius:18px; }
[data-testid="stExpander"] summary p{ color:var(--turquesa) !important; }
[data-testid="stAlert"]{ border-radius:16px; }

@media (max-width:640px){
  .block-container{ padding:1rem .8rem 3rem; }
  [class*="st-key-vidrio"]{ padding:1.1rem; border-radius:22px; }
}
"""
def estado_inicial():
    """Valores por defecto: la app siempre arranca en un estado válido."""
    por_defecto = {"pantalla": "portada", "sabe": "Sí", "gn": 1, "gd": 1,
                   "funcion": "", "ver_pasos": False,
                   "resultado": None, "clave_resultado": None}
    for k, v in por_defecto.items():
        st.session_state.setdefault(k, v)
def reiniciar():
    for k in ("pantalla", "sabe", "gn", "gd", "funcion", "ver_pasos", "resultado", "clave_resultado"):
        st.session_state.pop(k, None)
    for k in [k for k in st.session_state if k.startswith("w_")]:
        del st.session_state[k]
    estado_inicial()
def ir_a(destino):
    st.session_state.pantalla = destino
def _avanzar(destino, accion):
    if accion:
        accion()
    ir_a(destino)
def navegacion(anterior=None, siguiente=None, puede_avanzar=True,
               etiqueta="Siguiente", al_avanzar=None):
    """Botones Regresar / Siguiente presentes en cada carátula."""
    actual = st.session_state.pantalla
    c1, c2 = st.columns(2)
    with c1:
        if anterior:
            st.button("Regresar", key=f"atras_{actual}", on_click=ir_a,
                      args=(anterior,), use_container_width=True)
    with c2:
        if siguiente:
            st.button(etiqueta, key=f"sig_{actual}", on_click=_avanzar,
                      args=(siguiente, al_avanzar), disabled=not puede_avanzar,
                      type="primary", use_container_width=True)
def encabezado(titulo, subtitulo="", hero=False):
    idx = ORDEN.index(st.session_state.pantalla)
    ruta = "".join(f'<i class="{"on" if i <= idx else ""}"></i>' for i in range(len(ORDEN)))
    sub = f'<p class="sub">{subtitulo}</p>' if subtitulo else ""
    clase = "cab hero" if hero else "cab"
    st.markdown(f'<div class="ruta">{ruta}</div><div class="{clase}"><h1>{titulo}</h1>{sub}</div>',
                unsafe_allow_html=True)
def pregunta_si_no(texto, clave):
    """Respuesta cerrada: solo se puede elegir Sí o No (no hay nada que teclear)."""
    return st.radio(texto, ["Sí", "No"], index=None, horizontal=True, key=clave)
def imagen_a_texto(nombre):
    """Lee una imagen de la carpeta assets y la convierte en texto (base64).
    Si el archivo no existe, no es PNG/JPG o pesa demasiado, devuelve None
    y la app sigue funcionando sin ese logo."""
    try:
        ruta = CARPETA_IMAGENES / nombre
        tipo = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ruta.suffix.lower())
        if tipo is None or not ruta.is_file() or ruta.stat().st_size > MAX_BYTES_LOGO:
            return None
        return f"data:{tipo};base64," + base64.b64encode(ruta.read_bytes()).decode()
    except Exception:
        return None
def logo_html(nombre, descripcion):
    """HTML de un logo; si falta la imagen deja un hueco para no mover el otro logo."""
    fuente = imagen_a_texto(nombre)
    if not fuente:
        return "<span></span>"
    return f'<span class="logo"><img src="{fuente}" alt="{descripcion}"></span>'
def portada():
    ficha = f"{MATERIA}<br>Docente: {DOCENTE}<br>{SEMESTRE}"
    if INTEGRANTES:
        ficha += f"<br>{INTEGRANTES}"
    logos = (f'<div class="logos">{logo_html(LOGO_IZQUIERDO, "Logo de la universidad")}'
             f'{logo_html(LOGO_DERECHO, "Logo de la facultad")}</div>')
    st.markdown(
        logos
        + f'<div class="ruta">{"".join(["<i class=on></i>"] + ["<i></i>"] * (len(ORDEN) - 1))}</div>'
        f'<div class="cab hero"><p class="inst">{UNIVERSIDAD}</p>'
        f'<h1>Análisis de funciones racionales</h1>'
        f'<p class="formula">f(x) = P(x) / Q(x)</p>'
        f'<div class="ficha">{ficha}</div></div>',
        unsafe_allow_html=True)
    navegacion(siguiente="presentacion", etiqueta="Comenzar")
def presentacion():
    encabezado("Presentación",
               "Escribe una función racional y obtén su análisis completo, con los límites "
               "calculados por SymPy. Esta app no dibuja gráficas: solo muestra resultados.")
    with st.container(key="vidrio_pres"):
        st.markdown("**Qué vas a obtener**")
        st.markdown('<div class="chips"><span>Ordenada al origen</span><span>Raíces</span>'
                    '<span>Asíntotas verticales</span><span>Asíntota horizontal</span>'
                    '<span>Asíntota oblicua</span><span>Dominio</span><span>Rango</span></div>',
                    unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**Cómo se usa**")
        st.markdown("1. Indica el grado del numerador y del denominador.  \n"
                    "2. Confirma esos grados.  \n"
                    "3. Escribe la función con la calculadora o con el teclado.  \n"
                    "4. Confirma la función y revisa los resultados.")
    navegacion("portada", "ingresa_datos")
def ingresa_datos():
    encabezado("Ingresa los datos",
               "Una función racional es un polinomio entre otro polinomio. "
               "Dinos el grado de cada parte.")
    with st.container(key="vidrio_datos"):
        sabe = st.radio("¿Ya sabes cuál es el grado de la función?", ["Sí", "No"],
                        index=0 if st.session_state.sabe == "Sí" else 1,
                        horizontal=True, key="w_sabe")
        st.session_state.sabe = sabe
        with st.expander("¿Qué significa «grado»?", expanded=(sabe == "No")):
            st.markdown("El **grado** de un polinomio es el mayor exponente de x que aparece. "
                        "Ejemplo: en  f(x) = (x² − 1) / (x + 3)  el numerador tiene **grado 2** "
                        "y el denominador **grado 1**. Un número solo, como 5, tiene grado 0.")
        c1, c2 = st.columns(2)
        gn = c1.number_input("Grado del numerador", min_value=0, max_value=motor.MAX_GRADO,
                             value=int(st.session_state.gn), step=1, key="w_gn")
        gd = c2.number_input("Grado del denominador", min_value=0, max_value=motor.MAX_GRADO,
                             value=int(st.session_state.gd), step=1, key="w_gd")
        st.session_state.gn = int(gn or 0)
        st.session_state.gd = int(gd or 0)
        st.caption(f"Se aceptan grados del 0 al {motor.MAX_GRADO}.")
    navegacion("presentacion", "confirmar_funcion")
def confirmar_funcion():
    encabezado("Confirma los grados", "Revisa que sean los de tu función.")
    gn, gd = st.session_state.gn, st.session_state.gd
    with st.container(key="vidrio_conf1"):
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="cifra">{gn}<small>grado del numerador</small></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="cifra">{gd}<small>grado del denominador</small></div>', unsafe_allow_html=True)
        st.markdown("")
        resp = pregunta_si_no("¿El grado de la función ingresada es correcto?", "w_conf1")
    destino = "introducir_funcion" if resp == "Sí" else "ingresa_datos"
    navegacion("ingresa_datos", destino, puede_avanzar=resp is not None)
TECLAS = [
    [("7", "7", "n"), ("8", "8", "n"), ("9", "9", "n"), ("(", "(", "op"), (")", ")", "op")],
    [("4", "4", "n"), ("5", "5", "n"), ("6", "6", "n"), ("x", "x", "v"), ("^", "^", "op")],
    [("1", "1", "n"), ("2", "2", "n"), ("3", "3", "n"), ("+", "+", "op"), ("−", "-", "op")],
    [("0", "0", "n"), (".", ".", "n"), ("×", "*", "op"), ("÷", "/", "op"), ("⌫", "BORRAR", "c")],
]
def tecla(valor):
    """Callback de la calculadora: edita el texto de la función."""
    actual = st.session_state.get("w_expr", "")
    if valor == "BORRAR":
        nuevo = actual[:-1]
    elif valor == "LIMPIAR":
        nuevo = ""
    else:
        nuevo = actual + valor
    st.session_state["w_expr"] = nuevo[:motor.MAX_CARACTERES]
def calculadora():
    with st.container(key="calc"):
        for i, fila in enumerate(TECLAS):
            cols = st.columns(len(fila))
            for j, (etiqueta, valor, tipo) in enumerate(fila):
                cols[j].button(etiqueta, key=f"calc_{tipo}_{i}{j}", on_click=tecla,
                               args=(valor,), use_container_width=True)
        cols = st.columns([1, 1, 3])
        cols[0].button("x²", key="calc_v_sq", on_click=tecla, args=("x^2",), use_container_width=True)
        cols[1].button("x³", key="calc_v_cu", on_click=tecla, args=("x^3",), use_container_width=True)
        cols[2].button("Borrar todo", key="calc_c_all", on_click=tecla, args=("LIMPIAR",), use_container_width=True)
def introducir_funcion():
    encabezado("Introduce la función",
               "Usa la calculadora o escribe directamente. Ejemplo:  (x^2 - 1)/(x - 2)")
    if "w_expr" not in st.session_state:
        st.session_state["w_expr"] = st.session_state.funcion
    valida = False
    with st.container(key="vidrio_calc"):
        st.text_input("f(x) =", key="w_expr", max_chars=motor.MAX_CARACTERES,
                      placeholder="(x^2 - 1)/(x - 2)")
        texto = st.session_state.get("w_expr", "")
        st.session_state.funcion = texto
        if texto.strip():
            try:
                st.latex("f(x)=" + sp.latex(motor.interpretar(texto)["f"]))
                valida = True
            except ErrorEntrada as e:
                st.warning(str(e))
            except Exception:
                st.warning("No pude leer esa expresión. Revisa los símbolos.")
        else:
            st.caption("Todavía no hay nada escrito.")
        st.markdown("")
        calculadora()
        st.caption("Para dividir polinomios usa paréntesis: (x+1)/(x−2). "
                   "Para x al cuadrado usa x^2.")
    navegacion("confirmar_funcion", "confirmar_datos", puede_avanzar=valida)
def confirmar_datos():
    encabezado("Confirma la función", "Es la última revisión antes de calcular.")
    try:
        datos = motor.interpretar(st.session_state.funcion)
    except Exception:
        st.warning("La función guardada no es válida. Regresa y corrígela.")
        navegacion("introducir_funcion")
        return
    coincide = (datos["gn"] == st.session_state.gn and datos["gd"] == st.session_state.gd)
    with st.container(key="vidrio_conf2"):
        st.latex("f(x)=" + sp.latex(datos["f"]))
        st.markdown(f"Grados detectados: numerador **{datos['gn']}**, denominador **{datos['gd']}**.")
        if not coincide:
            st.warning(f"Indicaste grados {st.session_state.gn} y {st.session_state.gd}, pero la función "
                       f"tiene {datos['gn']} y {datos['gd']}. Elige «No» para corregir la función "
                       "o regresa dos pasos para corregir los grados.")
        resp = pregunta_si_no("¿La f(x) es correcta?", "w_conf2")
    destino = "resultados" if resp == "Sí" else "introducir_funcion"
    bloqueado = resp is None or (resp == "Sí" and not coincide)
    navegacion("introducir_funcion", destino, puede_avanzar=not bloqueado)
def _pintar_pasos(pasos):
    for tipo, contenido in pasos:
        if tipo == "t":
            st.markdown(contenido)
        else:
            st.latex(contenido)
def resultados():
    encabezado("Resultados", "Análisis completo calculado con SymPy.")
    try:
        datos = motor.interpretar(st.session_state.funcion)
        if st.session_state.clave_resultado != st.session_state.funcion:
            with st.spinner("Calculando con SymPy…"):
                st.session_state.resultado = motor.analizar(datos)
                st.session_state.clave_resultado = st.session_state.funcion
        res = st.session_state.resultado
    except Exception:
        st.error("No se pudo analizar esta función. Regresa y prueba con otra.")
        navegacion("confirmar_datos")
        return

    with st.container(key="vidrio_fx"):
        st.latex("f(x)=" + res["f_tex"])
        if res["simplificada_tex"]:
            st.caption("Después de cancelar factores comunes:")
            st.latex("f(x)=" + res["simplificada_tex"])
        ver = st.toggle("Mostrar el procedimiento completo", value=st.session_state.ver_pasos, key="w_ver")
        st.session_state.ver_pasos = ver

    for i, item in enumerate(res["items"]):
        with st.container(key=f"vidrio_r{i}"):
            st.markdown(f'<h3 class="rt">{item["titulo"]}</h3>', unsafe_allow_html=True)
            for linea in item["lineas"]:
                st.latex(linea)
            for nota in item["notas"]:
                st.markdown(nota)
            if ver and item["pasos"]:
                with st.expander("Procedimiento", expanded=True):
                    _pintar_pasos(item["pasos"])
    navegacion("confirmar_datos", "otro_calculo", etiqueta="Continuar")
def _nuevo_calculo():
    for k in ("funcion", "resultado", "clave_resultado"):
        st.session_state[k] = {"funcion": "", "resultado": None, "clave_resultado": None}[k]
    for k in ("w_expr", "w_conf1", "w_conf2"):
        st.session_state.pop(k, None)
def otro_calculo():
    encabezado("¿Otro cálculo?", "Puedes analizar otra función cuando quieras.")
    with st.container(key="vidrio_otro"):
        resp = pregunta_si_no("¿Quieres hacer otro cálculo?", "w_otro")
    if resp == "Sí":
        navegacion("resultados", "ingresa_datos", al_avanzar=_nuevo_calculo)
    else:
        navegacion("resultados", "despedida", puede_avanzar=resp is not None)
def despedida():
    st.markdown(
        f'<div class="ruta">{"".join(["<i class=on></i>"] * len(ORDEN))}</div>'
        '<div class="cab hero"><h1>¡Suerte con tus tareas!</h1>'
        '<p class="sub">Gracias por usar el análisis de funciones racionales.</p></div>',
        unsafe_allow_html=True)
    navegacion("otro_calculo", "portada", etiqueta="Volver al inicio", al_avanzar=reiniciar)
CARATULAS = {
    "portada": portada, "presentacion": presentacion, "ingresa_datos": ingresa_datos,
    "confirmar_funcion": confirmar_funcion, "introducir_funcion": introducir_funcion,
    "confirmar_datos": confirmar_datos, "resultados": resultados,
    "otro_calculo": otro_calculo, "despedida": despedida,
}
def pantalla_de_error():
    with st.container(key="vidrio_error"):
        st.markdown('<h3 class="rt">Algo salió distinto de lo esperado</h3>', unsafe_allow_html=True)
        st.markdown("La app sigue funcionando. Vuelve al inicio para empezar de nuevo.")
        st.button("Volver al inicio", key="err_reset", on_click=reiniciar, type="primary")
def main():
    estado_inicial()
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    pantalla = st.session_state.pantalla
    if pantalla not in CARATULAS:
        pantalla = st.session_state.pantalla = "portada"
    try:
        CARATULAS[pantalla]()
    except Exception:
        pantalla_de_error()
main()