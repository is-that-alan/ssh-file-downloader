import glob
import os
import re

import paramiko
import PySimpleGUI as sg
from fabric import Connection


def connect_and_download(
    host, user, private_key_file_path, ssh_file_path, download_location
):
    key = paramiko.RSAKey.from_private_key_file(private_key_file_path)
    conn = Connection(host, user=user, connect_kwargs={"pkey": key})
    conn.get(ssh_file_path, local=download_location)


def test_connection(host, user, private_key_file_path):
    if not os.path.isfile(private_key_file_path):
        sg.Popup("Private key file does not exist")
        return False

    try:
        key = paramiko.RSAKey.from_private_key_file(private_key_file_path)
        conn = Connection(host, user=user, connect_kwargs={"pkey": key})
        conn.close()
        return True
    except Exception as e:
        sg.Popup(f"Failed to connect: {str(e)}")
        return False


def get_ssh_config():
    with open(os.path.expanduser("~/.ssh/config")) as f:
        config = f.read()
    hosts = re.findall(r"Host (.*)", config)
    users = re.findall(r"User (.*)", config)
    return hosts, users


def get_pem_files():
    pem_files = glob.glob(os.path.expanduser("~/.ssh/*.pem"))
    return pem_files


def main():
    hosts, users = get_ssh_config()
    pem_files = get_pem_files()

    layout = [
        [sg.Text("Host"), sg.Combo(hosts, key="host")],
        [sg.Text("User"), sg.Combo(users, key="user")],
        [
            sg.Text("Private Key File Path"),
            sg.Combo(pem_files, key="private_key_file_path"),
        ],
        [sg.Text("SSH File Path"), sg.InputText(key="ssh_file_path")],
        [
            sg.Text("Download Location"),
            sg.InputText(key="download_location"),
            sg.FolderBrowse(),
        ],
        [sg.Button("Test Connection"), sg.Button("Download"), sg.Button("Cancel")],
    ]

    window = sg.Window("SSH File Downloader", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Cancel":
            break
        if event == "Test Connection":
            if test_connection(
                values["host"], values["user"], values["private_key_file_path"]
            ):
                sg.Popup("Connection successful!")
        if event == "Download":
            connect_and_download(
                values["host"],
                values["user"],
                values["private_key_file_path"],
                values["ssh_file_path"],
                values["download_location"],
            )

    window.close()


if __name__ == "__main__":
    main()
