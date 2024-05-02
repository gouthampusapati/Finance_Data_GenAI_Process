import pytesseract
from img2table.ocr import TesseractOCR
from img2table.document import Image
import pandas as pd
import streamlit as st
import db_connect
from datetime import datetime




def extract_image(file) :

    # Set the Tesseract OCR executable path
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    # Instantiate the TesseractOCR object
    ocr = TesseractOCR(n_threads=1, lang="eng", psm=11)

    # Instantiation of the image
    img = file.name

    #Instantiation of OCR
    ocr = TesseractOCR(n_threads=1, lang="eng")

    # Instantiation of document, either an image or a PDF
    doc = Image(img)

    # Table extraction
    extracted_tables = doc.extract_tables(ocr=ocr,
                                          implicit_rows=False,
                                          borderless_tables=False,
                                          min_confidence=50)



    # Generate list of table names
    table_names = [f"table_{j}" for j in range(1, len(extracted_tables) + 1)]

    for k,table in enumerate (range (0,len(extracted_tables))):

        # table_name = 'table'+str(i)
        # st.write(table_name)

        file_name = str(file.name)

        # Get table name from user input or use default format
        default_table_name = f'{file_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}'

        table_name_input = st.text_input(f"Enter table name: (Optional)",key =table_names[k])
        if (table_name_input ==''):
            selected_heading = default_table_name
        else:
            selected_heading = table_name_input


        if st.button("Save to DB",key =f'table{k}_{table_names[k]}'):
            db_connect.save_to_db(extracted_tables[table].df, selected_heading)


        # Print the DataFrame
        st.write("Table Name : ", selected_heading)
        st.write(extracted_tables[table].df)
        st.write("---------------------------------------------")
