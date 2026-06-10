from fastapi import HTTPException

TABLE_WHITELIST = {
    "Student", "Users", "Staff", "Bills", "Food_Items",
    "Ingredients", "Food_Item_Ingredients", "Menu_Food_Items",
    "Mess_Off", "Ratings", "Votes", "Registration_Requests",
}


class BaseDAO:
    def __init__(self, db):
        self.db = db

    def _fetchone(self, query, params=None):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()

    def _fetchall(self, query, params=None):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def _execute(self, query, params=None):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            self.db.commit()
            return cursor
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
        finally:
            cursor.close()

    def update_record(self, table_name, data_model, id_column, id_value):
        if table_name not in TABLE_WHITELIST:
            raise HTTPException(status_code=400, detail="Invalid table name")
        update_data = data_model.model_dump(exclude_unset=True)
        if not update_data:
            return {"message": "No changes detected"}
        column_placeholders = [f"{key} = %s" for key in update_data.keys()]
        set_clause = ", ".join(column_placeholders)
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
        parameters = list(update_data.values()) + [id_value]
        self._execute(query, parameters)
        return {"message": "Update successful"}

    def delete_record(self, table_name, id_column, id_value):
        if table_name not in TABLE_WHITELIST:
            raise HTTPException(status_code=400, detail="Invalid table name")
        query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
        cursor = self._execute(query, (id_value,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Record with ID {id_value} not found in {table_name}."
            )
        return {"message": f"Record {id_value} deleted successfully from {table_name}"}
