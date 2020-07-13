try:
    import unzip_requirements
except ImportError:
    pass

import json
import os
from fbchat import Client
from fbchat.models import Message, ThreadType
from pathlib import Path
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
from random import randrange
from typing import Dict

PARENT_PATH = Path(__file__).parent.absolute()

FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER")
FB_USERNAME = os.environ.get("FB_USERNAME")
FB_PASSWORD = os.environ.get("FB_PASSWORD")
FB_GROUP_ID = os.environ.get("FB_GROUP_ID")


def lambda_handler(event, context):
    if event.get("is_local") == "False":
        post_to_group(False)
    else:
        post_to_group(True)
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
    client = get_client()

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

    save_fb_session(client)
    os.remove(img_path)


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


def get_client() -> Client: 
    """ Gets Facebook client. 

        Session cookies are stored in `fb_session.json`. Logs in 
        without session cookies if the file is empty otherwise logs 
        in with session cookies. 
    """
    session_cookies: Dict[str, str] = {}
    try:
        with open('fb_session.json', 'r') as f:
            session_cookies = json.load(f)
    except:
        pass

    return Client(FB_USERNAME, FB_PASSWORD, session_cookies=session_cookies)

def save_fb_session(client: Client) -> None: 
    """ Saves facebook session cookies. """
    with open('fb_session.json', 'w') as f:
        json.dump(client.getSession(), f)


if __name__ == "__main__":
    lambda_handler({}, None)