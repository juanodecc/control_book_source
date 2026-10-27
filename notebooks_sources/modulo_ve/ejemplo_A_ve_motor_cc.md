---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.10.3
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

```{code-cell} ipython3
---
tags: [remove-cell]
---
import numpy as np
import control as ctrl
import matplotlib.pyplot as plt
```

+++

# Diseño para un motor de corriente continua

Supongamos que la transferencia de nuestro sistema es:

$$G(s)=\frac{10}{s(s+2)(s+8)}$$

Diseñar un controlador que ubique los polos en:

$$pc=[-1.42;\quad -1.04\pm2.14j]$$

y los del estimador tres veces más rápidos.

Como tenemos el sistema en forma de función transferencia, lo llevamos a una forma en espacio de estados.

+++

```{code-cell} ipython3
G=ctrl.tf(10,[1,10,16,0])
G
```

+++

## Expresión en variables de estado

De las formas canónicas disponibles (ver `help(ctrl.canonical_form)`), elegimos la forma canónica de observabilidad.

```{code-cell} ipython3
sys,_=ctrl.canonical_form(ctrl.ss(G),'observable')
sys
```

+++

## Ley de control y estimador completo

```{code-cell} ipython3
pc=np.array([-1.42, -1.04+2.14j,-1.04-2.14j])
pe = pc*3
```

+++

Notar que podríamos haber escrito `pc` como una lista de los valores donde queremos ubicar los polos a lazo cerrado. Sin embargo, luego `pc*3` sobre una lista repetiría la lista tres veces en lugar de multiplicar cada polo por 3.

+++

**Obtenemos la ley de control:**

```{code-cell} ipython3
K=ctrl.place(sys.A,sys.B,pc)
```

+++

**Obtenemos L del estimador:**

```{code-cell} ipython3
L=ctrl.place(sys.A.T,sys.C.T,pe).T
```

+++

Hemos podido utilizar el comando `place` debido a que los 3 polos, tanto del estimador como de la ley de control, son distintos. De haber querido ubicar dos polos en el mismo lugar, hubiéramos tenido que usar el comando `acker`.

Sin embargo, es necesario tener en cuenta que `acker` es numéricamente poco confiable para sistemas de orden mayor a 4.

+++

### Sistema controlador con estimador completo

```{code-cell} ipython3
Dc=ctrl.ss(sys.A-sys.B@K-L@sys.C,L,-K,0)
ctrl.tf(Dc)
```

```{code-cell} ipython3
Dc.poles()
```

+++

Podemos ver que el controlador diseñado es inestable. Esto no es deseable.

Las razones por las que no es deseable un controlador inestable son:

1. Presenta dificultades para ser probado, ya sea el compensador por sí solo o en lazo abierto durante la puesta en funcionamiento. Sin embargo, en algunos casos se puede lograr una mejor performance del sistema controlado con un controlador inestable (hay sistemas que ni siquiera pueden ser estabilizados con controladores estables). En ese caso se aceptan estos inconvenientes.

2. Para ganancias bajas, el sistema a lazo cerrado con un controlador inestable resulta inestable (ver el lugar de las raíces). En general, los actuadores presentan saturaciones, es decir, valores máximos de actuación. Cuando un actuador satura, desde el punto de vista del lazo se ve como una reducción de la ganancia, que lleva al sistema a la zona inestable o lo acerca a ella.

Los sistemas que se vuelven inestables cuando su ganancia se reduce se conocen como sistemas **condicionalmente estables** y **deben ser evitados** en la medida de lo posible.

+++

## Rediseñamos usando un estimador reducido

+++

Ahora pondremos los polos tal que $\omega_n=6$ rad/seg y $\zeta=0.707$

```{code-cell} ipython3
pe_red= np.roots([1,2*0.707*6,6**2])
pe_red
```

+++

Necesitamos las submatrices de $\mathbf A$ y $\mathbf B$ para calcular el estimador reducido:

```{code-cell} ipython3
Aaa=sys.A[0:1,0:1]
Aab=sys.A[0:1,1:]
Aba=sys.A[1:,0:1]
Abb=sys.A[1:,1:]

Ba = sys.B[0:1,0:]
Bb = sys.B[1:,0:]
```
+++

