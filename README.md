# RAAFYA Web Scraper

RAAFYA Web Scraper is a versatile web scraping tool designed to extract structured data from web pages. It utilizes Selenium to fetch HTML content, converts it to markdown, and extracts relevant information using OpenAI's GPT models. The scraped data is then formatted and saved as JSON, CSV, or markdown files.

## Features

- **Web Scraping with Selenium:** Fetches and cleans HTML content from the web.
- **Markdown Conversion:** Converts HTML content to markdown for easy readability.
- **Dynamic Data Extraction:** Uses OpenAI models to extract specific fields from the scraped content.
- **Cost Calculation:** Automatically calculates the cost of token usage for OpenAI models.
- **Data Export:** Exports the extracted data in JSON, CSV, and markdown formats.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yazanrisheh/AI-Webscraper.git
    cd AI-Webscraper
    ```

2. **Install Dependencies:**

    Ensure you have Python 3.8 or later installed. Install the required Python packages using:

    ```bash
    pip install -r requirements.txt
    ```

3. **Download ChromeDriver:**

    Download the ChromeDriver compatible with your operating system from [this link](https://googlechromelabs.github.io/chrome-for-testing/). Place the `chromedriver.exe` in the `./chromedriver-win64/` directory or update the path in the `scraper.py` script accordingly.

4. **Set Up Environment Variables:**

    Create a `.env` file in the root directory and add your OpenAI API key:

    ```bash
    OPENAI_API_KEY=your_openai_api_key_here
    ```

    Alternatively, you can copy the provided `.env.example` and fill in your API key.

    ```bash
    cp .env.example .env
    ```

## Usage

### Command-Line Usage

1. **Run the Web Scraper:**

    Modify the URL and fields you want to scrape in the `scraper.py` file, then execute:

    ```bash
    python scraper.py
    ```

2. **Scraped Data Output:**

    The scraped data will be saved in the `output/` directory as markdown and JSON files.

### Streamlit App Usage

1. **Start the Streamlit App:**

    Launch the Streamlit app to interactively scrape websites:

    ```bash
    streamlit run streamlit.py
    ```

2. **Interact with the App:**

    - Enter the URL of the webpage you want to scrape.
    - Specify the fields you want to extract.
    - Click the "Scrape" button to initiate the scraping process.

3. **Download Results:**

    After scraping, you can download the results in JSON, CSV, or markdown format directly from the app.

## Project Structure

- `scraper.py`: Contains the main logic for web scraping, data cleaning, markdown conversion, and data formatting.
- `streamlit.py`: Provides a Streamlit interface for interactive scraping and data download.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `.env.example`: Example of the environment variable file required for the OpenAI API key.
- `output/`: Directory where the scraped data will be saved.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or issues, feel free to contact me at yazanrisheh@hotmail.com or +971509108917

