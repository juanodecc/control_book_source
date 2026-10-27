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

+++

# Inserción de referencias

+++

Comenzaremos nuestro estudio agregando referencias a un sistema controlado mediante la ley de control $u(t)=-\mathbf{Kx}(t)$.
Siguiendo la idea de control clásico uno podría hacer $u=-\mathbf K \mathbf x + r$, siendo $r$ la referencia. Sin embargo, esto en general llevaría a tener errores en estado estacionario muy grandes.

La forma correcta sería calcular los estados y la entrada en estado estacionario ($t \rightarrow \infty$). Si entramos con el valor de estado estacionario de $u$ y hacemos que para $t \rightarrow \infty$ la realimentación sea 0, entonces nos aseguramos de que el sistema tendrá error nulo. Matemáticamente esto lo podemos lograr haciendo que:

$$u=u_{ss}-\mathbf K(\mathbf x - \mathbf{x}_{ss})$$

Para calcular cuánto valen $u_{ss}$ y $\mathbf{x}_{ss}$ debemos expresar las ecuaciones de estado con las condiciones de estado estacionario, es decir:

$$
\begin{align*}
0&=\mathbf{A}\mathbf{x}_{ss}+\mathbf{B}u_{ss} \\
y_{ss}&=\mathbf{C}\mathbf{x}_{ss}+Du_{ss}
\end{align*}
$$

Entonces se quieren obtener los valores para los cuales $y_{ss}=r_{ss}$ para cualquier $r_{ss}$. Para hacer esto hacemos que $\mathbf{x_{ss}}=\mathbf{N_x}r_{ss}$ y $u_{ss}=N_ur_{ss}$. Haciendo esto tenemos el siguiente sistema de ecuaciones:

$$
\begin{bmatrix}
\mathbf A & \mathbf B\\
\mathbf C & D
\end{bmatrix} \begin{bmatrix}
\mathbf{N_x}\\
N_u\\ \end{bmatrix} =\begin{bmatrix}
\mathbf 0\\
1\end{bmatrix}
$$

+++

De esta manera

$$\begin{bmatrix}
\mathbf{N_x}\\
N_u\\ \end{bmatrix} =
\begin{bmatrix}
\mathbf A & \mathbf B\\
\mathbf C & D
\end{bmatrix}^{-1}\begin{bmatrix}
\mathbf 0\\
1\end{bmatrix}.
$$

Con estos valores podemos introducir la referencia (de forma "no robusta") haciendo:

$$u=N_ur-\mathbf {K}(\mathbf{x} - \mathbf{N_x}r)$$

Sabiendo cuánto vale la ley de control, es decir $\mathbf{K}$, podemos simplificar la expresión anterior de la siguiente manera:

$$u=-\mathbf{Kx}+\bar Nr$$

donde $\bar N = N_u+\mathbf{KN_x}$.

+++

Para poder ver el esfuerzo de control como una salida más del sistema controlado, tenemos que expresarlo en función de las entradas (ahora la entrada es $r$) y de los estados (siguen siendo $\mathbf{x}$). Entonces la ecuación de salida que tenemos que agregar es

$$u=-\mathbf{K x}+\bar Nr$$

````{admonition} Funciones para el cálculo del seguimiento a referencia
:class: hint

Con esta función podemos calcular las matrices para el seguimiento a referencia:

```{code} ipython3
def seguimiento_referencia(sys):
    aux1=np.vstack((np.hstack((sys.A,sys.B)),
                   np.hstack((sys.C,sys.D))))
    n=np.shape(sys.A)[0]
    aux2=np.vstack((np.zeros((n,1)),[1]))
    N=np.linalg.inv(aux1)@aux2
    Nx=N[0:n]
    Nu=N[n]
    return Nx, Nu
```

Para simplificar la implementación podemos usar solo esta ganancia:

```{code} ipython3
def calculate_Nbar(Nx,Nu,K):
    return Nu+K@Nx
```
````

## Inserción de referencia a un controlador con estimador en forma general

Recordando la ecuación del estimador con la ley de control, resulta la ecuación:

$$
\begin{align*}
\dot{ \hat{ \mathbf{x}}}(t)&= (\mathbf A-\mathbf{BK-LC}) \hat{\mathbf x}(t)+\mathbf Ly(t)\\
u(t)&=-\mathbf{K}\hat{\mathbf{x}}(t) + 0\, y(t)
\end{align*}
$$

Podemos ver que este sistema, que es un controlador, tiene una sola entrada, que es la salida (o medición) de nuestra planta a controlar. A este tipo de controlador, que solo tiene como objetivo mantener al sistema controlado en su punto de trabajo con un determinado comportamiento dinámico, se lo conoce como **regulador**.

Para darle al sistema controlado la posibilidad de ser un servosistema, controlado por un **servorregulador**, es decir, que tenga la capacidad de seguir referencias, es necesario agregar de alguna manera al controlador la entrada de referencia.

Es importante destacar que el comportamiento dinámico del sistema controlado no debe cambiar. Es decir la matriz $\mathbf A$ del sistema controlado (a lazo cerrado) debe ser la misma que antes de introducir la referencia.

Por lo tanto, la forma general de introducir la referencia sin modificar las dinámicas obtenidas anteriormente es agregar a las ecuaciones anteriores un término con la referencia como entrada. Es decir:

