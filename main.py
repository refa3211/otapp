import threading
from datetime import datetime
import time
import flet as ft
import pyotp
from assets import JSONManager, parse
js = JSONManager.JSONManager(file_path=r'assets\otp_secrets.json')


class OTPTimer(ft.UserControl):
    def __init__(self, account_name, otp_key):
        super().__init__()
        self.otp_key = otp_key
        self.otp_text = ft.Text(size=30, text_align=ft.alignment.center)
        self.account_name = account_name
        self.countdown_text = ft.Text(size=30, color=ft.colors.DEEP_PURPLE_500)
        self.progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=18)

    def show_snakebar(self, e):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("OTP copied to clipboard"),
            duration=2000,)
        self.page.snack_bar.open = True
        self.page.update()
        
        try: 
            self.page.set_clipboard(self.otp_text.value) 
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
            content=ft.Text(e),
            duration=5000,)
            self.page.snack_bar.open = True
            self.page.update()
            

    def remove_instance(self, e):
        def remove_confirmed(e):
            print(f"e {e.data}")
            self.page.dialog.open = False
            js.delete_key_value(key=self.account_name)
            self.page.remove(self)
            self.page.update()

        def close_dlg(e):
            self.page.dialog.open = False
            print("closed")
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Remove"),
            content=ft.Text(f"Are you sure you want to remove the OTP for '{self.account_name}'?"),
            actions=[
                ft.TextButton("Yes", on_click=remove_confirmed),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def build(self):
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(self.account_name, size=14)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.otp_text, self.countdown_text, self.progress_ring],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )
        return ft.Container(
            content=content,
            ink=True,
            margin=1,
            border_radius=10,
            width=350,
            height=100,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.LIGHT_BLUE_100,
            on_click=self.show_snakebar,
            on_long_press=self.remove_instance
        )


def update_otps_and_timers(otptimer_instances):
    current_sec = datetime.now().second
    countdown = 30 - (current_sec % 30)
    progress = countdown / 30.0

    for instance in otptimer_instances.values():
        totp = pyotp.TOTP(instance.otp_key)
        instance.otp_text.value = f"{totp.now()}"
        instance.countdown_text.value = f"{countdown}"
        instance.progress_ring.value = progress
        instance.update()


def main(page: ft.Page):
    page.scroll = "ADAPTIVE"
    page.window_width = 400
    page.window_height = 600
    page.window_max_width = 400
    page.window_max_height = 600
    page.theme_mode = page.theme_mode.LIGHT
    page.title = "OTP App"
    page.horizontal_alignment = 'CENTER'
    text_field = ft.TextField(hint_text="Add otp", width=280, border_radius=15)
    floatbutton = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=lambda e: add_otp(otp_uri=text_field.value))
    #top container text filed and button
    top_ct = ft.Container(
        content=ft.Row([text_field,floatbutton]),
        margin=3,  
    )
    top_ct.padding = ft.padding.only(top=27)

    def snackbar(snake_text):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(snake_text),
            duration=2000,)
        page.snack_bar.open = True
        page.update()
    
    secret_dict = js.read_json()
    otptimer_instances = {account_name: OTPTimer(account_name, secret) for account_name, secret in secret_dict.items()}

    def add_otp(otp_uri):
        text_field.value = ""
        try:
            account_name, secret = parse.parse_otpauth_uri(otp_uri)
            if account_name in otptimer_instances:
                snackbar("OTP already added")
                return
            otptimer_instance = OTPTimer(account_name, secret)
            otptimer_instances[account_name] = otptimer_instance
            page.add(otptimer_instance)
            secret_dict[account_name] = secret

            js.add_key_value(key=account_name, value=secret)
        except (ValueError, IndexError):
            snackbar("Invalid OTP URI")

    text_field.on_submit = lambda e: add_otp(otp_uri=text_field.value)

    page.add(
        ft.Row(
            [top_ct],alignment=ft.MainAxisAlignment.CENTER
        )
    )

    for instance in otptimer_instances.values():
        page.add(instance)

    def timer_thread():
        while True:
            update_otps_and_timers(otptimer_instances)
            time.sleep(1)

    threading.Thread(target=timer_thread, daemon=True).start()


ft.app(target=main)
