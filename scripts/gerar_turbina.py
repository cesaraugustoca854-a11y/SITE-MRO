#!/usr/bin/env python3
"""Gera o desenho esquemático do turbofan (SVG) usado na seção "Peça por peça" da home.

Uso: python3 scripts/gerar_turbina.py  → imprime o <svg> para colar em index.html.
O motor é simétrico em torno do eixo (y = 240); cada estágio é um <g class="bp-part">
que se desloca no eixo quando a figura recebe a classe .is-exploded.
"""

AX = 240  # linha de centro


def mirror(points):
    """Espelha uma lista de (x, y) em torno do eixo."""
    return [(x, 2 * AX - y) for x, y in points]


def poly(points, closed=False):
    d = "M " + " L ".join(f"{x:g} {y:g}" for x, y in points)
    return d + (" Z" if closed else "")


def path(d, cls="bp-line"):
    return f'<path class="{cls}" d="{d}" pathLength="1"/>'


def sym(points, closed=False, cls="bp-line"):
    return path(poly(points, closed), cls) + path(poly(mirror(points), closed), cls)


def part(key, n, label, label_x, body):
    return (f'<g class="bp-part bp-part--{key}">{body}'
            f'<g class="bp-label" aria-hidden="true"><line x1="{label_x}" y1="{2 * AX - 40}" x2="{label_x}" y2="452"/>'
            f'<circle cx="{label_x}" cy="452" r="11"/><text x="{label_x}" y="456" class="bp-num">{n}</text>'
            f'<text x="{label_x}" y="486" class="bp-name">{label}</text></g></g>')


def build():
    out = []
    # Carenagem (estática): fica tracejada quando o motor é desmontado.
    cowl = [(198, 70), (204, 52), (232, 46), (720, 58), (836, 146)]
    out.append('<g class="bp-casing">' + sym(cowl) + "</g>")
    # Linha de centro (traço-ponto, convenção de desenho técnico).
    out.append(f'<line class="bp-axis" x1="120" y1="{AX}" x2="1060" y2="{AX}"/>')

    # 1. Fan: cone e pás largas.
    fan = path(f"M 148 {AX} Q 150 204 202 194 L 202 286 Q 150 276 148 {AX} Z")
    fan += sym([(204, 194), (214, 64), (234, 64), (228, 194)], closed=True)
    fan += sym([(252, 92), (258, 184)])  # aleta-guia de saída
    out.append(part("fan", 1, "Fan", 220, fan))

    # 2. Compressor: tambor que afunila e fileiras de pás cada vez menores.
    comp = sym([(276, 176), (520, 196)]) + sym([(276, 222), (520, 228)])
    for i in range(8):
        x = 290 + i * 29
        tip = 180 + i * 2.2
        comp += sym([(x, 222 + i * 0.6), (x + 10, tip + 4)])
    out.append(part("comp", 2, "Compressor", 398, comp))

    # 3. Câmara de combustão, com a chama em vermelho.
    comb = path(f"M 546 202 C 562 186 640 186 656 202 L 656 278 C 640 294 562 294 546 278 Z")
    comb += path(f"M 566 {AX} Q 600 220 636 {AX} Q 600 260 566 {AX} Z", "bp-line bp-hot")
    out.append(part("comb", 3, "Câmara de combustão", 601, comb))

    # 4. Turbina: fileiras que crescem no sentido do escoamento.
    turb = sym([(682, 196), (822, 172)]) + sym([(682, 228), (822, 222)])
    for i in range(4):
        x = 694 + i * 33
        comb_tip = 194 - i * 6
        turb += sym([(x, 228 - i * 1.5), (x + 12, comb_tip)])
    out.append(part("turb", 4, "Turbina", 752, turb))

    # 5. Bocal de exaustão e cone de cauda.
    noz = sym([(842, 150), (1008, 196)]) + path(f"M 842 222 L 962 {AX} L 842 258")
    out.append(part("noz", 5, "Bocal de exaustão", 925, noz))

    # Escoamento de ar (aparece com o motor montado): bypass e núcleo.
    flow = ('<g class="bp-flow" aria-hidden="true">'
            + sym([(170, 120), (520, 128), (840, 166), (1060, 200)], cls="bp-air")
            + sym([(170, 212), (540, 216), (700, 214), (1060, 232)], cls="bp-air bp-air--core")
            + "</g>")
    out.append(flow)

    return ('<svg class="blueprint__svg" viewBox="50 20 1080 490" role="img" aria-labelledby="turbina-titulo turbina-desc">'
            '<title id="turbina-titulo">Turbofan em corte, desenho esquemático</title>'
            '<desc id="turbina-desc">Motor turbofan visto em corte lateral, com cinco estágios na ordem do escoamento do ar: '
            '1, fan; 2, compressor; 3, câmara de combustão; 4, turbina; 5, bocal de exaustão.</desc>'
            + "".join(out) + "</svg>")


if __name__ == "__main__":
    print(build())