$$
\begin{align*}
\dot{ \hat{ \mathbf{x}}}(t)&= (\mathbf A-\mathbf{BK-LC}) \hat{\mathbf x}(t)+\mathbf Ly(t) + \mathbf M r(t)\\
u(t)&=-\mathbf{K}\hat{\mathbf{x}}(t) + 0\, y(t)+  N r(t)
\end{align*}
$$

La pregunta ahora es cómo elegir $\mathbf M$ y $N$ para que la inserción de referencias tenga una configuración correcta.

En este curso presentaremos 2 formas:
- Inserción de referencias para estimador autónomo: se eligen $\mathbf M$ y $N$ de forma tal que la dinámica del error de estimación no dependa de la referencia. Es decir, el error de estimación no se verá afectado cuando se cambie la referencia.
- Inserción de referencias mediante error de seguimiento: esto transforma nuevamente a nuestro sistema en uno de una sola entrada, $y(t)-r(t)$. Este sistema es más parecido al controlador/compensador clásico, ya que aparece la resta $y(t)-r(t)$ a la entrada. Esta forma de introducir la referencia en general tiene una peor performance que la anterior. Sin embargo, es útil cuando se mide directamente la diferencia entre lo que se quiere y lo que se tiene, es decir, cuando el sensor nos da directamente $y(t)-r(t)$. En cualquier otro caso es preferible la inserción de referencia con estimador autónomo.

## Estimador completo autónomo

Recordando la ecuación del estimador completo tenemos que:

$$\dot{ \hat{ \mathbf{x}}}(t)= (\mathbf A-\mathbf{BK-LC}) \hat{\mathbf x}(t)+\mathbf Ly(t) + \mathbf M r(t)$$

y

$$\dot{ \mathbf{x}}(t)= \mathbf A\mathbf x(t) +\mathbf{B} (-\mathbf K\hat{\mathbf{x}}(t)+ N r(t)) $$

Como queremos que la dinámica del error de estimación, $\dot{ \mathbf{x}}(t) -  \dot{ \hat{ \mathbf{x}}}(t)$, no dependa de $r(t)$, al restar las dos ecuaciones anteriores se deben anular los términos que dependen de $r(t)$. Entonces, por inspección notamos que:

$$ \mathbf M = \mathbf{B}  N $$

Se puede demostrar que, para que el error en estado estacionario sea cero (de forma "no robusta"), debe ser $N=\bar N$, calculada anteriormente.

Entonces:

$$\mathbf M = \mathbf{B}  \bar N$$

## Estimador por error de seguimiento

Se tienen que elegir $\mathbf M$ y $N$ tales que la entrada quede de la forma $y(t)-r(t)$. Inspeccionando las ecuaciones del controlador podemos notar que si elegimos:

$$\mathbf M = -\mathbf L$$

y

$$N=0$$

Entonces se tiene:

$$\dot{ \hat{ \mathbf{x}}}(t)= (\mathbf A-\mathbf{BK-LC}) \hat{\mathbf x}(t)+\mathbf L (y(t) - r(t))$$

y

$$u(t) = -\mathbf K\hat{\mathbf{x}}(t)$$

Por lo que ahora nuestro sistema controlador solo tiene una entrada igual a $y(t)-r(t)$.

+++

## Estimador reducido autónomo

Las ecuaciones para el sistema compensador con estimador reducido resultaron:

$$\begin{align*}
 \dot{\mathbf x}_c &= \mathbf A_r \mathbf x_c + \mathbf B_r y(t)\\
u(t) &= \mathbf C_r \mathbf x_c  + \mathbf D_r y(t)
\end{align*}$$

Donde las matrices que definen el espacio de estado son:

$$
\begin{align*}
 \mathbf A_r &= (\mathbf {A}_{bb}-\mathbf L\mathbf A_{ab})-(\mathbf B_b- \mathbf L B_a)\mathbf K_b \\
\mathbf B_r &= \mathbf {A}_r \mathbf L +\mathbf A_{ba}-\mathbf L \mathbf A_{aa} - (\mathbf B_b- \mathbf L B_a) K_a\\
\mathbf C_r &= -\mathbf K_b\\
\mathbf D_r &= -K_a -\mathbf K_b \mathbf L
\end{align*}
$$

Si ahora le agregamos la referencia tenemos:

$$\begin{align*}
 \dot{\mathbf x}_c &= \mathbf A_r \mathbf x_c + \mathbf B_r y(t) + \mathbf M_r r(t)\\
u(t) &= \mathbf C_r \mathbf x_c  + \mathbf D_r y(t) + N_r r(t)
\end{align*}$$

Por lo tanto la ecuación de la entrada resulta:

$$u(t) =-\mathbf K _b\mathbf x_c(t) +(-K_a - \mathbf K _b \mathbf L) y(t) + N_rr(t) $$

De forma análoga al caso anterior, el error de estimación $\mathbf x_b(t) - \hat {\mathbf x}_b(t)$ no debe depender de $r(t)$. Como el término $N_r r(t)$ de $u(t)$ entra a la planta a través de $\mathbf B_b$ y $B_a$, el estimador debe recibir ese mismo término, lo que lleva a:

$$\mathbf M_r = (\mathbf B_b - \mathbf L B_a)N_r$$

El valor de $N_r$ para que el sistema tenga error cero en estado estacionario (de forma no robusta) debe ser $N_r=\bar N$.

