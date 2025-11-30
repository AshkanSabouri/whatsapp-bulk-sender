# translations.py

import arabic_reshaper
from bidi.algorithm import get_display

# Current active language (can be changed at runtime)
_CURRENT_LANG = 'fa'

_TRANSLATIONS = {
    "fa": {
        "select_excel": "انتخاب فایل اکسل",
        "no_file": "فایلی انتخاب نشده",
        "delay_label": "فاصله بین پیام‌ها (ثانیه):",
        "contacts_count": "تعداد مخاطبین: {count} نفر",
        "read_error": "خطا در خواندن فایل!",
        "send_btn": "ارسال پیام ها",
        "browser_loading": "در حال راه‌اندازی مرورگر...",
        "scan_qr": "لطفاً QR را با گوشی خود اسکن کنید...",
        "connected": "اتصال برقرار شد. در حال آماده‌سازی...",
        "all_sent": "همه پیام‌ها ارسال شدند!",
        "invalid_file": "فایل اکسل معتبر نیست!",
        "connection_failed": "❌ اتصال ناموفق.",
        "browser_error": "❌ خطا در راه‌اندازی مرورگر",
        "chrome_update_title": "نیاز به آپدیت مرورگر",
        "chrome_update_msg": "برای اجرای این برنامه، مرورگر کروم شما نیازمند آپدیت به آخرین نسخه است!\nلطفاً مرورگر خود را بسته و از طریق تنظیمات یا وبسایت رسمی کروم، آن را به‌روزرسانی کنید، سپس مجدداً تلاش نمایید.",
        "got_it": "متوجه شدم",
        "version": "Version: {version}",
        "language": "انتخاب زبان",
        "keep_session": "باز نگه داشتن نشست واتساپ پس از ارسال",
        "sending_to": "در حال ارسال به: {name} ({phone})",
        "WhatsApp Marketing Bot": "ربات بازاریابی واتس اپ",
    },
    "en": {
        "select_excel": "Select Excel File",
        "no_file": "No file selected",
        "delay_label": "Delay between messages (seconds):",
        "contacts_count": "Contacts: {count}",
        "read_error": "Error reading file!",
        "send_btn": "Send Messages",
        "browser_loading": "Launching browser...",
        "scan_qr": "Please scan the QR code with your phone...",
        "connected": "Connected. Preparing to send...",
        "all_sent": "All messages sent!",
        "invalid_file": "Invalid Excel file!",
        "connection_failed": "❌ Connection failed.",
        "browser_error": "❌ Browser startup error",
        "chrome_update_title": "Browser Update Required",
        "chrome_update_msg": "This app requires the latest version of Chrome.\nPlease close Chrome, update it via settings or chrome.com, then try again.",
        "got_it": "Got it",
        "version": "Version: {version}",
        "language": "Language",
        "keep_session": "Keep WhatsApp session open after sending",
        "sending_to": "Sending to: {name} ({phone})",
    }
}

def get_lang():
    return _CURRENT_LANG

def set_lang(lang_code):
    global _CURRENT_LANG
    if lang_code in ("fa", "en"):
        _CURRENT_LANG = lang_code
    else:
        raise ValueError("Unsupported language")

def tr(key, **kwargs):
    lang = _CURRENT_LANG
    text = _TRANSLATIONS.get(lang, _TRANSLATIONS["fa"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    if lang == "fa":
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text