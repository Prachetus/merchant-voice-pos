import json
import os
import re
from datetime import datetime, timedelta, timezone
from difflib import get_close_matches
from typing import Any

import requests
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import ensure_indexes, get_database, seed_default_data
from backend_models import create_transaction, generate_receipt


load_dotenv()

DEFAULT_INVENTORY = [
    {"name": "milk", "displayName": "Milk", "unit": "l", "stock": 50, "reorderLevel": 12, "aliases": ["packet of milk", "milk packet", "milk"]},
    {"name": "bread", "displayName": "Bread", "unit": "loaf", "stock": 30, "reorderLevel": 6, "aliases": ["loaf of bread", "bread loaf"]},
    {"name": "sugar", "displayName": "Sugar", "unit": "kg", "stock": 100, "reorderLevel": 20, "aliases": ["packet of sugar", "sugar"]},
    {"name": "rice", "displayName": "Rice", "unit": "kg", "stock": 200, "reorderLevel": 40, "aliases": ["kilograms of rice", "rice"]},
    {"name": "water", "displayName": "Water", "unit": "bottle", "stock": 60, "reorderLevel": 12, "aliases": ["bottle of water", "water"]},
    {"name": "biscuits", "displayName": "Biscuits", "unit": "packet", "stock": 120, "reorderLevel": 24, "aliases": ["packet of biscuits", "biscuits"]},
    {"name": "soap", "displayName": "Soap", "unit": "bar", "stock": 75, "reorderLevel": 15, "aliases": ["bar of soap", "soap"]},
    {"name": "toothpaste", "displayName": "Toothpaste", "unit": "tube", "stock": 40, "reorderLevel": 10, "aliases": ["tube of toothpaste", "toothpaste"]},
]

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
}

UNIT_ALIASES = {
    "kg": "kg",
    "kgs": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "l": "l",
    "litre": "l",
    "litres": "l",
    "liter": "l",
    "liters": "l",
    "ml": "ml",
    "millilitre": "ml",
    "millilitres": "ml",
    "packet": "packet",
    "packets": "packet",
    "piece": "piece",
    "pieces": "piece",
    "bottle": "bottle",
    "bottles": "bottle",
    "box": "box",
    "boxes": "box",
    "loaf": "loaf",
    "loaves": "loaf",
    "dozen": "dozen",
    "tube": "tube",
    "tubes": "tube",
    "bar": "bar",
    "bars": "bar",
    "can": "can",
    "cans": "can",
    "bundle": "bundle",
    "bundles": "bundle",
}

