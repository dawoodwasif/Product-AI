import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from features import generate_product_description, classify_product_category
from PIL import Image
from io import BytesIO
import base64 
import requests

STREAMLIT_AGGRID_URL = "https://github.com/PablocFonseca/streamlit-aggrid"
st.set_page_config(
    layout="centered", page_icon="🖱️", page_title="Interactive table app"
)
st.title("📱 PIM Fabric AI Features")
st.write(
    """This app shows PIM platform's AI features, including a Product Description Generator, intuitive creation of collections through natural language, and automated Category Generation with smart product placement."""
)

st.write("## Data Selection")

st.write("Go ahead, click on a row in the table below!")


def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection


data = pd.read_csv(
    "data.csv"
)

selection = aggrid_interactive_table(df=data)

######################################


# Function to display the table and gather user input
def display_and_add_data_to_csv():
    # Read the CSV file or create an empty DataFrame if it doesn't exist
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["ProductId", "Gender", "Category", "SubCategory", "ProductType", "Colour", "Usage", "ProductTitle", "Image", "ImageURL"])

    # Show/Hide Add Data section based on user input
    add_data_button = st.checkbox("Show Add Data Section")
    if add_data_button:
        # Ask for user input for each column
        new_data = {}
        for column in st.session_state.data.columns:
            if column == "ImageURL":
                new_data[column] = st.text_input(column)
            else:
                new_data[column] = st.text_input(column, key=f"{column}_input")

        # Add Data to CSV button
        add_data_button = st.button("Add Data to CSV")

        # Append data to CSV when Add Data button is pressed
        if add_data_button:
            st.session_state.data = st.session_state.data.append(new_data, ignore_index=True)
            st.success("Data added to CSV successfully!")
            save_data_to_csv()  # Save data to CSV
            # Trigger a rerun of the entire app
            st.experimental_rerun()


# Function to save the data to CSV
def save_data_to_csv():
    existing_data = pd.read_csv("data.csv") if st.session_state.data.size > 0 else pd.DataFrame()
    updated_data = existing_data.append(st.session_state.data, ignore_index=True)
    updated_data.to_csv("data.csv", index=False)

# Display the table and add/clear data to CSV
display_and_add_data_to_csv()


#######################################

def display_image_from_url(image_url, width=300):
    try:
        # Load the image from the URL
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Display the image using HTML to control the width
        img_html = f'<img src="data:image/png;base64,{image_to_base64(img)}" width="{width}">'
        st.markdown(img_html, unsafe_allow_html=True)
    except Exception as e:
        # If there's an error, display a nice message
        st.markdown(
            f"""
            #### Image Not Found
            
            Unfortunately, the requested image could not be loaded. Please check the URL.
            
            Error details: {e}
            """
        )

def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])

selected_rows = selection["selected_rows"]
if len(selected_rows):
    st.write('Product Image:')
    display_image_from_url(selected_rows[0]['ImageURL'])



st.write("## PIM Features")


# Define your LLM functions (replace with your actual functions)
def function1(selected_row):
    # Your code here
    return f"Function 1 output for row {selected_row}"

def function2(selected_row):
    # Your code here
    return f"Function 2 output for row {selected_row}"

# Select a function to run
st.subheader("Select Function")
function_choice = st.selectbox("Choose a Function", ["Category Classification", "Product Description Generator"])

if function_choice == "Category Classification":
        
        # Ask if they want to manually enter categories
        manual_categories = st.checkbox("Manually Enter Categories")
        
        # If manual_categories is True, ask for the categories
        if manual_categories:
            categories = st.text_input("Enter Categories (comma-separated)", "")
        else:
            categories = None  # No categories provided
       
elif function_choice == "Product Description Generator":
    
    # Ask for tone of voice
    tone_of_voice = st.text_input("Enter Tone of Voice", "Neutral")



if st.button("Run Function"):

    output = ""
    if len(selected_rows) == 0:
        st.warning('Please select at least one row from the table')
    
    else:


        if function_choice == "Category Classification":
        
            for row in selected_rows:
                result = classify_product_category(row, categories)
                output += f"{result}\n"

        elif function_choice == "Product Description Generator":
            
            for row in selected_rows:
                result = generate_product_description(row, tone_of_voice)
                output += f"{result}\n"
        
        # Display the function output
        st.subheader("Function Output:")
        st.code(output, language="text")