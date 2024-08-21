import pandas as pd
import streamlit as st

def generate_metadata(uploaded_file):
    # Read the CSV file from the UploadedFile object
    df = pd.read_csv(uploaded_file)

    # Since there's no file path, use the uploaded file name and size directly
    file_name = uploaded_file.name
    file_size = uploaded_file.size / 1024  # Convert bytes to KB

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
        "Missing Values Count": df.isnull().sum().to_dict(),
        "Unique Values Count": df.nunique().to_dict(),
        "File Delimiter": ','  # Assuming CSV file with comma delimiter
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
    st.markdown(f"**File Delimiter:** {metadata['Operational Metadata']['File Delimiter']}")
    st.markdown(f"**Number of Rows:** {metadata['Descriptive Metadata']['Number of Rows']}")
    st.markdown(f"**Number of Columns:** {metadata['Descriptive Metadata']['Number of Columns']}")
    st.markdown("**Column Names:**")
    for column_name in metadata['Descriptive Metadata']['Column Names']:
        st.markdown(f"<p style='margin-left: 20px;'>╰┈➤ {column_name}</p>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)
    st.markdown(f"**Description:** {metadata['Descriptive Metadata']['Description']}")

    # Operational Metadata
    st.markdown("#### Operational Metadata")

    # Create three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        # Column Data Types
        st.markdown("**A. Column Data Types**")
        data_types_df = pd.DataFrame(list(metadata['Operational Metadata']['Column Data Types'].items()), columns=["Column Name", "Data Type"])
        st.markdown(data_types_df.to_html(index=False), unsafe_allow_html=True)

    with col2:
        # Missing Values Count
        st.markdown("**B. Missing Values Count**")
        missing_values_df = pd.DataFrame(list(metadata['Operational Metadata']['Missing Values Count'].items()), columns=["Column Name", "Missing Values"])
        st.markdown(missing_values_df.to_html(index=False), unsafe_allow_html=True)

    with col3:
        # Unique Values Count
        st.markdown("**C. Unique Values Count**")
        unique_values_df = pd.DataFrame(list(metadata['Operational Metadata']['Unique Values Count'].items()), columns=["Column Name", "Unique Values"])
        st.markdown(unique_values_df.to_html(index=False), unsafe_allow_html=True)