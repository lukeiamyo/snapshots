import os
import pathlib
import schedule 
import time
from fbchat import Client
from fbchat.models import Message, ThreadType
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from random import randrange

PARENT_PATH = pathlib.Path(__file__).parent.absolute()

FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER")
FB_USERNAME = os.environ.get("FB_USERNAME")
FB_PASSWORD = os.environ.get("FB_PASSWORD")
FB_GROUP_ID = os.environ.get("FB_GROUP_ID")

def post_to_group() -> None:
    """ Sends image to facebook group chat. 

        Location is demarcated by `thread_id`. 
        Scheduled to run every two days at 12:30 PM.
    """
    img_file_name = get_image()
    client = Client(FB_USERNAME, FB_PASSWORD)
    if not client.isLoggedIn():
        client.login(FB_USERNAME, FB_PASSWORD)

    img_path = f"{PARENT_PATH}/{img_file_name}"
    img_message = Message(text="This is a local image.")
    client.sendLocalImage(
        img_path, 
        message=img_message, 
        thread_id=FB_GROUP_ID, 
        thread_type=ThreadType.GROUP,
    )
    clean_up(img_path, client)

def get_image() -> str:
    """ Gets random image from Google Drive folder. 
    
        Silenty logs into Google Drive using local client secrets
        or locally stored credentials. Downloads file to directory.
        Configuration details stored in `settings.yaml`.

        Returns:
            img_file_name: Name of the downloaded file. 
    """ 
    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    # where folder id corresponds to snapshots-test
    folder_query = f"'{FOLDER_ID}' in parents and trashed=false"
    file_list = drive.ListFile({"q": folder_query}).GetList()

    rand_int = randrange(len(file_list))
    img_file = file_list[rand_int]

    img_file_name = img_file.get("title")
    img_file.GetContentFile(img_file_name)
    return img_file_name

def clean_up(img_path: str, client: Client) -> None:
    """ Removes local created image and logs out of facebook. """
    os.remove(img_path)
    client.logout()

# schedule.every(2).days.at("12:30").do(post_to_group)
schedule.every(2).minutes.do(post_to_group)

while True: 
    print(schedule.jobs)
    schedule.run_pending()
    time.sleep(1)
