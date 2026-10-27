---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell} ipython3
:tags: [remove-cell]

import control as ctrl
import numpy as np
```

# Análisis de los sistemas en su forma de espacio de estados

+++

Supongamos que tenemos la siguiente función transferencia:

```{code-cell} ipython3
G=ctrl.tf([1,1],[1,2,3])
G
```

De los apuntes de teoría podemos escribir una representación en espacio de estados en la forma canónica de controlabilidad que tendrá el mismo comportamiento externo que $G$ de la siguiente manera:

```{code-cell} ipython3
Ac=np.array([[-2, -3],[1,0]])
Ac
```

Antes de seguir, verificamos que los polos de $G$ sean los autovalores de $\mathbf {Ac}$

```{code-cell} ipython3
print(G.poles())
print(np.linalg.eigvals(Ac))
```

Ahora definimos el resto de las matrices

```{code-cell} ipython3
Bc=np.array([[1],[0]])
Bc
```

```{code-cell} ipython3
Cc=np.array([[1, 1]])
Cc
```

```{code-cell} ipython3
Dc=0
```

Vamos ahora a definir un sistema `sys_c` que se comporte igual que $G$:

```{code-cell} ipython3
sys_c=ctrl.ss(Ac,Bc,Cc,Dc)
```

Si `sys_c` tiene los mismos polos, los mismos ceros y la misma ganancia en estado estacionario, entonces se comportará igual que $G$.

Veamos los polos:

```{code-cell} ipython3
sys_c.poles()
```

Ahora los ceros:

```{code-cell} ipython3
sys_c.zeros()
```

+++ {"tags": []}

Y la ganancia en estado estacionario en particular (o en cualquier frecuencia en general):

```{code-cell} ipython3
sys_c.dcgain()
```

```{code-cell} ipython3
G.dcgain()
```

Por lo tanto podemos ver que la función transferencia de `sys_c` será la misma que la de $G$. Es decir, `sys_c` se comporta **externamente** igual que $G$. Verificamos:

```{code-cell} ipython3
ctrl.tf(sys_c)
```

Vamos ahora a definir el sistema en espacio de estados que se comporte como $G$ en la forma canónica de observabilidad. De la teoría sabemos que:

```{code-cell} ipython3
Ao=Ac.T
Bo=Cc.T
Co=Bc.T
Do=Dc
```

```{code-cell} ipython3
sys_o=ctrl.ss(Ao,Bo,Co,Do)
```

```{code-cell} ipython3
sys_o.poles()
```

```{code-cell} ipython3
sys_o.zeros()
```

```{code-cell} ipython3
sys_o.dcgain()
```

```{code-cell} ipython3
ctrl.tf(sys_o)
```

El módulo de control de Python puede transformar una función transferencia a una forma de estados (no necesariamente en alguna forma canónica). Esto se hace:

```{code-cell} ipython3
sys=ctrl.ss(G)
sys
```

Además Python puede transformar un sistema en espacio de estados a alguna de las formas canónicas.

Por ejemplo, para escribir `sys` (que está ahora en espacio de estados) en su forma canónica de controlabilidad podemos hacer:

```{code-cell} ipython3
sys_c, Tc=ctrl.canonical_form(sys, 'reachable') # controlable
sys_c, Tc
```

Notar que esta función necesita como primer argumento un sistema en espacio de estados.

Si queremos la forma canónica de observabilidad podemos hacer:

```{code-cell} ipython3
sys_o,To = ctrl.canonical_form(sys, 'observable')
sys_o, To
```

Existe otra forma canónica de representación en espacio de estados que se la conoce como forma canónica modal. Esta la podemos obtener haciendo:

```{code-cell} ipython3
sys_m, Tm = ctrl.canonical_form(sys, 'modal')
sys_m, Tm
```

Esta forma canónica lo que hace es aislar los modos unos de otros. Es decir, cada modo aparece en la diagonal. Sin embargo, como vemos en este caso, no tenemos una forma diagonal de la matriz $\mathbf A$. Esto sucede porque hay casos en que no se puede o no se desea aislarlos:

- en caso de que se tengan autovalores complejos conjugados, no se aíslan para que las matrices $\mathbf A$, $\mathbf B$ y $\mathbf C$ tengan coeficientes reales.
- en caso de que sean múltiples, en general no se pueden aislar porque no hay suficientes autovectores independientes para armar la transformación. Para estos casos se utiliza la forma de Jordan.

+++

Vamos a ver otro ejemplo:

```{code-cell} ipython3
s=ctrl.tf('s')
G2 = 1/((s+1)*(s+2)*(s+3))
G2
```

Vemos que esta función transferencia tiene los polos en -1, -2 y -3. Transformemos a espacio de estados usando la función `ss`.

```{code-cell} ipython3
sys2 = ctrl.ss(G2)
sys2
```

Veamos al sistema en su forma canónica de controlabilidad.

```{code-cell} ipython3
ctrl.canonical_form(sys2, 'reachable')
```

Ahora lo podemos ver en la forma canónica de observabilidad

```{code-cell} ipython3
ctrl.canonical_form(sys2, 'observable')
```

Finalmente obtengamos la forma canónica modal:

```{code-cell} ipython3
sys2_m, Tm =ctrl.canonical_form(sys2, 'modal')
sys2_m.A
```

```{note}
- La función `canonical_form` devuelve un sistema en la forma canónica solicitada y la matriz de transformación necesaria para obtenerlo
- en la diagonal de la matriz  $\mathbf A$ de la forma canónica modal tenemos los modos del sistema (polos de $G$ o autovalores de $A$)
- fuera de la diagonal $\mathbf A$ tenemos ceros o valores muy cercanos a ceros (debido a problemas numéricos en el cálculo).
- En caso de tener autovalores repetidos, tendremos una matriz $\mathbf{A}$ diagonal por bloques (forma de Jordan).
- En general, los autovalores complejos conjugados tampoco se ponen en la diagonal, para evitar tener matrices con valores complejos.
```

+++

Verificamos el resto de las matrices:

```{code-cell} ipython3
sys2_m.B
```

```{code-cell} ipython3
sys2_m.C
```

```{code-cell} ipython3
sys2_m.D
```

En esta forma canónica podemos interpretar la matriz $\mathbf B$ como la conexión de la entrada con cada modo del sistema y, de forma análoga, la matriz $\mathbf C$ como la conexión de cada modo con la salida del sistema.

+++

## Ejemplo: controlabilidad y observabilidad en la conexión de sistemas

Supongamos que se tienen las siguientes funciones transferencia $G_1$ y $G_2$:

```{code-cell} ipython3
G1=ctrl.tf(1,[1,1])
G2=ctrl.tf([1,1],[1,2])
G1
```

```{code-cell} ipython3
G2
```

Podemos ver que $G_1$ tiene un polo en -1 y $G_2$ tiene un polo en -2 y un cero en -1.

+++

Ahora supongamos que queremos un nuevo sistema que:

- conecta la salida de $G_1$ con la entrada de $G_2$,
- su salida es la salida de $G_2$,
- su entrada es la entrada de $G_1$.

+++

Para eso vamos a usar la función `interconnect`. Esta conecta sistemas en espacio de estados a partir de los nombres de sus señales: las entradas y salidas que tienen el mismo nombre se conectan entre sí. Entonces pasamos $G_1$ y $G_2$ a espacio de estados, nombrando sus señales de modo que la salida de $G_1$ (`v`) sea la entrada de $G_2$:

```{code-cell} ipython3
sys1 = ctrl.ss(G1, inputs='u', outputs='v', name='G1')
sys2 = ctrl.ss(G2, inputs='v', outputs='y', name='G2')
```

Y luego realizamos las conexiones, indicando cuáles son la entrada y la salida del sistema completo:

```{code-cell} ipython3
sys_c = ctrl.interconnect([sys1, sys2], inplist='u', outlist='y')
sys_c
```

Analizamos los polos y ceros del sistema ya interconectado:

```{code-cell} ipython3
sys_c.poles()
```

```{code-cell} ipython3
sys_c.zeros()
```

Vemos que el sistema conserva los mismos polos y los mismos ceros que $G_1$ y $G_2$, lo cual era de esperarse, ya que su función transferencia es $G_1G_2$.

+++

Obtengamos la forma canónica de controlabilidad del sistema:

```{code-cell} ipython3
sys_c, Tc=ctrl.canonical_form(sys_c, 'reachable')
sys_c
```

Podemos ver que las matrices $ \mathbf A$, $\mathbf B$, $\mathbf C$ y $\mathbf D$ coinciden con lo visto en teoría.

Ahora obtengamos la forma canónica de observabilidad:

```{code-cell} ipython3
:tags: [raises-exception]

