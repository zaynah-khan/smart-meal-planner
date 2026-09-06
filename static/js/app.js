// ---------- Nav switching (already wired up for you) ----------
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        ["recipes", "planner", "shopping"].forEach(v => {
            document.getElementById(`${v}-view`).style.display = v === btn.dataset.view ? "block" : "none";
        });
        if (btn.dataset.view === "planner") loadMealPlan();
        if (btn.dataset.view === "shopping") loadShoppingList();
    });
});

// ---------- Day 1-2: Recipes (fully implemented as your example) ----------

async function loadRecipes() {
    const res = await fetch("/api/recipes");
    const recipes = await res.json();
    const container = document.getElementById("recipe-list");

    container.innerHTML = recipes.map(r => `
        <div class="recipe-card">

            <h3>
                ${r.name} 
                <small>(${r.servings} servings)</small>
            </h3>

            <div class="recipe-tags">
                ${r.tags.map(tag => `<span class="tag">${tag}</span>`).join("")}
            </div>

            <ul>
                ${r.ingredients.map(i => `
                    <li>
                        ${i.quantity} ${i.unit} ${i.name}
                        <small>(${i.category})</small>
                    </li>
                `).join("")}
            </ul>

            <p>${r.instructions || ""}</p>

            <div class="recipe-actions">
                <button onclick="editRecipe(${r.id})">Edit</button>
                <button onclick="deleteRecipe(${r.id})">Delete</button>
            </div>

        </div>
    `).join("");
}

async function deleteRecipe(id) {
    await fetch(`/api/recipes/${id}`, { method: "DELETE" });
    loadRecipes();
}

async function editRecipe(id) {
    const res = await fetch("/api/recipes");
    const recipes = await res.json();

    const recipe = recipes.find(r => r.id === id);

    if (!recipe) {
        alert("Recipe not found.");
        return;
    }

    document.getElementById("recipe-name").value = recipe.name;
    document.getElementById("recipe-servings").value = recipe.servings;
    document.getElementById("recipe-instructions").value = recipe.instructions || "";
    document.getElementById("recipe-tags").value = recipe.tags.join(", ");

    document.getElementById("ingredient-rows").innerHTML = "";

    recipe.ingredients.forEach(ingredient => {
        const row = document.createElement("div");
        row.className = "ingredient-row";

        row.innerHTML = `
            <input type="text" class="ing-name" value="${ingredient.name}" placeholder="Ingredient">
            <input type="number" class="ing-qty" value="${ingredient.quantity}" placeholder="Qty" step="0.1">
            <input type="text" class="ing-unit" value="${ingredient.unit}" placeholder="Unit">
            <select class="ing-category">
                <option value="produce" ${ingredient.category === "produce" ? "selected" : ""}>Produce</option>
                <option value="dairy" ${ingredient.category === "dairy" ? "selected" : ""}>Dairy</option>
                <option value="meat" ${ingredient.category === "meat" ? "selected" : ""}>Meat</option>
                <option value="pantry" ${ingredient.category === "pantry" ? "selected" : ""}>Pantry</option>
                <option value="frozen" ${ingredient.category === "frozen" ? "selected" : ""}>Frozen</option>
                <option value="other" ${ingredient.category === "other" ? "selected" : ""}>Other</option>
            </select>
        `;

        document.getElementById("ingredient-rows").appendChild(row);
    });

    document.getElementById("recipe-form").dataset.editingId = id;

    document.querySelector("#recipe-form button[type='submit']").textContent = "Save Changes";
}

document.getElementById("add-ingredient-row").addEventListener("click", () => {
    const row = document.createElement("div");
    row.className = "ingredient-row";

    row.innerHTML = `
        <input type="text" class="ing-name" placeholder="Ingredient">
        <input type="number" class="ing-qty" placeholder="Qty" step="0.1">
        <input type="text" class="ing-unit" placeholder="Unit (g, ml, whole...)">

        <select class="ing-category">
            <option value="produce">Produce</option>
            <option value="dairy">Dairy</option>
            <option value="meat">Meat</option>
            <option value="pantry">Pantry</option>
            <option value="frozen">Frozen</option>
            <option value="other">Other</option>
        </select>
    `;

    document.getElementById("ingredient-rows").appendChild(row);
});

document.getElementById("recipe-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const recipeName = document.getElementById("recipe-name").value.trim();
    const servings = parseInt(document.getElementById("recipe-servings").value);

    if (!recipeName) {
        alert("Please give your recipe a name.");
        return;
    }

    if (!servings || servings < 1) {
        alert("Servings must be at least 1.");
        return;
    }
    const ingredients = [...document.querySelectorAll(".ingredient-row")].map(row => ({
        name: row.querySelector(".ing-name").value,
        quantity: parseFloat(row.querySelector(".ing-qty").value) || 0,
        unit: row.querySelector(".ing-unit").value,
        category: row.querySelector(".ing-category").value,
    })).filter(i => i.name);

    const tags = document.getElementById("recipe-tags").value
        .split(",")
        .map(tag => tag.trim())
        .filter(tag => tag);

    const recipeData = {
        name: recipeName,
        servings: servings,
        instructions: document.getElementById("recipe-instructions").value,
        tags: tags,
        ingredients: ingredients
    };

    const editingId = e.target.dataset.editingId;

    let url = "/api/recipes";
    let method = "POST";

    if (editingId) {
        url = `/api/recipes/${editingId}`;
        method = "PUT";
    }

    const res = await fetch(url, {
        method: method,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(recipeData)
    });

    if (!res.ok) {
        const error = await res.json();
        alert(error.error || "Something went wrong.");
        return;
    }

    e.target.reset();

    delete e.target.dataset.editingId;

    document.querySelector("#recipe-form button[type='submit']").textContent = "Save Recipe";

    document.getElementById("ingredient-rows").innerHTML = `
        <div class="ingredient-row">
            <input type="text" class="ing-name" placeholder="Ingredient">
            <input type="number" class="ing-qty" placeholder="Qty" step="0.1">
            <input type="text" class="ing-unit" placeholder="Unit (g, ml, whole...)">

            <select class="ing-category">
                <option value="produce">Produce</option>
                <option value="dairy">Dairy</option>
                <option value="meat">Meat</option>
                <option value="pantry">Pantry</option>
                <option value="frozen">Frozen</option>
                <option value="other">Other</option>
            </select>
        </div>`;
    loadRecipes();
});

loadRecipes();

// ---------- Day 3-4: Weekly Plan (TODO — build this yourself) ----------

async function loadMealPlan() {
    // TODO:
    // 1. Fetch your list of recipes (you already have loadRecipes logic to reuse/adapt).
    // 2. Fetch GET /api/meal-plan.
    // 3. Render a 7x3 table into #planner-grid — each cell a <select> of recipe names,
    //    pre-selected to whatever's already planned for that day/slot.
    // 4. On <select> change, POST to /api/meal-plan with the day/slot/recipe_id.
    console.log("TODO: implement loadMealPlan()");
}

// ---------- Day 5-6: Shopping List (TODO — build this yourself) ----------

async function loadShoppingList() {
    // TODO:
    // 1. Fetch GET /api/shopping-list (grouped by category).
    // 2. Render each category as a heading with a checklist under it.
    // 3. Bonus (Day 7 polish): persist checked-off state in localStorage so it
    //    survives a page refresh while you're stood in the shop.
    console.log("TODO: implement loadShoppingList()");
}
