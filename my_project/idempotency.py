from functools import wraps
from flask import request, jsonify, make_response
from redis.exceptions import RedisError
import json

from my_project.cache import redis_client

IDEMPOTENCY_TTL = 60 * 60 * 24


def idempotent(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    idem_key = request.headers.get("Idempotency-Key")

    if not idem_key:
      return jsonify({"error": "Idempotency-Key is required"}), 400

    if redis_client is None:
      return jsonify({"error": "Redis is unavailable"}), 503

    redis_key = f"idempotency:{idem_key}"

    try:
      cached_data = redis_client.get(redis_key)

      if cached_data:
        data = json.loads(cached_data)

        response = make_response(
          data["body"],
          data["status_code"]
        )
        response.headers["Content-Type"] = "application/json"
        response.headers["X-Idempotency"] = "HIT"

        return response

      response = make_response(f(*args, **kwargs))

      if response.status_code in (200, 201, 202):
        cache_payload = {
          "body": response.get_data(as_text=True),
          "status_code": response.status_code
        }

        redis_client.setex(
          redis_key,
          IDEMPOTENCY_TTL,
          json.dumps(cache_payload)
        )

      return response

    except (RedisError, json.JSONDecodeError):
      return jsonify({"error": "Idempotency storage unavailable"}), 503

  return decorated_function