ACTION_WORDS = {
    "add": "add",
    "restock": "add",
    "increase": "add",
    "top up": "add",
    "top-up": "add",
    "remove": "remove",
    "sell": "remove",
    "dispatch": "remove",
    "deduct": "remove",
    "decrease": "remove",
    "take": "remove",
    "set": "set",
}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
    if not jwt_secret_key or jwt_secret_key == "change-me-in-prod":
        raise RuntimeError("JWT_SECRET_KEY must be set to a strong random value before starting the API")

    app.config["JWT_SECRET_KEY"] = jwt_secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=int(os.getenv("JWT_ACCESS_TOKEN_DAYS", "7")))
    app.config["JSON_AS_ASCII"] = False

    cors_env_value = os.environ.get("CORS_ORIGINS")
    cors_value = (cors_env_value or "http://localhost:3000").strip()
    cors_origins = [origin.strip() for origin in cors_value.split(",") if origin.strip()]
    if os.getenv("FLASK_DEBUG", "0") != "1" and not cors_env_value:
        raise RuntimeError("CORS_ORIGINS must be explicitly configured for production deployments")

    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)
    JWTManager(app)

    db = get_database()
    try:
        db.client.admin.command("ping")
    except Exception as exc:
        raise RuntimeError("MongoDB is unavailable") from exc
    ensure_indexes(db)
    seed_default_data(db, DEFAULT_INVENTORY)

    @app.get("/")
    def home() -> tuple[dict[str, Any], int]:
        return {
            "name": "Merchant Voice POS API",
            "status": "ok",
            "version": "1.0.0",
            "endpoints": ["/api/health", "/api/auth/register", "/api/auth/login", "/api/inventory", "/api/voice/parse"],
        }, 200

    @app.get("/api/health")
    def health() -> tuple[dict[str, Any], int]:
        try:
            db.client.admin.command("ping")
            mongo_status = "ok"
            status_code = 200
        except Exception:
            mongo_status = "down"
            status_code = 503

        return {"status": "ok" if status_code == 200 else "degraded", "service": "merchant-voice-pos", "mongo": mongo_status}, status_code

    @app.post("/api/auth/register")
    def register() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
        name = str(payload.get("name", "")).strip()
        store_name = str(payload.get("storeName", "")).strip()

        if not email or not password or len(password) < 8:
            return {"error": "name, email, and password (min 8 chars) are required"}, 400

        if db.users.find_one({"email": email}):
            return {"error": "Unable to create account. Please try again."}, 400

        now = datetime.now(timezone.utc)
        user_doc = {
            "name": name or email.split("@")[0],
            "storeName": store_name or f"{name or email.split('@')[0]}'s Store",
            "email": email,
            "passwordHash": generate_password_hash(password),
            "role": payload.get("role", "merchant"),
            "createdAt": now,
            "lastLoginAt": now,
        }
        result = db.users.insert_one(user_doc)
        token = create_access_token(identity=str(result.inserted_id), additional_claims={"email": email, "name": user_doc["name"]})
        return {"user": serialize_document({**user_doc, "_id": result.inserted_id}), "token": token}, 201

    @app.post("/api/auth/login")
    def login() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))

        user = db.users.find_one({"email": email})
        if not user or not check_password_hash(user.get("passwordHash", ""), password):
            return {"error": "Invalid email or password"}, 401

        db.users.update_one({"_id": user["_id"]}, {"$set": {"lastLoginAt": datetime.now(timezone.utc)}})
        token = create_access_token(identity=str(user["_id"]), additional_claims={"email": user["email"], "name": user.get("name")})
        return {"user": serialize_document(user), "token": token}, 200

    @app.get("/api/auth/me")
    @jwt_required()
    def me() -> tuple[dict[str, Any], int]:
        user = get_current_user(db)
        if not user:
            return {"error": "User not found"}, 404
        return {"user": serialize_document(user)}, 200

    @app.get("/api/inventory")
    @jwt_required()
    def inventory_list() -> tuple[dict[str, Any], int]:
        query = str(request.args.get("q", "")).strip().lower()
        if query:
            cursor = db.inventory.find({"$or": [{"name": {"$regex": query, "$options": "i"}}, {"displayName": {"$regex": query, "$options": "i"}}, {"aliases": {"$regex": query, "$options": "i"}}]})
        else:
            cursor = db.inventory.find({})
        items = [serialize_document(item) for item in cursor.sort("updatedAt", -1)]
        return {"items": items}, 200

    @app.post("/api/inventory")
    @jwt_required()
    def create_inventory_item() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        name = str(payload.get("name", "")).strip().lower()
        if not name:
            return {"error": "name is required"}, 400

        now = datetime.now(timezone.utc)
        record = {
            "name": name,
            "displayName": str(payload.get("displayName") or name.title()).strip(),
            "unit": normalize_unit(payload.get("unit", "piece")),
            "stock": float(payload.get("stock", 0)),
            "reorderLevel": float(payload.get("reorderLevel", 10)),
            "aliases": [str(alias).strip().lower() for alias in payload.get("aliases", []) if str(alias).strip()],
            "category": str(payload.get("category", "general")).strip().lower(),
            "createdAt": now,
            "updatedAt": now,
        }
        result = db.inventory.insert_one(record)
        return {"item": serialize_document({**record, "_id": result.inserted_id})}, 201

    @app.patch("/api/inventory/<item_id>")
    @jwt_required()
    def update_inventory_item(item_id: str) -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        try:
            object_id = ObjectId(item_id)
        except Exception:
            return {"error": "Invalid item id"}, 400

        update_fields: dict[str, Any] = {"updatedAt": datetime.now(timezone.utc)}
        for field in ["displayName", "name", "stock", "reorderLevel", "category"]:
            if field in payload:
                update_fields[field] = payload[field]
        if "unit" in payload:
            update_fields["unit"] = normalize_unit(payload.get("unit"))
        if "aliases" in payload:
            update_fields["aliases"] = [str(alias).strip().lower() for alias in payload.get("aliases", []) if str(alias).strip()]

        result = db.inventory.update_one({"_id": object_id}, {"$set": update_fields})
        if result.matched_count == 0:
            return {"error": "Item not found"}, 404

        item = db.inventory.find_one({"_id": object_id})
        return {"item": serialize_document(item)}, 200

    @app.delete("/api/inventory/<item_id>")
    @jwt_required()
    def delete_inventory_item(item_id: str) -> tuple[dict[str, Any], int]:
        try:
            object_id = ObjectId(item_id)
        except Exception:
            return {"error": "Invalid item id"}, 400
        result = db.inventory.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            return {"error": "Item not found"}, 404
        return {"status": "deleted"}, 200

    @app.post("/api/voice/parse")
    @jwt_required()
    def parse_voice() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        spoken_text = str(payload.get("text", "")).strip()
        if not spoken_text:
            return {"error": "text is required"}, 400
        return {"result": parse_voice_command(spoken_text, db)}, 200

    @app.post("/api/voice/commit")
    @jwt_required()
    def commit_voice() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        spoken_text = str(payload.get("text", "")).strip()
        if not spoken_text:
            return {"error": "text is required"}, 400

        parsed = parse_voice_command(spoken_text, db)
        item = resolve_inventory_item(db, parsed.get("itemName", ""))
        if not item:
            return {"error": "No matching inventory item found", "parsed": parsed}, 404

        quantity = float(parsed.get("quantity", 1) or 1)
        action = parsed.get("action", "remove")
        direction = 1 if action in {"add", "restock", "increase", "set"} else -1
        delta = quantity * direction
        unit = normalize_unit(parsed.get("unit", item.get("unit", "piece")))

        now = datetime.now(timezone.utc)
        updated = db.inventory.find_one_and_update(
            {"_id": item["_id"]},
            {"$inc": {"stock": delta}, "$set": {"updatedAt": now}},
            return_document=True,
        )
        db.voice_events.insert_one(
            {
                "text": spoken_text,
                "parsed": parsed,
                "itemId": item["_id"],
                "createdAt": now,
            }
        )
        return {
            "status": "success",
            "parsed": parsed,
            "item": serialize_document(updated),
            "message": f"Applied {delta:+g} {unit} to {updated.get('displayName') or updated.get('name')}",
        }, 200

    @app.post("/api/pos/checkout")
    @jwt_required()
    def pos_checkout() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}
        lines = payload.get("lines") or []
        total = payload.get("total")
        if not lines or total is None:
            return {"error": "lines and total are required"}, 400

        user = get_current_user(db)
        if not user:
            return {"error": "unauthorized"}, 401

        tx = {
            "storeId": payload.get("storeId"),
            "userId": str(user.get("_id")),
            "lines": lines,
            "total": total,
            "paymentMethod": "cash",
        }

        try:
            created = create_transaction(db, tx)
            receipt = generate_receipt(created)
            # serialize id and createdAt
            created_serialized = serialize_document(created)
            return {"transaction": created_serialized, "receipt": receipt}, 201
        except Exception as exc:
            return {"error": str(exc)}, 500

    return app


