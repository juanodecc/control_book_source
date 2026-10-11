---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Diseño de controladores

Hasta aquí el curso se ocupó del **análisis**: dado un sistema, determinar cómo se comporta (estabilidad, respuesta transitoria, error en régimen permanente). Este capítulo plantea el problema inverso, el de **diseño** (síntesis): dados una planta y un conjunto de requisitos, encontrar el controlador que logre que el sistema se comporte como se pide.

Conviene tener presente desde el principio que calcular el controlador es **un paso dentro de un proceso más amplio**. Antes hay que entender la planta, modelarla, decidir qué se quiere controlar y con qué sensores y actuadores; después hay que verificar el diseño, simularlo, implementarlo y validarlo sobre el sistema real. Un controlador perfectamente calculado sobre un modelo equivocado, o sobre una planta mal concebida, no sirve de nada.

+++

## El problema de control

El objetivo de un sistema de control es lograr que la salida $y$ se comporte de la manera deseada actuando sobre la entrada $u$ de la planta. Según qué se busque, el problema recibe dos nombres:

- **Problema de regulación:** manipular $u$ para contrarrestar el efecto de una perturbación $d$ y mantener la salida en su valor deseado.
- **Problema de seguimiento (servo):** manipular $u$ para que la salida siga una referencia $r$ que puede cambiar.

En ambos casos se quiere que el error $e = r - y$ sea pequeño. El algoritmo que calcula $u$ a partir de la información disponible es el **controlador** (o **compensador**), que en estos apuntes se denota $D(s)$ o $C(s)$ que para simplificar la notación podemos usar simplemente $D$ o $C$ (en gran parte de la bibliografía de referencia se lo llama $K(s)$).

Para diseñarlo hace falta información *a priori* sobre las referencias y perturbaciones esperables y sobre los modelos de la planta, $G$, y de la perturbación, $G_d$ (estructura de modelo propuesta en el capítulo de modelado). Con modelos lineales:

$$y = G\,u + G_d\,d$$

Con realimentación negativa unitaria, $u = D\,e$, y llamando $L = GD$ a la ganancia de lazo, resulta

$$y=\underbrace{\frac{L}{1+L}}_{T}\,r+\underbrace{\frac{G_d}{1+L}}_{S\,G_d}\,d
\qquad\Longrightarrow\qquad
e = S\,r - S\,G_d\,d,\qquad S=\frac{1}{1+L}$$

Esta expresión resume buena parte del capítulo: tanto el seguimiento como el rechazo de perturbaciones se reducen a conseguir que la función de sensibilidad $S$ sea pequeña en las frecuencias donde están la referencia y la perturbación, sin perder estabilidad ni margen de robustez. Todo lo que se estudió hasta aquí (lugar de las raíces, diagramas de Bode, ubicación de polos) son herramientas para dar forma a $L$ y, por lo tanto, a $S$ y $T$.

+++

### ¿Qué es compensar?

**Compensar** es modificar la dinámica del lazo agregando polos y ceros mediante $D(s)$, de modo que el sistema cumpla las especificaciones. Lo único que define al compensador es su función de transferencia; la tecnología con que se implementa es secundaria: puede ser una red RC con amplificador operacional, un circuito analógico dedicado o un algoritmo discreto ejecutándose en un microcontrolador. En este último caso hay que sumar los efectos de la discretización, la cuantización y la saturación del actuador, que se mencionan más adelante en el proceso de diseño.

+++

## El proceso de diseño

El diseño de un sistema de control suele desarrollarse como una secuencia de pasos con realimentación entre ellos: cada vez que un paso no se cumple, se vuelve a un paso anterior. La siguiente lista toma como base el procedimiento propuesto por Skogestad y Postlethwaite (*Multivariable Feedback Control*, 2.ª ed., sec. 1.1).

