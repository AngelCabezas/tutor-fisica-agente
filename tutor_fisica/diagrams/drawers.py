from __future__ import annotations

import math

import matplotlib.pyplot as plt
import streamlit as st

from tutor_fisica.diagrams.detector import detectar_tipo_diagrama
from tutor_fisica.utils.text_formatting import normalizar_texto
from tutor_fisica.utils.value_extractors import (
    extraer_angulo_grados,
    extraer_coeficiente_friccion,
    extraer_friccion_estatica_maxima,
    extraer_fuerza_aplicada,
    extraer_gravedad,
    extraer_masa,
    extraer_peso_newton,
    extraer_primer_numero_con_unidad,
    extraer_rapidez,
    extraer_valores_en_newton,
)


def mostrar_figura(fig):
    try:
        fig.set_size_inches(7, 5)
        fig.tight_layout()
    except Exception:
        pass

    st.pyplot(fig, width="content")
    plt.close(fig)


def dibujar_vectores_desde_pregunta(pregunta: str):
    valores = extraer_valores_en_newton(pregunta)

    if len(valores) >= 2:
        fx = valores[0]
        fy = valores[1]
    else:
        fx = 3
        fy = 4

    resultante = math.sqrt(fx**2 + fy**2)
    angulo = math.degrees(math.atan2(fy, fx))

    fig, ax = plt.subplots(figsize=(6, 5))
    escala = max(fx, fy, resultante, 1)
    head = escala * 0.04

    ax.arrow(0, 0, fx, 0, head_width=head, length_includes_head=True)
    ax.text(fx / 2, escala * 0.06, f"Fx = {fx:g} N", fontsize=11)

    ax.arrow(0, 0, 0, fy, head_width=head, length_includes_head=True)
    ax.text(escala * 0.05, fy / 2, f"Fy = {fy:g} N", fontsize=11)

    ax.arrow(0, 0, fx, fy, head_width=head, length_includes_head=True)
    ax.text(fx / 2, fy / 2, f"R = {resultante:.2f} N", fontsize=11)

    ax.plot([fx, fx], [0, fy], linestyle="--", linewidth=1)
    ax.plot([0, fx], [fy, fy], linestyle="--", linewidth=1)

    ax.text(fx * 0.55, -escala * 0.12, f"θ = {angulo:.2f}°", fontsize=11)

    ax.set_xlim(-0.5, fx + escala * 0.3)
    ax.set_ylim(-0.5, fy + escala * 0.3)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True)
    ax.set_title("Diagrama vectorial de fuerzas perpendiculares")

    return fig


def dibujar_bloque_simple_desde_pregunta(pregunta: str):
    masa = extraer_primer_numero_con_unidad(pregunta, "kg", 5.0)
    fuerza_aplicada = extraer_fuerza_aplicada(pregunta, 20.0)
    aceleracion = fuerza_aplicada / masa if masa else 0.0

    fig, ax = plt.subplots(figsize=(7, 4.5))

    bloque = plt.Rectangle((3.0, 1.6), 1.6, 1.0, fill=False, linewidth=2)
    ax.add_patch(bloque)
    ax.text(3.25, 2.0, f"m = {masa:g} kg", fontsize=11)

    ax.plot([0.5, 7.0], [1.6, 1.6], linewidth=2)
    ax.text(0.7, 1.35, "mesa sin fricción", fontsize=10)

    ax.arrow(4.6, 2.1, 1.5, 0, head_width=0.14, length_includes_head=True)
    ax.text(5.1, 2.35, f"F = {fuerza_aplicada:g} N", fontsize=11)

    ax.arrow(3.8, 2.6, 0, 1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 3.25, "N", fontsize=11)

    ax.arrow(3.8, 1.6, 0, -1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 0.75, "mg", fontsize=11)

    ax.arrow(4.0, 1.2, 1.0, 0, head_width=0.10, length_includes_head=True)
    ax.text(4.2, 0.95, f"a = {aceleracion:.2f} m/s²", fontsize=11)

    ax.set_xlim(0, 7.6)
    ax.set_ylim(0.2, 4.0)
    ax.axis("off")
    ax.set_title("Diagrama de cuerpo libre: bloque sin fricción")

    return fig


