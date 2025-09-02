
import argparse
import sqlite3
import time
import requests
import re

API_URL = "http://universities.hipolabs.com/search"

def clean_space(s):
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s.strip())
    return s or None

def fetch_all():
    try:
        r = requests.get(API_URL, timeout=30)
        if r.status_code == 200 and isinstance(r.json(), list) and r.json():
            return r.json()
    except Exception:
        pass
    data = []
    for ch in "abcdefghijklmnopqrstuvwxyz":
        try:
            r = requests.get(API_URL, params={"name": ch}, timeout=30)
            if r.status_code == 200:
                data.extend(r.json())
        except Exception:
            pass
        time.sleep(0.05)
    return data

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS universities (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    country   TEXT NOT NULL,
    state     TEXT NOT NULL DEFAULT '',
    alpha2    TEXT,
    UNIQUE(name, country, state)
);

CREATE TABLE IF NOT EXISTS domains (
    university_id INTEGER NOT NULL,
    domain        TEXT NOT NULL,
    PRIMARY KEY (university_id, domain),
    FOREIGN KEY(university_id) REFERENCES universities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS web_pages (
    university_id INTEGER NOT NULL,
    url           TEXT NOT NULL,
    PRIMARY KEY (university_id, url),
    FOREIGN KEY(university_id) REFERENCES universities(id) ON DELETE CASCADE
);
"""

def run(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()

    raw = fetch_all()
    print(f"Registros brutos: {len(raw)}")

    for item in raw:
        name = clean_space(item.get("name"))
        country = clean_space(item.get("country"))
        state = clean_space(item.get("state-province") or item.get("state_province")) or ''
        alpha2 = (item.get("alpha_two_code") or "").strip().upper() or None

        if not (name and country):
            continue

        cur.execute("""
            INSERT OR IGNORE INTO universities(name, country, state, alpha2)
            VALUES (?, ?, ?, ?)
        """, (name, country, state, alpha2))
        conn.commit()

        uni_id = cur.execute("""
            SELECT id FROM universities
            WHERE name = ? AND country = ? AND state = ?
        """, (name, country, state)).fetchone()[0]

        for d in (item.get("domains") or []):
            d = (d or "").strip().lower()
            if not d: 
                continue
            cur.execute("""
                INSERT OR IGNORE INTO domains(university_id, domain)
                VALUES (?, ?)
            """, (uni_id, d))

        for url in (item.get("web_pages") or []):
            url = (url or "").strip().rstrip("/")
            if not url:
                continue
            if not re.match(r'^https?://', url, flags=re.I):
                url = "http://" + url
            cur.execute("""
                INSERT OR IGNORE INTO web_pages(university_id, url)
                VALUES (?, ?)
            """, (uni_id, url))

        conn.commit()

    total_u = cur.execute("SELECT COUNT(*) FROM universities").fetchone()[0]
    total_d = cur.execute("SELECT COUNT(*) FROM domains").fetchone()[0]
    total_w = cur.execute("SELECT COUNT(*) FROM web_pages").fetchone()[0]
    print(f"Universidades: {total_u} | Domínios: {total_d} | Páginas: {total_w}")
    conn.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="universities.sqlite")
    args = ap.parse_args()
    run(args.db)
