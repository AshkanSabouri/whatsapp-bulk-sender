# main.py

import time
import os
import sys
import urllib.parse
import pandas as pd
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, ListProperty

from translations import tr, get_lang, set_lang


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def register_persian_font():
    try:
        LabelBase.register(name="IRANSans", fn_regular=resource_path("fonts/IRANSans.ttf"))
    except:
        pass


# ------------------------------
# Config
# ------------------------------
APP_VERSION = "v1.5.0"
NEED_CHROME_VERSION = 142
QR_SCAN_TIMEOUT = 60
START_SEND_TIMEOUT = 20
EXIT_DRIVER_TIMEOUT = 10
QR_PATH = "qr_code.png"
driver = None
CHROMEDRIVER_PATH = resource_path("drivers/chromedriver")
KEEP_SESSION = False


# ------------------------------
# Selenium & WhatsApp functions
# ------------------------------
def is_chrome_version_compatible(driver):
    try:
        caps = driver.capabilities
        browser_version = caps.get('browserVersion')
        if not browser_version:
            chrome_info = caps.get('chrome', {})
            cd_version = chrome_info.get('chromedriverVersion', '')
            if cd_version:
                browser_version = cd_version.split(' ')[0]
        if not browser_version:
            return False, "Unknown"
        major_version = int(browser_version.split('.')[0])
        return major_version >= NEED_CHROME_VERSION, browser_version
    except:
        return False, "Version check error"


def capture_qr_code():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--window-size=800,1000")
    chrome_options.add_argument("--window-position=10000,0")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service(CHROMEDRIVER_PATH)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        err_msg = str(e)
        if "This version of ChromeDriver only supports Chrome version" in err_msg:
            import re
            match = re.search(r"only supports Chrome version (\d+)", err_msg)
            needed = match.group(1) if match else "148+"
            return False, f"Chrome version {needed}+ required."
        else:
            return False, f"Chrome startup error: {err_msg}"

    compatible, version = is_chrome_version_compatible(driver)
    if not compatible:
        driver.quit()
        return False, f"Chrome version ({version}) is too old. Update to {NEED_CHROME_VERSION}+."

    driver.get("https://web.whatsapp.com")
    print("Loading WhatsApp Web...")

    for i in range(35):
        time.sleep(1)
        try:
            qr_canvas = driver.find_element(
                By.XPATH,
                '//canvas[@aria-label="Scan this QR code to link a device!"]'
            )
            time.sleep(1.5)
            qr_temp_path = os.path.join(os.getcwd(), QR_PATH)
            qr_canvas.screenshot(qr_temp_path)

            from PIL import Image as PILImage
            if os.path.exists(qr_temp_path):
                img = PILImage.open(qr_temp_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                border = 10
                new_img = PILImage.new("RGB", (img.width + 2*border, img.height + 2*border), (255,255,255))
                new_img.paste(img, (border, border))
                new_img.save(qr_temp_path, quality=98)
            return True, None
        except:
            continue

    driver.quit()
    return False, "Failed to capture QR code."


def send_msg(phone, msg):
    global driver
    try:
        url = f"https://web.whatsapp.com/send?phone={phone}&text={msg}"
        driver.get(url)
        time.sleep(7)
        message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        message_box.send_keys(" ")
        time.sleep(0.5)
        message_box.send_keys(Keys.ENTER)
        return True
    except Exception as e:
        print(f"Error sending to {phone}: {e}")
        return False


# ------------------------------
# UI Components
# ------------------------------
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(16)
        self.spacing = dp(12)
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14),])

    def _update_canvas(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_name = "IRANSans" if get_lang() == 'fa' else "Roboto"
        self.font_size = dp(16)
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.145, 0.639, 0.396, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12),])


class StyledLabel(Label):
    def __init__(self, **kwargs):
        lang = get_lang()
        kwargs.setdefault('halign', 'right' if lang == 'fa' else 'left')
        kwargs.setdefault('font_name', 'IRANSans' if lang == 'fa' else 'Roboto')
        kwargs.setdefault('color', (0, 0, 0, 1))
        kwargs.setdefault('font_size', dp(14))
        kwargs.setdefault('text_size', (self.width, None))
        kwargs.setdefault('valign', 'middle')
        super().__init__(**kwargs)
        self.bind(size=lambda *x: setattr(self, 'text_size', (self.width, None)))


