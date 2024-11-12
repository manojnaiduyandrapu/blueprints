# generate_email.py

import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

def get_user_input(prompt_text, required=True):
    """
    Prompt the user for input and ensure required fields are not empty.
    """
    while True:
        user_input = input(prompt_text).strip()
        if required and not user_input:
            print("This field is required. Please provide a valid input.")
        else:
            return user_input

def get_recipient_details():
    """
    Gather detailed information about the email recipient.
    """
    print("\nPlease provide details about the email recipient:")
    name = get_user_input("Recipient's Name: ")
    relationship = get_user_input("Your relationship with the recipient (e.g., colleague, client, friend): ")
    purpose = get_user_input("Purpose of the email (e.g., follow-up, introduction, invitation): ")
    tone = get_tone()
    return {
        "name": name,
        "relationship": relationship,
        "purpose": purpose,
        "tone": tone
    }

def get_tone():
    """
    Allow the user to select a tone for the email from predefined options.
    """
    tones = ["Formal", "Informal", "Friendly", "Professional", "Persuasive"]
    print("\nSelect the desired tone for your email:")
    for idx, tone in enumerate(tones, start=1):
        print(f"{idx}. {tone}")
    
    while True:
        choice = get_user_input("Enter the number corresponding to your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(tones):
            return tones[int(choice)-1].lower()
        else:
            print(f"Please enter a number between 1 and {len(tones)}.")

def construct_prompt(recipient, subject, additional_info=""):
    """
    Construct the prompt to send to OpenAI based on user inputs.
    """
    prompt = f"""You are an expert email writer. Write a personalized email based on the following details:

Recipient's Name: {recipient['name']}
Relationship: {recipient['relationship']}
Purpose: {recipient['purpose']}
Tone: {recipient['tone']}

Subject: {subject}

{additional_info}

Requirements:
- Address the recipient by name.
- Keep the email concise and to the point.
- Maintain the specified tone throughout.
- Include a clear call-to-action if applicable.
"""
    return prompt

def generate_email(prompt):
    """
    Generate the email content using OpenAI's API.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert email writer."},
                {"role": "user", "content": prompt},
            ],
        )
        email_content = response['choices'][0]['message']['content'].strip()
        return email_content
    except openai.error.OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def main():
    print("=== AI Personalized Email Generator ===\n")
    
    # Gather recipient details
    recipient = get_recipient_details()
    
    # Gather email subject
    subject = get_user_input("\nEnter the email subject: ")
    
    # Optional: Gather additional information or context
    additional_info = get_user_input("\nAny additional information or context to include? (Press Enter to skip): ", required=False)
    
    # Construct the prompt
    prompt = construct_prompt(recipient, subject, additional_info)
    
    print("\nGenerating email... Please wait.\n")
    
    # Generate the email content
    email_content = generate_email(prompt)
    
    if email_content:
        print("\nGenerated Email Content:\n")
        print(email_content)
    else:
        print("❌ Failed to generate the email.")

if __name__ == "__main__":
    main()
