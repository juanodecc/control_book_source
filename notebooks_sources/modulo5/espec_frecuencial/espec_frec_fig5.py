"""Genera espec_frec_fig5.png: forma de |L|, |S| y |T| con las zonas de
especificación (loop-shaping).

Adaptada de la figura del apunte "Especificación de sistemas de control en el
dominio de la frecuencia" (Dpto. ISA, ETSII, Universidad de Valladolid) y de
Skogestad & Postlethwaite, "Multivariable Feedback Control".
"""
import control as ctrl
import matplotlib.pyplot as plt
import numpy as np

# Función de lazo de ejemplo: integrador + polo, MF ~ 50°
L = ctrl.tf(1.5, [0.5, 1, 0])
S = ctrl.feedback(1, L)
T = ctrl.feedback(L, 1)

omega = np.logspace(-2.5, 2.5, 2000)


def mag_db(sys):
    return 20 * np.log10(ctrl.frequency_response(sys, omega).magnitude)


L_db, S_db, T_db = mag_db(L), mag_db(S), mag_db(T)

_, pm, _, wc = ctrl.margin(L)
w_bw_S = omega[np.argmax(S_db >= -3)]  # primer cruce de |S| por -3 dB
w_bw_T = omega[np.argmax(T_db <= -3)]  # primer cruce de |T| por -3 dB

# Zonas de especificación (una década a cada lado de wc)
w1, w2 = wc / 10, wc * 10
Mb = np.floor(np.interp(w1, omega, L_db) / 5) * 5    # |L| > Mb para w <= w1
Ma = np.floor(-np.interp(w2, omega, L_db) / 5) * 5   # |L| < -Ma para w >= w2

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.semilogx(omega, L_db, color="C0", lw=2, label="$|L|$")
ax.semilogx(omega, S_db, color="C1", lw=2, label="$|S|$")
ax.semilogx(omega, T_db, color="C2", lw=2, label="$|T|$")

ylim = (-60, 50)
# Barreras: zona B (baja frecuencia) y zona A (alta frecuencia)
ax.fill_between([omega[0], w1], Mb, ylim[0], color="0.9", zorder=0)
ax.plot([omega[0], w1], [-Mb, -Mb], "k--", lw=1.5)
ax.plot([omega[0], w1, w1], [Mb, Mb, ylim[0]], "k", lw=2.5)
ax.fill_between([w2, omega[-1]], -Ma, ylim[1], color="0.9", zorder=0)
ax.plot([w2, w2, omega[-1]], [ylim[1], -Ma, -Ma], "k", lw=2.5)

ax.axhline(0, color="k", lw=0.8)
ax.axhline(-3, color="k", lw=0.8, ls=":")
for w in (w1, wc, w2):
    ax.axvline(w, color="k", lw=0.8, ls="--")

ax.plot(wc, 0, "ko")
ax.plot([w_bw_S, w_bw_T], [-3, -3], "ko", mfc="w")
ax.annotate(r"$\omega_{BW}^S$", (w_bw_S, -3), (w_bw_S / 4, -15),
            arrowprops=dict(arrowstyle="->"))
ax.annotate(r"$\omega_{BW}^T$", (w_bw_T, -3), (w_bw_T * 2, 12),
            arrowprops=dict(arrowstyle="->"))

ax.text(omega[1] * 1.5, Mb + 2, f"$M_b$ = {Mb:.0f} dB", va="bottom")
ax.text(w2 * 1.2, -Ma - 2, f"$-M_a$ = $-${Ma:.0f} dB", va="top")
ax.text(omega[1] * 1.5, -Mb - 2, f"$-M_b$ = $-${Mb:.0f} dB", va="top")

trans = ax.get_xaxis_transform()
for x, txt in ((np.sqrt(omega[0] * w1), "Zona B"),
               (wc, "Zona C"),
               (np.sqrt(w2 * omega[-1]), "Zona A")):
    ax.text(x, 1.02, txt, transform=trans, ha="center", va="bottom")

ax.set_xticks([w1, wc, w2])
ax.set_xticklabels([r"$\omega_1$", r"$\omega_c$", r"$\omega_2$"])
ax.set_xlim(omega[0], omega[-1])
ax.set_ylim(*ylim)
ax.set_ylabel("Magnitud [dB]")
ax.set_xlabel(r"$\omega$")
ax.legend(loc="lower left", bbox_to_anchor=(0.33, 0.02))
ax.grid(True, which="major", alpha=0.3)
fig.tight_layout()
fig.savefig("espec_frec_fig5.png", dpi=150)
print(f"wc={wc:.3f}, MF={pm:.1f}°, wBW_S={w_bw_S:.3f}, wBW_T={w_bw_T:.3f}, "
      f"Mb={Mb:.0f} dB, Ma={Ma:.0f} dB")
