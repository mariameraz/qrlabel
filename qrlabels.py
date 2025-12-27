# qrlabels.py

################## 
# Load libraries #
##################

import streamlit as st
import qrcode
import os
import io
import urllib.error
import urllib.request
from PIL import Image, ImageDraw, ImageFont

################################
# Font management with caching #
################################

@st.cache_resource
def download_unicode_fonts():
    """Download fonts with Unicode."""
    fonts = {}
    
    # Main font: Noto Sans (Latin, Cyrillic, Greek)
    noto_path = "/tmp/NotoSans-Regular.ttf"
    if not os.path.exists(noto_path):
        try:
            print("Downloading main font...")
            url = "https://github.com/notofonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
            urllib.request.urlretrieve(url, noto_path)
            if os.path.getsize(noto_path) > 0:
                fonts['main'] = noto_path
            else:
                raise ValueError("! Downloaded font file is empty")
        except urllib.error.URLError as e:
            print(f"> Network error downloading font: {e}")
        except (OSError, IOError) as e:
            print(f"> File system error handling font: {e}")
        except Exception as e:
            print(f"> Unexpected error downloading font: {e}")
    else:
        fonts['main'] = noto_path

    return fonts

###################################
# Select font with priority order #
###################################

def priority_fonts(text, size):
    # Try to get downloaded fonts with Unicode support
    fonts = download_unicode_fonts()

    # Try fonts in order of priority
    font_priority = []
    
    if 'main' in fonts:
        font_priority.append(fonts['main'])
    
    # Add system fonts as fallback
    font_priority.extend([
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "C:\\Windows\\Fonts\\seguisym.ttf",
        "C:\\Windows\\Fonts\\msgothic.ttc",
    ])
    
    # Try each font
    failed_fonts = []
    for font_path in font_priority:
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except OSError as e:
                failed_fonts.append(f"{font_path}: {str(e)}")
                continue
    
    # Log which fonts failed for debugging
    if failed_fonts:
        print("! Failed to load the following fonts:")
        for fail in failed_fonts:
            print(f"- {fail}")
    
    # Last resort
    print("> Using default font as fallback")
    return ImageFont.load_default()
########################################
# Generate label with text and QR code #
########################################

