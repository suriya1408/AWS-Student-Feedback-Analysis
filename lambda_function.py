import json
import os

POSITIVE = {"good", "great", "excellent", "helpful", "clear", "useful", "best", "happy", "nice", "love"}
NEGATIVE = {"bad", "poor", "boring", "difficult", "unclear", "slow", "worst", "unhelpful", "hate", "issue"}

def classify(text):
    words = set(text.lower().replace(".", " ").replace(",", " ").split())
    score = len(words & POSITIVE) - len(words & NEGATIVE)
    if score > 0:
        return "Positive"
    if score < 0:
        return "Negative"
    return "Neutral"

def lambda_handler(event, context):
    body = event.get("body", event)
    if isinstance(body, str):
        body = json.loads(body)
    feedback = body.get("feedback", "")
    sentiment = classify(feedback)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"sentiment": sentiment, "feedback": feedback})
    }
