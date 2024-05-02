from openai import OpenAI
import PyPDF2
import json
import pandas as pd
from spire.pdf import *
import streamlit as st
import db_connect
from datetime import datetime


def extract_table(pdf_reader, file):

    # Select LLM model
    my_ai_model = "gpt-3.5-turbo"

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key="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",
    )


    # Iterate through each page and extract text
    page = pdf_reader.pages[0]
    page_text = page.extract_text()

    messages = [
        {
            "role": "system",
            "content": """You are a PDF table extractor, a backend processor.
    - User input is messy raw text extracted from a PDF page by PyPDF2.
    - Do not output any body text, we are only interested in tables.
    - The goal is to identify tabular data, and reproduce it cleanly as comma-separated table.
    - Preface each output table with a line giving title and 10 word summary.
    - It is crucial to format the response in the form of a python dict of dict with table title as the main key, followed by summary and table as sub keys for each table. The table should not be a dict but a list of lists.
    - Reproduce each separate table found in page."""
        },
        {
            "role": "user",
            "content": "raw pdf text; extract and format tables:" + page_text
        }
    ]

    api_params = {"model": my_ai_model, "messages": messages, "temperature":0}
    api_response = client.chat.completions.create(**api_params)
    response_message = api_response.choices[0].message.content

    # Convert string to dictionary of dictionaries
    dict_of_tables = json.loads(response_message)

    # Generate list of table names
    table_names = [f"table_{i}" for i in range(1, len(dict_of_tables) + 1)]

    # for table in dict_of_tables:
    for j, table in enumerate(dict_of_tables):

        # Extract header and data
        column_list = dict_of_tables[table]['table'][0]
 
        # Generate unique replacement values based on position
        replacement_values = [f'default_value_{i}' for i in range(1, len(column_list)+1)]
        
        for i in range(len(column_list)):
            if column_list[i] is None or column_list[i] == '':
                column_list[i] = replacement_values[i]
        
        table_data = dict_of_tables[table]['table'][1:]

        # Convert to Pandas DataFrame
        df = pd.DataFrame(table_data, columns=column_list)
        table = table.replace(' ','')
        file_name = str(file.name)

        # Get table name from user input or use default format
        default_table_name = f'{file_name}_{datetime.now().strftime("%Y%m%d%H%M%S")}'

        table_name_input = st.text_input(f"Enter table name: (Optional)",key =table_names[j])
        if (table_name_input ==''):
            selected_heading = default_table_name
        else:
            selected_heading = table_name_input


        if st.button("Save to DB",key =f'table{j}_{table_names[j]}'):
            db_connect.save_to_db(df, selected_heading)


        # Print the DataFrame
        st.write("Table Name : ", selected_heading)
        st.write(df)
        st.write("---------------------------------------------")



def extract_pdf(file):

    # Create a PdfDocument object
    pdf = PdfDocument()
    st.write(file.name)

    # Load a PDF file
    pdf.LoadFromFile(file.name)


    selected_page = st.text_input(
        "Please enter the page number you want to process or type ALL if you want to process the entire pdf", key="page_number"
    )
    if selected_page == '':

        pdf_file = "./pdf/"+file.name+"_"+selected_page+".pdf"
        # Save the resulting files
        pdf.SaveToFile(pdf_file)
        # Close the PdfDocument objects\
        pdf.Close()
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extract_table(pdf_reader)
    else:
        # Create new PdfDocument objects
        newPdf_1 = PdfDocument()

        selected_page_num = int(selected_page)
        selected_page_number_str= str(selected_page_num)


        # Insert select pages into new PDF file
        newPdf_1.InsertPageRange(pdf, selected_page_num, selected_page_num)

        # pdf_file = "./pdf/OMV_28.pdf"
        pdf_file = "./pdf/"+file.name+"_"+selected_page_number_str+".pdf"

        # Save the resulting files
        newPdf_1.SaveToFile(pdf_file)

        # Close the PdfDocument objects
        pdf.Close()
        newPdf_1.Close()

        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extract_table(pdf_reader,file)