import streamlit as st
import pdf_extractor
import xlcsv_extractor
import image_extractor

st.set_page_config(layout="wide")

# Define the image paths
img_path_heading= r"C:\Users\Vaishali\Desktop\Vaishu\ISB\Capstone project\EY\Data\images\image1.png"

# Read the image files
img_heading = open(img_path_heading, "rb").read()

st.image(img_heading, use_column_width=False, width=1300)

# File upload
file = st.sidebar.file_uploader("Choose a file", type=['txt', 'pdf','jpg', 'xlsx'])

if file is not None:
    st.write("File uploaded successfully!")

    if file.type == 'application/pdf':
        pdf_extracted_op = pdf_extractor.extract_pdf(file)
    if (file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or file.type == 'application/csv') :
        excel_extracted_op = xlcsv_extractor.extract_xlcsv(file)
    if (file.type.startswith("image/") or file.name.lower().endswith(('.jpg', '.jpeg'))):
        image_extracted_op = image_extractor.extract_image(file)







