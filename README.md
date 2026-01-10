# QRLabel App (Streamlit)
![License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![Open in Streamlit](https://img.shields.io/badge/Open%20App-Streamlit-green)](https://qrlabel.streamlit.app)

Create personalized labels with custom text and unique QR codes by uploading a CSV, TXT, or TSV file. The app processes your file and generates a printable PDF with all your labels.

- This document is also available in Spanish: [Spanish README](README_ES.md)

<br>

## 🌐 Live Demo

Try our free app online:

👉 **[https://qrlabel.streamlit.app](https://qrlabel.streamlit.app)**


> **Note:** After a period of inactivity, Streamlit may put the app to sleep. If this happens, simply click **“Wake up app”** and wait a few seconds for it to restart.


<br>


## ⋆˙⟡ File Format

Upload one of the supported formats: **CSV, TXT, or TSV**.

### One column

The same value is used for both the **label text** and the **QR code content**.

### Two columns

* **Column 1:** Label text
* **Column 2:** QR code content

### More than two columns

* **Column 1:** Label text
* **Columns 2+ :** Combined together (separated by line breaks) and encoded into the QR code.

👉 **Example input files and sample generated labels can be found in the `examples/` [folder](examples/).**

<br>

## ⋆˙⟡ Output

The app generates a **print-ready PDF** containing all generated labels.

<br>

## ⋆˙⟡ Features

* Supports emojis (🎉❤️)
* Handles multilingual characters, including:

  * Japanese (お茶)
  * Chinese (中文)
  * Korean (한국)
  * Russian (Москва)
  * Mathematical symbols (∫π∑)
  * Accented characters

> Due to font limitations, only ASCII characters are fully guaranteed for label text rendering.
> Non-ASCII characters work best inside the QR code content.

<br>

## ⋆˙⟡ Encoding Notes

To avoid character display issues, make sure your file is encoded as **UTF-8**:

* **Google Sheets:** `File → Download → CSV` (recommended)
* **Excel:** `Save As → CSV UTF-8 (comma-delimited)`

<br>

## ✧٩(˃̵ᴗ˂̵๑)و✧ Run Locally

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
streamlit run qrlabels.py
```

Then open the URL shown in your terminal (usually `http://localhost:8501`).

<br>

## ☕🌱 Support

If you find this project useful, instead of buying us a coffee, consider [planting a tree](https://beacons.ai/mariameraz) to support global reforestation.  

Donations are processed by independent nonprofit organizations and **are not affiliated with this project or its authors**. This suggestion reflects our interest in supporting environmental conservation and long-term sustainability.

<br>

## ⋆˙⟡ License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

You may use, modify, and distribute this software. If you distribute it externally or provide access to it to third parties, including through a networked service, the source code of any modified version must be made available under the same license, in order to support open science and broad access to research.
