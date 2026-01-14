import sqlite3
from datetime import datetime
from app.models import get_connection


def insert_message(message: dict) -> bool:
    """
    Inserts message into DB.
    Returns True if inserted.
    Returns False if duplicate (same message_id).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message["message_id"],
                message["from"],
                message["to"],
                message["ts"],
                message.get("text"),
                datetime.utcnow().isoformat() + "Z",
            ),
        )

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        # Duplicate message_id
        return False
def list_messages(limit=10, offset=0, from_msisdn=None, to_msisdn=None):
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if from_msisdn:
        conditions.append("from_msisdn = ?")
        params.append(from_msisdn)

    if to_msisdn:
        conditions.append("to_msisdn = ?")
        params.append(to_msisdn)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # total count
    count_query = f"SELECT COUNT(*) FROM messages {where_clause}"
    total = cursor.execute(count_query, params).fetchone()[0]

    # data query
    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """
    rows = cursor.execute(
        data_query, params + [limit, offset]
    ).fetchall()

    conn.close()

    items = []
    for row in rows:
        items.append({
            "message_id": row["message_id"],
            "from": row["from_msisdn"],
            "to": row["to_msisdn"],
            "ts": row["ts"],
            "text": row["text"],
        })

    return total, items
