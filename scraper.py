import os
import time
import json
from typing import List, Type

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, create_model
import html2text
import tiktoken

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from openai import OpenAI

load_dotenv()


def setup_selenium():
    #options instance
    options = Options()


    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Randomize user-agent to mimic different users 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # Path to the Chromedriver in your pc
    service = Service(r"./chromedriver-win64/chromedriver.exe")  

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def fetch_html_selenium(url):
    driver = setup_selenium()
    try:
        #Opens the url
        driver.get(url)

        # Add random delays to mimic human behavior
        time.sleep(5)

        # Adds more realistic actions like scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Simulate time taken to scroll and read

        html = driver.page_source
        return html
    #Closes Chrome in case it crashes and not leave it open
    finally:
        #driver.close()
        driver.quit()

def clean_html(html_content):
    soup = BeautifulSoup(html_content, features = 'html.parser')
    
    # Remove headers and footers based on common HTML tags
    for element in soup.find_all(['header', 'footer']):
        element.decompose()  # Remove these tags and their content

    return str(soup)


def html_to_markdown_with_readability(html_content):
    
    cleaned_html = clean_html(html_content)  
    
    # Convert to markdown
    markdown_converter = html2text.HTML2Text()
    # Does not change if you set it to True
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    
    return markdown_content

pricing = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,  # $0.150 per 1M input tokens
        "output": 0.600 / 1_000_000, # $0.600 per 1M output tokens
    },
    "gpt-4o-2024-08-06": {
        "input": 2.5 / 1_000_000,  # $0.150 per 1M input tokens
        "output": 10 / 1_000_000, # $0.600 per 1M output tokens
    },


    # Add other models and their prices here if needed
}
 
def create_dynamic_listing_model(field_names: List[str]):

    #field_name is a list of names of the fields to extract from the markdown.

    field_definitions = {}
    for field in field_names:
        field_definitions[field] = (str, ...)
    return create_model('DynamicListingModel', **field_definitions)


def create_listings_container_model(listing_model: Type[BaseModel]):
    # Create a container model that holds a list of the given listing model.
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))


# Amazon is about 40k
def trim_to_token_limit(text, model, max_tokens=200000):
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    if len(tokens) > max_tokens:
        trimmed_text = encoder.decode(tokens[:max_tokens])
        return trimmed_text
    return text

def format_data(data, DynamicListingsContainer):
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    system_message = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
                        from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
                        with no additional commentary, explanations, or extraneous information. 
                        You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words before or after the JSON:"""

    user_message = f"Extract the following information from the provided text:\nPage content:\n\n{data}"

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature = 0.1,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        response_format=DynamicListingsContainer
    )
    return completion.choices[0].message.parsed
    

def save_formatted_data(formatted_data, timestamp, output_folder='output'):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Prepare formatted data as a dictionary
    formatted_data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

    # Save the formatted data as JSON with timestamp in filename
    json_output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.json')
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data_dict, f, indent=4)
    print(f"Formatted data saved to JSON at {json_output_path}")

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
        print("DataFrame created successfully.")

        # Save the DataFrame to an Excel file
        excel_output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.xlsx')
        df.to_excel(excel_output_path, index=False)
        print(f"Formatted data saved to Excel at {excel_output_path}")
        
        return df
    except Exception as e:
        print(f"Error creating DataFrame or saving Excel: {str(e)}")
        return None

def calculate_price(input_text, output_text, model="gpt-4o-mini"):
    
    encoder = tiktoken.encoding_for_model(model)
    
    input_token_count = len(encoder.encode(input_text))
    
    output_token_count = len(encoder.encode(output_text))
    
    input_cost = input_token_count * pricing[model]["input"]
    output_cost = output_token_count * pricing[model]["output"]
    total_cost = input_cost + output_cost
    
    return input_token_count, output_token_count, total_cost
