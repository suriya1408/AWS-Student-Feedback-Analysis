# Cloud-Based Student Feedback Analysis System (AWS)

A small portfolio project for demonstrating a cloud-hosted feedback application. It accepts student feedback, classifies sentiment, and displays a dashboard.

## Features
- Flask web application and dashboard
- Positive / Neutral / Negative sentiment classification
- Local demo mode (works without AWS credentials)
- AWS S3 JSON record upload
- AWS DynamoDB record storage
- AWS Lambda sentiment function
- Designed to be hosted on an AWS EC2 Linux instance
- Optional SageMaker endpoint integration can be added as an advanced extension

## 1. Run locally in VS Code

Open this folder in VS Code. In the terminal:

### Windows PowerShell
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\\Scripts\\Activate.ps1
```

Open http://127.0.0.1:5000

Submit a few sample feedback records:
- "The class was excellent and very helpful"
- "The explanation was unclear and boring"
- "The course was okay"

The application stores demo records in `feedback_local.json`.

## 2. Configure AWS

Create an AWS account only if you have permission and can monitor costs. Do not publish AWS access keys or commit them to GitHub.

Create:
1. An S3 bucket, for example `your-unique-feedback-bucket`
2. A DynamoDB table named `StudentFeedback`, with partition key `feedback_id` (String)
3. A Lambda function using `lambda_function.py` as its code, runtime Python 3.12, handler `lambda_function.lambda_handler`

Deploy Lambda:
- Create a ZIP containing `lambda_function.py`
- Upload it to Lambda
- Set handler to `lambda_function.lambda_handler`
- Copy the function name

Configure `.env`:
```env
AWS_REGION=ap-south-1
S3_BUCKET=your-unique-feedback-bucket
DDB_TABLE=StudentFeedback
LAMBDA_NAME=your-lambda-function-name
FLASK_SECRET_KEY=use-a-long-random-value
```

Set up AWS credentials using an approved IAM role or AWS CLI profile. For local development, `aws configure` can set up a profile. Never paste credentials into source code.

The identity used by the app needs:
- `s3:PutObject` on the chosen bucket
- `dynamodb:PutItem` and `dynamodb:Scan` on the table
- `lambda:InvokeFunction` on the Lambda function

For a real deployment, use least-privilege IAM policies and avoid public access to the S3 bucket.

## 3. AWS EC2 deployment (optional)

Launch a small Amazon Linux EC2 instance only if your account has access and you understand the charges. Attach an IAM role with the permissions above. Configure the security group to allow HTTP traffic only as needed. Connect using SSH, install Python and Git, copy the project, install requirements, and run the Flask app behind a production WSGI server such as Gunicorn. Do not expose Flask debug mode to the public internet.

For a quick demonstration, local mode is sufficient; clearly label it as a local prototype until AWS resources are actually connected.

## 4. SageMaker extension (optional)

The current project uses a transparent keyword-based sentiment classifier in Lambda. SageMaker is not required for the core demo. For an advanced ML version, deploy a text-classification model to a SageMaker real-time endpoint and have Lambda call `sagemaker-runtime:InvokeEndpoint`. This can incur charges, so do not deploy an endpoint just for a short demo unless your instructor/company specifically requires it.

## Architecture

Student browser -> Flask application on EC2 -> AWS Lambda (sentiment analysis)
                                          -> DynamoDB (structured feedback)
                                          -> S3 (JSON feedback archive)

## Important project explanation

This is a prototype. The included classifier is a simple keyword-based demonstration, not a trained AI model. SageMaker is an optional extension and should not be claimed as implemented unless you deploy and test an endpoint.
