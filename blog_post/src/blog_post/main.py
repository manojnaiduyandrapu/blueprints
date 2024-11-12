import os
import openai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=".env")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_user_input(prompt_text, required=True):
    while True:
        user_input = input(prompt_text).strip()
        if required and not user_input:
            print("This field is required. Please provide a valid input.")
        else:
            return user_input

def construct_prompt(title, keywords, audience, tone):
    prompt = f"""
You are an expert blog writer. Write a comprehensive blog post based on the following details:

Title: {title}
Keywords: {keywords}
Audience: {audience}
Tone: {tone}

Requirements:
- Include an engaging introduction.
- Divide the content into logical sections with clear headings.
- Provide actionable insights or takeaways.
- Conclude with a summary or call-to-action.
- Use SEO best practices, including the use of provided keywords naturally.
"""
    return prompt

def generate_blog_post(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert blog writer."},
                {"role": "user", "content": prompt},
            ],
        )
        blog_content = response['choices'][0]['message']['content'].strip()
        return blog_content
    except openai.error.OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

def main():
    print("=== AI Blog Post Generator ===\n")

    if not openai.api_key:
        print("API key not found. Please set your API key in the .env file.")
        return

    title = get_user_input("Enter the blog post title: ")
    keywords = get_user_input("Enter some keywords (comma-separated): ")
    audience = get_user_input("Describe your target audience: ")
    tone = get_user_input("What tone would you like? (e.g., formal, casual): ")

    prompt = construct_prompt(title, keywords, audience, tone)

    print("\nGenerating blog post... Please wait.\n")

    blog_content = generate_blog_post(prompt)

    if blog_content:
        print("\n=== ✅ Blog post generated ===\n")
        print(blog_content)
    else:
        print("❌ Failed to generate blog post.")

if __name__ == "__main__":
    main()
