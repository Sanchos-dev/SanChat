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

async def group(page: ft.Page ):
    group_name = ""
    page.clean()
    page.title(f"Group: {group_name}")


async def dm(page: ft.Page):
    page.clean()


async def main(page: ft.Page):
    page.clean()
    page.title = "SanChat main page"
    



async def reg_custom_prof(page: ft.Page):
    avatar_local_path: str | None = None
    file_picker = ft.FilePicker()

    async def handle_avatar_change_btn(e):
        nonlocal avatar_local_path
        files = await file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
            allow_multiple=False,
        )

        if files and len(files) > 0:
            avatar_local_path = files[0].path
            avatar.foreground_image_url = avatar_local_path
            avatar.content = None
            page.update()

    async def handle_custom_btn_clck(e):
        client.customize_profile(
            disp_name_field.value,
            avatar_local_path,
            description_field.value,
        )
        await main(page)

    page.clean()
    page.title = "Customize your profile"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    avatar = ft.CircleAvatar(
        content=ft.Text("FF"),
        radius=40,
    )
    disp_name_field = ft.TextField(
        label="Profile name", hint_text="Display name", width=300
    )
    description_field = ft.TextField(
        label="Description", hint_text="Description", width=300
    )

    shesh = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.TextButton(
                content="Change avatar",
                icon=ft.Icons.STAR_BORDER,
                icon_color=ft.Colors.BLUE_300,
                on_click=handle_avatar_change_btn,
            ),
            ft.TextButton(
                content="Proceed",
                on_click=handle_custom_btn_clck,
            ),
        ],
    )

    page.add(avatar, disp_name_field, description_field, shesh)


async def login(page: ft.Page):
    async def log_clicked(e: ft.ControlEvent):
        login = login_field.value
        password = password_field.value
        if client.login(login,password):
            await main(page)
        else:
            page.add(ft.Text("Login / Password isn't correct", size=16, italic = True ,weight=ft.FontWeight.W_600, color = ft.Colors.RED))

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
    page.title = "SanChat Register"
    page.clean()
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def show_dialog(dlg: ft.AlertDialog):
        if hasattr(page, "open"):
            page.open(dlg)
            page.update()  
        else:
            if dlg not in page.overlay:
                page.overlay.append(dlg)
            dlg.open = True
            page.update()

    def close_dialog(dlg: ft.AlertDialog):
        if hasattr(page, "close"):
            page.close(dlg)
            page.update()
        else:
            dlg.open = False
            page.update()

    login_exist_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registration Error"),
        content=ft.Text("This login already exists."),
        actions=[
            ft.TextButton("OK", on_click=lambda e: close_dialog(login_exist_dialog))
        ],
    )

    password_mismatch_dialog = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("Passwords do not match."),
        actions=[
            ft.TextButton("OK", on_click=lambda e: close_dialog(password_mismatch_dialog))
        ],
    )

    general_error_dialog = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("Failed to register. Please try again later."),
        actions=[
            ft.TextButton("OK", on_click=lambda e: close_dialog(general_error_dialog))
        ],
    )

    login_field = ft.TextField(
        label="Login",
        hint_text="Enter your login",
        width=300,
        autofocus=True,
    )
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter password",
        password=True,
        can_reveal_password=True,
        width=300,
    )
    password_confirm_field = ft.TextField(
        label="Confirm Password",
        hint_text="Re-enter password",
        password=True,
        can_reveal_password=True,
        width=300,
    )

    async def reg_clicked(e: ft.ControlEvent):
        login = login_field.value.strip() if login_field.value else ""
        password = password_field.value or ""
        password_confirm = password_confirm_field.value or ""

        if not login or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in all fields."))
            page.snack_bar.open = True
            page.update()
            return

        if password != password_confirm:
            show_dialog(password_mismatch_dialog)
            return

        try:
            user_exists = client.check_reg(login)
        except Exception as err:
           return

        if user_exists:
            show_dialog(login_exist_dialog)
            return

        success = client.register(login, password)
        if success:
            await reg_custom_prof(page)
        else:
            show_dialog(general_error_dialog)

    form = ft.Column(
        controls=[
            ft.Text("Create an Account", size=24, weight=ft.FontWeight.BOLD),
            login_field,
            password_field,
            password_confirm_field,
            ft.ElevatedButton("Register", width=300, on_click=reg_clicked),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
    )

    page.add(form)




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
