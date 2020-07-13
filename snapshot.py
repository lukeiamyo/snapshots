try:
    import unzip_requirements
except ImportError:
    pass

import os
from fbchat import Client
from fbchat.models import Message, ThreadType
from pathlib import Path
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
from random import randrange

PARENT_PATH = Path(__file__).parent.absolute()

FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER")
FB_USERNAME = os.environ.get("FB_USERNAME")
FB_PASSWORD = os.environ.get("FB_PASSWORD")
FB_GROUP_ID = os.environ.get("FB_GROUP_ID")


def lambda_handler(event, context):
    post_to_group(event.get("is_local", True))
    return {"message": event.get("message", "Hi. No message provided.")}


def post_to_group(is_local: bool) -> None:
    """ Sends image to facebook group chat.

        Location is demarcated by `thread_id`.
        Scheduled to run every two days at 12:30 PM.

        Args: 
            is_local: `True` if invoked locally,
                    `False` if invoked as a lambda function. 
    """
    img_file = get_image()

    client = Client(FB_USERNAME, FB_PASSWORD)
    if not client.isLoggedIn():
        client.login(FB_USERNAME, FB_PASSWORD)

    img_file_name = img_file.get("title")
    img_path = f"/tmp/{img_file_name}" if not is_local else f"{PARENT_PATH}/{img_file_name}"
    img_file.GetContentFile(img_path)
    img_message = Message(text="Sent from Lambda.")
    client.sendLocalImage(
        img_path,
        message=img_message,
        thread_id=FB_GROUP_ID,
        thread_type=ThreadType.GROUP,
    )
    clean_up(img_path, client)


def get_image() -> GoogleDriveFile:
    """ Gets random image from Google Drive folder.

        Silenty logs into Google Drive using local client secrets
        or locally stored credentials. Downloads file to directory.
        Configuration details stored in `settings.yaml`.

        Returns:
            img_file: Google Drive File instance.
    """
    # Authorized using local `client_secrets.json`, which can be
    # downloaded from Google's API projects page, accessed through
    # `settings.yaml`
    gauth = GoogleAuth()
    # Uses local `credentials.json` to provide stored credentials
    # to bypass verification proccess.
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    folder_query = f"'{FOLDER_ID}' in parents and trashed=false"
    file_list = drive.ListFile({"q": folder_query}).GetList()
    rand_int = randrange(len(file_list))
    img_file = file_list[rand_int]
    return img_file


def clean_up(img_path: str, client: Client) -> None:
    """ Removes local created image and logs out of facebook. """
    os.remove(img_path)
    client.logout()

lambda_handler({}, None)