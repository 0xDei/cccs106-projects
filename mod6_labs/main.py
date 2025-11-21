import flet as ft
import json, httpx
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = True
        
        # Center the window on desktop
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search_async,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search_async,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )

        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme
        )

        title_row = ft.Row([
                self.title,
                self.theme_button
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )

        self.fiveday_forcast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Current Location Weather Button
        self.current_loc = ft.ElevatedButton(
            "My Location",
            icon=ft.Icons.LOCATION_ON,
            on_click=self.get_current_location_weather,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )

        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    ft.Row([self.search_button, self.current_loc], wrap=True),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.fiveday_forcast_container
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.ALWAYS,
                expand=True
            )
        )
    
    async def on_search_async(self, e):
        """Async event handler."""
        await self.get_weather()
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city)
            await self.display_weather(weather_data)
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()

    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            # Convert existing temperature
            self.current_temp = (self.current_temp * 9/5) + 32
            self.update_display()
        else:
            self.current_unit = "metric"
            self.current_temp = (self.current_temp - 32) * 5/9
            self.update_display()
    
    async def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temperature = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)

        forecast = await self.weather_service.get_forecast(self.city_input.value.strip())
        
        temps = {}
        descriptions = {}

        for fdata in forecast["list"]:
            date = fdata["dt_txt"].split(" ")[0]
            
            if date not in temps: temps[date] = []
            if date not in descriptions: descriptions[date] = []

            temps[date].append(fdata["main"]["temp"])
            descriptions[date].append(fdata["weather"][0]["description"])

        fiveday_forcast = ft.Row([], wrap=True, alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        count = 0
        for date, temp in temps.items():
            # skip first element because that is the same date as the current
            if count == 0: 
                count += 1
                continue

            avg_temp = sum(temp) / len(temps)

            # get the most frequent na description
            desc_counts = {}
            for desc in descriptions[date]:
                if desc not in desc_counts: desc_counts[desc] = 0
                desc_counts[desc] += 1

            most_freq_desc = max(desc_counts, key=desc_counts.get)
            
            # add to fiveday_forecast row control
            fiveday_forcast.controls.append(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text(date, size=14, color=ft.Colors.GREY_700),
                            ft.Text(f"{avg_temp:.1f}°C", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                            ft.Text(most_freq_desc, size=16, color=ft.Colors.ORANGE_900)
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    width=150,
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                )
            )



        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True

        self.fiveday_forcast_container.animate_opacity = 600
        self.fiveday_forcast_container.opacity = 0
        self.fiveday_forcast_container.visible = True

        self.page.update()

        import asyncio
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.fiveday_forcast_container.opacity = 1
        self.page.update()
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                            color=ft.Colors.GREY_700
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temperature:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icon(ft.Icons.WATER_DROP, color=ft.Colors.BLUE_700),
                            "Humidity",
                            f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icon(ft.Icons.AIR, color=ft.Colors.YELLOW),
                            "Wind Speed",
                            f"{wind_speed} m/s"
                        ),
                        self.create_info_card(
                            ft.Icon(ft.Icons.COMPRESS, color=ft.Colors.RED),
                            "Pressure",
                            f"{pressure} hPa"
                        ),
                        self.create_info_card(
                            ft.Icon(ft.Icons.CLOUD, color=ft.Colors.GREY),
                            "Cloudiness",
                            f"{cloudiness}%"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.fiveday_forcast_container.content = fiveday_forcast
        
        self.error_message.visible = False
        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    icon,
                    ft.Text(label, size=12, color=ft.Colors.ORANGE_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    async def get_current_location_weather(self, e):
        """Get weather for current location using IP."""
        try:
            async with httpx.AsyncClient() as client:
                # Get location from IP
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get('city', '')
                
                if city:
                    self.city_input.value = city
                    await self.get_weather()
        except Exception as e:
            print(e)
            self.show_error("Could not detect your location:")


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)