import sys
import config
import client
import flet as ft
import asyncio

async def save_config(inst, val):
    setattr(config, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(config).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")

async def main(page: ft.Page):
    page.clean()
    page.title = "SanChat"

    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    
    page.add(ft.Text("Вы успешно вошли в чат!", size=20))
    page.update()

async def login(page: ft.Page):
    page.clean()
    page.title = "SanChat"
    page.add(ft.Text("Вы успешно вошли в чат!", size=20))
    page.update()

async def init(page: ft.Page):
    page.title = "Welcome to SanChat"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    server_key_field = ft.TextField(
        label="Server key input", 
        hint_text="Server_key", 
        width=300
    )

    async def button_clicked(e: ft.ControlEvent):
        key = server_key_field.value
        
        if config.DEBUG:
            print(f"button go inside clicked. server_key = {key}")

        page.clean()
        page.add(
            ft.Text(
                "Welcome to SanChat!", 
                size=20, 
                weight=ft.FontWeight.BOLD, 
                theme_style=ft.TextThemeStyle.DISPLAY_LARGE
            ),
            ft.Text("Checking server availability...", size=14),
            ft.ProgressRing()
        )
        page.update()
        server_ok = client.check_server_availability(key)

        if server_ok:
            await save_config("server_key", key)
            await login(page)
        else:

            dialog = ft.AlertDialog(
                title=ft.Text("Server not available"),
                content=ft.Text("Try again later"),
            )
            if hasattr(page, "open"):
                page.open(dialog)
            else:
                page.dialog = dialog
                dialog.open = True
                page.update()

            await asyncio.sleep(3)
            sys.exit(0)

    page.add(
        ft.Text(
            "Welcome to SanChat!", 
            size=20, 
            weight=ft.FontWeight.BOLD, 
            theme_style=ft.TextThemeStyle.DISPLAY_LARGE
        ),
        server_key_field,
        ft.ElevatedButton("Go inside!", on_click=button_clicked)
    )
    page.update()
async def start():
    if config.first_time:
        await ft.run_async(init)
    else:
        await ft.run_async(main)