Ahora calculemos el estimador reducido.

```{code-cell} ipython3
Ltred = ctrl.place(Abb.T,Aab.T,pe_red).T
Ltred
```

+++

### Sistema controlador con estimador reducido

```{code-cell} ipython3
Ka=K[0:1,0:1]
Kb=K[0:1,1:]

Ar = Abb-Ltred@Aab-(Bb-Ltred@Ba)@Kb
Br = Ar@Ltred + Aba - Ltred@Aaa - (Bb-Ltred@Ba)@Ka
Cr = -Kb
Dr = -Ka-Kb@Ltred
```

```{code-cell} ipython3
Dcr = ctrl.ss(Ar,Br,Cr,Dr)
Dcr
```

```{code-cell} ipython3
ctrl.tf(Dcr)
```

```{code-cell} ipython3
Dcr.poles()
```

```{code-cell} ipython3
Dcr.zeros()
```

+++

Si bien este diseño mejora al anterior, ya que el controlador resultante es estable, presenta un problema potencialmente menos dañino: es un controlador de fase no mínima, ya que tiene un cero en el semiplano derecho del plano $s$, lo que limita la velocidad del sistema controlado.

```{code-cell} ipython3
Lr=-ctrl.tf(Dcr)*G/ctrl.db2mag(6)
ctrl.bode(Lr,dB=True, display_margins=True, omega_num=2000);
plt.gcf().set_size_inches(12,8)
```

```{code-cell} ipython3
T=ctrl.feedback(Lr)
plt.figure()
ctrl.bode(T,dB=True);
plt.gcf().set_size_inches(12,8)
```

```{code-cell} ipython3
_=ctrl.nyquist(Lr);
plt.gcf().set_size_inches(8,6)
```

+++

Agregamos la referencia al controlador de orden reducido (ver la sección de inserción de referencias).

```{code-cell} ipython3
def seguimiento_referencia(sys):
    aux1=np.vstack((np.hstack((sys.A,sys.B)),
                   np.hstack((sys.C,sys.D))))
    n=np.shape(sys.A)[0]
    aux2=np.vstack((np.zeros((n,1)),[1]))
    N=np.linalg.inv(aux1)@aux2
    Nx=N[0:n]
    Nu=N[n]
    return Nx, Nu

def calculate_Nbar(Nx,Nu,K):
    return Nu+K@Nx
```

```{code-cell} ipython3
Nx, Nu = seguimiento_referencia(sys)
Nbar = calculate_Nbar(Nx,Nu, K)
Nbar
```

```{code-cell} ipython3
N=Nbar
M=(Bb-Ltred@Ba)@N
M
```

```{code-cell} ipython3
Dcr_ref = ctrl.ss(Ar, np.hstack((Br,M)), Cr, np.hstack((Dr,N)))
Dcr_ref
```

+++

## Rediseño usando SRL

+++

Vamos a diseñar el sistema para ubicar los polos de forma tal que se tenga un ancho de banda de 2.5 rad/s y que los polos del estimador estén aproximadamente 2.5 veces más rápidos.

+++

Para usar el lugar simétrico de las raíces (LSR) vamos a tomar $\mathbf{C_1} = \mathbf{C}$ para la ley de control y $\mathbf{B_1} = \mathbf{B}$ para el estimador, de modo que en ambos casos se usa $G(-s)G(s)$.

```{code-cell} ipython3
def conjugate_tf(G):
    """Devuelve G(-s) para un sistema SISO."""
    num = ctrl.tf(G).num[0][0]
    den = ctrl.tf(G).den[0][0]
    # el coeficiente i multiplica a s^(n-1-i)
    nume = [c*(-1)**(len(num)-1-i) for i, c in enumerate(num)]
    dene = [c*(-1)**(len(den)-1-i) for i, c in enumerate(den)]
    return ctrl.tf(nume, dene)
```

```{code-cell} ipython3
Gm=conjugate_tf(G)
Gm
```

