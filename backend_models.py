from typing import List, Dict, Any
from datetime import datetime, timezone
from pymongo import ReturnDocument
from database import get_client


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_transaction(db, transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Create a cash transaction and adjust inventory stock levels.

    Attempts to run within a MongoDB session/transaction if available. If transactions
    are not supported, falls back to best-effort updates (may leave inconsistencies
    in single-node configs without replica sets).
    """
    client = get_client()
    lines: List[Dict[str, Any]] = transaction.get("lines", [])
    total = transaction.get("total", 0)
    userId = transaction.get("userId")
    storeId = transaction.get("storeId")

    doc = {
        "storeId": storeId,
        "userId": userId,
        "lines": lines,
        "total": total,
        "paymentMethod": transaction.get("paymentMethod", "cash"),
        "createdAt": _now(),
    }

    # Try transactional commit
    try:
        with client.start_session() as session:
            with session.start_transaction():
                # adjust inventory
                for line in lines:
                    item_id = line.get("itemId")
                    qty = float(line.get("qty", 0))
                    if not item_id:
                        continue
                    res = db.inventory.find_one_and_update(
                        {"_id": item_id},
                        {"$inc": {"stock": -qty}},
                        session=session,
                        return_document=ReturnDocument.AFTER,
                    )
                    if res is None:
                        raise RuntimeError(f"Inventory item {item_id} not found")

                inserted = db.orders.insert_one(doc, session=session)
                doc["_id"] = inserted.inserted_id
                return doc
    except Exception:
        # Fallback: best-effort without transaction
        for line in lines:
            item_id = line.get("itemId")
            qty = float(line.get("qty", 0))
            if not item_id:
                continue
            db.inventory.update_one({"_id": item_id}, {"$inc": {"stock": -qty}})

        inserted = db.orders.insert_one(doc)
        doc["_id"] = inserted.inserted_id
        return doc


def generate_receipt(transaction_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Return a printable receipt object for the transaction."""
    lines = transaction_doc.get("lines", [])
    items = []
    subtotal = 0
    for l in lines:
        price = float(l.get("price", 0))
        qty = float(l.get("qty", 0))
        amount = price * qty
        subtotal += amount
        items.append({
            "name": l.get("name"),
            "qty": qty,
            "unit": l.get("unit"),
            "price": price,
            "amount": amount,
        })

    receipt = {
        "transactionId": str(transaction_doc.get("_id")),
        "createdAt": transaction_doc.get("createdAt"),
        "lines": items,
        "subtotal": subtotal,
        "total": transaction_doc.get("total", subtotal),
        "paymentMethod": transaction_doc.get("paymentMethod", "cash"),
    }
    return receipt
