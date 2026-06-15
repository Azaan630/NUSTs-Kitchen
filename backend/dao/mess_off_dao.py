from dao.base import BaseDAO
from dao.queries import requestMessOff, cancelMessOff, getMessOffStatus, getMessOffThisMonth, getMyMessOffThisMonth


class MessOffDAO(BaseDAO):
    def request_mess_off(self, user_id, start_date, end_date):
        return self._execute(requestMessOff, (user_id, start_date, end_date))

    def cancel_mess_off(self, mess_off_id):
        return self._execute(cancelMessOff, (mess_off_id,))

    def get_mess_off_status(self, mess_off_id):
        return self._fetchone(getMessOffStatus, (mess_off_id,))

    def get_mess_off_this_month(self):
        return self._fetchall(getMessOffThisMonth)

    def get_my_mess_off_this_month(self, user_id):
        return self._fetchall(getMyMessOffThisMonth, (user_id,))
