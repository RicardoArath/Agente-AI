"""Parser de fechas - versión simplificada"""
from datetime import datetime, timedelta
from typing import Dict

class DateParser:
    def extract_date_range(self, message: str, single_day: bool = False) -> Dict:
        message_lower = message.lower()
        today = datetime.now()
        
        if "hoy" in message_lower:
            start = today
            end = today
        elif "mañana" in message_lower:
            start = today + timedelta(days=1)
            end = start
        elif "esta semana" in message_lower:
            start = today
            end = today + timedelta(days=7)
        else:
            start = today
            end = today + timedelta(days=7)
        
        return {
            'start_iso': start.isoformat(),
            'end_iso': end.isoformat(),
            'start_display': start.strftime('%Y-%m-%d'),
            'end_display': end.strftime('%Y-%m-%d')
        }