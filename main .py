from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

from plyer import gps


class Root(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=16, spacing=12, **kwargs)

        self.status = Label(text="לחץ 'התחל' כדי לבקש הרשאת מיקום ולקרוא GPS", halign="right")
        self.coords = Label(text="Lat: -\nLon: -\nAlt: -\nSpeed: -", halign="right")
        self.err = Label(text="", halign="right")

        self.btn_start = Button(text="התחל", size_hint=(1, None), height=52)
        self.btn_stop = Button(text="עצור", size_hint=(1, None), height=52, disabled=True)

        self.btn_start.bind(on_press=self.start_gps)
        self.btn_stop.bind(on_press=self.stop_gps)

        self.add_widget(self.status)
        self.add_widget(self.coords)
        self.add_widget(self.err)
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_stop)

        self._gps_running = False

    def start_gps(self, *_):
        if self._gps_running:
            return

        self.err.text = ""
        self.status.text = "מבקש הרשאה… (בפעם הראשונה תופיע בקשת מיקום)"

        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            # minTime: מילישניות בין עדכונים, minDistance: מטרים בין עדכונים
            gps.start(minTime=1000, minDistance=0)
            self._gps_running = True
            self.btn_start.disabled = True
            self.btn_stop.disabled = False
        except Exception as e:
            self.err.text = f"שגיאה בהפעלת GPS: {e}"
            self.status.text = "נכשל בהפעלת GPS"

    def stop_gps(self, *_):
        if not self._gps_running:
            return
        try:
            gps.stop()
        except Exception:
            pass
        self._gps_running = False
        self.status.text = "GPS נעצר"
        self.btn_start.disabled = False
        self.btn_stop.disabled = True

    def on_location(self, **kwargs):
        # kwargs לדוגמה: lat, lon, altitude, speed, bearing, accuracy...
        lat = kwargs.get("lat")
        lon = kwargs.get("lon")
        alt = kwargs.get("altitude")
        spd = kwargs.get("speed")

        self.status.text = "קיבלתי מיקום ✅"
        self.coords.text = (
            f"Lat: {lat}\n"
            f"Lon: {lon}\n"
            f"Alt: {alt}\n"
            f"Speed: {spd}"
        )

    def on_status(self, stype, status):
        # סטטוסים משתנים לפי מערכת
        self.status.text = f"סטטוס: {stype} | {status}"


class GPSApp(App):
    def build(self):
        return Root()


if __name__ == "__main__":
    GPSApp().run()
