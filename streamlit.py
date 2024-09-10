import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
import json
from datetime import datetime
from scraper import fetch_html_selenium, format_data, calculate_price,html_to_markdown_with_readability, create_dynamic_listing_model,create_listings_container_model


# Initialize Streamlit app
st.set_page_config(page_title="AI Web Scraper")
st.title("RAAFYA Web Scraper")

st.sidebar.title("Web Scraper Settings")
# Defaults 2 first to save cost
model_selection = st.sidebar.selectbox("Select Model", options=["gpt-4o-mini", "gpt-4o-2024-08-06"], index=0)
url_input = st.sidebar.text_input("Enter URL")


# Tags input specifically in the sidebar
tags = st_tags_sidebar(
    label='Enter Fields to Extract:',
    text='Press enter to add a tag',
    value=["image", "price"],  # Default values if any
    maxtags=-1,  # -1 for unlimited tags
)

st.sidebar.markdown("---")

# Initialize variables to store token and cost information
input_tokens = output_tokens = total_cost = 0 

# Define the scraping function
def perform_scrape():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_html = fetch_html_selenium(url_input)
    markdown = html_to_markdown_with_readability(raw_html)
    DynamicListingModel = create_dynamic_listing_model(tags)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    formatted_data = format_data(markdown, DynamicListingsContainer)
    formatted_data_text = json.dumps(formatted_data.dict())
    input_tokens, output_tokens, total_cost = calculate_price(markdown, formatted_data_text, model=model_selection)
    
    # Prepare formatted data as a dictionary
    formatted_data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

    # Prepare data for DataFrame
    if isinstance(formatted_data_dict, dict):
        # If the data is a dictionary containing lists, assume these lists are records
        data_for_df = next(iter(formatted_data_dict.values())) if len(formatted_data_dict) == 1 else formatted_data_dict
    elif isinstance(formatted_data_dict, list):
        data_for_df = formatted_data_dict
    else:
        raise ValueError("Formatted data is neither a dictionary nor a list, cannot convert to DataFrame")

    try:
        df = pd.DataFrame(data_for_df)
    except Exception as e:
        print(f"Error creating DataFrame: {str(e)}")
        df = None

    return df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp


# Handling button press for scraping
if 'perform_scrape' not in st.session_state:
    st.session_state['perform_scrape'] = False

if st.sidebar.button("Scrape"):
    with st.spinner('Please wait... Data is being scraped.'):
        st.session_state['results'] = perform_scrape()
        st.session_state['perform_scrape'] = True

# Inside the 'if st.session_state.get('perform_scrape'):' block
if st.session_state.get('perform_scrape'):
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
    # Display the DataFrame
    st.write("Scraped Data:", df)
    st.sidebar.markdown("## Token Usage")
    st.sidebar.markdown(f"**Input Tokens:** {input_tokens}")
    st.sidebar.markdown(f"**Output Tokens:** {output_tokens}")
    st.sidebar.markdown(f"**Total Cost:** :green-background[***${total_cost:.4f}***]")
    
    # Create columns for download buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download JSON", data=json.dumps(formatted_data.dict(), indent=4), file_name=f"{timestamp}_data.json")
    with col2:
        # The DataFrame 'df' is already prepared in 'perform_scrape'
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name=f"{timestamp}_data.csv")
    with col3:
        st.download_button("Download Markdown", data=markdown, file_name=f"{timestamp}_data.md")

# Changing model wont affect the UI
if 'results' in st.session_state:
    df, formatted_data, markdown, input_tokens, output_tokens, total_cost, timestamp = st.session_state['results']
        