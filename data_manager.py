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

    def get_upcoming_events(self, event_type="생일", days=30):
        if self.df is None:
            return []

        today = datetime.now()
        upcoming = []

        target_col = "생년월일" if event_type == "생일" else "현직급 임용일"
        if target_col not in self.df.columns:
            return []

        for index, row in self.df.iterrows():
            date_str = str(row[target_col])
            try:
                # Format is YYYY.MM.DD
                parts = date_str.strip().split('.')
                if len(parts) == 3:
                    month = int(parts[1])
                    day = int(parts[2])
                    
                    # Create date object for this year
                    event_date = datetime(today.year, month, day)
                    
                    # If it already passed this year, check next year
                    if event_date < today:
                        event_date = datetime(today.year + 1, month, day)
                        
                    delta = (event_date - today).days
                    if 0 <= delta <= days:
                        upcoming.append({
                            "성명": row["성명"],
                            "직급": row["직급"],
                            "부서": "알 수 없음", # Data doesn't have department
                            "이벤트": event_type,
                            "날짜": f"{month}월 {day}일",
                            "D-Day": delta
                        })
            except Exception as e:
                pass
        
        return sorted(upcoming, key=lambda x: x["D-Day"])

    def get_member_info(self, name):
        if self.df is None:
            return None
        
        result = self.df[self.df["성명"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None