| Fase | Paso | Qué se decide |
|---|---|---|
| **Análisis** | 1 | Estudiar la planta y recoger los objetivos de control iniciales |
| | 2 | Modelar el sistema y simplificar el modelo si hace falta |
| | 3 | Escalar las variables, analizar el modelo y determinar sus propiedades (polos, ceros, retardos, controlabilidad) |
| **Estructura** | 4 | Elegir las variables a controlar (salidas controladas) |
| | 5 | Elegir las mediciones y las variables manipuladas: qué sensores y actuadores usar y dónde ubicarlos |
| | 6 | Elegir la configuración de control (lazo simple, cascada, prealimentación, etc.) |
| | 7 | Elegir el tipo de controlador (P, PI, PID, adelanto/retraso, realimentación de estados con observador) |
| **Diseño** | 8 | Fijar las especificaciones de desempeño a partir de los objetivos generales |
| | 9 | Diseñar el controlador |
| | 10 | Analizar el sistema controlado; si no cumple, modificar las especificaciones o el tipo de controlador |
| **Verificación** | 11 | Simular el sistema controlado (en computadora o en planta piloto) |
| | 12 | Repetir desde el paso 2 si es necesario |
| **Implementación** | 13 | Elegir el hardware y el software e implementar el controlador |
| | 14 | Probar y validar el sistema; sintonizar en línea si es necesario |

 %El diagrama de flujo siguiente muestra el mismo proceso con sus lazos de iteración. El código es texto plano, por lo que puede editarse directamente (ver el archivo `diagrama_proceso_diseno.mmd` o pegarlo en <https://mermaid.live>).%

```{mermaid}
flowchart TD
    subgraph F1["Fase 1 - Análisis"]
        A["1. Estudiar la planta y<br/>los objetivos de control"]
        B["2. Modelar y simplificar"]
        C["3. Escalar variables y analizar el modelo<br/>polos, ceros, retardos, controlabilidad"]
        Q0{"Controlabilidad<br/>suficiente?"}
        R0["0. Modificar la planta o<br/>reubicar sensores y actuadores"]
    end
    subgraph F2["Fase 2 - Estructura de control"]
        D["4. Elegir variables controladas"]
        E["5. Elegir sensores y actuadores"]
        F["6. Elegir configuración de control<br/>lazo simple, cascada, prealimentación"]
        G["7. Elegir tipo de controlador<br/>P, PI, PID, adelanto/retraso,<br/>realimentación de estados + observador"]
    end
    subgraph F3["Fase 3 - Diseño"]
        H["8. Fijar especificaciones<br/>transitorio, permanente,<br/>perturbaciones, robustez"]
        I["9. Diseñar el controlador"]
        J{"10. Se cumplen las<br/>especificaciones<br/>en el análisis?"}
    end
    subgraph F4["Fase 4 - Verificación"]
        K["11. Simular<br/>nominal, con incertidumbre,<br/>saturación y ruido"]
        L{"Simulación<br/>satisfactoria?"}
    end
    subgraph F5["Fase 5 - Implementación"]
        M["13. Elegir hardware y software<br/>e implementar<br/>Discretización, cuantización"]
        N["14. Probar y validar en la planta<br/>sintonizar en linea"]
        O{"Validación<br/>correcta?"}
    end
    Z(["Sistema de control en operación"])

    A --> B --> C --> Q0
    Q0 -->|No| R0 --> A
    Q0 -->|Si| D --> E --> F --> G --> H --> I --> J
    J -->|"No: relajar especificaciones"| H
    J -->|"No: cambiar tipo de controlador"| G
    J -->|Si| K --> L
    L -->|"No: paso 12, repetir desde el modelo"| B
    L -->|Si| M --> N --> O
    O -->|"Ajuste fino"| N
    O -->|"Modelo inadecuado"| B
    O -->|Si| Z
```

Algunas observaciones sobre el proceso:

- En los cursos de control suele ponerse el énfasis en los pasos 9 y 10 (métodos de diseño y análisis), que son los que se estudian en este capítulo. En la práctica, los pasos 4 a 7 (qué controlar, con qué medir y actuar, y con qué estructura) condicionan más el resultado final que el ajuste fino de los parámetros.
- Muchos sistemas reales funcionan bien con una jerarquía de lazos en cascada sintonizados en línea, sin pasar por un diseño formal. Pero eso exige que la estructura de control sea adecuada desde el inicio, y para elegirla conviene tener herramientas sistemáticas.
- El diagrama es iterativo por naturaleza: es normal volver varias veces a las especificaciones o al modelo antes de llegar a un diseño aceptable.

+++

## Controlabilidad: lo que ningún controlador puede arreglar

La **controlabilidad entrada-salida** es la capacidad de una planta de alcanzar un desempeño aceptable mediante control. Depende de la ubicación de los sensores y actuadores, pero fuera de eso **no puede modificarla el ingeniero de control**: es una propiedad de la planta. Dicho de otro modo, un buen controlador no convierte un sistema intrínsecamente difícil de controlar en uno fácil.

Por eso, en algunos casos el proceso de diseño debería incluir un **paso 0**: rediseñar el equipo o el proceso mismo. Ya en 1943 Ziegler y Nichols señalaban que controlador y proceso forman una unidad, y que el mérito o el fracaso del resultado corresponde a ambos por igual.

Un ejemplo clásico en electrónica es el convertidor boost: su función de transferencia de la entrada de control a salida tiene un **cero en el semiplano derecho**, que limita el ancho de banda alcanzable del lazo cerrado sin importar qué compensador se use. Del mismo modo, los retardos (por ejemplo, el de muestreo y cálculo en un controlador digital) o las saturaciones del actuador imponen límites que el diseño del compensador no puede eliminar, solo respetar.

+++

## Incertidumbre y robustez

Si bien el análisis de estos temas quedan fuera del alcance de este curso, no esta de mas reflexionar sobre estos conceptos. Los modelos $G$ y $G_d$ nunca son exactos y además pueden cambiar con el tiempo (envejecimiento de componentes, temperatura, tolerancias, variaciones de carga). Como la planta forma parte de un lazo realimentado, un error en $G$ puede degradar el desempeño o incluso desestabilizar el sistema.

Para tratar este problema se estudia, en lugar de un único modelo, una **familia de modelos** $G_p = G + E$, donde la perturbación $E$ está acotada pero es desconocida. Habitualmente se expresa como $E = w\,\Delta$, con $w(s)$ una función de ponderación y $\|\Delta\|\le 1$ una perturbación normalizada. Con esto se distinguen cuatro propiedades que un diseño puede cumplir o no:

| Propiedad | Sigla | Significado |
|---|---|---|
| Estabilidad nominal | NS | El sistema es estable con el modelo nominal, sin incertidumbre |
| Desempeño nominal | NP | Se cumplen las especificaciones con el modelo nominal |
| Estabilidad robusta | RS | El sistema es estable para toda planta perturbada, hasta la peor incertidumbre considerada |
| Desempeño robusto | RP | Se cumplen las especificaciones para toda planta perturbada, hasta la peor incertidumbre considerada |

Los métodos que se presentan en este capítulo se aplican al modelo nominal: garantizan NS y, si el diseño es bueno, NP. La robustez se verifica después, en las etapas de análisis y simulación, a través de los **márgenes de ganancia y de fase** y de simulaciones con la planta perturbada.

+++

## Contenido

Con este marco, se avanza de lo particular a lo general:

1. **Compensadores de adelanto y de retraso de fase**, diseñados por lugar de las raíces: tipos de compensación, criterios de ubicación de polo y cero, y compensadores PD y PI como casos particulares.
2. **Diseño en el dominio de la frecuencia** con diagramas de Bode, donde aparece el compromiso entre ancho de banda, márgenes de estabilidad y rechazo de ruido.

Finalmente continuaremos con el diseño desde el punto de vista control moderno, con:

3. **Control en el espacio de estados**: realimentación de estados y observadores.
4. **Introducción a control óptimo**: realimentación de estados y observadores.

En cada método conviene identificar a qué paso del proceso corresponde, qué especificaciones permite cumplir y cuáles no (por ejemplo, el lugar de las raíces con un compensador de adelanto trabaja sobre el transitorio pero no corrige el error de estado estacionario).

+++

## Preguntas para reflexionar

1. En el problema de regulación y en el de seguimiento, ¿qué función de transferencia en lazo cerrado determina el error? ¿Qué tienen en común?
2. ¿En qué pasos del proceso de diseño se decide qué sensores y actuadores usar? ¿Por qué esos pasos no pueden resolverse con un compensador?
3. Un diseño cumple NP pero no RS. ¿Es aceptable? ¿Qué puede pasar al implementarlo?
4. Un compensador se calcula en tiempo continuo y se implementa en un microcontrolador. ¿Qué pasos del proceso de diseño permiten detectar los efectos de la discretización antes de armar el prototipo?

+++

## Referencia

S. Skogestad, I. Postlethwaite, *Multivariable Feedback Control: Analysis and Design*, 2.ª ed., Wiley, 2005, cap. 1 (versión de trabajo de 2001).
