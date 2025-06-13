from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import oracledb

try:
    global_db_conn = oracledb.connect(
    user="C##TEST",
    password="test",
    dsn="localhost:1521/ORCLCDB"
    )
    print("Oracle connection established.")
except Exception as e:
    global_db_conn=None
    print(f"Lỗi kết nối DB: {e}")

class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # hard-coded balance for tutorial purposes. in production this
        # would be retrieved from a database or an API
        balance = 1000
        transfer_amount = tracker.get_slot("amount")
        has_sufficient_funds = transfer_amount <= balance
        return [SlotSet("has_sufficient_funds", has_sufficient_funds)]

class ActionQueryStocks(Action):
    def name(self) -> Text:
        return "action_query_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global global_db_conn

        if global_db_conn is None:
            dispatcher.utter_message("Không kết nối được đến cơ sở dữ liệu.")
            return []

        try:
            cursor = global_db_conn.cursor()
            cursor.execute("SELECT * FROM stocks")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            dispatcher.utter_message(text= f"{columns}")
             # Debug info
            dispatcher.utter_message(text=f"Columns: {columns}")
            dispatcher.utter_message(text=f"Number of rows found: {len(rows)}")

            if not rows:
                dispatcher.utter_message("Không tìm thấy dữ liệu cổ phiếu.")
                return []
            else:
                # Gửi thông tin từng dòng
                for row in rows:
                    stock_info = "\n".join([f"{col}: {val}" for col, val in zip(columns, row)])
                    dispatcher.utter_message(text=f"📈 Thông tin cổ phiếu:\n{stock_info}")

        except Exception as e:
            dispatcher.utter_message(text=f"Lỗi kết nối: {str(e)}")

        return []