```{code-cell} ipython3
_=ctrl.rlocus(G*Gm)
plt.gcf().set_size_inches(8,6)
```

+++

Con $\rho=26$ obtenemos los polos con una frecuencia de corte de 2.5 rad/s.

```{code-cell} ipython3
pc = ctrl.root_locus_map(G*Gm, gains=[26]).loci[0]
pc = pc[pc.real<0]
pc
```

+++

Y con $\rho=1350$ tenemos los polos del estimador.

```{code-cell} ipython3
pe = ctrl.root_locus_map(G*Gm, gains=[1350]).loci[0]
pe = pe[pe.real<0]
pe
```

```{code-cell} ipython3
print("Polos de la ley de control: ",pc)
print("Polos del estimador: ",pe)
```

```{code-cell} ipython3
K=ctrl.place(sys.A,sys.B,pc)
L=ctrl.place(sys.A.T,sys.C.T,pe).T
```

```{code-cell} ipython3
Dcsrl=ctrl.ss(sys.A-sys.B@K-L@sys.C,L,-K,0)
ctrl.tf(Dcsrl)
```

```{code-cell} ipython3
Dcsrl.poles()
```

```{code-cell} ipython3
Dcsrl.zeros()
```

```{code-cell} ipython3
_=ctrl.bode((-sys*Dc,-sys*Dcr,-sys*Dcsrl),omega_limits=(1e-2,1e2),dB=True)
plt.gcf().set_size_inches(12,8)
```

```{code-cell} ipython3
print(ctrl.margin(-sys*Dc))
print(ctrl.margin(-sys*Dcr))
print(ctrl.margin(-sys*Dcsrl))
```

```{code-cell} ipython3
T1=ctrl.feedback(-sys*Dc)
T2=ctrl.feedback(-sys*Dcr)
T3=ctrl.feedback(-sys*Dcsrl)
```

```{code-cell} ipython3
print(f"Los polos de T1 son: {T1.poles()}")
print(f"Los polos de T2 son: {T2.poles()}")
print(f"Los polos de T3 son: {T3.poles()}")
```

+++

### Respuesta del sistema controlado a condiciones iniciales (salida inicial distinta de 0)

```{code-cell} ipython3
t1,y1 = ctrl.initial_response(T1, X0=[0,0,0,-1,0,0], T=np.linspace(0,5,1000))
t2,y2 = ctrl.initial_response(T2, X0=[0,0,-1,0,0], T=np.linspace(0,5,1000))
t3,y3 = ctrl.initial_response(T3, X0=[0,0,0,-1,0,0], T=np.linspace(0,5,1000))
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t1,y1,label="T1")
ax.plot(t2,y2,label="T2")
ax.plot(t3,y3,label="T3")
plt.legend()
ax.set_title('Respuesta a condiciones iniciales')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Salida")
ax.grid()
```

+++

## Conexión de sistemas entrada/salida

+++

Podemos ver en el caso anterior que, al usar la función `ctrl.feedback`, perdemos (al menos parcialmente) el conocimiento de cómo están ordenados los estados del sistema.

Para tener mayor control de cómo están ubicados los estados, las entradas y las salidas, es conveniente usar la función `ctrl.interconnect`, que conecta sistemas a partir de los nombres de sus señales.

Primero damos nombre a las señales de la planta y de los controladores. La planta tiene entrada `u` y salida `y`; los controladores tienen entrada `y` y salida `uc`. Además definimos un sumador que forma la entrada de la planta como `u = uc + w`, donde `w` es una entrada auxiliar:

```{code-cell} ipython3
planta = ctrl.ss(sys.A, sys.B, sys.C, sys.D, inputs='u', outputs='y', name='planta')
suma = ctrl.summing_junction(inputs=['uc', 'w'], output='u', name='suma')

def controlador(Dsys):
    return ctrl.ss(Dsys.A, Dsys.B, Dsys.C, Dsys.D, inputs='y', outputs='uc', name='controlador')
```

Ahora conectamos la planta con cada uno de los tres controladores:

```{code-cell} ipython3
sys_conectado_1 = ctrl.interconnect([planta, controlador(Dc), suma], inplist='w', outlist=['y','uc'])
sys_conectado_1
```

