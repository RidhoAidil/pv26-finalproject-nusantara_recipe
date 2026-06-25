from database.db import get_connection, hash_password


# ── USER ────────────────────────────────────────────────
class UserModel:
    @staticmethod
    def login(username: str, password: str):
        conn = get_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def register(username: str, password: str, email: str):
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?,?,?)",
                (username, hash_password(password), email)
            )
            conn.commit()
            conn.close()
            return True, "Registrasi berhasil!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT id, username, email, role, created_at FROM users").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_profile(user_id, username, email):
        try:
            conn = get_connection()
            conn.execute(
                "UPDATE users SET username=?, email=? WHERE id=?",
                (username, email, user_id)
            )
            conn.commit()
            conn.close()
            return True, "Profil diperbarui."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def change_password(user_id, old_pw, new_pw):
        conn = get_connection()
        user = conn.execute(
            "SELECT id FROM users WHERE id=? AND password=?",
            (user_id, hash_password(old_pw))
        ).fetchone()
        if not user:
            conn.close()
            return False, "Password lama salah."
        conn.execute(
            "UPDATE users SET password=? WHERE id=?",
            (hash_password(new_pw), user_id)
        )
        conn.commit()
        conn.close()
        return True, "Password berhasil diubah."


# ── CATEGORY ────────────────────────────────────────────
class CategoryModel:
    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def add(name, description=""):
        try:
            conn = get_connection()
            conn.execute("INSERT INTO categories (name, description) VALUES (?,?)", (name, description))
            conn.commit()
            conn.close()
            return True, "Kategori ditambahkan."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update(cat_id, name, description):
        try:
            conn = get_connection()
            conn.execute("UPDATE categories SET name=?, description=? WHERE id=?", (name, description, cat_id))
            conn.commit()
            conn.close()
            return True, "Kategori diperbarui."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete(cat_id):
        try:
            conn = get_connection()
            conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
            conn.commit()
            conn.close()
            return True, "Kategori dihapus."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_recipe_count_per_category():
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.name, COUNT(r.id) as total
            FROM categories c
            LEFT JOIN recipes r ON r.category_id = c.id
            GROUP BY c.id ORDER BY total DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ── RECIPE ──────────────────────────────────────────────
