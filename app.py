"""
Meal Planner + Shopping List Generator
Day 1-2 (recipes) is fully implemented below as a working example.
Day 3-7 features are stubbed with TODOs — see README.md for the walkthrough
and hints for building them yourself.
"""
from flask import Flask, request, jsonify, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = "meal_planner.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


# ---------- RECIPES (Day 1-2 — fully implemented as your example) ----------

@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    db = get_db()
    recipes = db.execute("SELECT * FROM recipes").fetchall()
    result = []
    for r in recipes:
        ingredients = db.execute(
            """SELECT i.name, i.category, ri.quantity, ri.unit
               FROM recipe_ingredients ri
               JOIN ingredients i ON i.id = ri.ingredient_id
               WHERE ri.recipe_id = ?""",
            (r["id"],),
        ).fetchall()
        result.append({
            "id": r["id"],
            "name": r["name"],
            "servings": r["servings"],
            "instructions": r["instructions"],
            "tags": r["tags"].split(",") if r["tags"] else [],
            "ingredients": [dict(i) for i in ingredients],
        })
    return jsonify(result)


@app.route("/api/recipes", methods=["POST"])
def add_recipe():
    data = request.get_json()

    # Basic validation
    if not data:
        return jsonify({"error": "No recipe data provided"}), 400

    if not data.get("name", "").strip():
        return jsonify({"error": "Recipe name is required"}), 400

    servings = data.get("servings", 4)

    if not isinstance(servings, int) or servings < 1:
        return jsonify({"error": "Servings must be at least 1"}), 400

    if not isinstance(data.get("ingredients", []), list):
        return jsonify({"error": "Ingredients must be a list"}), 400

    for ing in data.get("ingredients", []):
        if not ing.get("name", "").strip():
            return jsonify({"error": "Every ingredient needs a name"}), 400

        if ing.get("quantity", 0) <= 0:
            return jsonify({
                "error": f"Quantity for {ing.get('name', 'ingredient')} must be greater than 0"
            }), 400

        ingredient_name = ing["name"].strip().lower()

    db = get_db()
    cur = db.execute(
        "INSERT INTO recipes (name, servings, instructions, tags) VALUES (?, ?, ?, ?)",
        (data["name"], data.get("servings", 4), data.get("instructions", ""),
         ",".join(data.get("tags", []))),
    )
    recipe_id = cur.lastrowid

    for ing in data.get("ingredients", []):
        # get_or_create the ingredient
        row = db.execute(
            "SELECT id FROM ingredients WHERE name = ?", (ingredient_name,)
        ).fetchone()
        if row:
            ingredient_id = row["id"]
        else:
            cur2 = db.execute(
                "INSERT INTO ingredients (name, category) VALUES (?, ?)",
                (ingredient_name, ing.get("category", "other")),
            )
            ingredient_id = cur2.lastrowid

        db.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
            (recipe_id, ingredient_id, ing["quantity"], ing.get("unit", "")),
        )

    db.commit()
    return jsonify({"id": recipe_id}), 201


@app.route("/api/recipes/<int:recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id):
    db = get_db()
    db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()
    return "", 204

@app.route("/api/recipes/<int:recipe_id>", methods=["PUT"])
def update_recipe(recipe_id):
    data = request.get_json()
    db = get_db()

    # Check that the recipe exists
    recipe = db.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    # Basic validation
    if not data or not data.get("name", "").strip():
        return jsonify({"error": "Recipe name is required"}), 400

    servings = data.get("servings", 4)

    if not isinstance(servings, int) or servings < 1:
        return jsonify({"error": "Servings must be at least 1"}), 400

    # Update basic recipe information
    db.execute(
        """UPDATE recipes
           SET name = ?, servings = ?, instructions = ?, tags = ?
           WHERE id = ?""",
        (
            data["name"].strip(),
            servings,
            data.get("instructions", ""),
            ",".join(data.get("tags", [])),
            recipe_id
        )
    )

    # Remove the old ingredient relationships
    db.execute(
        "DELETE FROM recipe_ingredients WHERE recipe_id = ?",
        (recipe_id,)
    )

    # Add the updated ingredients
    for ing in data.get("ingredients", []):
        if not ing.get("name", "").strip():
            continue

        quantity = ing.get("quantity", 0)

        if quantity <= 0:
            continue

        ingredient_name = ing["name"].strip().lower()

        # Find existing ingredient
        row = db.execute(
            "SELECT id FROM ingredients WHERE name = ?",
            (ingredient_name,)
        ).fetchone()

        if row:
            ingredient_id = row["id"]
        else:
            cur = db.execute(
                """INSERT INTO ingredients (name, category)
                   VALUES (?, ?)""",
                (
                    ingredient_name,
                    ing.get("category", "other")
                )
            )
            ingredient_id = cur.lastrowid

        db.execute(
            """INSERT INTO recipe_ingredients
               (recipe_id, ingredient_id, quantity, unit)
               VALUES (?, ?, ?, ?)""",
            (
                recipe_id,
                ingredient_id,
                quantity,
                ing.get("unit", "")
            )
        )

    db.commit()

    return jsonify({"message": "Recipe updated successfully"})


# ---------- MEAL PLAN (Day 3-4 — TODO: build this yourself) ----------

@app.route("/api/meal-plan", methods=["GET"])
def get_meal_plan():
    # TODO: query the meal_plan table, joining recipes to get names.
    # Return something shaped like:
    # { "Monday": {"breakfast": {...recipe...}, "lunch": null, "dinner": {...}}, "Tuesday": {...}, ... }
    #
    # Hint: initialise a dict with all 7 days and 3 slots set to None first,
    # then fill in whichever meal_plan rows exist.
    return jsonify({"error": "not implemented yet"}), 501


@app.route("/api/meal-plan", methods=["POST"])
def set_meal_plan_entry():
    # TODO: expects JSON like {"day_of_week": "Monday", "meal_slot": "dinner", "recipe_id": 3}
    # Should UPSERT into meal_plan — if a row for that day+slot exists, update it, else insert.
    # Hint: SQLite supports "INSERT ... ON CONFLICT ... DO UPDATE", but you'll need a
    # UNIQUE constraint on (day_of_week, meal_slot) in schema.sql for that to work —
    # or just do a SELECT-then-INSERT/UPDATE in Python, which is simpler to reason about.
    return jsonify({"error": "not implemented yet"}), 501


# ---------- SHOPPING LIST (Day 5-6 — TODO: build this yourself) ----------

@app.route("/api/shopping-list", methods=["GET"])
def get_shopping_list():
    # TODO: this is the core "useful" feature. Steps:
    # 1. Get all recipe_ids currently in the meal_plan table.
    # 2. For each, fetch its ingredients (with quantity + unit), scaled by
    #    (planned_servings / recipe.servings) if servings_override was set.
    # 3. Aggregate: sum quantities for the same ingredient+unit across all recipes.
    #    (Careful: "200g flour" + "1 cup flour" can't be summed directly — for v1,
    #    just group by exact unit match and note mismatches separately.)
    # 4. Group the aggregated list by ingredient category (produce/dairy/pantry/etc.)
    #    for easy in-store navigation.
    # Return: { "produce": [{"name": "onion", "quantity": 3, "unit": "whole"}, ...], "dairy": [...], ... }
    return jsonify({"error": "not implemented yet"}), 501


if __name__ == "__main__":
    app.run(debug=True)