def get_current_user(db):
    try:
        user_id = get_jwt_identity()
        return db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def serialize_document(document: dict[str, Any] | None) -> dict[str, Any]:
    if not document:
        return {}
    serialized: dict[str, Any] = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.astimezone(timezone.utc).isoformat()
        else:
            serialized[key] = value
    return serialized


def normalize_unit(value: Any) -> str:
    raw = str(value or "piece").strip().lower()
    return UNIT_ALIASES.get(raw, raw)


def parse_number_phrase(text: str) -> float | None:
    if not text:
        return None
    compact = text.strip().lower().replace("-", " ")
    if compact.replace(".", "", 1).isdigit():
        return float(compact)

    parts = [part for part in compact.split() if part not in {"and", "a", "an", "of"}]
    total = 0
    current = 0
    matched = False
    for part in parts:
        if part.isdigit():
            current += int(part)
            matched = True
        elif part in NUMBER_WORDS:
            matched = True
            number = NUMBER_WORDS[part]
            if number == 100 and current:
                current *= 100
            elif number == 100:
                current = 100
            else:
                current += number
        elif part == "half":
            matched = True
            current += 0.5
    total += current
    return float(total) if matched else None


def resolve_inventory_item(db, item_name: str) -> dict[str, Any] | None:
    search_term = str(item_name or "").strip().lower()
    if not search_term:
        return None

    exact = db.inventory.find_one({"$or": [{"name": search_term}, {"displayName": {"$regex": f"^{re.escape(search_term)}$", "$options": "i"}}]})
    if exact:
        return exact

    partial = db.inventory.find_one({"$or": [{"name": {"$regex": search_term, "$options": "i"}}, {"displayName": {"$regex": search_term, "$options": "i"}}, {"aliases": {"$regex": search_term, "$options": "i"}}]})
    if partial:
        return partial

    items = list(db.inventory.find({}, {"name": 1, "displayName": 1, "aliases": 1}))
    candidates: list[str] = []
    lookup: dict[str, dict[str, Any]] = {}
    for item in items:
        names = [item.get("name", ""), item.get("displayName", ""), *(item.get("aliases") or [])]
        for name in names:
            normalized = str(name).strip().lower()
            if normalized:
                candidates.append(normalized)
                lookup[normalized] = item

    match = get_close_matches(search_term, candidates, n=1, cutoff=0.6)
    if match:
        matched_item = lookup.get(match[0])
        if matched_item:
            return db.inventory.find_one({"_id": matched_item["_id"]})
    return None


