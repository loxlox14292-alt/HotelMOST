import importlib
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from hotel_app import config
from hotel_app.auth import password_hash


DB_ENV_KEYS = (
    "HOTEL_DB_HOST", "HOTEL_DB_PORT", "HOTEL_DB_USER",
    "HOTEL_DB_PASSWORD", "HOTEL_DB_NAME",
)


class ConfigurationTests(unittest.TestCase):
    def test_password_is_not_embedded(self):
        with patch.dict(os.environ, clear=True):
            settings = importlib.reload(config).DB_CONFIG
            self.assertEqual(settings["password"], "")
            self.assertEqual(settings["port"], 3306)
        importlib.reload(config)

    def test_connection_settings_can_be_overridden(self):
        values = dict(zip(DB_ENV_KEYS, (
            "localhost", "3307", "test_user", "test_only", "test_hotel",
        )))
        with patch.dict(os.environ, values):
            settings = importlib.reload(config).DB_CONFIG
            self.assertEqual(settings["host"], "localhost")
            self.assertEqual(settings["port"], 3307)
            self.assertEqual(settings["user"], "test_user")
            self.assertEqual(settings["password"], "test_only")
            self.assertEqual(settings["database"], "test_hotel")
        importlib.reload(config)


class DemoAccountTests(unittest.TestCase):
    def test_demo_passwords_match_seed_hashes(self):
        sql = (Path(__file__).resolve().parents[1] / "database.sql").read_text(encoding="utf-8")
        for login, role, name, password in (
            ("admin", "admin", "Демо Администратор", "admin123"),
            ("manager", "manager", "Демо Менеджер", "manager123"),
            ("guest", "guest", "Демо Гость", "guest123"),
        ):
            with self.subTest(login=login):
                self.assertIn(f"('{login}','{password_hash(password)}','{role}','{name}')", sql)

    def test_unicode_password_hash_is_stable(self):
        self.assertEqual(password_hash("пароль🔒"), password_hash("пароль🔒"))
        self.assertNotEqual(password_hash("пароль🔒"), password_hash("Пароль🔒"))
        self.assertEqual(len(password_hash("пароль🔒")), 64)


if __name__ == "__main__":
    unittest.main()
