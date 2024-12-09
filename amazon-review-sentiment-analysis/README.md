# Product Review Keyword and Sentiment Analysis

This project analyzes product reviews from a text file, extracts key keywords, and determines their associated sentiment (Positive, Negative, Neutral). The results are aggregated to provide insights into the overall perception of the product.

---

## Features

- **Review Parsing**: Reads reviews from a structured text file and extracts individual reviews.
- **Keyword and Sentiment Extraction**: Uses OpenAI's GPT model to analyze reviews for key keywords and their sentiment.
- **Error Handling**: Retries API calls and handles JSON parsing errors gracefully.
- **Keyword Aggregation**: Combines keyword occurrences and sentiment counts across all reviews.
- **Data Visualization**: Outputs results in a tabular format for easy interpretation.

---

## Prerequisites

- Python 3.7 or later
- OpenAI API key
- `dotenv`, `openai`, `pandas`, and `logging` Python libraries

---

## Installation


1. **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2. 2. **Install Dependencies**:
   Install all necessary dependencies using the following command:
   ```bash
   pip install -r requirements.txt
   ```   
3. **Open Terminal or Command Prompt:**
   ```
   Navigate to your project directory where `main.py` is located.
   ```

4. **Set the Directory:**
   If you are not already in the project directory, use the `cd` (change directory) command:
   ```bash
   cd path/to/cd amazon-review-sentiment-analysis/src/amazon_review_sentiment_analysis
    ```
3. **Create a `.env` file in the project directory and add your OpenAI API key:**
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

## Usage

1. Run the script:
    ```bash
    python main.py
    ```
## Example Output

Product Name: Canon EOS Rebel T7 DSLR Camera with 18-55mm Lens ,Built-in Wi-Fi, 24.1 MP CMOS Sensor, DIGIC 4+ Image Processor and Full HD Videos
Number of Reviews: 20

Processing Review 1/20...
Processing Review 2/20...
Processing Review 3/20...
Processing Review 4/20...
Processing Review 5/20...
Processing Review 6/20...
Processing Review 7/20...
Processing Review 8/20...
Processing Review 9/20...
Processing Review 10/20...
Processing Review 11/20...
Processing Review 12/20...
Processing Review 13/20...
Processing Review 14/20...
Processing Review 15/20...
Processing Review 16/20...
Processing Review 17/20...
Processing Review 18/20...
Processing Review 19/20...
Processing Review 20/20...

Aggregated Keyword Sentiment Analysis:
                 Keyword  Positive  Negative  Neutral
60                camera         1         2        3
43            auto focus         0         3        0
87    canon eos rebel t7         0         1        2
22                 price         2         1        0
27              friendly         2         0        0
..                   ...       ...       ...      ...
175            purchased         0         1        0
176           enthusiasm         0         1        0
177              replace         0         1        0
178           sweet deal         0         1        0
179  too good to be true         0         1        0