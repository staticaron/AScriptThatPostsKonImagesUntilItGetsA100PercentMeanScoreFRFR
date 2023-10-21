import pdb
import requests
import os
import sys
import random
import catbox
import json

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

        Artist : {artist}
        </center>
    """

CATBOX_BASE = "https://catbox.moe/user/api.php"

def select_random_image_file(details) -> bool:
    """ Select a random image from the image folder and return its details """

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

    if file_extension == "json":
        return select_random_image_file()
    
    return { 
        "file_name" : file_name,
        "file_extension" : file_extension 
    }
    
def fetch_details():
    """ Reads the content of config.json and return the values """

    config_file = json.load(open("config.json"))

    return {
        "token" : config_file.get("token"),
        "posted_image_dir" : config_file.get("posted_image_dir"),
        "unposted_image_dir" : config_file.get("unposted_image_dir"),
        "progress" : int(config_file.get("progress"))
    }

def main():

    pdb.set_trace()

    create_post_on_anilist = False

    if len(sys.argv) >= 2:
        create_post_on_anilist = sys.argv[2].lower() == "true"

    details = fetch_details()

    file_name, file_extension = select_random_image_file(details).values()

    if file_name is None:
        print("No Files found in " + details.get("unposted_image_dir"))
        print("Program Terminated!")
        return
    
    # The image data of the chosen image

    image_data = open(details.get("unposted_image_dir") + file_name + file_extension, "rb").read()

    uploader = catbox.Uploader("")

    # Try posting the image on Catbox.moe

    try:
        print("Posting Image to catbox.moe.....")

        image_url = uploader.upload(file_type=file_extension[1:], file_raw=image_data).get("file")

    except requests.exceptions.ConnectionError:
        print("Failed to upload image to Catbox.moe!")
        return

    activity_content = ACTIVITY_CONTENT_FORMAT.format(day=details.get("progress"), url=image_url, artist=file_name)

    variables = {
        "text" : activity_content
    }

    if create_post_on_anilist:

        # Create post on anilist with the generated content.

        anilist_response = requests.post(
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
    else:

        # Return the post content without creating a post on anilist.

        print("Post Content : ")
        print()
        print("==============================")
        print(activity_content)
        print("==============================")


    # Update the progress counter
    details["progress"] = details.get("progress", 0) + 1
    
    # Saved the modified json with the new progress
    with open("config.json", "w") as file_out:
        json.dump(details, file_out)

    # Move the used file into posted folder
    os.rename(details.get("unposted_image_dir") + file_name + file_extension, details.get("posted_image_dir") + file_name + file_extension)

























if __name__ == "__main__":
    main()
