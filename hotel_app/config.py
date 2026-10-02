import os


DB_CONFIG = {
    "host": os.getenv("HOTEL_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("HOTEL_DB_PORT", "3306")),
    "user": os.getenv("HOTEL_DB_USER", "hotel_course_admin"),
    "password": os.getenv("HOTEL_DB_PASSWORD", ""),
    "database": os.getenv("HOTEL_DB_NAME", "hotel_db"),
    "charset": "utf8mb4",
    "autocommit": False,
}

ROLE_LABELS = {"admin": "Администратор", "manager": "Менеджер", "guest": "Гость"}
