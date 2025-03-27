class User:
    TABLE_NAME = "user"

    SCHEMA = {
        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
        "name": "text NOT NULL",
        "email": "text UNIQUE NOT NULL",
        "password": "text NOT NULL",
        "created_at": "timestamp DEFAULT now()"
    }
