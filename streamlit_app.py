import streamlit as st
import pandas as pd
import math
from pathlib import Path
import base64
import boto3
import os
from botocore.exceptions import NoCredentialsError
import tempfile
import fitz
import re


aws_access_key_id = st.secrets["AWS_ACCESS_KEY"]
aws_secret_access_key = st.secrets["AWS_SECRET_KEY"]
region = st.secrets["AWS_REGION"]
bucket = st.secrets["BUCKET_NAME"]



# Upload file
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    s3 = boto3.client(
      "s3",
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      region_name=region
    )

    s3.upload_fileobj(uploaded_file, bucket, uploaded_file.name)
    st.success(f"Uploaded {uploaded_file.name} to S3 bucket {bucket}")



# UI: Ask user for S3 key
st.title("View PDF from S3")
'''pdf_key = st.text_input("Enter S3 key of the PDF (e.g., `invoices/INV001.pdf`):")'''

user_input = st.text_input("Enter text to search in PDF")



s3 = boto3.client(
      "s3",
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      region_name=region
    )

response = s3.list_objects_v2(Bucket=bucket)

if "Contents" in response:
    for obj in response["Contents"]:
        if obj["Key"].endswith(".pdf"):
            pdf_key = obj["Key"]
            break

st.title("View Frist PDF")


if pdf_key:
    st.write(f"Loading PDF: `{pdf_key}`")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            s3.download_fileobj(bucket, pdf_key, tmp_file)
            tmp_file_path = tmp_file.name
            st.write(f"Downloaded file size: {os.path.getsize(tmp_file_path)} bytes")

            # Open the PDF and extract text
            doc = fitz.open(tmp_file_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            lines = full_text.splitlines()
            insured_name = None

            for i, line in enumerate(lines):
                if "insurer a" in line.lower():
            # Look ahead for the next non-empty line
                    st.write(f"Found 'insurer' at line {i}: {line}")
                    match = re.search(re.escape(user_input) + r"insurer a[:\s]*(.+)", line, re.IGNORECASE)
                    if match :
                        insurer_a = match.group(1).strip()
                    break

            if insured_name:
                st.success(f"Insurer A Name: {insurer_a}")
            else:
                st.warning("Could not find the {insurer_a} name in the PDF.")




        '''with open(tmp_file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(
            f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" '
            'type="application/pdf"></iframe>',
            unsafe_allow_html=True
        )'''

    except Exception as e:
        st.error(f"Could not retrieve PDF: {e}")

