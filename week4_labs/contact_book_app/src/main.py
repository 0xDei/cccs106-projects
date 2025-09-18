import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact, search_contact, toggle_theme

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    db_conn = init_db()
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    inputs = (name_input, phone_input, email_input)
    contacts_list_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )
    toggle_theme_switch = ft.Switch(label_position=ft.LabelPosition.LEFT, label="Dark Mode", on_change=lambda e: toggle_theme(page), height=30)

    page.add(
        ft.Row([
            ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([toggle_theme_switch], expand=True, alignment=ft.MainAxisAlignment.END)
        ]),
        ft.Column(
            [
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.SearchBar(bar_hint_text="Search contact", width=350, height=35, on_submit=lambda e: search_contact(page, contacts_list_view, db_conn, e.control.value)),
                ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ]
        )
    )
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)