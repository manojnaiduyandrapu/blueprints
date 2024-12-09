# AI Personalized Email

This project is a command-line application to generate personalized email content using OpenAI's GPT model. The app takes input details such as the recipient's name, relationship, purpose of the email, tone, and subject, and produces a customized email tailored to the specified requirements.

## Features

- **Customizable Input Fields**: Specify recipient details, relationship, purpose, and tone.
- **Predefined Tones**: Choose from options like Formal, Informal, Friendly, Professional, and Persuasive.
- **Concise and Targeted Emails**: Emails are concise, to the point, and include clear calls-to-action where applicable.
- **Uses OpenAI GPT Models**: Leverages OpenAI's powerful API for generating high-quality email content.

## Prerequisites

- Python 3.7 or later
- An OpenAI API key
- `dotenv` and `openai` Python packages

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
   cd path/to/cd personalized_email/src/personalized_email
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

2. Follow the on-screen prompts:
   - Enter the recipient's name, your relationship, the purpose of the email, and the tone.
   - Provide the subject line and any additional context (optional).

3. Wait for the application to generate the email content and display it on the console.

## Example Output

**Input:**
- Recipient's Name: Akhil Simha
- Relationship: Academic Mentor
- Purpose: Request for recommendation letter
- Tone: Formal
- Subject: Request for a Recommendation Letter
- Additional Information: The recommendation is for a graduate school application.The deadline for submission is December 15th.The specific program is the "M.S. in Artificial Intelligence" at Stanford University.Include a reference to previous projects worked on together, specifically the "AI Ethics Research Paper."

**Generated Email:**

Subject: Request for a Recommendation Letter

Dear Akhil Simha,

I hope this message finds you well. I am writing to request a letter of recommendation for my application to the M.S. in Artificial Intelligence program at Stanford University. The deadline for submission is December 15th.

Reflecting on our collaboration on the "AI Ethics Research Paper," I believe that your insights into my work and our discussions on ethical considerations in artificial intelligence would provide a valuable perspective to my application. Your mentorship has been instrumental in shaping my academic journey, and I would be honored to have your support as I take this next step.

If you are willing and able to assist me with this request, please let me know, and I can provide any additional details you may need. 

Thank you very much for considering my request. I truly appreciate your time and support.

Warm regards,

[Your Name]  
[Your Contact Information]  
[Your University/Program]

