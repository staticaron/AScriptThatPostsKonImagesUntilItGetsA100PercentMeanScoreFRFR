import requests
import os
import sys
import random
import catbox
import json
import asyncio
from pysaucenao import SauceNao

BASE_URL = 'https://graphql.anilist.co'


CREATE_ACTIVITY_QUERY  = """
    mutation($text: String){
        SaveTextActivity(text:$text){
            id
            text
        }
    }
"""

ACTIVITY_CONTENT_FORMAT = """
<center>
<h1> <strong> Posting K-ON pictures until the anime get a 100% mean score: Day #{day} </strong>  </h1>

<img src="{url}">

Artist : [{artist}]({link})
</center>
"""

CATBOX_BASE = "https://catbox.moe/user/api.php"

def select_random_image_file(details) -> bool:
    """ Select a random image from the image folder and return its details """

    print("Selecting Random File .....")

    image_list = os.listdir(details.get("unposted_image_dir"))
    image_files = [x for x in image_list if os.path.isdir(details.get("unposted_image_dir") + "/" + x) == False]

    if len(image_files) <= 0:
        return {
            "file_name" : None,
            "file_extension" : None
        }

    random_image_file = random.choice(image_files)

    file_name = os.path.splitext(random_image_file)[0]
    file_extension = os.path.splitext(random_image_file)[1]

    print("Random File Selected!")
    print("File Name : " + file_name + file_extension)
    print()

    return { 
        "file_name" : file_name,
        "file_extension" : file_extension 
    }
    
def fetch_details():
    """ Reads the content of config.json and return the values """

    print("Reading config.json file!")

    try:
        with open("config.json") as file_in:
            config_file = json.load(file_in)

    except FileNotFoundError:
        print("Error while reading the config.json file! Make sure the file is present in the same folder as the main.py file! Download sample config.json file from https://github.com/Devanshu19/AScriptThatPostsKonImagesUntilItGetsA100PercentMeanScoreFRFR/blob/5492fb424b92c15ea9fd8ffc271dbdf52ccb30e2/main.py")
        return None

    try:
        data = {
            "token" : config_file.get("token"),
            "posted_image_dir" : config_file.get("posted_image_dir"),
            "unposted_image_dir" : config_file.get("unposted_image_dir"),
            "progress" : int(config_file.get("progress")),
            "use_file_name" : bool(config_file.get("use_file_name_if_source_not_found"))
        }

        print("config.json file OK")
        print()

        return data

    except:
        print("Corrupt config.json. Download sample config.json from https://github.com/Devanshu19/AScriptThatPostsKonImagesUntilItGetsA100PercentMeanScoreFRFR/blob/5492fb424b92c15ea9fd8ffc271dbdf52ccb30e2/main.py and change its values")
        return None

def upload_on_catbox(file_extension, image_data):
    """ Try uploading on catbox and return the image link """

    uploader = catbox.Uploader("")

    try:
        print("Uploading Image to catbox.moe.....")

        image_url = uploader.upload(file_type=file_extension[1:], file_raw=image_data).get("file")

        print("Image Uploaded!")
        print()

    except requests.exceptions.ConnectionError:
        print("Failed to upload image to Catbox.moe!")
        return None
    
    return image_url

async def find_sauce(details, image_url):

    print("Finding Pixiv Source...")

    sauce_finder = SauceNao(priority=[5, 6], api_key=details.get("saucenaotoken"))

    results = await sauce_finder.from_url(image_url)

    top_result = results[0]

    if top_result.similarity > 90:

        print("Source Found!")
        print("Author : " + top_result.author_name)
        print("Artwork Link : " + top_result.source_url)
        print()

        return [top_result.author_name , top_result.source_url]
    
    else:
        return None


def create_anilist_post(details, variables) -> bool:
    
    print("Creating Post on Anilist .....")

    try:
        requests.post(
                url=BASE_URL,
                json={
                    "query" : CREATE_ACTIVITY_QUERY,
                    "variables" : variables
                },
                headers={
                    'Authorization': details.get("token")
                },
                timeout=10*60
            )

        print("Post Created!")
        print()

    except Exception as e:
        print("Some error occurred while creating post on anilist!")
        return False

    return True

async def main():

    details = fetch_details()

    if details is None:
        return

    file_name, file_extension = select_random_image_file(details).values()

    if file_name is None:
        print("No Files found in " + details.get("unposted_image_dir"))
        print("Program Terminated!")
        return
    
    # The image data of the chosen image
    image_data = open(details.get("unposted_image_dir") + file_name + file_extension, "rb").read()

    image_url = upload_on_catbox(file_extension, image_data)

    sauce_data = await find_sauce(details, image_url)

    artist_name = sauce_data[0] if sauce_data is not None else file_name if details.get("use_file_name") else "Unknown"
    pixiv_link = sauce_data[1] if sauce_data is not None else ""

    activity_content = ACTIVITY_CONTENT_FORMAT.format(day=details.get("progress"), url=image_url, artist=artist_name, link=pixiv_link)

    variables = {
        "text" : activity_content
    }


    # Return the post content

    print("Post Content : ")
    print()
    print("==============================")
    print(activity_content)
    print("==============================")
    print()

    user_input = input("Post the activity on anilist? (Y/N) : ")

    if user_input.lower() == "y":
        if not create_anilist_post(details, variables):
            return
    else:
        print()
        print("Program Finished!")


    # Update the progress counter
    details["progress"] = details.get("progress", 0) + 1
    
    # Saved the modified json with the new progress
    with open("config.json", "w") as file_out:
        json.dump(details, file_out, indent=4)

    # Move the used file into posted folder
    os.rename(details.get("unposted_image_dir") + file_name + file_extension, details.get("posted_image_dir") + file_name + file_extension)

























if __name__ == "__main__":
    asyncio.run(main())
