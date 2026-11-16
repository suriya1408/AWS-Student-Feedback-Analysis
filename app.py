
import os
import json
import uuid
import boto3

from datetime import datetime, timezone
from decimal import Decimal
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "student-feedback-secret")

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
S3_BUCKET = os.getenv("S3_BUCKET", "")
DDB_TABLE = os.getenv("DDB_TABLE", "")
LAMBDA_NAME = os.getenv("LAMBDA_NAME", "")

LOCAL_FILE = "feedback_local.json"

# AWS connections
try:
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=AWS_REGION
    )
    table = dynamodb.Table(DDB_TABLE) if DDB_TABLE else None

    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION
    )

    lambda_client = boto3.client(
        "lambda",
        region_name=AWS_REGION
    )

except Exception as exc:
    app.logger.warning("AWS connection setup failed: %s", exc)
    table = None
    s3 = None
    lambda_client = None


# Sentiment analysis
def analyse_feedback(feedback):
    text = feedback.lower()

    positive_words = [
        "good", "excellent", "great", "helpful",
        "nice", "best", "clear", "awesome",
        "happy", "satisfied"
    ]

    negative_words = [
        "bad", "poor", "worst", "difficult",
        "confusing", "boring", "slow",
        "unhappy", "unsatisfied"
    ]

    positive = sum(word in text for word in positive_words)
    negative = sum(word in text for word in negative_words)

    if positive > negative:
        return "Positive"
    elif negative > positive:
        return "Negative"
    else:
        return "Neutral"


# Local JSON storage
def load_local_feedback():
    if not os.path.exists(LOCAL_FILE):
        return []

    try:
        with open(LOCAL_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        app.logger.warning("Could not read local feedback file.")
        return []


def save_local_feedback(record):
    records = load_local_feedback()
    records.append(record)

    with open(LOCAL_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)


# Save feedback to DynamoDB
def save_to_dynamodb(record):
    if table is None:
        return False

    try:
        item = dict(record)

        # Required partition key in your DynamoDB table
        item["StudentFeedback"] = record["feedback_id"]

        table.put_item(Item=item)
        app.logger.info("Feedback saved to DynamoDB.")
        return True

    except Exception as exc:
        app.logger.warning("DynamoDB save failed: %s", exc)
        return False


# Save feedback JSON to S3
def save_to_s3(record):
    if not S3_BUCKET or s3 is None:
        return False

    try:
        object_key = "feedback/" + record["feedback_id"] + ".json"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=object_key,
            Body=json.dumps(record),
            ContentType="application/json"
        )

        app.logger.info("Feedback uploaded to S3.")
        return True

    except Exception as exc:
        app.logger.warning("S3 save failed: %s", exc)
        return False


# Optional Lambda sentiment processing
def analyse_with_lambda(feedback):
    if not LAMBDA_NAME or lambda_client is None:
        return None

    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps({"feedback": feedback})
        )

        result = json.loads(response["Payload"].read())

        if "sentiment" in result:
            return result["sentiment"]

    except Exception as exc:
        app.logger.warning("Lambda invocation failed: %s", exc)

    return None


# Save one feedback record
def save_feedback(record):
    # Always save locally as backup
    try:
        save_local_feedback(record)
    except Exception as exc:
        app.logger.warning("Local save failed: %s", exc)

    # Save to AWS services
    save_to_dynamodb(record)
    save_to_s3(record)


# Load feedback from DynamoDB
def load_feedback():
    if table is not None:
        try:
            response = table.scan()
            records = response.get("Items", [])

            while "LastEvaluatedKey" in response:
                response = table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                records.extend(response.get("Items", []))

            if records:
                return sorted(
                    records,
                    key=lambda item: item.get("created_at", ""),
                    reverse=True
                )

        except Exception as exc:
            app.logger.warning("DynamoDB read failed: %s", exc)

    # Use local records if DynamoDB has no records or is unavailable
    return list(reversed(load_local_feedback()))


# Main website
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        student = request.form.get("student", "").strip()
        course = request.form.get("course", "").strip()
        feedback = request.form.get("feedback", "").strip()

        if not student or not course or not feedback:
            flash("Please complete all fields.", "error")
            return redirect(url_for("index"))

        feedback_id = str(uuid.uuid4())

        sentiment = analyse_feedback(feedback)

        # Use Lambda result if Lambda is configured and returns one
        lambda_sentiment = analyse_with_lambda(feedback)
        if lambda_sentiment in ["Positive", "Neutral", "Negative"]:
            sentiment = lambda_sentiment

        record = {
            "StudentFeedback": feedback_id,
            "feedback_id": feedback_id,
            "student": student,
            "course": course,
            "feedback": feedback,
            "sentiment": sentiment,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        save_feedback(record)

        flash("Feedback submitted successfully!", "success")
        return redirect(url_for("index"))

    records = load_feedback()

    counts = {
        "Positive": 0,
        "Neutral": 0,
        "Negative": 0
    }

    for item in records:
        label = item.get("sentiment", "Neutral")
        counts[label] = counts.get(label, 0) + 1

    return render_template(
        "index.html",
        records=records,
        counts=counts,
        total=len(records)
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )
