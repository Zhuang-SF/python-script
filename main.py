from datetime import datetime
import dateutil.parser
import json
import os
import requests
import sqlite3
import youtube_dl

json_file_path = 'watch-history.json'
sqlite_file = '/Users/Helen/Library/Mobile Documents/com~apple~CloudDocs/Wang/Develop/db/test.db'
video_detail_cache_folder = '/Users/Helen/Desktop/cache/%s'
video_url = 'http://www.youtube.com/watch?v=%s'

conn = sqlite3.connect(sqlite_file)


def insert_channel(name, channel_id):
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO channel (channel_id, name) VALUES (?, ?)", (channel_id, name))


def insert_video(title, video_id, channel_id, time):
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO video (video_id, channel_id, title,view_time) VALUES (?, ?, ?, ?)",
              (video_id, channel_id, title, time))


def insert_history(timestamp, video_id):
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO history (timestamp, video_id) VALUES (?, ?)", (timestamp, video_id))


def video_key(keyNumber):
    switcher = {
        1: "duration",
        2: "view_count",
        3: "created_timestamp",
    }
    return switcher.get(keyNumber, "Invalid month")


def update_video_info(video_id, key, key_value):
    c = conn.cursor()
    table_key = video_key(key)
    c.execute("UPDATE video SET " + table_key + " = ? WHERE video_id=?", (key_value, video_id))


def populate_database():
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

    with open(json_file_path) as json_file:
        data = json.load(json_file)
        for history in data:
            print(history)
            if "subtitles" not in history or "titleUrl" not in history or not history["title"].startswith("Watched "):
                continue

            channel_id = ""
            for subtitle in history["subtitles"]:
                channel_id = subtitle["url"].replace("https://www.youtube.com/channel/", "")
                insert_channel(subtitle["name"], channel_id)

            title = history["title"].replace("Watched ", "")
            video_id = history["titleUrl"].replace("https://www.youtube.com/watch?v=", "")
            time = int(dateutil.parser.parse(history["time"]).timestamp())
            insert_video(title, video_id, channel_id, time)

            duration = get_video_duration(ydl, video_id, 1)
            view_count = get_video_duration(ydl, video_id, 2)
            update_video_info(video_id, 1, duration)
            update_video_info(video_id, 2, view_count)

            timestamp = int(dateutil.parser.parse(history["time"]).timestamp())
            insert_history(timestamp, video_id)


def get_video_duration(ydl, video_id, key):
    table_key = video_key(key)
    file_path = video_detail_cache_folder % video_id
    print(ydl, video_id, file_path)
    url = video_url % video_id

    if not os.path.exists(file_path):
        try:
            result = ydl.extract_info(url, download=False)
        except:
            return -1

        with open(file_path, 'w') as f:
            f.write(json.dumps(result))

    with open(file_path) as json_file:
        data = json.load(json_file)
        return data[table_key]


populate_database()

conn.commit()
conn.close()
