import streamlit as st
import fitz  # PyMuPDF
import io
import os

# --- ASSETS ---
HEADER_PATH = "header.jpg"
FOOTER_PATH = "footer.jpg"
CENTER_PATH = "logo.png"

def get_aspect_ratio(path):
    try:
        pix = fitz.Pixmap(path)
        ar = pix.width / pix.height
        pix = None
        return ar
    except:
        temp_doc = fitz.open(path)
        ar = temp_doc[0].rect.width / temp_doc[0].rect.height
        temp_doc.close()
        return ar

def process_document(uploaded_file, h_height, f_height, c_height):
    # SAFETY CHECK: PyMuPDF can only read PDF bytes
    if uploaded_file.name.lower().endswith('.docx'):
        st.error("⚠️ Streamlit Cloud cannot convert Word to PDF directly yet. Please save your file as a PDF and upload it again.")
        return None

    # Open PDF from memory
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    h_ar = get_aspect_ratio(HEADER_PATH)
    f_ar = get_aspect_ratio(FOOTER_PATH)
    c_ar = get_aspect_ratio(CENTER_PATH)
    margin = 20

    for page in doc:
        page_rect = page.rect
        # Center Image
        c_w = c_height * c_ar
        c_x0 = (page_rect.width - c_w) / 2
        c_y0 = (page_rect.height - c_height) / 2
        page.insert_image(fitz.Rect(c_x0, c_y0, c_x0 + c_w, c_y0 + c_height), filename=CENTER_PATH)

        # Header
        h_w = h_height * h_ar
        h_x0 = (page_rect.width - h_w) / 2
        page.insert_image(fitz.Rect(h_x0, 0, h_x0 + h_w, h_height), filename=HEADER_PATH)

        # Footer
        f_w = f_height * f_ar
        f_x0 = (page_rect.width - f_w) / 2
        page.insert_image(fitz.Rect(f_x0, page_rect.height - f_height, f_x0 + f_w, page_rect.height), filename=FOOTER_PATH)

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()

# --- UI ---
st.set_page_config(page_title="Document Brander", layout="wide")
st.title("📂 Universal Document Brander")

with st.sidebar:
    st.header("🔢 Image Heights (px)")
    h_val = st.number_input("Header", min_value=10, value=80)
    f_val = st.number_input("Footer", min_value=10, value=50)
    c_val = st.number_input("Logo", min_value=50, value=500)

uploaded_file = st.file_uploader("Upload PDF", type=["pdf", "docx"])

if uploaded_file and st.button("✨ Apply Branding"):
    result = process_document(uploaded_file, h_val, f_val, c_val)
    if result:
        st.success("Branding complete!")
        st.download_button("📥 Download PDF", data=result, file_name="branded_document.pdf")