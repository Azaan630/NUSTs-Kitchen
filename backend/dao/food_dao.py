from dao.base import BaseDAO
from dao.queries import (
    createFood, getAllFoodItems, getAllFoodCosts,
    getFoodByID, getIngredients, getRecipes, addRecipe,
    createIngredient, giveFoodRating, getFoodRating,
)
from io import StringIO
import csv


class FoodDAO(BaseDAO):
    def get_all_food_items(self):
        return self._fetchall(getAllFoodItems)

    def get_food_by_id(self, item_id):
        return self._fetchall(getFoodByID, (item_id,))

    def create_food(self, name, quantity, price):
        return self._execute(createFood, (name, quantity, price))

    def get_all_food_costs(self):
        return self._fetchall(getAllFoodCosts)

    def get_ingredients(self):
        return self._fetchall(getIngredients)

    def get_recipes(self):
        return self._fetchall(getRecipes)

    def get_recipes_detailed(self):
        return self._fetchall(getRecipesDetailed)

    def get_recipe_steps(self, item_id):
        return self._fetchall(getRecipeSteps, (item_id,))

    def create_ingredient(self, name, total_quantity, unit, unit_cost):
        return self._execute(createIngredient, (name, total_quantity, unit, unit_cost))

    def add_recipe(self, item_id, ingredient_id, quantity):
        return self._execute(addRecipe, (item_id, ingredient_id, quantity))

    def update_recipe_ingredient(self, item_id, ingredient_id, data_model):
        """Update ingredient quantity in a recipe, bypassing TABLE_WHITELIST check
        since Food_Item_Ingredients is not a standalone table for generic update_record."""
        update_data = data_model.model_dump(exclude_unset=True)
        if not update_data:
            return {"message": "No changes detected"}
        column_placeholders = [f"{key} = %s" for key in update_data.keys()]
        set_clause = ", ".join(column_placeholders)
        query = f"UPDATE Food_Item_Ingredients SET {set_clause} WHERE Item_ID = %s AND Ingredient_ID = %s"
        parameters = list(update_data.values()) + [item_id, ingredient_id]
        self._execute(query, parameters)
        return {"message": "Recipe updated successfully"}

    def delete_recipe(self, item_id, ingredient_id):
        query = "DELETE FROM Food_Item_Ingredients WHERE Item_ID = %s AND Ingredient_ID = %s"
        cursor = self._execute(query, (item_id, ingredient_id))
        if cursor.rowcount == 0:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"Record with ID {item_id} + {ingredient_id} not found."
            )
        return {"message": "Recipe deleted successfully"}

    def rate_food_item(self, user_id, item_id, schedule_id, score):
        return self._execute(giveFoodRating, (user_id, item_id, schedule_id, score))

    def get_food_rating(self, schedule_id, item_id):
        return self._fetchone(getFoodRating, (schedule_id, item_id))

    def search_food_items(self, query, limit=20):
        pattern = f"%{query}%"
        return self._fetchall(
            "SELECT * FROM Food_Items WHERE Name LIKE %s LIMIT %s",
            (pattern, limit)
        )

    def get_low_stock_ingredients(self, threshold=10):
        return self._fetchall(
            "SELECT * FROM Ingredients WHERE Total_Quantity < %s ORDER BY Total_Quantity ASC",
            (threshold,)
        )
