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
    page.update()


async def login(page: ft.Page):
    async def log_clicked(e: ft.ControlEvent):
        login = login_field.value
        password = password_field.value
        if client.login(login,password):
            await main(page)
        else:
            print("shit")

    page.title = "SanChat login"
    page.clean()
    login_field = ft.TextField(
        label="Login", 
        hint_text="login", 
        width=300
    )
    password_field = ft.TextField(
        label="Password", 
        hint_text="password", 
        width=300
    )

    page.add(login_field,password_field, ft.ElevatedButton("Login", on_click=log_clicked))



async def register(page: ft.Page):
    async def reg_clicked(e: ft.ControlEvent):
        login = login_field.value
        password = password_field.value
        password_confirm = password_confirm_field.value
        if password == password_confirm:
            if client.check_reg(login): 
                page.open(login_exist)
                if hasattr(page, "open"):
                    page.open(login_exist)
                else:
                    page.login_exist = login_exist
                    login_exist.open = True
                    page.update()
            else:
                if client.register(login, password):
                    await main(page)
                else:
                    print("shit")

        else:
            if hasattr(page, "open"):
                page.open(password_dont_match)
            else:
                page.password_dont_match = password_dont_match
                password_dont_match.open = True
                page.update()
    page.title = "SanChat register"
    page.clean()

    login_exist = ft.AlertDialog(
        title=ft.Text("This login alredy exists"),
        content=ft.Text("This login alredy exists"),
        )

    password_dont_match = ft.AlertDialog(
        title=ft.Text("Passwords dont match"),
        content=ft.Text("Passwords dont match"),
        )
    login_field = ft.TextField(
        label="Login", 
        hint_text="login", 
        width=300
    )
    password_field = ft.TextField(
        label="Password", 
        hint_text="password", 
        width=300
    )
    password_confirm_field = ft.TextField(
        label="Confirm password", 
        hint_text="Confirm password", 
        width=300
    )
    page.add(login_field,password_field,password_confirm_field,ft.ElevatedButton("Register", on_click=reg_clicked))











async def l_or_r(page: ft.Page):
    async def login_but(e: ft.ControlEvent):
        await login(page)
        if config.DEBUG:
            print("login button clicked")

    async def register_but(e: ft.ControlEvent):
        await register(page)
        if config.DEBUG:
            print("register button clicked")

    page.clean()
    page.title = "SanChat login/register"
    page.add(ft.ElevatedButton("Login", on_click=login_but))
    page.add(ft.ElevatedButton("Register", on_click=register_but))

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
            await l_or_r(page)
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
        ft.ElevatedButton("Next", on_click=button_clicked)
    )
    page.update()

async def start():
    if config.first_time:
        await ft.run_async(init)
    else:
        await ft.run_async(main)
