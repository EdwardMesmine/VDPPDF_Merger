"""
Streamlit app to:
1. Upload a 2‑page master PDF (Page 1 = front; Page 2 = back template).
2. Upload a multi‑page PDF (N pages).
3. Produce a final PDF of **2 × N pages**: each multi‑page page gets merged on top of master Page 1, and each of these has a back side (master Page 2) with numbering.
4. Ask the starting number and the (x, y) position to place the number on the back side.

Dependencies:
    pip install streamlit PyPDF2 reportlab

Run:
    streamlit run merge_double_sided.py
"""

import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Double‑Sided PDF Merger", layout="centered")
st.title("Double‑Sided PDF Merger with Numbering by Edward(9500017075)")

st.markdown("""
### How it works
- Upload a **2‑page master PDF**: Page 1 is used as the front template; Page 2 is the back template.
- Upload a **multi‑page PDF**.
- Each page from the multi‑PDF is placed on top of master Page 1.
- A back page is generated for each merged front using master Page 2 + numbering.
- You enter the starting number and its (x, y) coordinates.

If multi‑PDF has **100 pages**, output PDF will have **200 pages**.
""")

# Upload inputs
st.subheader("Position Settings for Front Side (overlay multi‑PDF page)")
front_x = st.number_input("Front X position (default center)", value=-1.0, help="Leave -1 for auto-center")
front_y = st.number_input("Front Y position (default center)", value=-1.0, help="Leave -1 for auto-center")

st.subheader("Position Settings for Back Side Numbering")
master_pdf_file = st.file_uploader("Upload 2‑page Master PDF", type=["pdf"])
multi_pdf_file = st.file_uploader("Upload Multi‑Page PDF", type=["pdf"])

start_num = st.number_input("Starting Back‑Side Number", min_value=1, value=1)
x_pos = st.number_input("Number X position", value=50.0)
y_pos = st.number_input("Number Y position", value=50.0)

if st.button("Create Double‑Sided PDF"):
    if not master_pdf_file or not multi_pdf_file:
        st.error("Please upload both master and multi‑page PDFs.")
    else:
        try:
            master_reader = PdfReader(master_pdf_file)
            multi_reader = PdfReader(multi_pdf_file)

            if len(master_reader.pages) < 2:
                st.error("Master PDF must contain at least 2 pages.")
            else:
                writer = PdfWriter()

                master_front = master_reader.pages[0]
                master_back = master_reader.pages[1]

                number = start_num

                for page in multi_reader.pages:
                    # ---- FRONT PAGE ----
                    temp_writer = PdfWriter()
                    temp_writer.add_page(master_front)
                    temp_bytes = BytesIO()
                    temp_writer.write(temp_bytes)
                    temp_bytes.seek(0)
                    temp_reader = PdfReader(temp_bytes)
                    merged_front = temp_reader.pages[0]

                    # Calculate auto-centering if needed
                    mw = float(master_front.mediabox.width)
                    mh = float(master_front.mediabox.height)
                    pw = float(page.mediabox.width)
                    ph = float(page.mediabox.height)

                    fx = front_x if front_x >= 0 else (mw - pw) / 2
                    fy = front_y if front_y >= 0 else (mh - ph) / 2

                    try:
                        merged_front.merge_translated_page(page, fx, fy)
                    except Exception:
                        try:
                            merged_front.merge_page(page)
                        except:
                            pass

                    writer.add_page(merged_front)

                    # ---- BACK PAGE WITH NUMBER ----
                    # Create number as small PDF
                    num_stream = BytesIO()
                    w = float(master_back.mediabox.width)
                    h = float(master_back.mediabox.height)

                    c = canvas.Canvas(num_stream, pagesize=(w, h))
                    c.setFont("Helvetica", 20)
                    c.drawString(x_pos, y_pos, str(number))
                    c.showPage()
                    c.save()
                    num_stream.seek(0)

                    num_reader = PdfReader(num_stream)
                    num_page = num_reader.pages[0]

                    temp_writer = PdfWriter()
                    temp_writer.add_page(master_back)
                    temp_bytes = BytesIO()
                    temp_writer.write(temp_bytes)
                    temp_bytes.seek(0)
                    temp_reader = PdfReader(temp_bytes)
                    merged_back = temp_reader.pages[0]

                    try:
                        merged_back.merge_page(num_page)
                    except:
                        try:
                            merged_back.merge_translated_page(num_page, 0, 0)
                        except:
                            pass

                    writer.add_page(merged_back)

                    number += 1

                # Output PDF
                out_bytes = BytesIO()
                writer.write(out_bytes)
                out_bytes.seek(0)

                st.success("Double‑sided merged PDF created successfully!")
                st.download_button(
                    "Download Final PDF", data=out_bytes,
                    file_name="double_sided_merged.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.exception(e)

st.markdown("---")
st.info("Each page from the multi‑PDF produces a front + numbered back, giving a total of 2× pages.")
