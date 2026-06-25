import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "resep.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            origin_region TEXT,
            description TEXT,
            cook_time_minutes INTEGER DEFAULT 0,
            servings INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount TEXT,
            unit TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_no INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            added_at TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(user_id, recipe_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );
    """)

    # Seed admin
    admin_pw = hash_password("admin123")
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, email, role)
        VALUES ('admin', ?, 'admin@resepnusantara.id', 'admin')
    """, (admin_pw,))

    # Seed categories
    categories = [
        ("Sup & Soto", "Masakan berkuah khas Nusantara"),
        ("Masakan Padang", "Masakan khas Sumatera Barat"),
        ("Masakan Jawa", "Masakan khas Pulau Jawa"),
        ("Masakan Bali", "Masakan khas Pulau Bali"),
        ("Gorengan", "Berbagai jenis gorengan"),
        ("Kue & Jajanan", "Aneka kue dan jajanan tradisional"),
        ("Minuman", "Minuman tradisional Indonesia"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
        categories
    )

    # Seed sample recipes
    conn.commit()
    cat = {row["name"]: row["id"] for row in cur.execute("SELECT id, name FROM categories")}

    sample_recipes = [
        ("Soto Ayam Lamongan", cat["Sup & Soto"], "Lamongan, Jawa Timur",
         "Soto ayam bening yang segar dengan bumbu rempah khas Lamongan.", 60, 4, None),
        ("Rendang Daging", cat["Masakan Padang"], "Minangkabau, Sumatera Barat",
         "Rendang daging sapi dengan santan dan bumbu rempah yang kaya.", 180, 6, None),
        ("Nasi Goreng Spesial", cat["Masakan Jawa"], "Jawa",
         "Nasi goreng dengan telur, ayam, dan bumbu kecap manis.", 20, 2, None),
        ("Ayam Betutu", cat["Masakan Bali"], "Bali",
         "Ayam yang dimasak dengan bumbu base genep khas Bali.", 240, 4, None),
        ("Tempe Mendoan", cat["Gorengan"], "Banyumas, Jawa Tengah",
         "Tempe dibalut tepung berbumbu dan digoreng setengah matang.", 30, 4, None),
    ]

    for r in sample_recipes:
        cur.execute("""
            INSERT OR IGNORE INTO recipes
              (name, category_id, origin_region, description, cook_time_minutes, servings, created_by)
            VALUES (?,?,?,?,?,?,?)
        """, r)

    conn.commit()

    # Seed ingredients for Soto Ayam
    cur.execute("SELECT id FROM recipes WHERE name='Soto Ayam Lamongan'")
    row = cur.fetchone()
    if row:
        rid = row["id"]
        ingr = [
            (rid, "Ayam kampung", "1", "ekor"),
            (rid, "Bawang merah", "8", "siung"),
            (rid, "Bawang putih", "5", "siung"),
            (rid, "Kunyit", "3", "cm"),
            (rid, "Jahe", "2", "cm"),
            (rid, "Serai", "2", "batang"),
            (rid, "Garam", "secukupnya", ""),
        ]
        cur.executemany(
            "INSERT OR IGNORE INTO ingredients (recipe_id, name, amount, unit) VALUES (?,?,?,?)",
            ingr
        )
        steps_data = [
            (rid, 1, "Rebus ayam hingga empuk, angkat dan suwir-suwir dagingnya."),
            (rid, 2, "Haluskan bawang merah, bawang putih, kunyit, dan jahe."),
            (rid, 3, "Tumis bumbu halus hingga harum, masukkan serai."),
            (rid, 4, "Masukkan bumbu ke dalam kaldu ayam, didihkan."),
            (rid, 5, "Sajikan dengan ayam suwir, perkedel, dan tauge."),
        ]
        cur.executemany(
            "INSERT OR IGNORE INTO steps (recipe_id, step_no, instruction) VALUES (?,?,?)",
            steps_data
        )

    conn.commit()
    conn.close()