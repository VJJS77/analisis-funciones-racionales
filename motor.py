import re
from types import SimpleNamespace

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
X = sp.Symbol("x", real=True)
MAX_GRADO = 6          # grado máximo permitido para numerador y denominador
MAX_PESO = 30          # tope de "tamaño" de la expresión antes de evaluarla
MAX_EXPONENTE = 12     # exponente máximo escrito por el usuario
MAX_CARACTERES = 80    # longitud máxima del texto
TRANSF = standard_transformations + (implicit_multiplication_application, convert_xor)
class ErrorEntrada(Exception):
    """Error de captura con un mensaje pensado para mostrarse al usuario."""
def _peso(e):
    """Cota del tamaño de la expresión SIN evaluarla (evita potencias gigantes)."""
    if e.is_Number or e.is_Symbol:
        return 1
    if e.is_Add:
        return max(_peso(a) for a in e.args)
    if e.is_Mul:
        return sum(_peso(a) for a in e.args)
    if e.is_Pow:
        base, exp = e.args
        if not exp.is_Integer or abs(int(exp)) > MAX_EXPONENTE:
            raise ErrorEntrada(
                f"Los exponentes deben ser enteros de a lo más {MAX_EXPONENTE}."
            )
        return abs(int(exp)) * _peso(base)
    raise ErrorEntrada("Hay una operación que no está permitida.")
def _grado(p):
    return 0 if p.is_zero else int(p.degree())
def interpretar(texto):
    t = (texto or "").strip()
    if not t:
        raise ErrorEntrada("Escribe una función o usa la calculadora.")
    # Acepta "f(x)=" o "y=" al inicio
    t = re.sub(r"^\s*(f\s*\(\s*x\s*\)|y)\s*=", "", t, flags=re.I)
    for viejo, nuevo in (("÷", "/"), ("×", "*"), ("−", "-"), ("–", "-"),
                         (",", "."), ("**", "^"), ("X", "x")):
        t = t.replace(viejo, nuevo)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > MAX_CARACTERES:
        raise ErrorEntrada(f"La función es muy larga (máximo {MAX_CARACTERES} caracteres).")
    if not re.fullmatch(r"[0-9x+\-*/^().\s]+", t):
        raise ErrorEntrada(
            "Solo se permiten números, la variable x y los símbolos + − × ÷ ^ ( )."
        )
    if t.count("(") != t.count(")"):
        raise ErrorEntrada("Los paréntesis no están balanceados: revisa cuáles faltan o sobran.")
    locales = {"x": X}
    try:  # 1) árbol sin evaluar: se mide antes de calcular nada
        arbol = parse_expr(t, local_dict=locales, transformations=TRANSF, evaluate=False)
        if _peso(arbol) > MAX_PESO:
            raise ErrorEntrada("La función es demasiado grande para analizarla aquí.")
        # 2) ya es seguro evaluarla
        f = parse_expr(t, local_dict=locales, transformations=TRANSF)
    except ErrorEntrada:
        raise
    except Exception:
        raise ErrorEntrada(
            "No pude entender la expresión. Revisa que cada operador tenga números o x a ambos lados."
        )
    if f.has(sp.Float):
        f = sp.nsimplify(f, rational=True)
    if f.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise ErrorEntrada("La expresión divide entre cero.")
    if not f.free_symbols <= {X}:
        raise ErrorEntrada("Solo se puede usar la variable x.")
    if f == 0:
        raise ErrorEntrada("La función no puede ser cero.")
    n, d = sp.fraction(sp.together(f))
    try:
        pn, pd = sp.Poly(n, X), sp.Poly(d, X)
    except sp.PolynomialError:
        raise ErrorEntrada("Debe ser una función racional: un polinomio entre otro polinomio.")
    if pd.is_zero:
        raise ErrorEntrada("El denominador no puede ser cero.")
    return {"f": f, "pn": pn, "pd": pd, "gn": _grado(pn), "gd": _grado(pd)}
def _flt(v):
    return float(sp.N(v, 30))
def _clave(v):
    return round(_flt(v), 9)
def _raices_reales(p):
    """Raíces reales distintas de un Poly, ordenadas de menor a mayor."""
    if p.is_zero or p.degree() <= 0:
        return []
    try:
        crudas = list(sp.real_roots(p))
    except Exception:
        crudas = [sp.Float(r.as_real_imag()[0]) for r in p.nroots()
                  if abs(sp.im(r)) < 1e-9]
    vistas, unicas = set(), []
    for r in crudas:
        k = _clave(r)
        if k not in vistas:
            vistas.add(k)
            unicas.append(r)
    return sorted(unicas, key=_flt)
