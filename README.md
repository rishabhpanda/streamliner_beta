# Streamliner AI (beta)
## Solution for big data challenges at your fingertips

**Streamliner AI** is an advanced AI-powered data cleaning web application, built with the Streamlit framework and integrated with GPT-4 for seamless, intuitive data processing.

### Key Features:
- **AI-Powered Data Cleaning**: Leverage the power of GPT-4 to clean, transform, and manipulate big data with natural language prompts.
- **User-Friendly Interface**: Built using Streamlit, the application provides a simple and intuitive interface for non-technical users.
- **Upload & Download Functionality**: Easily upload datasets in various formats, clean them with AI-driven prompts, and download the cleaned data.
- **Big Data Handling**: Designed to handle large datasets efficiently, ensuring smooth performance for complex data processing tasks.
- **Customizable Processing**: Input custom prompts to tailor the data cleaning process to your specific needs.
  
### How It Works:
1. **Upload Your Dataset**: Import your dataset via the simple file upload feature.
2. **Input AI Prompts**: Write prompts instructing the AI on how to clean or transform the data.
3. **AI Processing**: Streamliner AI uses GPT-4 to understand the prompts and clean the data accordingly.
4. **Download Cleaned Data**: Once processed, the cleaned dataset is available for download in your preferred format.

### Installation and Setup:

1. Clone the repository:
    ```bash
    git clone https://github.com/rishabh-panda/streamliner_beta
    cd streamliner_beta
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv appenv
    appenv\Scripts\activate  # On Windows
    ```

3. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

### Requirements:
- Python 3.8+
- Libraries:
  - `streamlit`
  - `pandas`
  - `openai`
  - `hashlib`, `json`, `os`, `base64` (Standard Python libraries)

### Contribution:
Feel free to contribute by submitting issues or pull requests to improve the application.

### License:
This project is licensed under the MIT License.