```{code-cell} ipython3
sys_conectado_2 = ctrl.interconnect([planta, controlador(Dcr), suma], inplist='w', outlist=['y','uc'])
sys_conectado_2
```

```{code-cell} ipython3
sys_conectado_3 = ctrl.interconnect([planta, controlador(Dcsrl), suma], inplist='w', outlist=['y','uc'])
sys_conectado_3
```

+++

La manera en que `ctrl.interconnect` trabaja es:

1. El primer argumento es la lista de sistemas que se quieren interconectar. Cada sistema tiene sus entradas y salidas con nombre.

2. Las señales que tienen el mismo nombre se conectan automáticamente: la salida `y` de la planta se conecta con la entrada `y` del controlador, y la salida `uc` del controlador con la entrada `uc` del sumador, cuya salida `u` es la entrada de la planta.

3. `inplist` indica qué entradas son las del sistema completo. Aquí no hay una referencia, pero el módulo de control tiene algunos problemas con sistemas sin entradas. Por eso tomamos como entrada la señal auxiliar `w`, que se suma a la salida del controlador en la entrada de la planta.

4. `outlist` indica las salidas del sistema completo. Tomamos la salida de la planta `y` y el esfuerzo de control `uc`.

Los estados del sistema conectado quedan ordenados según el orden de la lista: primero los 3 estados de la planta y luego los del controlador (el observador).

+++

Vamos a realizar nuevamente las simulaciones con los sistemas definidos mediante `interconnect`.

```{code-cell} ipython3
t1,y1 = ctrl.initial_response(sys_conectado_1, X0=[1,0,0,0,0,0], T=np.linspace(0,5,1000))
t2,y2 = ctrl.initial_response(sys_conectado_2, X0=[1,0,0,0,0], T=np.linspace(0,5,1000))
t3,y3 = ctrl.initial_response(sys_conectado_3, X0=[1,0,0,0,0,0], T=np.linspace(0,5,1000))
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t1,y1[0,:],label="sys conectado 1")
ax.plot(t2,y2[0,:],label="sys conectado 2")
ax.plot(t3,y3[0,:],label="sys conectado 3")
plt.legend()
ax.set_title('Respuesta a condiciones iniciales')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Salida")
ax.grid()
```

+++

Podemos también mirar el esfuerzo de control, ya que es una salida del sistema conectado.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t1,y1[1,:],label="sys conectado 1")
ax.plot(t2,y2[1,:],label="sys conectado 2")
ax.plot(t3,y3[1,:],label="sys conectado 3")
plt.legend()
ax.set_title('Respuesta a condiciones iniciales')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Esfuerzo de control")
ax.grid()
```

+++

Este ejemplo muestra claramente cómo la elección de los polos usando criterios de optimización, como el del lugar simétrico de las raíces, nos da un control mucho mejor, tanto en tiempo de respuesta como en esfuerzo de control.

### Seguimiento de referencia con el estimador reducido

Conectamos la planta con el controlador de orden reducido con referencia, `Dcr_ref`, que tiene dos entradas: la salida de la planta `y` y la referencia `r`. El sistema conectado tiene como entrada la referencia y como salidas la salida de la planta `y` y el esfuerzo de control `u`.

```{code-cell} ipython3
Dcr_ref_n = ctrl.ss(Dcr_ref.A, Dcr_ref.B, Dcr_ref.C, Dcr_ref.D,
                    inputs=['y','r'], outputs='u', name='controlador')
