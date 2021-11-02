import logging
import os
import threading
import time

import dotenv
import praw
import wget
from PIL import Image
from PIL import ImageFilter


def cleanup():
    cl_dir = os.fsencode(properties.img_path)
    for file in os.listdir(cl_dir):
        file = os.fsdecode(file)
        if file.endswith(".jpg") or file.endswith(".REMOVE_ME"):
            os.remove(properties.img_path + file)
            logging.info(f"Removed File {file} from system.")
        else:
            logging.info(f"Skipping {file}")


def download_top_posts(top_posts):
    file_id = 1
    dl_count = 0
    for submission in top_posts:
        url = submission.url
        file_name = f"{file_id}{properties.img_name}.jpg"
        logging.info(f'Starting download of {file_name} from {url} now.')
        try:
            wget.download(url, properties.img_path + f"{file_name}")
            image = Image.open(f"{properties.img_path}{file_name}")
            image_size = image.size
            larger_image = image.copy()
            if image_size[0] > image_size[1]:
                larger_image = larger_image.resize((image_size[0], image_size[0]), Image.ANTIALIAS)
                larger_image = larger_image.filter(
                    ImageFilter.GaussianBlur(radius=image_size[0] / int(properties.img_radius)))
                img_size_diff0 = int((image_size[0] - image_size[0]) / 2)
                img_size_diff1 = int((image_size[0] - image_size[1]) / 2)
                larger_image.paste(image, (img_size_diff0, img_size_diff1))
                larger_image.save(f"{properties.img_path}{file_name}")
            elif image_size[0] < image_size[1]:
                larger_image = larger_image.resize((image_size[1], image_size[1]), Image.ANTIALIAS)
                larger_image = larger_image.filter(
                    ImageFilter.GaussianBlur(radius=image_size[0] / int(properties.img_radius)))
                img_size_diff0 = int((image_size[1] - image_size[0]) / 2)
                img_size_diff1 = int((image_size[1] - image_size[1]) / 2)
                larger_image.paste(image, (img_size_diff0, img_size_diff1))
                larger_image.save(f"{properties.img_path}{file_name}")
            logging.info('Download successful!')
            dl_count = dl_count + 1
            file_id = file_id + 1
        except Exception as e:
            logging.error(e)
            logging.error('Download failed!')
            os.remove(properties.img_path + f"{file_name}")
    logging.info(f'Download count: {dl_count}')


def repetition(repetition_time):
    time_start = time.time()
    cleanup()
    time_end = time.time()
    time_diff = time_end - time_start
    logging.info(f"Cleanup took {time_diff} seconds.")

    time_start = time.time()
    download_top_posts(subreddit_instance.top("day", limit=int(properties.img_limit)))
    time_end = time.time()
    time_diff = time_end - time_start
    logging.info(f"Download took {time_diff} seconds.")

    threading.Timer(int(repetition_time) * 60 * 60 - int(time_diff), repetition).start()
    logging.info(f'Scheduled next routine ({repetition_time} hours)')


class ImageProperties:
    def __init__(self, img_path, img_name, img_limit, img_radius):
        self.img_path = img_path
        self.img_name = img_name
        self.img_limit = img_limit
        self.img_radius = img_radius


class Login:
    def __init__(self, user, password):
        self.user = user
        self.password = password


if __name__ == '__main__':
    dotenv.load_dotenv()
    properties = ImageProperties(os.getenv('Bild_Pfad'),
                                 os.getenv('Bild_Name'),
                                 os.getenv('Bild_Limit'),
                                 os.getenv('Bild_FilterRadius'))
    logging.info(f"Image Properties:")
    logging.info(f"{properties}")

    login = Login(os.getenv('Name'), os.getenv('Passwort'))
    instance = praw.Reddit(client_id='bFJrhhapK7k1JA',
                           client_secret='zZs2VMjCpABMS5cL3SgTQuPEyMw',
                           user_agent='Pyros Reddit Scraper',
                           username=login.user,
                           password=login.password)
    subreddit_instance = instance.subreddit(os.getenv("Subreddit"))

    repetition(os.getenv('Stunden'))
