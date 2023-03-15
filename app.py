import streamlit as st

import io
import os

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import mm


st.title("PDF Merge")
st.write("cord: https://github.com/oo96r/pdf_merge")

#file upload
#st.markdown("## file upload")
uploaded_file = []
uploaded_file = st.file_uploader(
    "Upload pdf file",
    type=".pdf",
    accept_multiple_files=True)


#merge setting
st.markdown("### setting")
files = {f.name: f for f in uploaded_file}

help_txt  = "The selected files will be combined in order."
help_txt += "If nothing is selected, all uploaded files will be combined in order of file name."

file_order = st.multiselect("Select the order of file merging",
                            options = files.keys(),
                            help = help_txt,
                            default = None)

if file_order==[]:
    file_order = sorted(files.keys())  


#page No. setting
st.markdown("### setting - page No.")
pageNo_button = st.checkbox("add page No.")
if pageNo_button:
    
    col1, col2 = st.columns(2)
        
    prefix = col1.text_input("prefix", "- ")
    suffix = col1.text_input("suffix", " -")
    col1.write(f"sample:    {prefix}{1}{suffix}")

    fontsize = col2.number_input("font size",value = 10.5)
    font     = col2.selectbox("font", ["HeiseiKakuGo-W5"])
    loc_bottom = col2.number_input("bottom margin",
                                   value = 10,
                                   help = "unit: mm")
    
    pdfmetrics.registerFont(UnicodeCIDFont(font))
    loc_bottom *= mm
    


#mearge pdf
pdf_merged = PyPDF2.PdfFileMerger(strict=False)
for f in file_order:
    pdf_merged.append(files[f])
    
bs = io.BytesIO()
pdf_merged.write(bs)
pdf_merged.close()


pdf_merged = PyPDF2.PdfFileReader(bs)
pages_num = pdf_merged.getNumPages()

if pageNo_button:

    bs = io.BytesIO()
    c = canvas.Canvas(bs)
    
    for i in range(pages_num):

        page = pdf_merged.getPage(i)

        page_box = page.mediaBox
        width = page_box.getUpperRight_x() - page_box.getLowerLeft_x()
        height = page_box.getUpperRight_y() - page_box.getLowerLeft_y()
        page_size = (float(width), float(height))
        
        c.setPageSize(page_size)
        c.setFont(font, fontsize)
        c.drawCentredString(page_size[0] / 2.0,
                            loc_bottom,
                            f"{prefix}{i+1}{suffix}")
        c.showPage()
    c.save()

    pdf_num = PyPDF2.PdfFileReader(bs)
    

pdf_output = PyPDF2.PdfFileWriter()

for i in range(pages_num):
    
    merged_page = pdf_merged.getPage(i)
    
    if pageNo_button:
        num_page    = pdf_num.getPage(i)
        merged_page.mergePage(num_page)
        
    pdf_output.addPage(merged_page)

        
bs = io.BytesIO()
pdf_output.write(bs)

if uploaded_file:
    st.download_button(
        label="Download",
        data = bs,
        mime='application/pdf')
