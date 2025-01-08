# Bandcamp scraper that generates database links for online publication
# It takes data from Rekordbox history files and searches for Bandcamp links
# It's useful for DJs who want to share Bandcamp links in their playlists

import os
import requests
from bs4 import BeautifulSoup
import json


class HistoryDB:
    def __init__(self, history_file_name):
        self.history_location = ""  # put the path to the HISTORY files output by Rekordbox in the quotes
        self.link_database_name = "link_database.json"  # name of the database file
        self.history_file = self.history_location + "\\" + history_file_name

    def find_most_recent_history(self):
        # find the most recent HISTORY file in the history_location
        files = os.listdir(self.history_location)
        files = [os.path.join(self.history_location, file) for file in files]
        most_recent_file = max(files, key=os.path.getmtime)
        print(f"Most recent HISTORY file: {most_recent_file}")
        return most_recent_file

    def generate_track_list(self):
        # open the Rekordbox playlist history file and read the contents
        with open(self.history_file, 'rt', newline="\n", encoding="utf-16") as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]

            self.track_list = []
            for line in lines:
                track_info = line.split("\t")
                track_dict = {
                    "track title": track_info[2],
                    "artist": track_info[3],
                    "album": track_info[4],
                    "label": track_info[5],
                    "itemurl": ""
                }
                self.track_list.append(track_dict)
        print("Track list generated!")

    def load_database(self):
        # load the link_database.json file. This should have all the previous Bandcamp links
        with open("link_database.json", "r") as fin:
            self.link_database = json.load(fin)
        print("Database loaded!")

    def find_bandcamp_links(self):
        # search for Bandcamp links for each track in the track_list unless it already exists in the link_database
        print("Finding Bandcamp links")
        print()
        for track in self.track_list[1:]:
            # check the link_database for previous entries
            litemurl = next((ltrack['itemurl'] for ltrack in self.link_database if ltrack['track title'] == track['track title'] and ltrack['artist'] == track['artist']), False)
            # if the track is already in the database, use the existing link
            if litemurl != False:
                track['itemurl'] = litemurl
            # if the track is not in the database, search for a new link
            else:
                print()
                print(f"Searching:  {track['artist']} - {track['track title']}")
                search_url = "https://www.bandcamp.com/search?q=" + track['artist'] + " " + track['track title']
                search_url.replace(" ", "%2B")
                results = requests.get(search_url)
                soup = BeautifulSoup(results.text, "html.parser")
                try:
                    track['itemurl'] = soup.find(class_="itemurl").a.get("href")
                    print(f"    Bandcamp link found! --- {track['itemurl'][0:24]}...")
                except:
                    track['itemurl'] = ""
                    print("    (No link found)")
                self.link_database.append(track)
        print("Finished searching Bandbamp links.")
    
    def create_database(self):
        # create a blank database
        while os.path.exists(self.link_database_name):
            self.link_database_name = self.link_database_name.split(".")[0] + "_new.json"
        with open(self.link_database_name, "w") as fout:
            json.dump(self.track_list, fout)
        print(f"Database created: {self.link_database_name}")


    def update_database(self):
        # update the link_database.json file with the new links
        with open(self.link_database_name, "w") as fout:
            json.dump(self.link_database, fout)
        print("Database updated!")

    def generate_html_table(self):
        # generate an HTML table of the currently loaded track_list from the history playlist
        html_table = "<table>"
        html_table += "<tr><th>Artist</th><th>Track Title</th><th>Label</th><th>Link</th></tr>"
        for track in self.track_list[1:]:
            if track['itemurl'] is None:
                html_table += f"<tr><td>{track['artist']}</td><td>{track['track title']}</td><td>{track['label']}</td><td>&nbsp</td></tr>"
            else:
                html_table += f"<tr><td>{track['artist']}</td><td>{track['track title']}</td><td>{track['label']}</td><td><a href='{track['itemurl']}'>Bandcamp Link</a></td></tr>"
        html_table += "</table>"

        with open("track_list_html_table.html", "w") as file:
            file.write(html_table)
        print("HTML table generated!")

if __name__ == "__main__":
    input_name = ""
    while input_name == "":
        history_file_name = input("Enter the name of the HISTORY file: ")
    hdb = HistoryDB(history_file_name)
    hdb.generate_track_list()
    hdb.load_database()
    hdb.find_bandcamp_links()
    hdb.update_database()