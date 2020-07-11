import os
import pathlib 
from fbchat import Client
from fbchat._exception import FBchatFacebookError
from fbchat.models import Message, ThreadType 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from random import randrange

PARENT_PATH = pathlib.Path(__file__).parent.absolute()

FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER')
FB_USERNAME = os.environ.get('FB_USERNAME')
FB_PASSWORD = os.environ.get('FB_PASSWORD')
FB_GROUP_ID = os.environ.get('FB_GROUP_ID')

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# where folder id corresponds to snapshots-test
folder_query = f"'{FOLDER_ID}' in parents and trashed=false"
file_list = drive.ListFile({"q": folder_query}).GetList()

rand_int = randrange(len(file_list))
img_file = file_list[rand_int]

img_title = img_file.get('title')
img_file.GetContentFile(img_title)

client = Client(FB_USERNAME, FB_PASSWORD)
if not client.isLoggedIn():
    client.login(FB_USERNAME, FB_PASSWORD)

img_path = f"{PARENT_PATH}/{img_title}"
img_message = Message(text="This is a local image.")
client.sendLocalImage(
    img_path,
    message=img_message,
    thread_id=FB_GROUP_ID,
    thread_type=ThreadType.GROUP,
)

os.remove(img_path)
client.logout()