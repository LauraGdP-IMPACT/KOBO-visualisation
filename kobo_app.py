#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:10:12 2024

@authors: laura-gr
"""


import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import numpy as np
import re
import math

logo_paht="IMPACT_Logo.jpg"

def remove_html_tags(text):
    # Define a regex pattern for HTML tags
    clean = re.compile('<.*?>')
    # Substitute HTML tags with an empty string
    return re.sub(clean, '', text)

def extract_bracket_content(text):
    # Define a regex pattern to match content inside curly brackets
    pattern = r'\{([^}]+)\}'
    # Search for the pattern in the text
    match = re.search(pattern, text)
    # If a match is found, return the content inside the brackets, else return None
    if match:
        return match.group(1)
    else:
        return None
    
def display_nicely(title, text, indent_level, font_size=10):

    # Multiplier for indentation in pixels
    indent = indent_level * 10  # Each indent level increases by 10 pixels
    text=remove_html_tags(text)
    html_str = f"""<div>
        <p style="font-size: {font_size}px;">{title}</p><p style="font-size: {font_size}px; text-indent: {indent}px;">{text}</p>
    </div>
    """
    
    st.markdown(html_str, unsafe_allow_html=True)

def load_excel(file, survey_sheet="survey", choices_sheet="choices"):
    try:
        xl = pd.ExcelFile(file)
        survey = pd.read_excel(xl, sheet_name=survey_sheet)
        choices = pd.read_excel(xl,sheet_name=choices_sheet )
        return choices, survey
    except Exception as e:
        st.error(f"Error loading Excel file: {e}. \n Maybe check the names of the sheets ?")
        return None, None

def visualize_choices(choices_df):
    st.header("Choices")
    st.dataframe(choices_df)


def visualize_survey(survey_df, choices_df, type_col, name_col, label_col, constraint_col, constraint_message_col,calculation_col, repeat_col,relevant_col):
    
    question_counter=1    
    for row_num, row in survey_df.iterrows():
        question_type = row[type_col].split(" ")[0]
        if "select" in question_type:
            list_name=row[type_col].split(" ")[1]

        question_name = row[name_col]
        question_label = row[label_col]

        if question_type in ["start","end","today","audit","deviceid"]:
            continue
        if question_type=="begin_group":
            st.divider()
            st.caption(f"Beginning of a group of questions on {question_name}")
            continue
        if question_type=="end_group":
            st.caption(f"End of the group of questions on {question_name}")
            st.divider()
            continue

        if question_type=="note":
            text_to_display=remove_html_tags(question_label)

            if row[constraint_col]==row[constraint_col] or row[relevant_col]==row[relevant_col]:
                st.write("If the following condition applies")

                if row[constraint_col]==row[constraint_col]:
                    st.code(row[constraint_col])
                else :
                    st.code(row[relevant_col]) 
                display_nicely(title="the following note will appear to the interviewer:", text=text_to_display, indent_level=4)
                

            else :
                display_nicely(title="Note:", text=text_to_display, indent_level=4)
            continue

        if question_type=="begin_repeat":
            st.divider()
            var_repeat=extract_bracket_content(row[repeat_col])
            st.subheader(f"The following questions will be repeated based on the value of _{var_repeat}_.")
            st.caption("Begin of a repeat cycle." )
            continue


        
        container=st.container(border=True)
        if question_type=="calculate" :
            container.markdown(f"{question_counter}. Calculated field to create _{question_name}_")
        else :
            container.write(f"{question_counter}. {question_label}") 
            container.write(f"The name of the variable in the data is _{question_name}_")

            if row[constraint_col]==row[constraint_col]:
                container.write(f"These are the constraints: \n ")
                container.code(row[constraint_col])
        
        if question_type == 'text':
            container.caption("This is an open text question.")
            question_counter+=1

        elif question_type == 'integer':
            container.caption("Requested to enter an integer.")
            question_counter+=1
        
        elif question_type =="calculate":
            container.caption("This is the formula used:")
            container.code(row[calculation_col])
            question_counter+=1

        elif "select" in question_type:
            container.caption(f"This is a {question_type} question. \n The available choices are:")
            choices_list = choices_df[choices_df['list_name'] == list_name]['name'].tolist()
            
            if len(choices_list)>7:
                show_choices=container.selectbox(label="There are more than 7 different choices. To see them, scroll through the menu.",options=choices_list, key=question_counter)
            else :
                s=''
                for i in choices_list:
                    s += "- " + str(i) + "\n"
                container.markdown(s)
            question_counter+=1
        

        elif question_type=="date":
            container.caption(f"This is a {question_type} question. Requested to enter a date.")

        else:   
            st.write(f"Unsupported question type: {question_type}")
    

def load_choices_params(survey_df):
    return survey_df.columns

    
def main():
    st.empty()
    col1,_,_,col4= st.columns(4)
    with col4:
        st.image(logo_paht, width=356)
    st.title("KOBO Questionnaire Visualizer")
    st.write("Upload an Excel file with 'choice' and 'survey' sheets to visualize the questionnaire.")

    
    with st.expander("Uploading the survey and choices files."):

        choices_df = None
        survey_df = None

        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
        survey_name=st.text_input("Please input the sheet name for the survey", value="survey")
        choices_name=st.text_input("Please input the sheet name for the choices", value="choices")
        
        uploaded= st.toggle('Please confirm you have uploaded the kobo tool and input the correct paraments.')
        
    
        if uploaded:
            choices_df, survey_df = load_excel(uploaded_file, survey_sheet=survey_name, choices_sheet=choices_name)


        else :
            st.write("Please check the format of the files and the input parameter boxes and try again.")

    

    if uploaded:
        survey_cols=load_choices_params(survey_df)

        with st.expander("Parameters for reading the survey"):

            type_col=st.selectbox("Name of the column containing the type.", options=survey_cols)
            name_col=st.selectbox("Name of the column containing the name.", options=survey_cols)
            label_col=st.selectbox("Name of the column containing the label.", options=survey_cols)

            constraint_col=st.selectbox("Name of the column containing the constraints.", options=survey_cols)
            constraint_message_col = st.selectbox("Name of the column containg the constraint message.", options=survey_cols)
            calculation_col = st.selectbox("Name of the column containing the formulas for calculated fields.", options=survey_cols)
            repeat_col=st.selectbox("Name of the column with the repeat variable.", options=survey_cols)
            relevant_col=st.selectbox("Name of the column with the relevant parameter.",options=survey_cols)

            completed_params=st.toggle("Please confirm you have filled in the above fields.")



            if choices_df is not None and survey_df is not None and completed_params:
                st.subheader("Questionnaire Preview")
                visualize_survey(survey_df,choices_df, type_col, name_col, label_col, constraint_col, constraint_message_col, calculation_col, repeat_col,relevant_col)

                with st.expander("Preview of the choices tab."):
                    visualize_choices(choices_df)
            elif completed_params:
                st.error("Unable to load data from the Excel file. Please check the file format and that you provided the necessary parameters as well as you confirmation.")
            
    
    # st.markdown(":rainbow[This little app was made by [L. Grave de Peralta](https://github.com/Laura-gr)]")

    


if __name__ == "__main__":
    main()