class CustomCheckBox(Widget):
    active = BooleanProperty(False)
    color_active = ListProperty([0.145, 0.639, 0.396, 1])   # WhatsApp green
    color_inactive = ListProperty([0.85, 0.85, 0.85, 1])    # Light gray
    size_box = ListProperty([dp(22), dp(22)])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = self.size_box
        self.bind(pos=self.update_canvas, size=self.update_canvas, active=self.update_canvas)
        self.update_canvas()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = not self.active
            return True
        return super().on_touch_down(touch)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            color = self.color_active if self.active else self.color_inactive
            Color(*color)
            Rectangle(pos=self.pos, size=self.size_box)
            # No tick — only colored square


# ------------------------------
# Main App
# ------------------------------
class WhatsAppKivyApp(App):
    def build(self):
        self.title = "WhatsApp Marketing Bot"
        self.excel_path = ""
        self.wait_time = 10
        self.df = None
        self.current_index = 0

        from kivy.core.window import Window
        Window.minimum_width = 700
        Window.minimum_height = 680
        Window.size = (800, 750)
        Window.clearcolor = (0.96, 0.96, 0.96, 1)

        try:
            Window.set_icon(resource_path('img/icon.png'))
        except:
            pass

        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # === Header ===
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45))
        self.title_label = Label(
            text="WhatsApp Marketing Bot",
            font_size=dp(18),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='left',
            valign='middle',
            size_hint_x=None,
            width=dp(260),
            text_size=(dp(260), None)
        )
        self.version_label = Label(
            text="",
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign='right',
            size_hint_x=1
        )
        header.add_widget(self.title_label)
        header.add_widget(self.version_label)
        root.add_widget(header)

        # === File Selection Card ===
        file_card = Card()
        self.file_title_label = StyledLabel(text="")
        self.file_button = StyledButton(text="", size_hint_y=None, height=dp(45))
        self.file_button.bind(on_press=self.open_file_chooser)
        self.file_label = StyledLabel(text="")
        file_card.add_widget(self.file_title_label)
        file_card.add_widget(self.file_button)
        file_card.add_widget(self.file_label)
        file_card.height = dp(130)
        root.add_widget(file_card)

        # === Settings Card ===
        settings_card = Card()
        self.delay_title_label = StyledLabel(text="")
        self.delay_input = TextInput(
            text="10",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(40),
            halign="center",
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1),
            padding=(dp(10), dp(10)),
            cursor_color=(0.145, 0.639, 0.396, 1)
        )
        settings_card.add_widget(self.delay_title_label)
        settings_card.add_widget(self.delay_input)

        ctrl_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(15))
        session_layout = BoxLayout(orientation='horizontal', size_hint_x=0.6, spacing=dp(10))
        self.keep_session_checkbox = CustomCheckBox()
        self.keep_session_label = StyledLabel(text="")
        session_layout.add_widget(self.keep_session_checkbox)
        session_layout.add_widget(self.keep_session_label)
        ctrl_row.add_widget(session_layout)

        self.lang_spinner = Spinner(
            text="Persian",
            values=["Persian", "English"],
            size_hint_x=0.4,
            background_color=(0.145, 0.639, 0.396, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        self.lang_spinner.bind(text=self.on_lang_select)
        ctrl_row.add_widget(self.lang_spinner)
        settings_card.add_widget(ctrl_row)
        settings_card.height = dp(140)
        root.add_widget(settings_card)

        # === Status & Progress Card ===
        status_card = Card()
        self.contact_count_label = StyledLabel(text="")
        self.current_status = StyledLabel(text="", font_size=dp(13), color=(0.2, 0.2, 0.2, 1))
        self.progress_label = StyledLabel(text="0%", font_size=dp(12), color=(0.4, 0.4, 0.4, 1))
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(8))
        status_card.add_widget(self.contact_count_label)
        status_card.add_widget(self.current_status)
        status_card.add_widget(self.progress_label)
        status_card.add_widget(self.progress_bar)
        status_card.height = dp(130)
        root.add_widget(status_card)

        # === QR Preview Card ===
        qr_card = Card(padding=dp(12))
        self.qr_title_label = StyledLabel(text="")
        self.qr_image = Image(source="", size_hint_y=0.8, allow_stretch=True, keep_ratio=True)
        qr_card.add_widget(self.qr_title_label)
        qr_card.add_widget(self.qr_image)
        qr_card.height = dp(280)
        root.add_widget(qr_card)

        # === Start Button ===
        self.start_button = StyledButton(text="", size_hint_y=None, height=dp(55))
        self.start_button.bind(on_press=self.on_start_button)
        root.add_widget(self.start_button)

        # Final UI refresh
        self.refresh_ui()
        return root

    # Language mapping
    lang_display_to_code = {"Persian": "fa", "English": "en"}
    lang_code_to_display = {"fa": "Persian", "en": "English"}

    def on_lang_select(self, spinner, text):
        lang_code = self.lang_display_to_code.get(text, 'en')
        set_lang(lang_code)
        if lang_code == 'fa':
            register_persian_font()
        self.refresh_ui()

    def refresh_ui(self):
        lang = get_lang()

        # Set fonts for dynamic widgets
        self.file_button.font_name = "IRANSans" if lang == 'fa' else "Roboto"
        self.delay_input.font_name = "IRANSans" if lang == 'fa' else "Roboto"
        self.start_button.font_name = "IRANSans" if lang == 'fa' else "Roboto"
        self.lang_spinner.font_name = "IRANSans" if lang == 'fa' else "Roboto"

        # Update all texts
        self.version_label.text = tr("version", version=APP_VERSION)
        self.file_title_label.text = tr("select_excel")
        self.file_button.text = tr("select_excel")
        self.file_label.text = tr("no_file") if not self.excel_path else os.path.basename(self.excel_path)
        self.delay_title_label.text = tr("delay_label")
        self.keep_session_label.text = tr("keep_session")
        self.lang_spinner.text = self.lang_code_to_display[lang]
        self.start_button.text = tr("send_btn")
        self.qr_title_label.text = tr("scan_qr")

        if self.df is not None:
            count = len(self.df)
            self.contact_count_label.text = tr("contacts_count", count=count)

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        filechooser = FileChooserIconView(filters=["*.xlsx", "*.xls"])
        select_btn = StyledButton(text=tr("select_excel"), size_hint=(1, 0.12))
        content.add_widget(filechooser)
        content.add_widget(select_btn)

        popup = Popup(
            title=tr("select_excel"),
            content=content,
            size_hint=(0.9, 0.9),
            background_color=(0.98, 0.98, 0.98, 1),
            title_font="IRANSans" if get_lang() == 'fa' else "Roboto"
        )

        def select_file(btn):
            if filechooser.selection:
                self.excel_path = filechooser.selection[0]
                self.file_label.text = os.path.basename(self.excel_path)
                try:
                    self.df = pd.read_excel(self.excel_path)
                    count = len(self.df)
                    self.contact_count_label.text = tr("contacts_count", count=count)
                    self.start_button.disabled = False
                except:
                    self.contact_count_label.text = tr("read_error")
            popup.dismiss()

        select_btn.bind(on_press=select_file)
        popup.open()

    def show_chrome_update_popup(self, version):
        content = BoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20))
        label = StyledLabel(
            text=tr("chrome_update_msg"),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(120),
            font_size=dp(15),
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(20), None)))

        btn = StyledButton(text=tr("got_it"), size_hint=(0.5, None), height=dp(48))
        btn_container = BoxLayout(size_hint_y=None, height=dp(60))
        btn_container.add_widget(Label())
        btn_container.add_widget(btn)
        btn_container.add_widget(Label())

        content.add_widget(label)
        content.add_widget(Label(size_hint_y=None, height=dp(10)))
        content.add_widget(btn_container)

        popup = Popup(
            title=tr("chrome_update_title"),
            content=content,
            size_hint=(0.75, 0.5),
            auto_dismiss=False,
            separator_color=(0.145, 0.639, 0.396, 1),
            title_font="IRANSans" if get_lang() == 'fa' else "Roboto",
            title_size=dp(18),
            title_color=(1, 1, 1, 1),
            background_color=(1, 1, 1, 1),
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_start_button(self, instance):
        global KEEP_SESSION
        if not self.excel_path or self.df is None:
            self.current_status.text = tr("invalid_file")
            return

        try:
            self.wait_time = int(self.delay_input.text) or 10
        except:
            self.wait_time = 10

        KEEP_SESSION = self.keep_session_checkbox.active

        self.start_button.disabled = True
        self.current_status.text = tr("browser_loading")
        self.progress_bar.value = 0
        self.progress_label.text = "0%"
        Thread(target=self.connect_and_send, daemon=True).start()

    def connect_and_send(self):
        global driver, KEEP_SESSION
        if driver is None:
            success, error_msg = capture_qr_code()
            if not success:
                def schedule_error(dt):
                    if "old" in error_msg.lower() or "update" in error_msg.lower() or str(NEED_CHROME_VERSION) in error_msg:
                        self.show_chrome_update_popup("Unknown")
                    else:
                        msg = tr("browser_error") + f"\n{error_msg}"
                        self.current_status.text = msg
                    self.start_button.disabled = False
                Clock.schedule_once(schedule_error, 0)
                return

            Clock.schedule_once(lambda dt: self.update_qr(), 0)
            Clock.schedule_once(lambda dt: setattr(self.current_status, 'text', tr("scan_qr")), 0)

            wait_counter = 0
            while wait_counter < QR_SCAN_TIMEOUT:
                try:
                    driver.find_element(By.XPATH, '//canvas')
                    time.sleep(2)
                    wait_counter += 2
                except:
                    break

            if wait_counter >= QR_SCAN_TIMEOUT:
                Clock.schedule_once(lambda dt: setattr(self.current_status, 'text', tr("connection_failed")), 0)
                Clock.schedule_once(lambda dt: setattr(self.start_button, 'disabled', False), 0)
                return

        Clock.schedule_once(lambda dt: setattr(self.current_status, 'text', tr("connected")), 0)
        time.sleep(START_SEND_TIMEOUT)

        total = len(self.df)
        possible_columns = {
            'name': ['نام', 'name'],
            'family': ['نام خانوادگی', 'family'],
            'prefix': ['پیشوند', 'prefix'],
            'phone': ['شماره همراه', 'phone'],
            'message': ['متن پیام', 'message']
        }

        def get_value(row, keys):
            for key in keys:
                if key in row and not pd.isna(row[key]):
                    val = str(row[key]).strip()
                    if val.lower() not in ('nan', 'none', 'null', ''):
                        return val
            return ''

        for idx in range(len(self.df)):
            row = self.df.iloc[idx]
            name = get_value(row, possible_columns['name'])
            family = get_value(row, possible_columns['family'])
            prefix = get_value(row, possible_columns['prefix'])
            phone_raw = get_value(row, possible_columns['phone'])
            body = get_value(row, possible_columns['message'])

            if not phone_raw:
                continue

            phone = ''.join(filter(str.isdigit, phone_raw))
            full_name = ' '.join([x for x in [name, family] if x]).strip() or "User"
            msg_lines = [x for x in [prefix, full_name if full_name != "User" else "", body] if x]
            full_message = '\n'.join(msg_lines).strip() or "(No message)"
            encoded_msg = urllib.parse.quote(full_message)
            status_text = tr("sending_to", name=full_name, phone=phone)

            Clock.schedule_once(lambda dt, s=status_text: setattr(self.current_status, 'text', s), 0)
            progress = (idx + 1) / total * 100
            Clock.schedule_once(lambda dt, p=progress: setattr(self.progress_bar, 'value', p), 0)
            Clock.schedule_once(lambda dt, p=int(progress): setattr(self.progress_label, 'text', f"{p}%"), 0)

            success = send_msg(phone, encoded_msg)
            if not success:
                print(f"⚠️ Failed to send to {phone}")

            if idx < total - 1:
                time.sleep(self.wait_time)

        Clock.schedule_once(lambda dt: setattr(self.current_status, 'text', tr("all_sent")), 0)
        time.sleep(EXIT_DRIVER_TIMEOUT)

        if driver and not KEEP_SESSION:
            try:
                driver.quit()
            except:
                pass
            driver = None

        Clock.schedule_once(lambda dt: setattr(self.start_button, 'disabled', False), 0)

    def update_qr(self):
        qr_path = os.path.join(os.getcwd(), QR_PATH)
        if os.path.exists(qr_path):
            self.qr_image.source = qr_path
            self.qr_image.reload()


# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    if get_lang() == 'fa':
        register_persian_font()
    WhatsAppKivyApp().run()