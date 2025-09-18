import flet as ft
from database import *
import re

def display_contacts(page, contacts_list_view, db_conn, search=None):
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contacts_list_view.controls.append(
            ft.Card(
                ft.ListTile(
                    title=ft.Row([ft.Icon(ft.Icons.PERSON), ft.Text(name)]),
                    subtitle=ft.Column([
                        ft.Divider(),
                        ft.Row([ft.Icon(ft.Icons.PHONE, size=15), ft.Text(phone)]),
                        ft.Row([ft.Icon(ft.Icons.EMAIL, size=15), ft.Text(email)])
                        ]),
                    trailing=ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                text="Edit",
                                icon=ft.Icons.EDIT,
                                on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                            ),
                            ft.PopupMenuItem(
                                text="Delete",
                                icon=ft.Icons.DELETE,
                                on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view)
                            )
                        ]
                    )
                )  
            )
        )
    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    name_input, phone_input, email_input, = inputs

    if name_input.value.strip() == "":
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    name_input.error_text = ""

    if phone_input.value.isdigit() == False:
        phone_input.error_text = "Invalid phone number"
        page.update()
        return
    phone_input.error_text = ""
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(regex, email_input.value):
        email_input.error_text = "Invalid Email"
        page.update()
        return
    email_input.error_text = ""

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page, contact_id, db_conn, contacts_list_view):

    def delete_and_close(e):
        dialog.open = False
        page.update()
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmation"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("No", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Yes", on_click=delete_and_close)
        ]
    )

    page.open(dialog)

def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact

    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close)
        ]
    )

    page.open(dialog)

def search_contact(page, contacts_list_view, db_conn, search):
    if search.strip() == "": display_contacts(page, contacts_list_view, db_conn)
    else: display_contacts(page, contacts_list_view, db_conn, search)

def toggle_theme(page):
    if page.theme_mode == ft.ThemeMode.LIGHT: mode = ft.ThemeMode.DARK
    else: mode = ft.ThemeMode.LIGHT
    page.theme_mode = mode
    page.update()
    