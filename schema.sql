-- Day 1-2: Core data model
-- Run this once to set up the database: python init_db.py

DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS meal_plan;

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    servings INTEGER NOT NULL DEFAULT 4,
    instructions TEXT,
    tags TEXT  -- comma-separated, e.g. "vegetarian,quick,dinner"
);

CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT  -- e.g. "produce", "dairy", "pantry", "meat" — used for shopping list grouping
);

-- Join table: which ingredients (and how much) each recipe needs
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT,  -- e.g. "g", "ml", "cups", "whole"
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
);

-- Day 3-4: Weekly meal plan — which recipe is assigned to which day/slot
CREATE TABLE meal_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week TEXT NOT NULL,  -- "Monday", "Tuesday", etc.
    meal_slot TEXT NOT NULL,    -- "breakfast", "lunch", "dinner"
    recipe_id INTEGER,
    servings_override INTEGER,  -- optional: scale servings for this specific plan entry
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE SET NULL
    UNIQUE (day_of_week, meal_slot)  -- only one recipe per day/slot
);
