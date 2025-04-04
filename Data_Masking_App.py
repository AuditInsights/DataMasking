import streamlit as st
import pandas as pd
import numpy as np
import random
import string
import io
import zipfile

# ------------------------------
# Helper Functions
# ------------------------------

def random_string(length):
    """Generate a random string of uppercase letters of given length."""
    return ''.join(random.choices(string.ascii_uppercase, k=length))

def create_text_mapping(series):
    """Create a mapping for text values in a pandas Series."""
    unique_values = series.dropna().unique()
    max_len = max(map(len, unique_values.astype(str)))  # Get max length
    mapping = {val: random_string(max_len) for val in unique_values}
    return mapping

def detect_column_type(series):
    """Detect column type: Number, Date, or Text."""
    try:
        numeric_series = pd.to_numeric(series, errors='coerce')
        if numeric_series.notna().all():
            return "number"
    except:
        pass

    try:
        date_series = pd.to_datetime(series, errors='coerce')
        if date_series.notna().sum() / series.dropna().shape[0] >= 0.8:
            return "date"
    except:
        pass

    return "text"

# ------------------------------
# Streamlit App
# ------------------------------

st.title("Data Masking App")
st.write("Upload a CSV file and select options for masking/modifying sensitive data.")

# 1. Upload CSV File
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Original Data Preview")
    st.dataframe(df.head())

    st.write("### Select columns to mask (Only Text Columns Displayed)")

    text_columns = [col for col in df.columns if detect_column_type(df[col]) == "text"]
    masking_options = {}

    with st.form("masking_form"):
        for col in text_columns:
            col1, col2 = st.columns([4, 2])
            col1.write(f"**{col}**")
            masking_options[col] = col2.selectbox(
                f"Mask '{col}'?", 
                options=["No", "Yes"], 
                key=f"mask_{col}"
            )

        submitted = st.form_submit_button("Run")

    if submitted:
        masked_df = df.copy()
        mapping_dict = {}

        for col in text_columns:
            if masking_options.get(col) == "Yes":
                mapping = create_text_mapping(df[col])
                mapping_dict[col] = mapping
                masked_df[col] = df[col].map(mapping).fillna(df[col])
            else:
                st.info(f"Column '{col}' was not masked.")

        st.subheader("Masked Data Preview")
        st.dataframe(masked_df.head())

        # Creating ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Save masked data
            masked_csv_buffer = io.StringIO()
            masked_df.to_csv(masked_csv_buffer, index=False)
            zf.writestr("masked_data.csv", masked_csv_buffer.getvalue())

            # Save mapping dictionary in an Excel file
            if mapping_dict:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    for col, mapping in mapping_dict.items():
                        mapping_df = pd.DataFrame(list(mapping.items()), columns=["Original", "Masked"])
                        mapping_df.to_excel(writer, sheet_name=col[:31], index=False)
                zf.writestr("mapping_file.xlsx", excel_buffer.getvalue())

        zip_buffer.seek(0)
        st.download_button(
            label="Download ZIP (Masked CSV + Mapping Excel)",
            data=zip_buffer,
            file_name="masked_mapping.zip",
            mime="application/zip"
        )