def dibujar_bloque_con_friccion_desde_pregunta(pregunta: str):
    masa = extraer_primer_numero_con_unidad(pregunta, "kg", 10.0)
    fuerza_aplicada = extraer_fuerza_aplicada(pregunta, 50.0)
    mu = extraer_coeficiente_friccion(pregunta, 0.30)
    g = extraer_gravedad(pregunta, 9.8)

    peso = masa * g
    normal = peso
    friccion = mu * normal
    fuerza_neta = fuerza_aplicada - friccion
    aceleracion = fuerza_neta / masa if masa else 0.0

    fig, ax = plt.subplots(figsize=(8, 4.8))

    bloque = plt.Rectangle((3.0, 1.6), 1.6, 1.0, fill=False, linewidth=2)
    ax.add_patch(bloque)
    ax.text(3.25, 2.0, f"m = {masa:g} kg", fontsize=11)

    ax.plot([0.5, 7.3], [1.6, 1.6], linewidth=2)
    ax.text(0.7, 1.35, "superficie rugosa", fontsize=10)

    ax.arrow(4.6, 2.1, 1.5, 0, head_width=0.14, length_includes_head=True)
    ax.text(5.15, 2.32, f"F = {fuerza_aplicada:.2f} N", fontsize=10)

    ax.arrow(3.0, 2.1, -1.3, 0, head_width=0.14, length_includes_head=True)
    ax.text(1.25, 2.32, f"fk = {friccion:.2f} N", fontsize=10)

    ax.arrow(3.8, 2.6, 0, 1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 3.25, f"N = {normal:.2f} N", fontsize=10)

    ax.arrow(3.8, 1.6, 0, -1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 0.75, f"mg = {peso:.2f} N", fontsize=10)

    if fuerza_neta >= 0:
        ax.arrow(4.0, 1.25, 1.0, 0, head_width=0.10, length_includes_head=True)
        ax.text(4.25, 1.0, f"Fneta = {fuerza_neta:.2f} N", fontsize=10)
    else:
        ax.arrow(4.0, 1.25, -1.0, 0, head_width=0.10, length_includes_head=True)
        ax.text(2.25, 1.0, f"Fneta = {fuerza_neta:.2f} N", fontsize=10)

    resumen = f"μk = {mu:g}\ng = {g:g} m/s²\na = {aceleracion:.2f} m/s²"
    ax.text(
        6.0,
        0.55,
        resumen,
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    ax.set_xlim(0, 7.8)
    ax.set_ylim(0.2, 4.1)
    ax.axis("off")
    ax.set_title("Diagrama de cuerpo libre: bloque con fricción")

    return fig


def dibujar_friccion_estatica_coeficiente_desde_pregunta(pregunta: str):
    peso = extraer_peso_newton(pregunta, 30.0)
    friccion_max = extraer_friccion_estatica_maxima(pregunta, 15.0)

    normal = peso
    mu_s = friccion_max / normal if normal else 0.0

    fig, ax = plt.subplots(figsize=(7, 4.5))

    bloque = plt.Rectangle((3.0, 1.6), 1.6, 1.0, fill=False, linewidth=2)
    ax.add_patch(bloque)
    ax.text(3.18, 2.0, "bloque de acero", fontsize=10)

    ax.plot([0.5, 7.0], [1.6, 1.6], linewidth=2)
    ax.text(0.7, 1.35, "superficie horizontal de madera", fontsize=10)

    # Normal
    ax.arrow(3.8, 2.6, 0, 1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 3.25, f"N = {normal:.2f} N", fontsize=10)

    # Peso
    ax.arrow(3.8, 1.6, 0, -1.0, head_width=0.14, length_includes_head=True)
    ax.text(3.95, 0.75, f"W = {peso:.2f} N", fontsize=10)

    # Tendencia de movimiento
    ax.arrow(4.6, 2.1, 1.2, 0, head_width=0.12, length_includes_head=True)
    ax.text(4.85, 2.35, "tendencia de movimiento", fontsize=9)

    # Fricción estática máxima
    ax.arrow(3.0, 2.1, -1.2, 0, head_width=0.12, length_includes_head=True)
    ax.text(1.0, 2.35, f"fs,max = {friccion_max:.2f} N", fontsize=10)

    resumen = (
        f"N = W = {normal:.2f} N\n"
        f"fs,max = {friccion_max:.2f} N\n"
        f"μs = fs,max / N\n"
        f"μs = {mu_s:.2f}"
    )

    ax.text(
        5.25,
        0.45,
        resumen,
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
    )

    ax.set_xlim(0, 7.4)
    ax.set_ylim(0.2, 4.1)
    ax.axis("off")
    ax.set_title("Fricción estática máxima y coeficiente de fricción")

    return fig


def dibujar_plano_inclinado_desde_pregunta(pregunta: str):
    theta = extraer_angulo_grados(pregunta, 30.0)
    theta_rad = math.radians(theta)
    masa = extraer_primer_numero_con_unidad(pregunta, "kg", 1.0)
    g = extraer_gravedad(pregunta, 9.8)
    mu = extraer_coeficiente_friccion(pregunta, 0.0)
    con_friccion = any(p in normalizar_texto(pregunta) for p in ["friccion", "rozamiento", "rugosa", "μk", "mu_k"])

    peso = masa * g
    normal = peso * math.cos(theta_rad)
    componente = peso * math.sin(theta_rad)
    friccion = mu * normal if con_friccion else 0.0

    fig, ax = plt.subplots(figsize=(7, 5))

    x0, y0 = 1.0, 1.0
    L = 5.0
    x1 = x0 + L * math.cos(theta_rad)
    y1 = y0 + L * math.sin(theta_rad)

    ax.plot([x0, x1], [y0, y1], linewidth=2)
    ax.plot([x0, x1], [y0, y0], linewidth=2)
    ax.plot([x1, x1], [y0, y1], linewidth=2)

    xb = x0 + 0.45 * L * math.cos(theta_rad)
    yb = y0 + 0.45 * L * math.sin(theta_rad)
    bloque = plt.Rectangle((xb, yb), 0.9, 0.55, angle=theta, fill=False, linewidth=2)
    ax.add_patch(bloque)
    ax.text(xb + 0.1, yb + 0.45, f"m = {masa:g} kg", fontsize=10)

    ux = math.cos(theta_rad)
    uy = math.sin(theta_rad)
    nx = -math.sin(theta_rad)
    ny = math.cos(theta_rad)

    cx = xb + 0.45
    cy = yb + 0.35

    ax.arrow(cx, cy, 0, -1.1, head_width=0.12, length_includes_head=True)
    ax.text(cx + 0.15, cy - 0.75, f"mg = {peso:.1f} N", fontsize=10)

    ax.arrow(cx, cy, nx * 1.0, ny * 1.0, head_width=0.12, length_includes_head=True)
    ax.text(cx + nx * 1.15, cy + ny * 1.15, f"N = {normal:.1f} N", fontsize=10)

    ax.arrow(cx, cy, ux * 1.1, uy * 1.1, head_width=0.12, length_includes_head=True)
    ax.text(cx + ux * 1.25, cy + uy * 1.25, f"mg senθ = {componente:.1f} N", fontsize=9)

    if con_friccion:
        ax.arrow(cx, cy, -ux * 0.9, -uy * 0.9, head_width=0.12, length_includes_head=True)
        ax.text(cx - ux * 1.35, cy - uy * 1.25, f"fk = {friccion:.1f} N", fontsize=9)

    ax.text(x1 - 0.6, y0 + 0.15, f"θ = {theta:g}°", fontsize=12)

    ax.set_xlim(0, 7)
    ax.set_ylim(0.3, 4.7)
    ax.axis("off")
    ax.set_title("Diagrama de apoyo: plano inclinado")

    return fig


def dibujar_sistema_polea_desde_pregunta(pregunta: str):
    m1 = extraer_masa(pregunta, "m1", 8)
    m2 = extraer_masa(pregunta, "m2", 4)
    g = extraer_gravedad(pregunta, 9.8)

    a = m2 * g / (m1 + m2) if (m1 + m2) else 0.0
    tension = m1 * a

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot([0.5, 4.7], [2.2, 2.2], linewidth=2)

    bloque1 = plt.Rectangle((1.5, 2.2), 1.2, 0.8, fill=False, linewidth=2)
    ax.add_patch(bloque1)
    ax.text(1.65, 2.52, f"m1 = {m1:g} kg", fontsize=10)

    polea = plt.Circle((5, 2.8), 0.35, fill=False, linewidth=2)
    ax.add_patch(polea)

    ax.plot([2.7, 5], [2.8, 2.8], linewidth=1.5)
    ax.plot([5.35, 5.35], [2.8, 1.1], linewidth=1.5)

    bloque2 = plt.Rectangle((4.9, 0.4), 0.9, 0.7, fill=False, linewidth=2)
    ax.add_patch(bloque2)
    ax.text(4.97, 0.65, f"m2 = {m2:g} kg", fontsize=10)

    ax.arrow(2.1, 3.0, 1.0, 0, head_width=0.12, length_includes_head=True)
    ax.text(2.65, 3.2, f"T ≈ {tension:.1f} N", fontsize=10)

    ax.arrow(5.35, 1.1, 0, 0.9, head_width=0.12, length_includes_head=True)
    ax.text(5.5, 1.65, "T", fontsize=11)

    ax.arrow(5.35, 0.4, 0, -0.8, head_width=0.12, length_includes_head=True)
    ax.text(5.5, 0.0, "m2g", fontsize=11)

    ax.arrow(2.0, 1.9, 0.9, 0, head_width=0.1, length_includes_head=True)
    ax.text(2.15, 1.65, f"a ≈ {a:.2f} m/s²", fontsize=10)

    ax.arrow(4.6, 0.85, 0, -0.6, head_width=0.1, length_includes_head=True)
    ax.text(4.15, 0.45, "a", fontsize=11)

    ax.set_xlim(0, 6.8)
    ax.set_ylim(-0.6, 4)
    ax.axis("off")
    ax.set_title("Sistema de bloques con cuerda y polea")

    return fig


def dibujar_atwood_desde_pregunta(pregunta: str):
    m1 = extraer_masa(pregunta, "m1", 3.0)
    m2 = extraer_masa(pregunta, "m2", 5.0)
    g = extraer_gravedad(pregunta, 9.8)

    masa_total = m1 + m2

    if masa_total == 0:
        a = 0.0
        tension = 0.0
    else:
        a = abs(m2 - m1) * g / masa_total
        tension = (2 * m1 * m2 * g) / masa_total

    fig, ax = plt.subplots(figsize=(7, 5))

    # Polea
    polea = plt.Circle((3.5, 3.4), 0.45, fill=False, linewidth=2)
    ax.add_patch(polea)

    # Soporte
    ax.plot([3.5, 3.5], [4.4, 3.85], linewidth=2)
    ax.plot([2.6, 4.4], [4.4, 4.4], linewidth=2)

    # Cuerda
    ax.plot([3.05, 2.0], [3.4, 3.4], linewidth=1.8)
    ax.plot([3.95, 5.0], [3.4, 3.4], linewidth=1.8)
    ax.plot([2.0, 2.0], [3.4, 1.6], linewidth=1.8)
    ax.plot([5.0, 5.0], [3.4, 1.1], linewidth=1.8)

    # Bloques
    bloque1 = plt.Rectangle((1.45, 0.9), 1.1, 0.7, fill=False, linewidth=2)
    bloque2 = plt.Rectangle((4.45, 0.4), 1.1, 0.7, fill=False, linewidth=2)

    ax.add_patch(bloque1)
    ax.add_patch(bloque2)

    ax.text(1.58, 1.17, f"m1 = {m1:g} kg", fontsize=10)
    ax.text(4.58, 0.67, f"m2 = {m2:g} kg", fontsize=10)

    # Tensiones
    ax.arrow(2.0, 1.6, 0, 0.7, head_width=0.12, length_includes_head=True)
    ax.text(2.15, 2.05, "T", fontsize=11)

    ax.arrow(5.0, 1.1, 0, 0.7, head_width=0.12, length_includes_head=True)
    ax.text(5.15, 1.55, "T", fontsize=11)

    # Pesos
    ax.arrow(2.0, 0.9, 0, -0.55, head_width=0.12, length_includes_head=True)
    ax.text(2.15, 0.45, "m1g", fontsize=10)

    ax.arrow(5.0, 0.4, 0, -0.55, head_width=0.12, length_includes_head=True)
    ax.text(5.15, -0.05, "m2g", fontsize=10)

    # Dirección de aceleración
    if m2 > m1:
        ax.arrow(5.75, 1.1, 0, -0.65, head_width=0.11, length_includes_head=True)
        ax.text(5.95, 0.65, f"a = {a:.2f} m/s²", fontsize=10)

        ax.arrow(1.25, 0.9, 0, 0.65, head_width=0.11, length_includes_head=True)
        ax.text(0.35, 1.25, "a", fontsize=10)

    elif m1 > m2:
        ax.arrow(1.25, 1.6, 0, -0.65, head_width=0.11, length_includes_head=True)
        ax.text(0.35, 1.15, f"a = {a:.2f} m/s²", fontsize=10)

        ax.arrow(5.75, 0.4, 0, 0.65, head_width=0.11, length_includes_head=True)
        ax.text(5.95, 0.8, "a", fontsize=10)

    else:
        ax.text(2.55, 0.2, "a = 0 m/s²", fontsize=10)

    ax.text(
        2.75,
        0.25,
        f"T ≈ {tension:.2f} N",
        fontsize=11,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    ax.set_xlim(0, 7)
    ax.set_ylim(-0.4, 4.8)
    ax.axis("off")
    ax.set_title("Máquina de Atwood: dos masas colgantes")

    return fig


def dibujar_tiro_parabolico_desde_pregunta(pregunta: str):
    v0 = extraer_rapidez(pregunta, 20.0)
    theta = extraer_angulo_grados(pregunta, 30.0)
    g = extraer_gravedad(pregunta, 9.8)
    theta_rad = math.radians(theta)

    v0x = v0 * math.cos(theta_rad)
    v0y = v0 * math.sin(theta_rad)
    t_total = 2 * v0y / g if g else 0.0

    puntos = 80
    tiempos = [i * t_total / puntos for i in range(puntos + 1)]
    xs = [v0x * t for t in tiempos]
    ys = [v0y * t - 0.5 * g * t**2 for t in tiempos]

    alcance = max(xs) if xs else 0.0
    altura = max(ys) if ys else 0.0

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(xs, ys, linewidth=2)
    ax.arrow(0, 0, v0x * 0.12, v0y * 0.12, head_width=max(altura, 1) * 0.06, length_includes_head=True)
    ax.text(alcance * 0.08, altura * 0.25, f"v0 = {v0:g} m/s\nθ = {theta:g}°", fontsize=10)

    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)
    ax.scatter([alcance / 2], [altura])
    ax.text(alcance / 2, altura * 1.04, f"hmax ≈ {altura:.2f} m", fontsize=10)
    ax.text(alcance * 0.55, -max(altura, 1) * 0.12, f"R ≈ {alcance:.2f} m", fontsize=10)

    ax.set_xlim(-alcance * 0.05, alcance * 1.08 if alcance else 1)
    ax.set_ylim(-max(altura, 1) * 0.2, altura * 1.25 if altura else 1)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True)
    ax.set_title("Trayectoria parabólica")

    return fig