def generate_label(label_text, qr_text, width=600, height=200, margin=5, font_size=50, 
                   qr_size=185, draw_border=True, border_width=4, border_margin=5, 
                   correction_level='H', qr_color=(0,0,0,255), text_color=(0,0,0,255), 
                   label_color=(255,255,255,255), border_color=(0,0,0,255)):
    '''
    Generate a label with text and QR code
    '''
    
    # Create label rectangle with the specified background color
    label = Image.new('RGBA', (width, height), color=label_color)
    draw = ImageDraw.Draw(label)

    # Draw border if enabled
    if draw_border:
        draw.rectangle(
            [(border_margin, border_margin), (width - border_margin - 1, height - border_margin - 1)],
            outline=border_color,
            width=border_width
        )

    # Generate QR code
    # Map correction levels to qrcode constants
    error_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    if correction_level not in error_map:
        correction_level = 'H'  # Default to high if invalid

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_map.get(correction_level, qrcode.constants.ERROR_CORRECT_H),
        box_size=10,
        border=4
    )

    # Encode as UTF-8
    try: 
        qr_bytes = qr_text.encode('utf-8')
        qr.add_data(qr_bytes, optimize=0)
    except Exception:
        qr.add_data(qr_text)

    # Create the QR code
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=qr_color[:3], back_color="white")  # Use RGB only for QR
    qr_img = qr_img.resize((qr_size, qr_size))

    # Position QR code on the right
    qr_x = width - qr_size - margin
    qr_y = (height - qr_size) // 2
    label.paste(qr_img, (qr_x, qr_y))

    # Calculate text position
    text_area_width = qr_x - margin * 2
    text_area_height = height - margin * 2

    # Adjust font size to fit text area if necessary
    current_size = font_size
    lines = []

    for attempt in range(5):
        font = priority_fonts(label_text, current_size)

        # Split text into lines that fit within text area width
        words = label_text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            try: 
                bbox = draw.textbbox((0,0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            except Exception:
                text_width = text_area_width + 1  # Force overflow

            if text_width <= text_area_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Calculate total text height
        try:
            bbox = draw.textbbox((0,0), 'Ay', font=font)
            line_height = bbox[3] - bbox[1]
        except Exception:
            line_height = current_size  # Approximate

        line_spacing = line_height * 0.1  # 10% of line height
        total_text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing

        # Check if text fits within text area height
        text_overflow = False
        for line in lines:
            try:
                bbox_line = draw.textbbox((0,0), line, font=font)
                line_width = bbox_line[2] - bbox_line[0]
                if line_width > text_area_width:
                    text_overflow = True
                    break
            except Exception:
                text_overflow = True
                break
        
        if not text_overflow and total_text_height <= text_area_height:
            break  # Text fits, exit loop
        
        current_size = int(current_size * 0.9)  # Reduce font size and try again
        if current_size < 10:
            break  # Prevent font size from getting too small

    # Draw text
    try:
        bbox = draw.textbbox((0,0), 'Ay', font=font)
        line_height = bbox[3] - bbox[1]
    except Exception:
        line_height = current_size  # Approximate

    line_spacing = line_height * 0.1  # 10% of line height
    total_text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing

    y_start = (height - total_text_height) // 2

    for i, line in enumerate(lines):
        y = y_start + i * (line_height + line_spacing)

        try:
            draw.text((margin * 2, y), line, font=font, fill=text_color)
        except Exception as e:
            x_offset = margin * 2
            
            for char in line:
                try: 
                    draw.text((x_offset, y), char, font=font, fill=text_color)
                    bbox = draw.textbbox((x_offset, y), char, font=font)
                    x_offset += bbox[2] - bbox[0]
                except Exception as e:
                    x_offset += current_size // 2

    return label

#################################
## Detect separator in csv/tsv ##
#################################

def detect_separator(line):
    """Detect separator used in CSV line."""
    counts = {',': line.count(','), '\t': line.count('\t')}
    return max(counts, key=counts.get)

###########################
## Read input file data ##
###########################

def file_reader(file):
    data = []

    try:
        raw_bytes = file.read()
        
        # Multiple encodings
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1', 'windows-1252', 'shift-jis', 'gb2312', 'big5', 'euc-kr']

        content = None
        encoding_used = None

        for encoding in encodings:
            try:
                content = raw_bytes.decode(encoding)
                encoding_used = encoding
                break
            except (UnicodeDecodeError, AttributeError):
                continue

        if content is None:
            content = raw_bytes.decode('utf-8', errors='replace')
            encoding_used = 'utf-8 (with errors)'
            st.warning("> File encoding issue. Save your file as UTF-8.")
        elif encoding_used not in ['utf-8', 'utf-8-sig']:
            st.info(f"> File encoding detected: {encoding_used}")

        lines = content.splitlines()

        # Detect csv/tsv formats
        if ',' in lines[0] or '\t' in lines[0]:
            separator = detect_separator(lines[0])

            first_col = lines[0].split(separator)[0].strip().lower()
            # Determine if there's a header
            start = 1 if first_col in ['id', 'ids', 'code', 'name', 'product', 'text', 'label', 'etiqueta'] else 0

            for line in lines[start:]:
                if line.strip():
                    parts = [p.strip() for p in line.split(separator)]

                    # Filter out empty lines
                    parts = [p for p in parts if p]

                    if len(parts) == 0:
                        continue

                    if len(parts) == 2: 
                        visible = parts[0]
                        qr_text = parts[1]

                        if "|" in qr_text:
                            qr_text = qr_text.replace("|", "\n")
                        if "\\n" in qr_text:
                            qr_text = qr_text.replace("\\n", "\n")

                        data.append((visible, qr_text))
                    elif len(parts) >= 3:
                        visible = parts[0]
                        qr_lines = parts[1:]
                        qr_text = '\n'.join(qr_lines)
                        data.append((visible, qr_text))
                    elif len(parts) == 1:
                        text = parts[0]
                        data.append((text, text))
        else: 
            for line in lines:
                line = line.strip()
                if line:
                    data.append((line, line))

    except Exception as e:
        st.error(f"> Error reading file: {str(e)}")
        return []
    
    return data

###########################
# Group labels into grids #
###########################

def group_labels(labels, rows=3, cols=2, spacing=20):
    grids = []

    if not labels:
        return grids
    
    label_width = labels[0].width
    label_height = labels[0].height

    grid_width = cols * label_width + (cols + 1) * spacing
    grid_height = rows * label_height + (rows + 1) * spacing

    labels_per_grid = rows * cols
    num_grids = (len(labels) + labels_per_grid - 1) // labels_per_grid

    for i in range(num_grids):
        grid = Image.new('RGBA', (grid_width, grid_height), color=(255, 255, 255, 255))

        start = i * labels_per_grid
        end = min((i + 1) * labels_per_grid, len(labels))
        current_labels = labels[start:end]
        
        for idx, label in enumerate(current_labels):
            row = idx // cols
            col = idx % cols
            
            x = spacing + col * (label_width + spacing)
            y = spacing + row * (label_height + spacing)
            
            grid.paste(label, (x, y))
        
        grids.append(grid)
    
    return grids

###########################
## Create PDF from grids ##
###########################

def create_pdf(grids, dpi=150, qual=95):
    if not grids:
        return None
    
    pdf_bytes = io.BytesIO()
    grids[0].save(pdf_bytes, format='PDF', save_all=True, append_images=grids[1:],
                  resolution=dpi, quality=qual)
    pdf_bytes.seek(0)
    
    return pdf_bytes


def get_current_params():
    """Get current parameters as a tuple for comparison"""
    return (
        st.session_state.get('label_width'),
        st.session_state.get('label_height'),
        st.session_state.get('font_size'),
        st.session_state.get('qr_size'),
        st.session_state.get('margin'),
        st.session_state.get('correction_level'),
        st.session_state.get('draw_border'),
        st.session_state.get('border_width'),
        st.session_state.get('border_margin'),
        st.session_state.get('qr_color_rgba'),
        st.session_state.get('label_text_color_rgba'),
        st.session_state.get('label_color_rgba'),
        st.session_state.get('grid_rows'),
        st.session_state.get('grid_cols'),
        st.session_state.get('grid_spacing'),
    )


########################
## Streamlit web app ##
########################


st.set_page_config(page_title="QRLabels", page_icon="✨", layout="wide")

st.title("QRLabels   ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧ ")

github_badge_text = """
<div style="position: fixed; top: 70px; right: 20px; z-index: 999;">
    <a href="https://github.com/mariameraz/qrlabel" target="_blank" style="text-decoration: none;">
        <div style="background: #24292e; color: white; padding: 8px 16px; border-radius: 20px; 
                    display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;">
            <svg width="20" height="20" fill="white" viewBox="0 0 16 16">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            <span style="font-weight: 600; font-size: 14px;">GitHub</span>
        </div>
    </a>
</div>
"""
st.markdown(github_badge_text, unsafe_allow_html=True)

with st.expander("**✨👇 Generate Custom Labels with QR Codes**", expanded=True):
    st.info("""
    Create personalized labels for your samples with custom text and unique QR codes by uploading a CSV, TXT, or TSV file.

    File format:

    ✅ One column → the same text is used for both the label and the QR code.  
    ✅ Two columns → the first column is the label text, and the second is the QR data.  
    ✅ More than two columns → the first column is used as the label, and the remaining columns are combined (separated by line breaks) for the QR code.

    You can find example files in our GitHub repository.

    📄 The result is a printable PDF containing all your generated labels.

    ✨ Notes:

    • Supports emojis (🎉❤️) and special characters such as Japanese (お茶), Chinese (中文), Korean (한국), Russian (Москва), math symbols (∫π∑), and accented letters.  
    • Due to font limitations, only ASCII characters are fully supported in label text.  
    • If special characters are included, make sure your input file is UTF-8 encoded to display them correctly:

    Google Sheets: File → Download → CSV (recommended)  
    Excel: Save As → CSV UTF-8 (comma-delimited)

    """)

st.markdown("---")
with st.sidebar:
    # Buy me a tree button (mantener como está)
    st.markdown("""
    <style>
    .tree-button {
        background: rgba(206, 156, 156, 0.8);
        color: #000000 !important;
        padding: 5px 5px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: block;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        border: 1px solid rgba(148, 225, 255, 0);
    }
    .tree-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        background: rgba(240, 180, 144, 0.7);
        color: white !important;
        text-decoration: none;
        border-color: rgba(240, 180, 144, 0);
    }
    .tree-button:visited {
        color: #000000 !important;
    }
    .tree-emoji {
        font-size: 24px;
        margin-right: 8px;
    }
    </style>
    <a href="https://beacons.ai/mariameraz" target="_blank" class="tree-button">
        <span class="tree-emoji">🌳</span>Buy Us a Tree
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección Label format - COLAPSABLE
    with st.expander("⟡ Label format ˎˊ˗", expanded=True):
        size1, size2 = st.columns(2)
        with size1:
            label_width = st.number_input("Width (px)", min_value=100, max_value=2000, value=600, step=10)
        with size2:
            label_height = st.number_input("Height (px)", min_value=50, max_value=1000, value=200, step=10)
        
        font, qrsize = st.columns(2)
        with font:
            font_size = st.number_input("Font Size", min_value=10, max_value=200, value=50, step=1)
        with qrsize:
            qr_size = st.number_input("QR Code Size (px)", min_value=50, max_value=500, value=180, step=5)
        
        mar, corr = st.columns(2)
        with mar:
            margin = st.number_input("Margin (px)", min_value=0, max_value=100, value=15, step=1)
        with corr:
            correction_level = st.selectbox("QR Error Level", options=['L (7%)', 'M (15%)', 'Q (25%)', 'H (30%)'], index=3,
                                           help="Error correction level determines how much damage the QR can sustain. Higher levels make the QR code more resistant to damage but store less data.")
        
        # Border
        draw_border = st.checkbox("Draw Border", value=True)
        if draw_border:
            bw, bm = st.columns(2)
            with bw:
                border_width = st.number_input("Border Width (px)", min_value=1, max_value=20, value=4, step=1)
            with bm:
                border_margin = st.number_input("Border Margin (px)", min_value=0, max_value=50, value=5, step=1)
        else:
            border_width = 0
            border_margin = 0
    
    # Sección Colors - COLAPSABLE
    with st.expander("⟡ Colors ˎˊ˗", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            qr_color = st.color_picker("QR Code", value="#000000")
            qr_opacity = int(st.slider("QR Opacity", min_value=0, max_value=100, value=100) * 2.55)
        with col2:
            label_text_color = st.color_picker("Label Text", value="#000000")
            text_opacity = int(st.slider("Text Opacity", min_value=0, max_value=100, value=100) * 2.55)
        with col3:
            label_color = st.color_picker("Background", value="#FFFFFF")
            bg_opacity = int(st.slider("BG Opacity", min_value=0, max_value=100, value=100) * 2.55)
    
    # Convert hex colors to RGBA
    def hex_to_rgba(hex_color, opacity):
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        return rgb + (opacity,)
    
    qr_color_rgba = hex_to_rgba(qr_color, qr_opacity)
    label_text_color_rgba = hex_to_rgba(label_text_color, text_opacity)
    label_color_rgba = hex_to_rgba(label_color, bg_opacity)
    border_color_rgba = (0, 0, 0, 255)
    
    # Sección Grid - COLAPSABLE
    with st.expander("⟡ Grid ˎˊ˗", expanded=True):
        grid_spacing = st.number_input("Spacing between labels (px)", min_value=0, max_value=100, value=20, step=1)
        
        page_width_px = int(8.5 * 150)
        page_height_px = int(11 * 150)
        
        max_cols = max(1, (page_width_px - grid_spacing) // (label_width + grid_spacing))
        max_rows = max(1, (page_height_px - grid_spacing) // (label_height + grid_spacing))
        labels_per_page = max_cols * max_rows
        
        grow, gcol = st.columns(2)
        with grow:
            grid_rows = st.number_input("Labels per row", min_value=1, max_value=20, 
                                        value=min(3, max_rows), step=1)
        with gcol:
            grid_cols = st.number_input("Labels per column", min_value=1, max_value=10, 
                                        value=min(2, max_cols), step=1)
            
# Store current params in session state for comparison
current_params = (label_width, label_height, font_size, qr_size, margin, correction_level,
                 draw_border, border_width, border_margin, qr_color_rgba, label_text_color_rgba,
                 label_color_rgba, grid_rows, grid_cols, grid_spacing)

# Main area
col_upload, col_preview = st.columns([1, 1])

with col_upload:
    st.subheader("📤 Upload your file")
    uploaded_file = st.file_uploader("Upload a file with your labels:", type=['csv', 'tsv', 'txt'], key="file_uploader")
    
    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        data_list = file_reader(uploaded_file)

        if data_list:
            #st.info(f"ℹ️ {len(data_list)} labels found in the file.")

            with st.expander("Preview file data"):
                for idx, (vis, qr) in enumerate(data_list[:10], 1):
                    qr_prev = qr.replace('\n', ' | ')[:50]
                    st.text(f"{idx}. Label: '{vis}' | QR: {qr_prev}")
                if len(data_list) > 10:
                    st.text(f"... +{len(data_list)-10} more")

            # Check if parameters changed
            params_changed = False
            file_changed = False
            
            # Create unique file identifier
            current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            
            # Check if it's a new file
            if 'last_file_id' not in st.session_state or st.session_state['last_file_id'] != current_file_id:
                file_changed = True
                st.session_state['last_file_id'] = current_file_id
            
            # Check if parameters changed
            if 'last_params' in st.session_state:
                if st.session_state['last_params'] != current_params and 'labels' in st.session_state:
                    params_changed = True

            # Auto-regenerate if file is new, parameters changed, or no labels exist yet
            if file_changed or params_changed or 'labels' not in st.session_state:
                #if params_changed and auto_update:
                #    st.info("🔄 Parameters changed - auto-updating labels...")
                
                with st.spinner("Generating labels..."):
                    labels = []
                    progress = st.progress(0)
                    
                    for idx, (vis, qr) in enumerate(data_list):
                        label = generate_label(
                            label_text=vis,
                            qr_text=qr,
                            width=label_width,
                            height=label_height,
                            margin=margin,
                            font_size=font_size,
                            qr_size=qr_size,
                            draw_border=draw_border,
                            border_width=border_width,
                            border_margin=border_margin,
                            correction_level=correction_level[0],  # Take only the letter (L, M, Q, H)
                            qr_color=qr_color_rgba,
                            text_color=label_text_color_rgba,
                            label_color=label_color_rgba,
                            border_color=border_color_rgba
                        )
                        labels.append(label)
                        progress.progress((idx + 1) / len(data_list))
                        grids = group_labels(labels, grid_rows, grid_cols, grid_spacing)
                    
                    progress.empty()  # Clear progress bar
                    #st.success(f"✅ {len(grids)} grids created")
                    st.info(f"✅ {len(labels)} labels & {len(grids)} grids generated")
                    

                    
                    st.session_state['labels'] = labels
                    st.session_state['grids'] = grids
                    st.session_state['data'] = data_list
                    st.session_state['last_params'] = current_params
                    
                    # Rerun to show updated preview immediately
                    st.rerun()

with col_preview:
    st.subheader("🪄 Preview")

    if 'labels' in st.session_state and 'grids' in st.session_state:
        tabs = st.tabs(["Labels", "Grids", "Download"])

        with tabs[0]:  # Labels tab
            st.info(f"★ Showing first 3 of {len(st.session_state['labels'])} labels")
            for idx in range(min(3, len(st.session_state['labels']))):
                st.image(st.session_state['labels'][idx])
        
        with tabs[1]:  # Grids tab
            if st.session_state.get('grids'):
                st.info(f"★ Showing first grid of {len(st.session_state['grids'])} total pages")
                st.image(st.session_state['grids'][0], caption="Grid 1 (Page 1)")
            else:
                st.info("No grids available")
        
        with tabs[2]:  # Download tab
            # Download Section
            pdf_name = st.text_input("PDF file name", value="labels", 
                                   help="Enter the name for your PDF file (without .pdf extension)")
            
            # PDF Quality Settings
            pdf1, pdf2 = st.columns(2)
            with pdf1:
                qual = st.slider("Image Quality", min_value=10, max_value=100, value=95, step=5,
                                help="Higher quality results in better images but larger file sizes.")
            with pdf2:
                dpi = st.slider("DPI", min_value=70, max_value=600, value=150, step=10,
                               help="Higher DPI (Dots Per Inch) results in better print quality but larger file sizes.")
            
            st.markdown("---")

            # Generar PDF primero (sin mostrar botón de descarga separado)
            with st.spinner("Preparing PDF..."):
                pdf_bytes = create_pdf(st.session_state['grids'], dpi=dpi, qual=qual)
            
            # Botón único de descarga
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"{pdf_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            
            # Mensaje informativo
            st.info(f"""
            Your PDF will be saved to your browser's default ***download*** folder (❀❛ ֊ ❛„)♡
            """)

# Footer with links and Created by
st.markdown("---")
footer_html = """
<div style='text-align:center;color:#888;padding:20px;'>
    <div style='margin-bottom:20px;'>
        <a href='https://github.com/mariameraz/qrlabel' target='_blank' style='color:#888;text-decoration:none;margin:0 30px;'>
            <img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' width='40' style='vertical-align:middle;margin-right:5px;'> 
            GitHub
        </a>
        •
        <a href='https://www.linkedin.com/in/alemeraz/' target='_blank' style='color:#888;text-decoration:none;margin:0 30px;'>
            <img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg' width='40' style='vertical-align:middle;margin-right:5px;'> 
            LinkedIn
        </a>
        •
        <a href='mailto:ale.meraz@outlook.com' style='color:#888;text-decoration:none;margin:0 30px;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg' width='30' style='vertical-align:middle;margin-right:5px;'> 
            Contact
        </a>
        •
        <a href='https://github.com/mariameraz/qrlabel/issues/new' target='_blank' style='color:#888;text-decoration:none;margin:0 30px;'>
            <span style='font-size:30px;vertical-align:middle;margin-right:5px;'>🐞</span> Report Bug
        </a>
        •
        <a href='https://github.com/mariameraz/qrlabel/discussions' target='_blank' style='color:#888;text-decoration:none;margin:0 30px;'>
            <span style='font-size:30px;vertical-align:middle;margin-right:5px;'>💬</span> Ask Question
        </a>
        </a>
    </div>
    <div style='margin-top:30px;padding-top:20px;border-top:1px solid #ddd;'>
        <p style='font-size:14px;color:#666;margin:0;'>
            Created by <a href='https://www.linkedin.com/in/alemeraz/' target='_blank' style='color:#666;text-decoration:none;font-weight:bold;'>Alejandra Meraz</a> </p>
        <p style='font-size:12px;color:#999;margin:5px 0 0 0;'>
            © 2025 QRLabels • Open Source
        </p>
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)