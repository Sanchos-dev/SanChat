import os
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
    page.title = "SanChat"

async def init(page: ft.Page):
    server_key_field_data = ""
    def handle_field_change(e: ft.Event[ft.TextField]):
        nonlocal server_key_field_data
        server_key_field_data = e.control.value
        if config.DEBUG:
            print(e.control.value)
            print(server_key_field_data)
    def button_clicked(e: ft.Event[ft.Button]):
    	if config.DEBUG:
            print(f"button go inside clicked. server_key_field_data = {server_key_field_data}")
    page.title = "Welcome to SanChat"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        ft.Text(
            "Welcome to SanChat!", 
            size=20, 
            weight=ft.FontWeight.BOLD, 
            theme_style=ft.TextThemeStyle.DISPLAY_LARGE
        ),
        ft.TextField(label="Server key input", hint_text="Server_key", on_change=handle_field_change, width=300),
        ft.Button(content="Go inside!", on_click=button_clicked,)
    )

async def start():
    if config.first_time:
        await ft.run_async(init)
    else:
        await ft.run_async(main)
