import os
import sys
import json
import time
import logging
import signal
import boto3
from datetime import date
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from my_project.database import SessionLocal
from my_project.domain.models import Review, Film, User
from my_project.domain.schemas import ReviewCreate
from my_project.service import review_service
from my_project.service.review_service import (
    FilmNotFoundException,
    UserNotFoundException,
    ReviewExistsException,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-1")

if not SQS_QUEUE_URL:
    logger.error("SQS_QUEUE_URL is not set")
    sys.exit(1)

sqs = boto3.client("sqs", region_name=AWS_REGION)

running = True

def handle_signal(signum, frame):
    global running
    logger.info("Received signal %s — shutting down gracefully", signum)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def process_message(body: dict) -> bool:
    """
    True  - message processed or permanently rejected
    False - temporary error, message should be retried
    """

    db = SessionLocal()

    try:
        review_schema = ReviewCreate.model_validate(body)
        review_service.create_new_review(db, review_schema)

        logger.info(
            "Review created: film=%s, user=%s",
            review_schema.film_id,
            review_schema.user_id,
        )

        return True

    except ValidationError:
        db.rollback()
        logger.exception("Invalid review message — discarding")
        return True

    except (FilmNotFoundException, UserNotFoundException) as e:
        db.rollback()
        logger.warning("Permanent review rejection: %s", e)
        return True

    except ReviewExistsException:
        db.rollback()
        logger.info("Review already exists — treating as successful")
        return True

    except IntegrityError:
        db.rollback()

        try:
            review_schema = ReviewCreate.model_validate(body)
            existing = db.get(
                Review,
                (review_schema.film_id, review_schema.user_id),
            )

            if existing is not None:
                logger.info("Duplicate review detected — treating as success")
                return True

        except Exception:
            logger.exception("Could not verify duplicate review")

        logger.exception("Database integrity error")
        return False

    except Exception:
        db.rollback()
        logger.exception("Temporary error processing review")
        return False

    finally:
        db.close()

def main():
    logger.info("Worker started — polling %s", SQS_QUEUE_URL)

    while running:
        try:
            response = sqs.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
                VisibilityTimeout=30,
            )

            messages = response.get("Messages", [])

            for msg in messages:
                receipt_handle = msg["ReceiptHandle"]
                try:
                    body = json.loads(msg["Body"])
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in message %s — discarding", msg["MessageId"])
                    sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
                    continue

                success = process_message(body)

                if success:
                    sqs.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
                    logger.info("Deleted message %s from queue", msg["MessageId"])
                else:
                    logger.warning(
                        "Message %s will return to queue after visibility timeout",
                        msg["MessageId"],
                    )

        except Exception as e:
            logger.exception("Error polling SQS: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()