def dibujar_mrua_desde_pregunta(pregunta: str):
    a = extraer_primer_numero_con_unidad(pregunta, "m/s", 3.0)
    tiempo = extraer_primer_numero_con_unidad(pregunta, "s", 8.0)

    ts = [i * tiempo / 50 for i in range(51)]
    vs = [a * t for t in ts]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ts, vs, linewidth=2)
    ax.fill_between(ts, vs, alpha=0.15)

    ax.text(tiempo * 0.55, max(vs) * 0.45 if vs else 1, "Área bajo la curva = desplazamiento", fontsize=10)
    ax.scatter([tiempo], [a * tiempo])
    ax.text(tiempo * 0.65, a * tiempo * 0.92, f"v = {a * tiempo:.2f} m/s", fontsize=10)

    ax.set_xlabel("t (s)")
    ax.set_ylabel("v (m/s)")
    ax.set_title("Gráfica velocidad-tiempo para MRUA")
    ax.grid(True)

    return fig


def dibujar_campo_magnetico_desde_pregunta(pregunta: str):
    fig, ax = plt.subplots(figsize=(6, 5))

    radio = 1.6
    puntos = 120
    angulos = [2 * math.pi * i / puntos for i in range(puntos + 1)]
    xs = [radio * math.cos(t) for t in angulos]
    ys = [radio * math.sin(t) for t in angulos]

    ax.plot(xs, ys, linewidth=2)
    ax.arrow(-radio, 0, 0.85, 0.0, head_width=0.12, length_includes_head=True)
    ax.text(-radio * 0.95, 0.2, "v", fontsize=12)
    ax.text(0.15, 0.15, "B perpendicular al plano", fontsize=10)
    ax.text(0.25, -0.25, "⊗", fontsize=24)
    ax.text(radio * 0.55, radio * 0.55, "trayectoria circular", fontsize=10)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.0, 2.0)
    ax.grid(True)
    ax.set_title("Partícula cargada en campo magnético")

    return fig