def parse_voice_command(text: str, db) -> dict[str, Any]:
    llm_result = parse_with_llm(text)
    if llm_result:
        llm_result["itemName"] = llm_result.get("itemName") or llm_result.get("item") or ""
        llm_result["unit"] = normalize_unit(llm_result.get("unit", "piece"))
        if "quantity" in llm_result:
            try:
                llm_result["quantity"] = float(llm_result["quantity"])
            except Exception:
                llm_result["quantity"] = 1
        return llm_result

    return parse_voice_command_locally(text, db)


def parse_with_llm(text: str) -> dict[str, Any] | None:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    if not api_key or not base_url:
        return None

    prompt = (
        "Extract a merchant inventory command into JSON with these keys: "
        "action (add, remove, set), itemName, quantity, unit, confidence, notes. "
        "Return JSON only. Normalize kilograms/grams/liters/pieces/packets and keep fractional quantities. "
        f"Text: {text}"
    )

    try:
        response = requests.post(
            base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a precise inventory parsing engine."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"},
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        if isinstance(content, str):
            return json.loads(content)
    except Exception:
        return None

    return None


def parse_voice_command_locally(text: str, db) -> dict[str, Any]:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    cleaned = normalized.replace("please", "").replace("now", "").strip()
    action = "remove"
    for keyword, resolved in ACTION_WORDS.items():
        if keyword in cleaned:
            action = resolved
            break

    quantity = None
    unit = "piece"
    item_name = cleaned

    patterns = [
        r"(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>kg|kgs|kilograms?|g|grams?|ml|liters?|litres?|l|packets?|packs?|pieces?|bottles?|boxes?|dozens?|loaves?|tubes?|bars?|cans?|bundles?)\s+of\s+(?P<item>.+)",
        r"(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>kg|kgs|kilograms?|g|grams?|ml|liters?|litres?|l|packets?|packs?|pieces?|bottles?|boxes?|dozens?|loaves?|tubes?|bars?|cans?|bundles?)\s+(?P<item>.+)",
        r"(?P<quantity>[a-z\- ]+)\s*(?P<unit>kg|kgs|kilograms?|g|grams?|ml|liters?|litres?|l|packets?|packs?|pieces?|bottles?|boxes?|dozens?|loaves?|tubes?|bars?|cans?|bundles?)\s+(?:of\s+)?(?P<item>.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            quantity = parse_number_phrase(match.group("quantity")) or 1
            unit = normalize_unit(match.group("unit"))
            item_name = match.group("item").strip()
            break

    if quantity is None:
        leading_match = re.match(r"^(?P<quantity>\d+(?:\.\d+)?|[a-z\- ]+)\s+(?P<rest>.+)$", cleaned)
        if leading_match:
            quantity = parse_number_phrase(leading_match.group("quantity")) or 1
            remainder = leading_match.group("rest").strip()
            words = remainder.split()
            if words:
                maybe_unit = normalize_unit(words[0])
                if maybe_unit in set(UNIT_ALIASES.values()):
                    unit = maybe_unit
                    item_name = " ".join(words[1:]).strip() or remainder
                else:
                    item_name = remainder
        else:
            quantity = 1

    item_name = item_name.replace("of ", "").strip()
    if item_name.startswith("the "):
        item_name = item_name[4:]

    matched_item = resolve_inventory_item(db, item_name)
    resolved_name = matched_item.get("displayName") if matched_item else item_name
    resolved_unit = matched_item.get("unit") if matched_item else unit
    return {
        "action": action,
        "itemName": resolved_name,
        "quantity": quantity,
        "unit": resolved_unit,
        "confidence": 0.72 if matched_item else 0.52,
        "notes": "Parsed locally; connect an LLM provider for richer understanding.",
        "rawText": text,
    }


app = create_app()


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "0.0.0.0"), port=int(os.getenv("FLASK_PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "0") == "1")
