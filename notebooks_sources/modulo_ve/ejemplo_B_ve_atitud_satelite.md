---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.2
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Diseño del sistema de control de actitud de un satélite

```{code-cell} ipython3
:tags: [remove-cell]

import numpy as np
import control as ctrl
import matplotlib.pyplot as plt
```

## Definición del sistema

Diseñar un compensador para la planta:

$$ \dot{\mathbf{x}}=\begin{bmatrix}
0&1\\
0&0\\
\end{bmatrix}\mathbf{x}+\begin{bmatrix}
0\\
1
\end{bmatrix}u$$

$$ y=\begin{bmatrix}
1&0\end{bmatrix}\mathbf{x}.$$

que ubique los polos de lazo cerrado tal que $\omega_n =1$ y $\zeta=0.707$:

```{code-cell} ipython3
A=[[0,1],[0,0]]
B=[[0],[1]]
C=[[1,0]]
D=[[0]]
sys=ctrl.ss(A,B,C,D)
```

## Análisis de controlabilidad y observabilidad

Calculamos el rango de las matrices de observabilidad y de controlabilidad. Con las matrices $\mathbf B$ y $\mathbf C$ dadas, el sistema es observable y controlable (rango 2). Sin embargo, no lo sería si se midiera la velocidad en lugar de la posición, $\mathbf C = [0\;\;1]$, o si se actuara sobre la posición en lugar de la aceleración, $\mathbf B = [1\;\;0]^T$:

```{code-cell} ipython3
print("Observabilidad con C dada:", np.linalg.matrix_rank(ctrl.obsv(A,C)))
print("Observabilidad midiendo la velocidad:", np.linalg.matrix_rank(ctrl.obsv(A,[[0,1]])))
print("Controlabilidad con B dada:", np.linalg.matrix_rank(ctrl.ctrb(A,B)))
print("Controlabilidad con B=[1 0]':", np.linalg.matrix_rank(ctrl.ctrb(A,[[1],[0]])))
```

Para cumplir con los requerimientos debemos ubicar los polos en $\alpha_c = -0.707 \pm 0.707j$.

## Ley de control

Usando el comando `acker` o `place` obtenemos la ley de control que ubica los polos del sistema donde queremos.

```{code-cell} ipython3
wnc=1
zetac=np.sqrt(2)/2
polyc=[1,2*zetac*wnc,wnc**2]
alpha_c =np.roots(polyc)
print(alpha_c)
```

```{code-cell} ipython3
K = ctrl.place(A,B,alpha_c)
print(K)
```

Usando `acker` obtenemos el mismo resultado. Notar que `acker` devuelve un vector 1-D, por lo que lo convertimos en una matriz fila para poder operar con él:

```{code-cell} ipython3
K = np.atleast_2d(ctrl.acker(A,B,alpha_c))
print(K)
```

Controlamos que las cuentas estén bien hechas, verificando que los autovalores de $\mathbf{A}-\mathbf{BK}$ den donde tienen que dar:

```{code-cell} ipython3
l,_=np.linalg.eig(A-B@K)
print(l)
```

## Diseño del estimador

Ahora ubicamos los polos del estimador 5 veces más rápidos ($\omega_n=5$) y con $\zeta=0.5$.

```{code-cell} ipython3
wne=5
zetae=0.5
polye =[1,2*zetae*wne,wne**2]
rootse=np.roots(polye)
print(rootse)
```

```{code-cell} ipython3
Lt=ctrl.place(sys.A.T,sys.C.T,rootse).T
print(Lt)
```

## Definición del sistema de control

Expresando las ecuaciones de estado del controlador $D_c$ nos queda:

$$\begin{align*}
\mathbf{\dot{\hat{x}}}&=(\mathbf{A-BK-LC}) \mathbf{\hat {x}}+\mathbf{L}y\\
u&=-\mathbf{K}\mathbf{\hat{x}}\end{align*}$$

```{code-cell} ipython3
Dc=ctrl.ss(A-B@K-Lt@C,Lt,-K,[0])
ctrl.tf(Dc)
```

Con este controlador podemos hacer un análisis del sistema igual que lo hacíamos en control clásico. La función de transferencia de lazo es $-D_c(s)G(s)$, porque el signo de la realimentación ya está incluido en $D_c$:

```{code-cell} ipython3
_=ctrl.bode(sys*-Dc,dB=True)
plt.gcf().set_size_inches(12,8)
```

```{code-cell} ipython3
gm, pm, wcg, wcp = ctrl.margin(sys*-Dc)
print(f"Margen de ganancia: {ctrl.mag2db(gm):.1f} dB, margen de fase: {pm:.1f}°")
```

```{code-cell} ipython3
_=ctrl.rlocus(sys*-Dc,grid=True)
plt.gcf().set_size_inches(8,6)
```

Podemos ver que este diseño tiene un margen de fase de aproximadamente 50°.

## Con estimador reducido

Pondremos ahora el polo del estimador en $-5$ rad/s.

```{code-cell} ipython3
polesered=[-5]
Aaa=sys.A[0:1,0:1]
Aab=sys.A[0:1,1:]
Aba=sys.A[1:,0:1]
Abb=sys.A[1:,1:]

Ba = sys.B[0:1,:]
Bb = sys.B[1:,:]
```

```{code-cell} ipython3
Ltred = np.atleast_2d(ctrl.acker(Abb.T,Aab.T,polesered)).T
Ltred
```

Ahora podemos obtener el controlador con estimador reducido mediante las ecuaciones vistas en teoría. Para esto necesitamos separar la parte de $\mathbf K$ que multiplica al estado medido ($K_a$) de la que multiplica a los no medidos ($\mathbf{K_b}$).

## Definición del sistema controlador con estimador de orden reducido

```{code-cell} ipython3
Ka=K[:,0:1]
Kb=K[:,1:]

Ar = Abb-Ltred@Aab-(Bb-Ltred@Ba)@Kb
Br = Ar@Ltred + Aba - Ltred@Aaa - (Bb-Ltred@Ba)@Ka
Cr = -Kb
Dr = -Ka-Kb@Ltred
```

```{code-cell} ipython3
Dcr = ctrl.ss(Ar,Br,Cr,Dr)
ctrl.tf(-Dcr)
```

```{code-cell} ipython3
_=ctrl.bode((-Dcr*sys),dB=True)
plt.gcf().set_size_inches(12,8)
```

```{code-cell} ipython3
gm, pm, wcg, wcp = ctrl.margin(-Dcr*sys)
print(f"Margen de fase: {pm:.1f}°")
```

```{code-cell} ipython3
_=ctrl.rlocus(-Dcr*sys)
plt.gcf().set_size_inches(8,6)
```

Con el estimador reducido el controlador es de primer orden y el margen de fase es algo mayor, de aproximadamente 53°. En este caso no tiene sentido hablar de margen de ganancia: la fase de la función de lazo sólo vale $-180°$ en $\omega \rightarrow 0$, y el lugar de las raíces muestra que el lazo cerrado es estable para cualquier ganancia positiva.
