# Resume Extractor

This project is a Python-based application that extracts structured data from resumes in various file formats (`.doc`, `.docx`, `.pdf`, `.txt`). It uses OpenAI's API to process the extracted text and organize it into predefined categories such as contact information, education, skills, and experience.

---

## Features

- **File Format Support**: Extracts text from `.doc`, `.docx`, `.pdf`, and `.txt` resume files.
- **AI-Powered Processing**: Utilizes OpenAI's API to parse resume text into structured JSON data.
- **Predefined Schema**: Organizes resume details into categories like contact info, education, skills, and work experience.
- **Error Handling**: Logs errors during text extraction and API processing.
- **Logging**: Uses `structlog` for detailed logging of each step in the workflow.

---

## Prerequisites

- Python 3.7 or later
- OpenAI API key
- Required Python packages:
  - `agentifyme`
  - `dotenv`
  - `pydantic`
  - `structlog`
  - `docx`
  - `PyPDF2`

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
   cd path/to/cd resume_extraction/src/resume_extraction
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

```
2024-12-09 16:12:13.794 | INFO     | agentifyme.workflows.workflow:run:78 - Running workflow: Extract Resume Workflow
2024-12-09 16:12:13.857 | INFO     | agentifyme.tasks.task:run:53 - Running task: process_resume_text
{
    "contact": {
        "first_name": "Lavanya",
        "last_name": "Pinnaboina",
        "middle_name": "NA",
        "phone_number": "341-202-6956",
        "email": "lavanya7925@gmail.com",
        "linkedin": "https://www.linkedin.com/in/lavanya-pinnaboina-617831b7/"
    },
    "education": [
        {
            "degree": "Bachelor of Technology",
            "year": "2017",
            "college": "BVRIT, JNTUH"
        }
    ],
    "skills": {
        "programming_languages": [
            "Ruby",
            "Power Shell",
            "Python",
            "Perl",
            "Shell"
        ],
        "frameworks_libraries": [
            "Chef",
            "Puppet",
            "Ansible",
            "Jenkins",
            "Team City",
            "Docker",
            "Maven",
            "Apache ANT"
        ],
        "tools_technologies": [
            "AWS",
            "Terraform",
            "SonarQube",
            "JIRA",
            "Confluence",
            "Git",
            "Bitbucket",
            "TFS",
            "CVS",
            "SVN",
            "Team Foundation Server",
            "JFrog",
            "Nagios",
            "Kubernetes",
            "Tomcat"
        ]
    },
    "experience": [
        {
            "company_client": "BMO Harris Bank",
            "job_role": "DevOps Engineer",
            "summary_of_responsibilities": "Coordinated with resources by working closely with Project Manager for the release and Project Manager for all the Operational Projects. Responsible for defining branching & merging strategy, check-in policies, improving code quality, automated Gated Check-ins, and defining backup and archival plans. Actively involved in the architecture of the DevOps platform and cloud solutions.",
            "place": "Chicago, IL",
            "start_date": "May 2022",
            "end_date": "Till Date"
        },
        {
            "company_client": "Budco Financial",
            "job_role": "DevOps Engineer",
            "summary_of_responsibilities": "Worked on the Microsoft Release management server for maintaining the release management activities. Troubleshoot Build and Deploy Issues, with little downtime.",
            "place": "Detroit, MI",
            "start_date": "Mar 2021",
            "end_date": "Apr 2022"
        },
        {
            "company_client": "Cigna Health Care",
            "job_role": "DevOps/Build-Release Engineer",
            "summary_of_responsibilities": "Participated in the release cycle of the product which involves environments like Development QA UAT and Production. Builds and deploys J2EE application in JBoss using Python scripts.",
            "place": "Denver, CO",
            "start_date": "Oct 2019",
            "end_date": "Feb 2021"
        },
        {
            "company_client": "JC Penney",
            "job_role": "Build-Release Engineer",
            "summary_of_responsibilities": "Worked portal for triggering builds and releasing them to stakeholders by understanding the pain points of Developers and QA engineers. Maintained the FTP server in which the builds were copied.",
            "place": "Plano, TX",
            "start_date": "Jun 2017",
            "end_date": "Sep 2019"
        }
    ]
}
```