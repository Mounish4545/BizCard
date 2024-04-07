











import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3


def image_to_text(path):
  input_img= Image.open(path)

  # converting image to array
  image_arr= np.array(input_img)

  reader= easyocr.Reader(['en'])
  text= reader.readtext(image_arr, detail= 0)

  return text, input_img


def extracted_text(texts):
  extrd_dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[], "ADDERSS":[], "PINCODE":[]}

  extrd_dict["NAME"].append(texts[0])

  extrd_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extrd_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extrd_dict["EMAIL"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small= texts[i].lower()
      extrd_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extrd_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):
      extrd_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,;]','',texts[i])
      extrd_dict["ADDERSS"].append(remove_colon)

  for key,value in extrd_dict.items():
    if len(value)>0:
      concatenate= " ".join(value)
      extrd_dict[key] = [concatenate]

    else:
      value = "NA"
      extrd_dict[key]= [value]


  return extrd_dict


# streamlit

st.set_page_config(layout = "wide")
st.title("EXTRACTUBG BUSINESS CARD DATA WITH 'OCR'")


with st.sidebar:

  select= option_menu("Main Menu", ["Home", "Upload & Modiying", "Delete"])

if select == "Home":
    st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")



    st.write(
              "### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
    st.write(
              '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

elif select == "Upload & Modiying":
  img = st.file_uploader("Upload the image", type= ["png","jpg","jpeg"])

  if img is not None:
    st.image(img , width= 300)

    text_image, input_img= image_to_text(img)

    text_dict = extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED")


    df= pd.DataFrame(text_dict)

    Image_bytes = io.BytesIO()
    input_img.save(Image_bytes, format="PNG")

    image_data = Image_bytes.getvalue()

    # Creating dictionary

    data = {"IMAGE":[image_data]}

    df_1 = pd.DataFrame(data)

    concat_df= pd.concat([df,df_1],axis= 1)

    st.dataframe(concat_df)

    button = st.button("save",use_container_width= True)

    if button:

      mydb = sqlite3.connect("bizcard")
      cursor = mydb.cursor()


      create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard (
                                  name VARCHAR(300),
                                  designation VARCHAR(300),
                                  company_name VARCHAR(300),
                                  contact VARCHAR(300),
                                  email VARCHAR(300),
                                  website TEXT,
                                  address TEXT,
                                  pincode VARCHAR(300),
                                  image TEXT
                              )'''

      cursor.execute(create_table_query)
      mydb.commit()


      insert_query = '''INSERT INTO bizcard(name,
                            designation,
                            company_name,
                            contact,
                            email,
                            website,
                            address,
                            pincode,
                            image)

                            values(?,?,?,?,?,?,?,?,?)'''


      datas = concat_df.values.tolist()[0]
      cursor.execute(insert_query,datas)
      mydb.commit()

      st.success("SAVE SUCCESSFULLY")

  method = st.radio("select the Method",["None","preview","Modify"])

  if method =="None":
    st.write("")

  if method == "preview":


    mydb = sqlite3.connect("bizcard")
    cursor = mydb.cursor()

    select_query = "SELECT * FROM bizcard"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table,columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    st.dataframe(table_df)

  elif method == "Modify":

    mydb = sqlite3.connect("bizcard")
    cursor = mydb.cursor()

    select_query = "SELECT * FROM bizcard"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table,columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    st.dataframe(table_df)

    col1,col2 = st.columns(2)
    with col1:

      selected_name = st.selectbox("Select the Name", table_df["NAME"])


    df_3 = table_df[table_df["NAME"] == selected_name]



    df_4 = df_3.copy()



    col1,col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("NAME", df_3["NAME"].unique()[0])
      mo_disig = st.text_input("DESIGNATION", df_3["DESIGNATION"].unique()[0])
      mo_com_na = st.text_input("COMPANY_NAME", df_3["COMPANY_NAME"].unique()[0])
      mo_cont = st.text_input("CONTACT", df_3["CONTACT"].unique()[0])
      mo_email = st.text_input("EMAIL", df_3["EMAIL"].unique()[0])

      df_4["NAME"] = mo_name
      df_4["DESIGNATION"] = mo_disig
      df_4["COMPANY_NAME"] = mo_com_na
      df_4["CONTACT"] = mo_cont
      df_4["EMAIL"] = mo_email

    with col2:
        mo_website = st.text_input("WEBSITE", df_3["WEBSITE"].unique()[0])
        mo_addre = st.text_input("ADDRESS", df_3["ADDRESS"].unique()[0])
        mo_pincode = st.text_input("PINCODE", df_3["PINCODE"].unique()[0])
        mo_image = st.text_input("IMAGE", df_3["IMAGE"].unique()[0])

        df_4["WEBSITE"] = mo_website
        df_4["ADDRESS"] = mo_addre
        df_4["PINCODE"] = mo_pincode
        df_4["IMAGE"] = mo_image

    st.dataframe(df_4)

    col1,col2= st.columns(2)

    with col1:
      button_3 =st.button("Modify",use_container_width = True)

    if button_3:
        mydb = sqlite3.connect("bizcard")
        cursor = mydb.cursor()

        cursor.execute(f"DELETE FROM bizcard WHERE NAME = '{selected_name}'")
        mydb.commit()


        insert_query = '''INSERT INTO bizcard(name,
                              designation,
                              company_name,
                              contact,
                              email,
                              website,
                              address,
                              pincode,
                              image)

                              values(?,?,?,?,?,?,?,?,?)'''


        datas = df_4.values.tolist()[0]
        cursor.execute(insert_query,datas)
        mydb.commit()

        st.success("Modifiyed SUCCESSFULLY")




elif select == "Delete":

    mydb = sqlite3.connect("bizcard")
    cursor = mydb.cursor()

    col1,col2 = st.columns(2)
    with col1:

      select_query = "SELECT NAME FROM bizcard"

      cursor.execute(select_query)
      table1 = cursor.fetchall()
      mydb.commit()

      names = []

      for i in table1:
        names.append(i[0])

      names_select = st.selectbox("select the name", names)


    with col2:

      select_query = f"SELECT DESIGNATION FROM bizcard WHERE NAME = '{names_select}'"

      cursor.execute(select_query)
      table2 = cursor.fetchall()
      mydb.commit()

      designation = []

      for j in table2:

        designation.append(j[0])

      designation_select = st.selectbox("select the designation", designation)

    if names_select and designation_select:
      col1,col2,col3 = st.columns(3)

      with col1:
        st.write(f"selected Name : {names_select}")
        st.write("")
        st.write("")
        st.write("")
        st.write(f"selected Designation : {designation_select}")

      with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        remove = st.button("Delete", use_container_width= True)

        if remove:
          cursor.execute(f"DELETE FROM bizcard WHERE NAME = '{names_select}' AND DESIGNATION = '{designation_select}'")
          mydb.commit()

          st.warning("DELETE")
