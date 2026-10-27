"""Genera los diagramas de bloques del sistema realimentado genérico, donde el
error se mide como e = r - y (error de seguimiento real) con un sumador aparte:

- espec_frec_fig1_err.png: sin perturbación a la entrada de la planta.
- espec_frec_fig4_err.png: con perturbación l a la entrada de la planta.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle

BLUE, RED = "#1f6fc5", "#d62728"
R = 0.28  # radio de los sumadores


def draw(filename, with_l=False):
    with plt.xkcd(scale=0.6, length=120, randomness=2):
        fig, ax = plt.subplots(figsize=(11, 6.2))
        ax.set_xlim(-0.5, 16)
        ax.set_ylim(-1.2, 7.5)
        ax.set_aspect("equal")
        ax.axis("off")

        def arrow(x0, y0, x1, y1, color="k"):
            ax.annotate("", (x1, y1), (x0, y0),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=2.2,
                                        mutation_scale=18, shrinkA=0,
                                        shrinkB=0))

        def line(xs, ys, color="k", lw=2.2):
            ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round")

        def block(xc, yc, w, h, txt):
            ax.add_patch(Rectangle((xc - w / 2, yc - h / 2), w, h,
                                   fill=False, lw=2.5))
            ax.text(xc, yc, txt, ha="center", va="center", fontsize=18)

        def summer(xc, yc):
            ax.add_patch(Circle((xc, yc), R, fill=False, lw=2.5))

        def label(x, y, txt, color="k", size=18, **kw):
            ax.text(x, y, txt, color=color, fontsize=size, **kw)

        def node(x, y):
            ax.plot(x, y, "ko", ms=9, zorder=5)

        y0 = 4.0          # línea principal
        yfb = 1.6         # realimentación
        yerr = 0.0        # medición del error

        # Posiciones
        x_s1, x_G, x_s2, x_s3 = 2.0, 8.6, 10.6, 12.2
        x_K = 4.2 if with_l else 4.6
        x_l = 5.9         # sumador de la perturbación l
        xu = 7.0 if with_l else 6.6
        x_box = 6.6 if with_l else 6.2
        x_se = 1.0
        x_eb = 11.2       # derivación de y para medir el error

        # r -> sumador 1
        line([0, x_s1 - R - 0.4], [y0, y0])
        arrow(x_s1 - R - 0.4, y0, x_s1 - R, y0)
        label(0, y0 + 0.25, "$r$", size=20)
        label(x_s1 - 0.75, y0 + 0.3, "+")
        summer(x_s1, y0)

        # sumador 1 -> K
        arrow(x_s1 + R, y0, x_K - 0.9, y0)
        block(x_K, y0, 1.8, 1.0, "$K(s)$")

        # K -> (sumador l) -> G
        if with_l:
            arrow(x_K + 0.9, y0, x_l - R, y0)
            summer(x_l, y0)
            arrow(x_l, y0 + 1.6, x_l, y0 + R)
            label(x_l + 0.2, y0 + 1.2, "$l$", size=20)
            label(x_l - 0.6, y0 + 0.3, "+")
            label(x_l + 0.15, y0 + 0.45, "+")
            arrow(x_l + R, y0, x_G - 0.9, y0)
        else:
            arrow(x_K + 0.9, y0, x_G - 0.9, y0)
        block(x_G, y0, 1.8, 1.0, "$G(s)$")

        # u (entrada de la planta)
        line([xu, xu, xu + 0.4], [y0, y0 + 0.75, y0 + 0.75], color=BLUE,
             lw=1.8)
        arrow(xu + 0.4, y0 + 0.75, xu + 0.7, y0 + 0.75, color=BLUE)
        label(xu + 0.8, y0 + 0.6, "$u$", color=BLUE, size=20)

        # G -> sumador 2, perturbación d
        arrow(x_G + 0.9, y0, x_s2 - R, y0)
        label(x_s2 - 0.75, y0 + 0.25, "+")
        summer(x_s2, y0)
        block(x_s2, y0 + 1.9, 1.5, 0.9, "$G_d(s)$")
        arrow(x_s2, y0 + 3.3, x_s2, y0 + 2.35)
        label(x_s2 + 0.2, y0 + 2.85, "$d$", size=20)
        arrow(x_s2, y0 + 1.45, x_s2, y0 + R)
        label(x_s2 + 0.15, y0 + 0.5, "+")

        # salida y
        arrow(x_s2 + R, y0, 14.6, y0)
        label(14.8, y0 - 0.15, "$y$", size=22)

        # realimentación con ruido de medición: y_m = y + eta
        node(x_s3, y0)
        arrow(x_s3, y0, x_s3, yfb + R)
        summer(x_s3, yfb)
        label(x_s3 + 0.2, yfb + 0.45, "+")
        arrow(14.6, yfb, x_s3 + R, yfb)
        label(14.8, yfb - 0.15, r"$\eta$", size=22)
        label(x_s3 + 0.45, yfb + 0.12, "+")
        line([x_s3 - R, x_s1], [yfb, yfb])
        arrow(x_s1, yfb, x_s1, y0 - R)
        label(x_s1 - 0.6, y0 - 0.9, "$-$", size=20)
        label(x_s1 + 0.25, yfb + 0.9, "$y_m$", color=RED, size=20)

        # medición del error: e = r - y (sumador aparte)
        node(x_eb, y0)
        line([x_eb, x_eb], [y0, yfb + 0.18])
        # salto sobre la línea de realimentación
        ax.add_patch(Arc((x_eb, yfb), 0.36, 0.36, theta1=-90, theta2=90,
                         lw=2.2))
        line([x_eb, x_eb, x_se + R], [yfb - 0.18, yerr, yerr])
        arrow(x_se + 0.6, yerr, x_se + R, yerr)
        summer(x_se, yerr)
        label(x_se + 0.35, yerr + 0.3, "$-$", size=20)

        node(x_se, y0)
        arrow(x_se, y0, x_se, yerr + R)
        label(x_se - 0.55, yerr + 0.45, "+")

        line([x_se, x_se], [yerr - R, yerr - 0.8], color=BLUE, lw=1.8)
        arrow(x_se, yerr - 0.8, x_se + 0.6, yerr - 0.8, color=BLUE)
        label(x_se + 0.75, yerr - 1.0, "$e = r - y$", color=BLUE, size=20)

        # planta (recuadro rojo punteado)
        ax.add_patch(Rectangle((x_box, 0.9), 13.2 - x_box, 5.7, fill=False,
                               ec=RED, lw=1.8, ls="--"))

        fig.tight_layout()
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        plt.close(fig)


draw("espec_frec_fig1_err.png")
draw("espec_frec_fig4_err.png", with_l=True)