ctrl.canonical_form(sys_c, 'observable')
```

Podemos ver que este sistema no puede ser escrito en su forma canónica de observabilidad. Esto sucede porque el sistema no es observable.

```{admonition} Interpretación
:class: hint

Un sistema observable necesita tener evidencia de lo que sucede con cada modo en al menos una salida del sistema. Como el modo en -1 queda completamente tapado por el cero en esa misma frecuencia, este sistema no es observable: no hay ninguna evidencia del modo en -1 a la salida.

```

+++

Ahora hagamos la conexión al revés (primero $G_2$ y luego $G_1$):

Para esto cambiamos los nombres de las señales: ahora la salida de $G_2$ (`v`) es la entrada de $G_1$:

```{code-cell} ipython3
sys1_o = ctrl.ss(G1, inputs='v', outputs='y', name='G1')
sys2_o = ctrl.ss(G2, inputs='u', outputs='v', name='G2')
sys_o = ctrl.interconnect([sys1_o, sys2_o], inplist='u', outlist='y')
sys_o
```

Obtengamos la forma canónica observable:

```{code-cell} ipython3
sys_o, To=ctrl.canonical_form(sys_o, 'observable')
sys_o
```

Y ahora la forma canónica controlable:

```{code-cell} ipython3
:tags: [raises-exception]