def _lim(expr, punto, dir="+"):
    """Límite con SymPy; devuelve None si no se pudo determinar."""
    try:
        r = sp.limit(expr, X, punto, dir)
        if r in (sp.nan, sp.zoo) or r.has(sp.AccumBounds):
            return None
        return r
    except Exception:
        return None
def L(e):
    return sp.latex(e)
def _num(v):
    if v.has(sp.CRootOf):
        return L(sp.N(v, 6))
    exacto = sp.simplify(v)
    s = L(exacto)
    if exacto.is_finite and not exacto.is_Rational:
        s += r"\approx " + L(sp.N(exacto, 5))
    return s
def _etq(v):
    """Etiqueta corta para usar dentro de un límite o intervalo."""
    return L(sp.N(v, 5)) if v.has(sp.CRootOf) else L(v)
def _t(texto):
    return ("t", texto)
def _m(latex):
    return ("m", latex)
def _ordenada(c):
    p0, q0 = c.pn.eval(0), c.pd.eval(0)
    pasos = [
        _t("La ordenada al origen es el valor de la función cuando x = 0."),
        _m(rf"f(0)=\dfrac{{P(0)}}{{Q(0)}}=\dfrac{{{L(p0)}}}{{{L(q0)}}}"),
    ]
    if q0 == 0:
        return {"titulo": "Ordenada al origen",
                "lineas": [r"f(0)\ \text{no existe}"],
                "notas": ["x = 0 no pertenece al dominio, porque ahí el denominador vale 0."],
                "pasos": pasos}
    v = sp.nsimplify(p0 / q0)
    pasos.append(_m(rf"f(0)={L(v)}"))
    return {"titulo": "Ordenada al origen",
            "lineas": [rf"f(0)={L(v)}", rf"\text{{Punto: }}\left(0,\ {L(v)}\right)"],
            "notas": [], "pasos": pasos}
def _raices(c):
    pasos = [
        _t("Las raíces son los valores de x donde f(x) = 0. Se iguala a cero el numerador "
           "de la función ya simplificada y se resuelve:"),
        _m(rf"{L(sp.factor(c.pn_r.as_expr()))}=0"),
    ]
    if not c.raices:
        return {"titulo": "Raíces", "lineas": [],
                "notas": ["No tiene raíces reales: la función nunca vale 0."],
                "pasos": pasos + [_t("La ecuación no tiene soluciones reales.")]}
    lineas = [rf"x={_num(r)}" for r in c.raices]
    pasos.append(_t("Soluciones reales: " + ", ".join(f"x ≈ {float(_flt(r)):.4g}" for r in c.raices)))
    return {"titulo": "Raíces", "lineas": lineas, "notas": [], "pasos": pasos}
def _vertical(c):
    pasos = [
        _t("Las asíntotas verticales están en los ceros reales del denominador de la función "
           "simplificada (cuando el numerador no se anula ahí). Se resuelve:"),
        _m(rf"{L(sp.factor(c.pd_r.as_expr()))}=0"),
    ]
    lineas, notas = [], []
    if not c.vert:
        notas.append("No hay asíntotas verticales.")
    for a in c.vert:
        izq, der = _lim(c.fr, a, "-"), _lim(c.fr, a, "+")
        et = _etq(a)
        lineas.append(rf"x={_num(a)}")
        pasos.append(_t(f"Límites laterales en x = {float(_flt(a)):.4g}:"))
        for sig, val in (("-", izq), ("+", der)):
            txt = L(val) if val is not None else r"\text{no determinado}"
            linea = rf"\lim_{{x\to {et}^{{{sig}}}}} f(x)={txt}"
            lineas.append(linea)
            pasos.append(_m(linea))
    for h in c.huecos:
        v = _lim(c.fr, h)
        notas.append(f"En x = {float(_flt(h)):.4g} hay un agujero (discontinuidad evitable): "
                     "se cancela un factor, por eso no es asíntota."
                     + (f" Ahí f tiende a {float(_flt(v)):.4g}." if v is not None and v.is_finite else ""))
    return {"titulo": "Asíntotas verticales", "lineas": lineas, "notas": notas, "pasos": pasos}