class RecipeModel:
    @staticmethod
    def get_all(search="", category_id=None, sort_col="name", sort_order="ASC"):
        conn = get_connection()
        query = """
            SELECT r.*, c.name as category_name
            FROM recipes r
            LEFT JOIN categories c ON c.id = r.category_id
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (r.name LIKE ? OR r.origin_region LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        if category_id:
            query += " AND r.category_id = ?"
            params.append(category_id)
        safe_cols = {"name": "r.name", "cook_time_minutes": "r.cook_time_minutes",
                     "servings": "r.servings", "created_at": "r.created_at"}
        col = safe_cols.get(sort_col, "r.name")
        order = "DESC" if sort_order == "DESC" else "ASC"
        query += f" ORDER BY {col} {order}"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(recipe_id):
        conn = get_connection()
        recipe = conn.execute("""
            SELECT r.*, c.name as category_name
            FROM recipes r LEFT JOIN categories c ON c.id = r.category_id
            WHERE r.id = ?
        """, (recipe_id,)).fetchone()
        ingredients = conn.execute(
            "SELECT * FROM ingredients WHERE recipe_id=? ORDER BY id", (recipe_id,)
        ).fetchall()
        steps = conn.execute(
            "SELECT * FROM steps WHERE recipe_id=? ORDER BY step_no", (recipe_id,)
        ).fetchall()
        conn.close()
        return (dict(recipe) if recipe else None,
                [dict(i) for i in ingredients],
                [dict(s) for s in steps])

    @staticmethod
    def add(name, category_id, origin_region, description, cook_time, servings, user_id,
            ingredients, steps):
        conn = get_connection()
        try:
            cur = conn.execute("""
                INSERT INTO recipes (name, category_id, origin_region, description,
                    cook_time_minutes, servings, created_by)
                VALUES (?,?,?,?,?,?,?)
            """, (name, category_id, origin_region, description, cook_time, servings, user_id))
            rid = cur.lastrowid
            for ing in ingredients:
                conn.execute(
                    "INSERT INTO ingredients (recipe_id, name, amount, unit) VALUES (?,?,?,?)",
                    (rid, ing["name"], ing["amount"], ing["unit"])
                )
            for i, step in enumerate(steps, 1):
                conn.execute(
                    "INSERT INTO steps (recipe_id, step_no, instruction) VALUES (?,?,?)",
                    (rid, i, step)
                )
            conn.commit()
            return True, "Resep berhasil ditambahkan."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def update(recipe_id, name, category_id, origin_region, description, cook_time, servings,
               ingredients, steps):
        conn = get_connection()
        try:
            conn.execute("""
                UPDATE recipes SET name=?, category_id=?, origin_region=?,
                    description=?, cook_time_minutes=?, servings=?
                WHERE id=?
            """, (name, category_id, origin_region, description, cook_time, servings, recipe_id))
            conn.execute("DELETE FROM ingredients WHERE recipe_id=?", (recipe_id,))
            conn.execute("DELETE FROM steps WHERE recipe_id=?", (recipe_id,))
            for ing in ingredients:
                conn.execute(
                    "INSERT INTO ingredients (recipe_id, name, amount, unit) VALUES (?,?,?,?)",
                    (recipe_id, ing["name"], ing["amount"], ing["unit"])
                )
            for i, step in enumerate(steps, 1):
                conn.execute(
                    "INSERT INTO steps (recipe_id, step_no, instruction) VALUES (?,?,?)",
                    (recipe_id, i, step)
                )
            conn.commit()
            return True, "Resep berhasil diperbarui."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def delete(recipe_id):
        try:
            conn = get_connection()
            conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
            conn.commit()
            conn.close()
            return True, "Resep dihapus."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_stats():
        conn = get_connection()
        total = conn.execute("SELECT COUNT(*) as c FROM recipes").fetchone()["c"]
        cat_count = conn.execute("SELECT COUNT(*) as c FROM categories").fetchone()["c"]
        regions = conn.execute(
            "SELECT COUNT(DISTINCT origin_region) as c FROM recipes WHERE origin_region != ''"
        ).fetchone()["c"]
        recent = conn.execute("""
            SELECT r.id, r.name, c.name as category_name, r.created_at
            FROM recipes r LEFT JOIN categories c ON c.id=r.category_id
            ORDER BY r.created_at DESC LIMIT 5
        """).fetchall()
        conn.close()
        return {
            "total_recipes": total,
            "total_categories": cat_count,
            "total_regions": regions,
            "recent": [dict(r) for r in recent],
        }


# ── FAVORITES ────────────────────────────────────────────
class FavoriteModel:
    @staticmethod
    def toggle(user_id, recipe_id):
        conn = get_connection()
        exists = conn.execute(
            "SELECT id FROM favorites WHERE user_id=? AND recipe_id=?",
            (user_id, recipe_id)
        ).fetchone()
        if exists:
            conn.execute("DELETE FROM favorites WHERE user_id=? AND recipe_id=?", (user_id, recipe_id))
            msg = "Dihapus dari favorit."
        else:
            conn.execute("INSERT INTO favorites (user_id, recipe_id) VALUES (?,?)", (user_id, recipe_id))
            msg = "Ditambahkan ke favorit!"
        conn.commit()
        conn.close()
        return msg

    @staticmethod
    def is_favorite(user_id, recipe_id):
        conn = get_connection()
        r = conn.execute(
            "SELECT id FROM favorites WHERE user_id=? AND recipe_id=?",
            (user_id, recipe_id)
        ).fetchone()
        conn.close()
        return r is not None

    @staticmethod
    def get_user_favorites(user_id):
        conn = get_connection()
        rows = conn.execute("""
            SELECT r.*, c.name as category_name
            FROM favorites f
            JOIN recipes r ON r.id = f.recipe_id
            LEFT JOIN categories c ON c.id = r.category_id
            WHERE f.user_id = ?
            ORDER BY f.added_at DESC
        """, (user_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]