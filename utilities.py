import datetime

import langdetect

from config import DIRECTORY_PATH


def post_log(text, directory=DIRECTORY_PATH):
    with open(directory, "a") as f:
        now = str(datetime.datetime.now())
        f.write(f"{now}: {text}\n")


def get_language(text):
    try:
        return langdetect.detect(text)
    except langdetect.lang_detect_exception.LangDetectException:
        return "UNKNOWN"