ctrl.canonical_form(sys_o, 'reachable')
```

Podemos ver que ahora no podemos obtener la forma canónica de controlabilidad.

```{admonition} Interpretación
:class: hint

La razón de esto es que no se puede excitar el modo -1, que ahora quedó tapado desde el lado de la entrada. Toda excitación que tenga "frecuencia generalizada -1" será bloqueada por el cero en -1. Por lo tanto este sistema no es controlable, ya que no se puede excitar el modo -1 desde esa entrada.
```

Es importante destacar que ambos sistemas presentan la misma función transferencia $G_1G_2$, pero uno es solo controlable y el otro es solo observable. Esto se debe a que la controlabilidad y la observabilidad son propiedades internas de un sistema.

```{attention}
La **controlabilidad** y la **observabilidad**  no pueden ser decididas a partir de modelos externos de un sistema como son las funciones transferencias.
```

Estas dos mismas propiedades pueden ser analizadas con la forma modal. Tomemos el sistema `sys_c`, donde la entrada está conectada a $G_1$ y la salida a $G_2$:

```{code-cell} ipython3
sys_mc, Tmc = ctrl.canonical_form(sys_c, 'modal')
sys_mc
```

Podemos ver que la matriz $\mathbf B$ tiene todos los valores distintos de 0. Esto significa que todos los modos están conectados a la entrada, por lo que deducimos que el sistema es controlable.

Pero podemos ver que $\mathbf C$ tiene un 0 (o un valor numéricamente despreciable) en la posición del modo -1 de la diagonal de $\mathbf A$. Esto quiere decir que no hay ninguna evidencia del modo -1 en la salida, por lo que el sistema no es observable.

+++

Probemos ahora con la segunda conexión:

```{code-cell} ipython3
sys_mo, Tmo = ctrl.canonical_form(sys_o, 'modal')
sys_mo
```

Podemos ver ahora que la matriz $\mathbf C$ no tiene ningún valor igual a 0, por lo que ahora el sistema es observable (todos los modos están presentes de alguna manera en la salida). Pero tenemos un 0 (o un valor numéricamente despreciable) en la fila de $\mathbf B$ que se corresponde con el modo en -1. Esto quiere decir que no podemos excitar este modo. Por lo tanto no es controlable.

```{important}
La controlabilidad y la observabilidad pueden ser evaluadas con el sistema en su forma **canónica modal**, analizando las relaciones de las matrices $\mathbf{B}$ y $\mathbf{C}$ con la matriz $\mathbf{A}$.
```
