# Angry Birds Demo

Este es un **proyecto académico** que recrea una versión simplificada del clásico juego **Angry Birds** usando **Python**, **Arcade** y **Pymunk**.
El objetivo es lanzar pájaros con un tirachinas para derribar estructuras y eliminar a los cerdos de cada nivel.

## Características principales

* **Gráficos 2D** usando la librería Arcade.
* **Física realista** usando Pymunk.
* **Sonidos y música** para mejorar la experiencia de juego.
* **Seis niveles** jugables con diferentes estructuras y desafíos.
* **Tres pájaros** diferentes con habilidades únicas:

  * **Red Bird** → Pájaro estándar.
  * **Blue Bird** → Se divide en tres al presionar `ESPACIO`.
  * **Yellow Bird** → Aumenta su velocidad con `ESPACIO`.

---

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

* **Python 3.10+** (https://www.python.org/downloads/)
* **uv** para tener un entorno virtual.

## Instalación y ejecución

Sigue estos pasos:

### 1. Clonar el repositorio

Abre una terminal o CMD y ejecuta:

```bash
git clone https://github.com/joackagui/info_1er_parcial_A.git
```

### 2. Entrar en la carpeta del proyecto

```bash
cd info_1er_parcial_A
```

### 3. Crear un entorno virtual (opcional pero recomendado)

```bash
uv venv --seed -p 3.12

.venv\Scripts\activate
```

### 4. Instalar las dependencias

```bash
pip install arcade pymunk
```

### 5. Ejecutar el juego

Se puede presionar en la flecha de play de arriba a la derecha o ejecutar el sigueinte código:

```bash
python main.py
```

---

## Controles del juego

| Acción                       | Tecla / Botón                                |
| ---------------------------- | -------------------------------------------- |
| Apuntar y lanzar             | Arrastrar con **click izquierdo**            |
| Activar habilidad especial   | `ESPACIO`                                    |
| Cambiar de nivel             | Hacer click desde el **selector de niveles** |
| Volver a la pantalla inicial | `ESC` en el juego                            |
| Cerrar el juego              | `ESC` en el menú inicial                     |

## **Autor**

**Nombre:** Joaquín Aguilera

**Año:** 2025
