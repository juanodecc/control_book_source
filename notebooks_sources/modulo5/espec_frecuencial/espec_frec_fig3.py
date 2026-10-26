"""Genera espec_frec_fig3.png: márgenes de ganancia y de fase sobre el
diagrama de Bode de la función de lazo L.
"""
import control as ctrl
import matplotlib.pyplot as plt
import numpy as np

# Función de lazo de ejemplo: integrador + dos polos
L = ctrl.tf(0.7, np.polymul([1, 1, 0], [0.2, 1]))

omega = np.logspace(-1, 1, 1000)
resp = ctrl.frequency_response(L, omega)
mag_db = 20 * np.log10(resp.magnitude)
phase = np.unwrap(resp.phase) * 180 / np.pi

gm, pm, w180, wc = ctrl.margin(L)
mag_w180 = 20 * np.log10(np.abs(L(1j * w180)))
phase_wc = np.angle(L(1j * wc), deg=True)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

# Magnitud
ax1.semilogx(omega, mag_db, color="C0", lw=2)
ax1.axhline(0, color="k", lw=0.8)
ax1.plot([w180, w180], [mag_w180, 0], color="C3", lw=3)
ax1.text(w180 * 1.08, mag_w180 / 2, f"$MG$ = {-mag_w180:.1f} dB",
         color="C3", va="center", fontsize=12)
ax1.set_ylabel("Magnitud [dB]")
ax1.set_ylim(-60, 25)

# Fase
ax2.semilogx(omega, phase, color="C0", lw=2)
ax2.axhline(-180, color="k", lw=0.8)
ax2.plot([wc, wc], [-180, phase_wc], color="C3", lw=3)
ax2.text(wc / 1.08, (phase_wc - 180) / 2, f"$MF$ = {pm:.1f}°",
         color="C3", va="center", ha="right", fontsize=12)
ax2.set_ylabel("Fase [grados]")
ax2.set_xlabel(r"Frecuencia $\omega$ [rad/s]")
ax2.set_ylim(-275, -85)
ax2.set_yticks(np.arange(-270, -89, 30))

for ax in (ax1, ax2):
    ax.axvline(wc, color="k", lw=0.8, ls="--")
    ax.axvline(w180, color="k", lw=0.8, ls="--")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlim(omega[0], omega[-1])

trans = ax1.get_xaxis_transform()
ax1.text(wc, 1.02, r"$\omega_c$", transform=trans, ha="center", fontsize=13)
ax1.text(w180, 1.02, r"$\omega_{180}$", transform=trans, ha="center",
         fontsize=13)

fig.tight_layout()
fig.savefig("espec_frec_fig3.png", dpi=150)
print(f"wc={wc:.3f}, w180={w180:.3f}, MG={-mag_w180:.1f} dB, MF={pm:.1f}°")