def dibujar_flotacion_desde_pregunta(pregunta: str):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    fluidos = [
        ("Agua dulce", 0.65),
        ("Agua salada", 0.58),
        ("Mercurio", 0.22),
    ]

    for i, (nombre, fraccion_sumergida) in enumerate(fluidos):
        x = i * 2.2 + 0.8
        ax.add_patch(plt.Rectangle((x, 0.5), 1.5, 2.2, fill=False, linewidth=2))
        ax.plot([x, x + 1.5], [1.8, 1.8], linewidth=2)

        radio = 0.45
        centro_y = 1.8 + radio * (1 - 2 * fraccion_sumergida)
        ax.add_patch(plt.Circle((x + 0.75, centro_y), radio, fill=False, linewidth=2))

        ax.text(x + 0.15, 0.15, nombre, fontsize=10)
        ax.text(x + 0.1, 3.0, f"Emergido\n≈ {(1-fraccion_sumergida)*100:.0f}%", fontsize=9)

    ax.set_xlim(0, 7.2)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    ax.set_title("Comparación cualitativa de flotación")

    return fig


def dibujar_hidrostatica_desde_pregunta(pregunta: str):
    labels = ["Agua dulce\n20 cm", "Agua salada\n20 cm", "Mercurio\n5 cm"]
    valores = [1000 * 0.20, 1025 * 0.20, 13600 * 0.05]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, valores)
    ax.set_ylabel("ρh relativo")
    ax.set_title("Comparación de presión hidrostática")
    ax.grid(axis="y")

    return fig

