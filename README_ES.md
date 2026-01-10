# QRLabel App (Streamlit)

![License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![Open in Streamlit](https://img.shields.io/badge/Open%20App-Streamlit-green)](https://qrlabel.streamlit.app)

Available in: [![English](https://img.shields.io/badge/Language-English-pink)](README.md)

Crea etiquetas personalizadas con códigos QR únicos cargando un archivo CSV, TXT o TSV.
La aplicación procesa tu archivo y genera un PDF imprimible con todas tus etiquetas.

<br>

## 🌐 Demo en línea

Prueba la app gratis:

👉 **[https://qrlabel.streamlit.app](https://qrlabel.streamlit.app)**

> Nota: Despues de un periodo de inactividad, Streamlit puede poner la app a 'dormir'. Si esto sucede, simplemente da click en “Wake up app” y espera unos segundos para restaurar la página.

<br>

## ⋆˙⟡ Formato de archivo

Sube uno de los formatos compatibles: **CSV, TXT o TSV**.

### Una columna

El mismo valor se usa tanto para el **texto de la etiqueta** como para el **contenido del QR**.

### Dos columnas

* **Columna 1:** Texto de la etiqueta
* **Columna 2:** Contenido del código QR

### Más de dos columnas

* **Columna 1:** Texto de la etiqueta
* **Columnas 2+:** Se combinan (separadas por saltos de línea) y se codifican dentro del QR.

👉 **Algunos archivos de ejemplo y sus respectivas etiquetas generadas se encuentran en la carpeta `examples/`.**

<br>

## ⋆˙⟡ Salida

La aplicación genera un **PDF listo para imprimir** con todas las etiquetas.

<br>

## ⋆˙⟡ Características

* Soporta emojis (🎉❤️)
* Maneja caracteres multilingües, incluyendo:

  * Japonés (お茶)
  * Chino (中文)
  * Coreano (한국)
  * Ruso (Москва)
  * Símbolos matemáticos (∫π∑)
  * Caracteres acentuados

> Debido a limitaciones de fuente, solo los caracteres ASCII están totalmente garantizados para el texto de la etiqueta.
> Los caracteres no ASCII funcionan mejor dentro del contenido del código QR.

<br>

## ⋆˙⟡ Notas sobre la codificación

Para evitar problemas de visualización, asegúrate de que tu archivo esté codificado en **UTF-8**:

* **Google Sheets:** `Archivo → Descargar → CSV` (recomendado)
* **Excel:** `Guardar como → CSV UTF-8 (delimitado por comas)`

<br>

## ✧٩(˃̵ᴗ˂̵๑)و✧ Ejecutar localmente

Clona el repositorio e instala las dependencias:

```bash
pip install -r requirements.txt
streamlit run qrlabels.py
```

Luego abre la URL que aparece en la terminal (generalmente `http://localhost:8501`).

<br>

## ☕🌱 Apoyo

Si este proyecto te resulta útil, en lugar de invitarnos un café, considera **[plantar un árbol](https://beacons.ai/mariameraz)** para apoyar a la reforestación global.

Las donaciones son procesadas por organizaciones sin fines de lucro independientes, las cuales no están afiliadas a este proyecto ni a sus autores. Esta sugerencia surge de nuestro interés en apoyar la conservación ambiental y su sostenibilidad a largo plazo.

<br>

## ⋆˙⟡ Licencia

Este proyecto está protegido bajo la **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Puedes usar, modificar y distribuir este software. Si se comparte externamente o se pone a disposición de terceros, incluso mediante un servicio en red, el código fuente de cualquier versión modificada debe estar disponible bajo la misma licencia, con el fin de apoyar la ciencia abierta y el acceso amplio a la investigación.

Consulta el archivo `LICENSE` para más detalles.