def _horizontal(c):
    dn, dd = c.pn_r.degree(), c.pd_r.degree()
    lp, lm = _lim(c.fr, sp.oo), _lim(c.fr, -sp.oo)
    pasos = [_t(f"Se comparan los grados del numerador ({dn}) y del denominador ({dd}) "
                "de la función simplificada, y se calculan los límites en el infinito:")]
    lineas = []
    for et, val in ((r"+\infty", lp), (r"-\infty", lm)):
        txt = L(val) if val is not None else r"\text{no determinado}"
        pasos.append(_m(rf"\lim_{{x\to {et}}} f(x)={txt}"))
    if lp is not None and lp.is_finite and lm is not None and lm.is_finite:
        lineas = [rf"y={L(lp)}", rf"\lim_{{x\to \pm\infty}} f(x)={L(lp)}"]
        pasos.append(_t("Como el límite es un número finito, la recta y = L es asíntota horizontal."))
        return {"titulo": "Asíntota horizontal", "lineas": lineas, "notas": [], "pasos": pasos}
    pasos.append(_t("El límite no es finito, así que no hay asíntota horizontal."))
    return {"titulo": "Asíntota horizontal", "lineas": [],
            "notas": ["No hay asíntota horizontal."], "pasos": pasos}
def _oblicua(c):
    dn, dd = c.pn_r.degree(), c.pd_r.degree()
    pasos = [_t("Existe asíntota oblicua cuando el grado del numerador es exactamente uno más "
                f"que el del denominador. Aquí: {dn} y {dd}.")]
    if dn != dd + 1:
        return {"titulo": "Asíntota oblicua", "lineas": [],
                "notas": ["No hay asíntota oblicua."], "pasos": pasos}
    q, r = sp.div(c.pn_r, c.pd_r)
    recta = q.as_expr()
    pasos += [
        _t("Se divide el numerador entre el denominador; el cociente es la recta buscada:"),
        _m(rf"\dfrac{{{L(c.pn_r.as_expr())}}}{{{L(c.pd_r.as_expr())}}}={L(recta)}+\dfrac{{{L(r.as_expr())}}}{{{L(c.pd_r.as_expr())}}}"),
    ]
    lineas = [rf"y={L(recta)}"]
    for et in (r"+\infty", r"-\infty"):
        val = _lim(c.fr - recta, sp.oo if et.startswith("+") else -sp.oo)
        if val is not None:
            linea = rf"\lim_{{x\to {et}}}\left[f(x)-({L(recta)})\right]={L(val)}"
            lineas.append(linea)
            pasos.append(_m(linea))
    return {"titulo": "Asíntota oblicua", "lineas": lineas, "notas": [], "pasos": pasos}
def _dominio(c):
    puntos = [-sp.oo] + c.excl + [sp.oo]
    intervalos = [sp.Interval.open(a, b) for a, b in zip(puntos, puntos[1:])]
    pasos = [
        _t("Los únicos valores prohibidos son los que hacen cero al denominador original "
           "(antes de simplificar):"),
        _m(rf"{L(sp.factor(c.pd.as_expr()))}=0"),
    ]
    if c.excl:
        prohibidos = ",\\ ".join(_etq(e) for e in c.excl)
        lineas = [rf"\operatorname{{Dom}}f=\mathbb{{R}}\setminus\left\{{{prohibidos}\right\}}"]
    else:
        lineas = [r"\operatorname{Dom}f=\mathbb{R}"]
    try:
        union = sp.Union(*intervalos)
        lineas.append(rf"\operatorname{{Dom}}f={L(union)}")
        pasos.append(_m(rf"\operatorname{{Dom}}f={L(union)}"))
    except Exception:
        pass
    return {"titulo": "Dominio", "lineas": lineas, "notas": [], "pasos": pasos}
