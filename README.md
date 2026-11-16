# Cloud-Based Student Feedback Analysis System Using AWS

A portfolio project demonstrating a cloud-integrated student feedback application. The system collects student feedback, classifies its sentiment, and displays the results through a web-based dashboard using AWS services.

## Features

- Flask-based web application and dashboard.
- Positive, Neutral, and Negative sentiment classification.
- Local demo mode that works without AWS credentials.
- Amazon S3 integration for JSON feedback archives.
- Amazon DynamoDB integration for structured feedback storage.
- AWS Lambda function for sentiment analysis.
- CloudWatch integration for monitoring Lambda execution.
- Designed for deployment on an AWS EC2 Linux instance.
- Optional Amazon SageMaker integration as a future enhancement.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | Web application framework |
| HTML and CSS | User interface |
| AWS Lambda | Sentiment processing |
| Amazon DynamoDB | Feedback data storage |
| Amazon S3 | JSON archive storage |
| Amazon CloudWatch | Execution monitoring |
| Boto3 | AWS integration |

## 1. Running the Project Locally

### Prerequisites

- Python installed on your system.
- Git installed.
- Visual Studio Code (recommended).

### Setup Instructions

Clone the repository:

```bash
git clone https://github.com/suriya1408/AWS-Student-Feedback-Analysis.git
```

Navigate to the project directory:

```bash
cd AWS-Student-Feedback-Analysis
```

Create a virtual environment:

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

Create your environment configuration file:

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables and run the application:

```powershell
python app.py
```

Open the application in your browser:

`http://127.0.0.1:5000`

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Sample Feedback

Try submitting the following feedback:

- "The class was excellent and very helpful."
- "The explanation was unclear and boring."
- "The course was okay."

In local demo mode, feedback records are stored in `feedback_local.json`.

## 2. AWS Cloud Integration

The application integrates multiple AWS services to support feedback processing and storage.

### AWS Services Used

**Amazon S3**

Stores JSON archives of submitted feedback.

**Amazon DynamoDB**

Maintains structured feedback records, including sentiment results.

**AWS Lambda**

Processes feedback and performs sentiment classification using predefined keyword-based rules.

**Amazon CloudWatch**

Records Lambda execution logs and helps monitor the serverless function.

### AWS Configuration

The project uses the following configuration:

| Configuration | Value |
|---|---|
| AWS Region | `ap-southeast-2` |
| DynamoDB Table | `StudentFeedback` |
| Lambda Function | `student-feedback-sentiment` |
| S3 Bucket | Configured using environment variables |

### Environment Variables

Configure the following values in your local `.env` file:

```env
AWS_REGION=ap-southeast-2
S3_BUCKET=your-unique-feedback-bucket
DDB_TABLE=StudentFeedback
LAMBDA_NAME=student-feedback-sentiment
FLASK_SECRET_KEY=your-long-random-secret
```

Replace the S3 bucket name with your actual bucket name.

### AWS Permissions

The application's AWS identity requires appropriate permissions for:

- `s3:PutObject` – Uploading feedback archives.
- `dynamodb:PutItem` – Storing feedback records.
- `dynamodb:Scan` – Reading feedback records.
- `lambda:InvokeFunction` – Invoking the sentiment analysis function.

For deployment, use an IAM role with least-privilege permissions. Keep S3 buckets private and never publish AWS access keys or secret credentials.

## 3. System Architecture

The application follows a cloud-integrated architecture in which the Flask web application communicates with AWS services.

### Workflow

Student Browser  
↓  
Flask Web
