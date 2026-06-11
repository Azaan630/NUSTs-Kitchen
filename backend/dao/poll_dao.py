import mysql.connector
from fastapi import HTTPException
from dao.base import BaseDAO


class PollDAO(BaseDAO):
    def start_poll(self, item_ids, meal_type):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("UPDATE Food_Items SET Vote_Count = 0")
            cursor.execute("DELETE FROM Votes")
            poll_str = ",".join(map(str, item_ids))
            query = """INSERT INTO System_Config (Config_Key, Value)
                       VALUES (%s, %s) ON DUPLICATE KEY UPDATE Value = %s"""
            cursor.execute(query, ("active_poll_items", poll_str, poll_str))
            cursor.execute(query, ("active_poll_meal_type", meal_type, meal_type))
            self.db.commit()
            return {"status": "Poll Started"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

    def get_active_poll(self):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_items'")
            active_poll_items = cursor.fetchone()
            cursor.execute("SELECT Value FROM System_Config WHERE Config_Key = 'active_poll_meal_type'")
            active_meal_type = cursor.fetchone()
            if not active_poll_items or not active_poll_items['Value']:
                return {"active": False}
            id_list = active_poll_items['Value'].split(",")
            format_strings = ','.join(['%s'] * len(id_list))
            query = f"SELECT Item_ID, Name, Price FROM Food_Items WHERE Item_ID IN ({format_strings})"
            cursor.execute(query, tuple(id_list))
            items = cursor.fetchall()
            for item in items:
                if 'Price' in item and item['Price'] is not None:
                    item['Price'] = float(item['Price'])
            return {
                "active": True,
                "meal_type": active_meal_type['Value'] if active_meal_type else "Poll",
                "items": items
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

    def cast_vote(self, user_id, item_id):
        cursor = self.db.cursor()
        try:
            cursor.callproc('sp_AddVote', [user_id, item_id])
            self.db.commit()
        except mysql.connector.Error as err:
            if err.errno == 1062:
                raise HTTPException(status_code=400, detail="You already voted for this!")
            raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
        finally:
            cursor.close()
        return {"status": "Voted successfully"}

    def end_poll(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM System_Config WHERE Config_Key IN ('active_poll_items', 'active_poll_meal_type')")
            self.db.commit()
            return {"status": "Poll Ended"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()

    def get_poll_results(self):
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT Item_ID, Name, Vote_Count
                FROM Food_Items
                WHERE Vote_Count > 0
                ORDER BY Vote_Count DESC
            """)
            results = cursor.fetchall()
            return {"results": results}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cursor.close()