def _rango(c):
    pasos = []
    derivada = sp.together(sp.diff(c.fr, X))
    pdn = sp.Poly(sp.fraction(derivada)[0], X)

    # Función constante
    if pdn.is_zero:
        valor = sp.nsimplify(sp.simplify(c.fr))
        pasos.append(_t("La derivada es 0, así que la función es constante."))
        return {"titulo": "Rango", "lineas": [rf"\operatorname{{Ran}}f=\left\{{{L(valor)}\right\}}"],
                "notas": [], "pasos": pasos}
    claves_excl = {_clave(e) for e in c.excl}
    crit = [r for r in _raices_reales(pdn) if _clave(r) not in claves_excl]
    pasos += [
        _t("Dentro de cada intervalo del dominio la función es continua, así que su imagen es "
           "un intervalo. Sus extremos salen de los límites en las orillas y de los valores "
           "en los puntos críticos (donde f′(x) = 0):"),
        _m(rf"f'(x)=0 \;\Rightarrow\; {L(sp.factor(pdn.as_expr()))}=0"),
    ]
    if crit:
        pasos.append(_t("Puntos críticos: " + ", ".join(f"x ≈ {_flt(r):.4g}" for r in crit)))
    else:
        pasos.append(_t("No hay puntos críticos reales."))
    puntos = [-sp.oo] + c.excl + [sp.oo]
    imagenes = []
    for a, b in zip(puntos, puntos[1:]):
        izq = _lim(c.fr, -sp.oo, "+") if a == -sp.oo else _lim(c.fr, a, "+")
        der = _lim(c.fr, sp.oo, "-") if b == sp.oo else _lim(c.fr, b, "-")
        if izq is None or der is None:
            raise ValueError("límite no determinado")
        cand = [(izq, False), (der, False)]
        for r in crit:
            if _flt(a) < _flt(r) < _flt(b):
                v = sp.simplify(c.fr.subs(X, r))
                cand.append((sp.N(v, 8) if v.has(sp.CRootOf) else sp.nsimplify(v), True))
        lo = min(cand, key=lambda p: _flt(p[0]))[0]
        hi = max(cand, key=lambda p: _flt(p[0]))[0]
        lo_cerrado = any(es_c and abs(_flt(v) - _flt(lo)) < 1e-9 for v, es_c in cand) and lo.is_finite
        hi_cerrado = any(es_c and abs(_flt(v) - _flt(hi)) < 1e-9 for v, es_c in cand) and hi.is_finite
        if abs(_flt(lo) - _flt(hi)) < 1e-12:
            iv = sp.FiniteSet(lo)
        else:
            iv = sp.Interval(lo, hi, not lo_cerrado, not hi_cerrado)
        imagenes.append(iv)
        pasos.append(_m(rf"x\in\left({_etq(a)},\,{_etq(b)}\right)\;\Rightarrow\; f(x)\in {L(iv)}"))
    try:
        total = sp.Union(*imagenes)
    except Exception:
        total = None
    if total is None:
        lineas = [r"\operatorname{Ran}f=" + r"\ \cup\ ".join(L(i) for i in imagenes)]
    elif total == sp.S.Reals:
        lineas = [r"\operatorname{Ran}f=\mathbb{R}"]
    else:
        lineas = [rf"\operatorname{{Ran}}f={L(total)}"]
    pasos.append(_t("El rango es la unión de las imágenes de todos los intervalos."))
    return {"titulo": "Rango", "lineas": lineas, "notas": [], "pasos": pasos}
def analizar(datos):
    """Calcula todos los resultados. Si uno falla, los demás siguen funcionando."""
    pn, pd = datos["pn"], datos["pd"]
    g = sp.gcd(pn, pd)
    pn_r, pd_r = sp.quo(pn, g), sp.quo(pd, g)
    if pd_r.LC() < 0:
        pn_r, pd_r = -pn_r, -pd_r
    c = SimpleNamespace(pn=pn, pd=pd, pn_r=pn_r, pd_r=pd_r)
    c.fr = pn_r.as_expr() / pd_r.as_expr()
    c.excl = _raices_reales(pd)
    c.vert = _raices_reales(pd_r)
    claves_vert = {_clave(r) for r in c.vert}
    claves_excl = {_clave(r) for r in c.excl}
    c.huecos = [h for h in c.excl if _clave(h) not in claves_vert]
    c.raices = [r for r in _raices_reales(pn_r) if _clave(r) not in claves_excl]
    items = []
    for titulo, fn in (("Ordenada al origen", _ordenada), ("Raíces", _raices),
                       ("Asíntotas verticales", _vertical), ("Asíntota horizontal", _horizontal),
                       ("Asíntota oblicua", _oblicua), ("Dominio", _dominio), ("Rango", _rango)):
        try:
            items.append(fn(c))
        except Exception:
            items.append({"titulo": titulo, "lineas": [], "pasos": [],
                          "notas": ["No pude determinar este resultado con la función ingresada."]})
    simplificada = None
    if g.degree() > 0:
        simplificada = L(c.fr)
    return {"f_tex": L(datos["f"]), "simplificada_tex": simplificada, "items": items}
