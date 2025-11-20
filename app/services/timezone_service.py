"""
Service for checking timezone and business hours
"""
from typing import Dict, Any, Optional
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

class TimezoneService:
    """
    Service for checking if current time is within business hours in a lead's timezone
    """
    
    # Map countries to their primary timezone
    COUNTRY_TIMEZONE_MAP = {
        "United States": "America/New_York",
        "USA": "America/New_York",
        "US": "America/New_York",
        "India": "Asia/Kolkata",
        "United Kingdom": "Europe/London",
        "UK": "Europe/London",
        "Canada": "America/Toronto",
        "Australia": "Australia/Sydney",
        "Germany": "Europe/Berlin",
        "France": "Europe/Paris",
        "Japan": "Asia/Tokyo",
        "China": "Asia/Shanghai",
        "Brazil": "America/Sao_Paulo",
        "Mexico": "America/Mexico_City",
        "Spain": "Europe/Madrid",
        "Italy": "Europe/Rome",
        "Netherlands": "Europe/Amsterdam",
        "Belgium": "Europe/Brussels",
        "Switzerland": "Europe/Zurich",
        "Sweden": "Europe/Stockholm",
        "Norway": "Europe/Oslo",
        "Denmark": "Europe/Copenhagen",
        "Poland": "Europe/Warsaw",
        "Russia": "Europe/Moscow",
        "South Korea": "Asia/Seoul",
        "Singapore": "Asia/Singapore",
        "Hong Kong": "Asia/Hong_Kong",
        "Taiwan": "Asia/Taipei",
        "Thailand": "Asia/Bangkok",
        "Indonesia": "Asia/Jakarta",
        "Malaysia": "Asia/Kuala_Lumpur",
        "Philippines": "Asia/Manila",
        "Vietnam": "Asia/Ho_Chi_Minh",
        "New Zealand": "Pacific/Auckland",
        "South Africa": "Africa/Johannesburg",
        "UAE": "Asia/Dubai",
        "United Arab Emirates": "Asia/Dubai",
        "Saudi Arabia": "Asia/Riyadh",
        "Israel": "Asia/Jerusalem",
        "Turkey": "Europe/Istanbul",
        "Argentina": "America/Argentina/Buenos_Aires",
        "Chile": "America/Santiago",
        "Colombia": "America/Bogota",
        "Peru": "America/Lima",
        "Venezuela": "America/Caracas",
    }
    
    def get_timezone_for_country(self, country: Optional[str]) -> str:
        """
        Get timezone for a country
        
        Args:
            country: Country name
        
        Returns:
            Timezone string (defaults to UTC if country not found)
        """
        if not country:
            return "UTC"
        
        # Try exact match first
        country_normalized = country.strip()
        if country_normalized in self.COUNTRY_TIMEZONE_MAP:
            return self.COUNTRY_TIMEZONE_MAP[country_normalized]
        
        # Try case-insensitive match
        country_lower = country_normalized.lower()
        for country_key, timezone in self.COUNTRY_TIMEZONE_MAP.items():
            if country_key.lower() == country_lower:
                return timezone
        
        # Default to UTC if not found
        logger.warning(f"Timezone not found for country '{country}', defaulting to UTC")
        return "UTC"
    
    def is_business_hours(self, timezone: str, start_hour: int = 9, end_hour: int = 19) -> Dict[str, Any]:
        """
        Check if current time is within business hours (Mon-Fri, 9 AM - 7 PM)
        
        Args:
            timezone: Timezone string (e.g., "Asia/Kolkata", "America/New_York")
            start_hour: Business hours start (default: 9)
            end_hour: Business hours end (default: 19, which is 7 PM)
        
        Returns:
            Dict with:
                - is_business_hours: bool
                - current_time: datetime in that timezone
                - day_of_week: int (0=Monday, 6=Sunday)
                - day_name: str
                - reason: str (why it's not business hours if applicable)
        """
        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            current_hour = now.hour
            day_of_week = now.weekday()  # 0=Monday, 6=Sunday
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Check if it's a weekday (Monday=0 to Friday=4)
            is_weekday = day_of_week < 5
            
            # Check if it's within business hours
            is_within_hours = start_hour <= current_hour < end_hour
            
            is_business_time = is_weekday and is_within_hours
            
            reason = None
            if not is_business_time:
                if not is_weekday:
                    reason = f"It's {day_names[day_of_week]} (weekend)"
                elif current_hour < start_hour:
                    reason = f"Too early ({current_hour}:00 < {start_hour}:00)"
                elif current_hour >= end_hour:
                    reason = f"Too late ({current_hour}:00 >= {end_hour}:00)"
            
            return {
                "is_business_hours": is_business_time,
                "current_time": now,
                "timezone": timezone,
                "day_of_week": day_of_week,
                "day_name": day_names[day_of_week],
                "current_hour": current_hour,
                "is_weekday": is_weekday,
                "reason": reason
            }
        
        except Exception as e:
            logger.error(f"Error checking business hours for timezone {timezone}: {e}")
            # Default to UTC
            now = datetime.utcnow()
            return {
                "is_business_hours": False,
                "current_time": now,
                "timezone": "UTC",
                "day_of_week": now.weekday(),
                "day_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][now.weekday()],
                "current_hour": now.hour,
                "is_weekday": now.weekday() < 5,
                "reason": f"Error checking timezone: {str(e)}"
            }
    
    def check_lead_business_hours(self, country: Optional[str], start_hour: int = 9, end_hour: int = 19) -> Dict[str, Any]:
        """
        Check if it's business hours for a lead based on their country
        
        Args:
            country: Lead's country
            start_hour: Business hours start (default: 9)
            end_hour: Business hours end (default: 19, which is 7 PM)
        
        Returns:
            Dict with business hours check result
        """
        timezone = self.get_timezone_for_country(country)
        result = self.is_business_hours(timezone, start_hour, end_hour)
        result["country"] = country
        return result

