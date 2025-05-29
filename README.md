# Resume Shortlisting System Using NLP

## Overview

This application is a comprehensive solution for parsing resumes, managing candidate information, and shortlisting candidates based on job descriptions. It features:

- Resume parsing (PDF, DOCX, DOC, TXT)
- Candidate profile management
- Job description storage
- AI-powered candidate shortlisting
- Cloud storage integration (AWS S3)

## Functionalities

### Core Features
- **Resume Upload & Parsing**: Extract candidate information from resumes
- **Candidate Dashboard**: View and manage all candidates
- **Job Description Management**: Store and manage job descriptions
- **Smart Shortlisting**: Automatically rank candidates based on job requirements
- **Candidate Profiles**: Detailed view of each candidate's information

### Technical Features
- Flask backend with SQLAlchemy ORM
- AWS S3 integration for resume storage
- NLP-based candidate ranking
- Responsive Bootstrap frontend



## Setup Instructions

### Prerequisites

* Python 3.8+
* PostgreSQL
* AWS account (for S3 storage)
* Git

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/priyan-09/resume-shortlisting-system.git
   cd resume-parser
   ```

2. **Create PostgreSQL Database Using Schema File**:

   * Open **pgAdmin** or any PostgreSQL client
   * Create a new empty database
   * Open the `schema.sql` file located in the repository
   * Run the SQL script on the newly created database to create all required tables and relationships

3. **Create and activate virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Create `.env` file**:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your configuration:

   ```
   # Database
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_db_name

   # AWS S3
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   S3_BUCKET_NAME=your-bucket-name
   S3_REGION=your-region





### Running the Application

1. **Development server**:
    Inside you project directory with all the required files run command:
    ```bash
   python run.py
   ```

2. **Access the application**:
   Open `http://localhost:5000` in your browser

## Usage Guide

### Basic Workflow

1. **Upload Resumes**:
   - Navigate to the homepage
   - Upload resume files (PDF/DOCX/DOC/TXT)
   - System will parse and store candidate information

2. **View Candidates**:
   - Go to `/candidates`
   - View list of all candidates
   - Click on any candidate to see detailed profile

3. **Create Job Description**:
   - Go to `/job_descriptions`
   - Click "Shortlist Candidates"
   - Enter job description text

4. **Shortlist Candidates**:
   - System will automatically rank candidates
   - Top 10% candidates will be shortlisted
   - View shortlisted candidates for each job description

### Advanced Features

- **Resume Storage**: All resumes are stored in AWS S3
- **Candidate Search**: Filter candidates by skills or experience
- **Profile Management**: Edit candidate information if needed




## Contact

Priyanka Gaikwad- priyanka.gaikwad22@vit.edu
