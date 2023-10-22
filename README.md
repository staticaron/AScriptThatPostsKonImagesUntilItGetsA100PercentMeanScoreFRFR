# AScriptThatPostsKonImagesUntilItGetsA100PercentMeanScoreFRFR

# How to get it working?

### Step 1 : Get the Code.
Clone the repo and make sure you have python installed. Recommended version : 3.10

### Step 2 : Install Dependencies
    pip install requirements.txt 

### Step 3 : Set up config.json
Rename ```sampleconfig.json``` to ```config.json``` and set the values.

- **token** : _your anilist token_ Get it from this [link](https://anilist.co/api/v2/oauth/authorize?client_id=15004&response_type=token).
- **saucenaotoken** : _token required for image detection_ Get it by registering [here](https://saucenao.com/user.php?page=search-api) (FREE).
- **posted_image_dir** : _Directory where the posted images will go_.
- **unposted_image_dir** : _Directory where the unposted images are_.
- **progress** : _Current progress_.
- **use_file_name** : _true, if you want to use image_file_name as artist name if saucenao is unavailable_.

### Step 4 : Run the script!
    python main.py
