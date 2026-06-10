from datetime import date, timedelta
from dao.base import BaseDAO
from dao.queries import getMenuByDate, getWeeklyMenu, getCurrentScheduleID, addMenuItem


class MenuDAO(BaseDAO):
    def get_todays_menu(self, target_date, user_id=None):
        return self._fetchall(getMenuByDate, (user_id, target_date))

    def get_ratings_summary(self):
        """Aggregate rating averages for all food items that have been rated."""
        return self._fetchall("""
            SELECT fi.Item_ID, fi.Name,
                   ROUND(AVG(r.Score), 2) AS avg_rating,
                   COUNT(r.Rating_ID) AS rating_count,
                   fi.Ratings_Average
            FROM Food_Items fi
            LEFT JOIN Ratings r ON fi.Item_ID = r.Item_ID
            GROUP BY fi.Item_ID, fi.Name, fi.Ratings_Average
            ORDER BY avg_rating DESC
        """)

    def get_weekly_menu(self, today=None, user_id=None):
        if today is None:
            today = date.today()
        return self._fetchall(getWeeklyMenu, (user_id, today, today))

    def get_current_schedule_id(self, target_date, meal_type):
        return self._fetchone(getCurrentScheduleID, (target_date, meal_type))

    def add_menu_item(self, schedule_id, item_id):
        return self._execute(addMenuItem, (schedule_id, item_id))

    def delete_menu_item(self, item_id, schedule_id):
        query = "DELETE FROM Menu_Food_Items WHERE Item_ID = %s AND Schedule_ID = %s"
        cursor = self._execute(query, (item_id, schedule_id))
        if cursor.rowcount == 0:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail=f"Record {item_id} + {schedule_id} not found in Menu_Food_Items."
            )
        return {"message": "Menu item deleted successfully"}

    def maintain_menu_schedule(self):
        today = date.today()
        next_week_check = today + timedelta(days=7)
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT 1 FROM Menu_Schedule WHERE Date = %s LIMIT 1",
                (next_week_check,)
            )
            exists = cursor.fetchone()
            if not exists:
                for i in range(15):
                    target_date = today + timedelta(days=i)
                    for meal in ['Breakfast', 'Lunch', 'Dinner']:
                        cursor.execute(
                            """INSERT IGNORE INTO Menu_Schedule (Date, meal_type, status)
                            VALUES (%s, %s, 'active')""",
                            (target_date, meal)
                        )
                self.db.commit()
        except Exception as e:
            print(f"Maintenance Error: {e}")
            self.db.rollback()
        finally:
            cursor.close()
