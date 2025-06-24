import streamlit as st
import pandas as pd
import math
from pathlib import Path
import base64
import boto3
import os
from botocore.exceptions import NoCredentialsError
import tempfile


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
pdf_key = st.text_input("Enter S3 key of the PDF (e.g., `invoices/INV001.pdf`):")


s3 = boto3.client(
      "s3",
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      region_name=region
    )

if pdf_key:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            s3.download_fileobj(bucket, pdf_key, tmp_file)
            tmp_file_path = tmp_file.name

        with open(tmp_file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        st.markdown(
            f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" '
            'type="application/pdf"></iframe>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Could not retrieve PDF: {e}")

