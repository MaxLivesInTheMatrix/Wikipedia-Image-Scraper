''' I built this code in 2 stages. I knew I had two tasks to complete. 
    The first thing I looked into was first scraping, saving and filtering for relevant images.
    The second part of the task was to use an LLM to identify if an object is in the picture, 
    in the exmaple used, we used photos of ed sheran and a guitar.
    The results are printed out and stored within a hashmap'''
    
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from groq import Groq
import base64

print("Please enter a website to scrape:") # https://en.wikipedia.org/wiki/Ed_Sheeran
urlToScrap = input()
print()
print("Please enter a object to search for:") # Enter Guitar
item = str(input())

def download_thumbnails(wiki_url, download_dir="thumbnails"):
    # Create a directory to save thumbnails
    os.makedirs(download_dir, exist_ok=True)

    # Fetch the Wikipedia page
    response = requests.get(wiki_url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all <img> tags for thumbnails
    images = soup.find_all("img")
    if not images:
        print("No thumbnails found on the page.")
        return

    for img in images:
        # Get the image URL
        img_url = img.get("src")
        if not img_url:
            continue

        # Convert relative URLs to absolute URLs
        img_url = urljoin("https:", img_url) if img_url.startswith("//") else urljoin(wiki_url, img_url)

        # Download the image
        img_name = os.path.join(download_dir, os.path.basename(img_url))
        try:
            img_data = requests.get(img_url).content
            with open(img_name, "wb") as img_file:
                img_file.write(img_data)
            print(f"Downloaded: {img_name}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

wiki_page_url = urlToScrap
download_thumbnails(wiki_page_url)


def remove_non_numerical_files(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue
        
        # Check if the first three characters are numerical
        if not file_name[:3].isdigit():
            print(f"Removing non-numerical file: {file_name}")
            os.remove(file_path)

folder_path = '/Users/max/gitRepositories/photoScrape/thumbnails'
remove_non_numerical_files(folder_path)



# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def classification(image_path):

    # Getting the base64 string
    base64_image = encode_image(image_path)

    client = Groq(api_key) # You need a groq API key

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Is there a"+ item +"in this image? Say Yes or No"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )

    return chat_completion.choices[0].message.content

hashmap = {"guitar" : [],
           "no guitar": [],
        }
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    tmp = classification(file_path)
    tmp = str(tmp)
    print(tmp), print(file_name)
    print()
    if "Yes" in tmp or "yes" in tmp:
        hashmap["guitar"].append(file_path)
    else:
        hashmap["no guitar"].append(file_path)

print(hashmap)