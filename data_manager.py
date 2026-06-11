import pandas as pd
from datetime import datetime, timedelta
import os

class DataManager:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = None
        self.load_data()

    def load_data(self):
        try:
            self.df = pd.read_excel(self.excel_path)
        except Exception as e:
            print(f"Failed to load excel: {e}")

    def get_all_members(self):
        if self.df is None:
            return []

        today = datetime.now()
        members = []

        for index, row in self.df.iterrows():
            closest_event = "생일"
            min_days = 999
            
            for event_type, target_col in [("생일", "생년월일"), ("승진", "현직급 임용일")]:
                if target_col in self.df.columns:
                    date_str = str(row[target_col])
                    try:
                        parts = date_str.strip().split('.')
                        if len(parts) == 3:
                            month, day = int(parts[1]), int(parts[2])
                            event_date = datetime(today.year, month, day)
                            if event_date < today:
                                event_date = datetime(today.year + 1, month, day)
                            delta = (event_date - today).days
                            if delta < min_days:
                                min_days = delta
                                closest_event = event_type
                    except Exception:
                        pass
            
            members.append({
                "성명": row["성명"],
                "직급": row.get("직급", ""),
                "defaultType": closest_event,
                "D-Day": min_days if min_days != 999 else "-"
            })
            
        return sorted(members, key=lambda x: x["D-Day"] if isinstance(x["D-Day"], int) else 9999)

    def get_member_info(self, name):
        if self.df is None:
            return None
        
        result = self.df[self.df["성명"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