DIAGRAM_DRAWERS = {
    "friccion_estatica_coeficiente": dibujar_friccion_estatica_coeficiente_desde_pregunta,
    "friccion": dibujar_bloque_con_friccion_desde_pregunta,
    "vectores": dibujar_vectores_desde_pregunta,
    "plano_inclinado": dibujar_plano_inclinado_desde_pregunta,
    "polea": dibujar_sistema_polea_desde_pregunta,
    "atwood": dibujar_atwood_desde_pregunta,
    "bloque_simple": dibujar_bloque_simple_desde_pregunta,
    "tiro_parabolico": dibujar_tiro_parabolico_desde_pregunta,
    "mrua": dibujar_mrua_desde_pregunta,
    "campo_magnetico": dibujar_campo_magnetico_desde_pregunta,
    "flotacion": dibujar_flotacion_desde_pregunta,
    "hidrostatica": dibujar_hidrostatica_desde_pregunta,
}


def crear_diagrama_desde_pregunta(pregunta: str):
    tipo_diagrama = detectar_tipo_diagrama(pregunta)
    if tipo_diagrama is None:
        return None, None

    drawer = DIAGRAM_DRAWERS.get(tipo_diagrama)
    if drawer is None:
        return tipo_diagrama, None

    return tipo_diagrama, drawer(pregunta)
