from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

def set_driver():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("-—no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    # Enable cookies
    opts.set_preference("network.cookie.cookieBehavior", 0)
    opts.set_preference("network.cookie.lifetimePolicy", 2)
    # Disable images
    opts.set_preference("permissions.default.image", 2)
    # Disable CSS
    opts.set_preference("permissions.default.stylesheet", 2)
    # Disable Flash
    opts.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", "false")
    driver = webdriver.Firefox(options=opts)
    return driver


def get_songs_from_artist(source_url, driver):
    xpath_base = "/html/body/div[1]/div[1]/div[1]/div[5]/div[3]/div[1]/div[2]/div[2]/div[{n}]/ul/li/a"

    driver.get(source_url)
    # Scroll down a bit
    driver.execute_script("window.scrollTo(0, 500);")
    artist = driver.find_element(
        By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[5]/div[2]/div[1]/a/h1"
    ).text
    # Click button
    # driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[5]/div[3]/div[1]/div[2]/div[1]/div/a").click()
    urls = []
    n_errors = 0

    for i in range(1, 5000):
        if n_errors == 100:
            break
        try:
            url = driver.find_element(
                By.XPATH, xpath_base.format(n=str(i))
            ).get_attribute("href")
            urls.append(url)
        except:
            n_errors += 1

    if urls == []:
        driver.get(source_url + "/mais_acessadas.html")

    # Find the a elements with the song-name class
    elements = driver.find_elements(By.CLASS_NAME, "song-name")

    # Extract the href attribute values
    urls = [element.get_attribute("href") for element in elements]

    return {"urls": urls, "main_artist": artist}


def get_lyrics_from_url(lyric_url, driver):
    driver.get(lyric_url)
    # Title h1 in <div class"cnt-head_title"> <h1> title </h1> </div>
    title = driver.find_element(By.XPATH, "//div[2]/h1").text
    # title = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[7]/article/div[1]/div[2]/h1").text

    # Get position of the last "("
    if "(" in title:
        last_par = title.rfind("(")
        title = title[:last_par]
        featuring_artists = (
            title[last_par + 1 : -1].replace("part.", "").replace("Part.", "")
        )
    else:
        featuring_artists = None

    # Lyrics (css cnt-letra)
    lyrics = driver.find_element(By.CSS_SELECTOR, "div.cnt-letra")
    # Get all texts in all paragraphs in the lyrics
    all_p = lyrics.find_elements(By.TAG_NAME, "p")
    lyrics = "\n\n".join([p.text for p in all_p])

    # Main artist (h2 text)
    main_artist = driver.find_element(By.XPATH, "//div[2]/h2").text
    return {
        "title": title,
        "main_artist": main_artist,
        "featuring_artists": featuring_artists,
        "lyrics": lyrics,
    }


def get_artists_from_genre(genre_url, driver):
    driver.get(genre_url)

    # Click in button /html/body/div[1]/div[1]/div[1]/div[3]/div[4]/a
    driver.find_element(
        By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[3]/div[4]/a"
    ).click()

    # Get all artists class top-list_art
    artists = driver.find_element(By.CLASS_NAME, "top-list_art")

    artists_info = []

    artist_names = artists.find_elements(By.TAG_NAME, "a")
    artist_urls = artists.find_elements(By.TAG_NAME, "a")  # .get_attribute("href")

    for i in range(len(artist_names)):
        artist_name = artist_names[i].text
        artist_url = artist_urls[i].get_attribute("href")
        artists_info.append({"name": artist_name, "url": artist_url})

    return artists_info


if __name__ == "__main__":
    source_url = "https://www.letras.com/ms-nina/"
    driver = set_driver()
    # print(get_songs_from_artist(source_url, driver))

    # source_url = "https://www.letras.com/bad-bunny/me-porto-bonito-part-chencho-corleone/"
    # print(get_lyrics_from_url(source_url, driver))

    # source_url = "https://www.letras.com/estilos/reggaeton/"
    # print(get_artists_from_genre(source_url, driver))
    print(get_lyrics_from_url("https://www.letras.com/marcianeke/dimelo-ma/", driver))
