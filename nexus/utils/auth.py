# -*- coding: utf-8 -*-
import json
import os
import hashlib

AUTH_FILE = "D:\\ai-career-assistant\\users.json"

def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _load_users() -> dict:
    if not os.path.exists(AUTH_FILE):
        return {
            "admin@careerai.com": {
                "name": "Admin Recruiter",
                "password": _hash_pw("admin123"),
                "role": "Recruiter"
            }
        }
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users(users: dict):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def signup_user(name: str, email: str, password: str, role: str = "Recruiter") -> tuple[bool, str]:
    email = email.strip().lower()
    if not email or not password or not name:
        return False, "Please fill in all fields."
    users = _load_users()
    if email in users:
        return False, "An account with this email already exists."
    users[email] = {
        "name": name.strip(),
        "password": _hash_pw(password),
        "role": role
    }
    _save_users(users)
    return True, "Account created successfully! Please sign in."

def authenticate_user(email: str, password: str) -> tuple[bool, dict]:
    email = email.strip().lower()
    users = _load_users()
    if email not in users:
        return False, {}
    if users[email]["password"] == _hash_pw(password):
        return True, {
            "email": email,
            "name": users[email].get("name", "User"),
            "role": users[email].get("role", "Recruiter")
        }
    return False, {}
