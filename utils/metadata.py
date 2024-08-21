import pandas as pd
import numpy as np
import streamlit as st
import io

def generate_metadata(file_like):
    # Check if the input is a StringIO object (from SQL query) or an UploadedFile
    if isinstance(file_like, io.StringIO):
        df = pd.read_csv(file_like)
        file_name = "Fetched Data from SQL"
        file_size = len(file_like.getvalue()) / 1024  # Estimate size in KB
    else:
        df = pd.read_csv(file_like)
        file_name = file_like.name
        file_size = file_like.size / 1024  # Convert bytes to KB

    # Descriptive Metadata
    descriptive_metadata = {
        "File Name": file_name,
        "File Size": f"{file_size:.2f} KB",
        "Number of Rows": df.shape[0],
        "Number of Columns": df.shape[1],
        "Column Names": list(df.columns),
        "Description": f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns."
    }
    
    # Operational Metadata
    operational_metadata = {
        "Column Data Types": df.dtypes.to_dict(),
        "Null Count": df.isnull().sum().to_dict(),
        "Unique Values Count": df.nunique().to_dict(),
        "Empty Cells Count": df.apply(lambda x: np.sum(x.astype(str).str.strip() == '') if x.dtype == "object" else 0).to_dict()
    }
    
    # Combine the metadata
    metadata = {
        "Descriptive Metadata": descriptive_metadata,
        "Operational Metadata": operational_metadata
    }
    
    return metadata


def display_metadata(metadata):
    # Descriptive Metadata
    st.markdown("#### Descriptive Metadata")
    st.markdown(f"**File Name:** {metadata['Descriptive Metadata']['File Name']}")
    st.markdown(f"**File Size:** {metadata['Descriptive Metadata']['File Size']}")
    st.markdown(f"**Number of Rows:** {metadata['Descriptive Metadata']['Number of Rows']}")
    st.markdown(f"**Number of Columns:** {metadata['Descriptive Metadata']['Number of Columns']}")
    st.markdown("**Column Names:**")
    for column_name in metadata['Descriptive Metadata']['Column Names']:
        st.markdown(f"<p style='margin-left: 20px;'>╰┈➤ {column_name}</p>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    st.markdown(f"**Description:** {metadata['Descriptive Metadata']['Description']}")

    # Operational Metadata
    st.markdown("#### Operational Metadata")

    # Combine the three pieces of metadata into a single DataFrame
    data_types_df = pd.DataFrame(list(metadata['Operational Metadata']['Column Data Types'].items()), columns=["Column Name", "Data Type"])
    null_values_df = pd.DataFrame(list(metadata['Operational Metadata']['Null Count'].items()), columns=["Column Name", "Null Count"])
    empty_values_df = pd.DataFrame(list(metadata['Operational Metadata']['Empty Cells Count'].items()), columns=["Column Name", "Empty Count"])
    unique_values_df = pd.DataFrame(list(metadata['Operational Metadata']['Unique Values Count'].items()), columns=["Column Name", "Unique Count"])

    # Merge the DataFrames on the "Column Name"
    combined_df = pd.merge(data_types_df, null_values_df, on="Column Name")
    combined_df = pd.merge(combined_df, unique_values_df, on="Column Name")
    combined_df = pd.merge(combined_df, empty_values_df, on="Column Name")

    def highlight_rows(row):
        return ['background-color: #efefef' if i % 2 == 0 else 'background-color: #ffffff' for i in range(len(row))]

    combined_df = combined_df.style.apply(highlight_rows, axis=0)

    # Display the styled DataFrame as a Streamlit dataframe
    st.dataframe(combined_df)