psys_controlado_con_ref = ctrl.interconnect([planta, Dcr_ref_n], inplist='r', outlist=['y','u'])
psys_controlado_con_ref.poles()
```

La ganancia en continua desde la referencia hasta la salida debe ser 1:

```{code-cell} ipython3
ctrl.dcgain(psys_controlado_con_ref)
```

```{code-cell} ipython3
t,y = ctrl.step_response(psys_controlado_con_ref)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t,y[0,:].T,label="psys conectado con ref")
ax.set_title('Respuesta al escalón en la referencia')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Salida")
ax.grid()
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t,y[1,:].T,label="psys conectado con ref")
ax.set_title('Respuesta al escalón en la referencia')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Esfuerzo de control")
ax.grid()
```

+++

## Control integral y estimador de orden completo

Para obtener error nulo en estado estacionario de forma robusta, agregamos un estado integrador $x_I$ con $\dot x_I = y - r$. El sistema aumentado (con $r=0$) es:

$$
\begin{bmatrix}\dot x_I\\ \dot{\mathbf x}\end{bmatrix} =
\underbrace{\begin{bmatrix} 0 & \mathbf C\\ \mathbf 0 & \mathbf A\end{bmatrix}}_{\mathbf A_u}
\begin{bmatrix} x_I\\ \mathbf x\end{bmatrix} +
\underbrace{\begin{bmatrix} 0\\ \mathbf B\end{bmatrix}}_{\mathbf B_u} u
$$

y diseñamos una ley de control $u = -\mathbf K_u [x_I \;\; \mathbf x]^T = -K_i x_I - \mathbf K \mathbf x$ para el sistema aumentado.

```{code-cell} ipython3
Au=np.vstack((np.hstack((np.zeros((1,1)), sys.C)),
              np.hstack((np.zeros((3,1)), sys.A))))
Au
```

```{code-cell} ipython3
Bu = np.vstack((0,sys.B))
Bu
```

```{code-cell} ipython3
Ku = ctrl.place(Au,Bu, np.array([-1.42, -1.04+2.14j,-1.04-2.14j, -3]))
Ku
```

```{code-cell} ipython3
Ki=Ku[0,0]
Ki
```

El integrador calcula $K_i\int (r - y)\,dt = -K_i x_I$; su entrada 1 es la referencia y su entrada 2 la salida de la planta:

```{code-cell} ipython3
integrador=ctrl.ss([[0]],[[Ki,-Ki]],[1],[0, 0])
integrador
```

```{code-cell} ipython3
# Estimador más ley de control

L=ctrl.place(sys.A.T, sys.C.T, np.array([-1.42, -1.04+2.14j,-1.04-2.14j])*3).T
L
```

```{code-cell} ipython3
Ae=sys.A-L@sys.C
Ae
```

```{code-cell} ipython3
Be=np.hstack((L,sys.B))
Be
```

```{code-cell} ipython3
Ce=-Ku[0:1,1:]
Ce
```

```{code-cell} ipython3
---
tags: [hide-output]
---
De=0
estim = ctrl.ss(Ae,Be,Ce,De)
estim
```

Conectamos la planta, el estimador y el integrador. El estimador recibe la salida de la planta `y` y la entrada de la planta `u`; la entrada de la planta es la suma de las salidas del estimador `ue` y del integrador `ui`; y la entrada del integrador `r` es la referencia. Tomamos como salidas la salida de la planta y el esfuerzo de control `u` total:

```{code-cell} ipython3
---
tags: [hide-output]
---
estim_n = ctrl.ss(estim.A, estim.B, estim.C, estim.D,
                  inputs=['y','u'], outputs='ue', name='estimador')
integrador_n = ctrl.ss(integrador.A, integrador.B, integrador.C, integrador.D,
                       inputs=['r','y'], outputs='ui', name='integrador')
suma_u = ctrl.summing_junction(inputs=['ue','ui'], output='u', name='suma_u')

planta_controlada = ctrl.interconnect([planta, estim_n, integrador_n, suma_u],
                                      inplist='r', outlist=['y','u'])
planta_controlada
```

```{code-cell} ipython3
t,y = ctrl.step_response(planta_controlada)
```

```{code-cell} ipython3
---
tags: [hide-input]
---
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t,y[0,:].T,label="control integral")
ax.set_title('Respuesta al escalón en la referencia')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Salida")
ax.grid()
```

```{code-cell} ipython3
planta_controlada.poles()
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12,4))
ax.plot(t,y[1,:].T,label="control integral")
ax.set_title('Respuesta al escalón en la referencia')
ax.set_xlabel("Tiempo")
ax.set_ylabel("Esfuerzo de control")
ax.grid()
```