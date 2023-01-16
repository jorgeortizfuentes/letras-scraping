from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from config import DB_PATH
from models import Artists, Songs, engine
from scraping import (
    get_artists_from_genre,
    get_lyrics_from_url,
    get_songs_from_artist,
    set_driver,
)
from utilities import get_language, post_log


def get_session(engine):
    # Create a connection to the database
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def save_url_songs_from_artist_to_db(source_url, driver, session):
    songs = get_songs_from_artist(source_url, driver)
    main_artist = songs["main_artist"]
    songs = songs["urls"]
    for url in songs:
        if session.query(Songs).filter(Songs.url == url).first() is None:
            session.add(Songs(url=url, main_artist=main_artist))
    if len(songs) > 0:
        # Add to the database the artist if it is not in the database
        if session.query(Artists).filter(Artists.url == source_url).first() is None:
            session.add(Artists(url=source_url, name=main_artist))
    session.commit()
    post_log(f"{len(songs)} songs from {main_artist} added to the database")
    print(f"{len(songs)} songs from {main_artist} added to the database")


def save_artists_from_genre_to_db(source_url, driver, session):
    artists = get_artists_from_genre(source_url, driver)
    for artist in artists:
        name = artist["name"]
        url = artist["url"]
        if session.query(Artists).filter(Artists.url == url).first() is None:
            session.add(Artists(url=url, name=name))
    session.commit()
    post_log(f"{len(artists)} artists from {source_url} added to the database")
    print(f"{len(artists)} artists from {source_url} added to the database")


def save_url_songs_from_db_to_db(driver, session):
    # Get all the artists from the database
    artists = session.query(Artists).all()
    for artist in artists:
        try:
            songs = get_songs_from_artist(artist.url, driver)
            main_artist = songs["main_artist"]
            songs = songs["urls"]
            for url in songs:
                # If the song is not in the database, add it
                if session.query(Songs).filter(Songs.url == url).first() is None:
                    session.add(Songs(url=url, main_artist=main_artist))
            print(f"{len(songs)} songs from {main_artist} added to the database")
            post_log(f"{len(songs)} songs from {main_artist} added to the database")
        except:
            print(f"Problem with {artist.url}")
    session.commit()
    print(f"{len(artists)} artists added to the database")
    post_log(f"{len(artists)} artists added to the database")


def save_lyrics_from_db(driver, session):
    # Get all the songs from the database without lyrics
    songs = session.query(Songs).filter(Songs.lyrics == None).all()
    i = 0
    for song in tqdm(songs):
        try:
            lyrics = get_lyrics_from_url(song.url, driver)
            song.lyrics = lyrics["lyrics"]
            song.title = lyrics["title"]
            song.featuring_artists = lyrics["featuring_artists"]
            song.main_artist = lyrics["main_artist"]
            # print(f"Lyrics {song.url} from {song.main_artist} added to the database")
            post_log(f"Lyrics {song.url} from {song.main_artist} added to the database")
        except Exception as e:
            e = str(e).replace("\n", "")
            print(
                f"Lyrics {song.url} from {song.main_artist} not added to the database. Error: {e}"
            )
            post_log(
                f"Lyrics {song.url} from {song.main_artist} not added to the database. Error: {e}"
            )
        i += 1
        if i % 50 == 0:
            session.commit()
    session.commit()
    print(f"{len(songs)} lyrics added to the database")
    post_log(f"{len(songs)} lyrics added to the database")


def get_language_from_db(session):
    # Get all the songs from the database without language
    songs = session.query(Songs).filter(Songs.language == None).all()
    # Get the language of the lyrics with get_language() and save it in the database
    for s in songs:
        s.language = get_language(s.lyrics)
    session.commit()
    print(f"{len(songs)} languages added to the database")
    post_log(f"{len(songs)} languages added to the database")


if __name__ == "__main__":
    driver = set_driver()
    session = get_session(engine)
    # singers = ["https://www.letras.com/rosalia/",
    #          "https://www.letras.com/bizarrap/",
    #          "https://www.letras.com/soda-stereo/",
    #          "https://www.letras.com/gustavo-cerati/",
    #          "https://www.letras.com/luis-alberto-spinetta/",
    #          "https://www.letras.com/los-jaivas/",
    #          "https://www.letras.com/victor-jara/",
    #          "https://www.letras.com/quilapayun/",
    #          "https://www.letras.com/inti-illimani/",
    #          "https://www.letras.com/los-prisioneros/",
    #          "https://www.letras.com/los-autenticos-decadentes/"]

    # for singer in singers:
    #     save_url_songs_from_artist_to_db(singer, driver, session)

    genre_urls = [
        "https://www.letras.com/estilos/hip-hop-rap/",
        "https://www.letras.com/estilos/cumbia/",
        "https://www.letras.com/estilos/reggaeton/",
        "https://www.letras.com/estilos/trova/",
        "https://www.letras.com/estilos/bolero/",
        "https://www.letras.com/estilos/pop/",
        "https://www.letras.com/estilos/poprock/",
        "https://www.letras.com/estilos/punk-rock/",
    ]

    for genre_url in genre_urls:
        save_artists_from_genre_to_db(genre_url, driver, session)

    # save_url_songs_from_db_to_db(driver, session)
    save_lyrics_from_db(driver, session)
    get_language_from_db(session)
    session.close()
