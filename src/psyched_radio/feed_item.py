import logging
from dataclasses import dataclass
from datetime import date
from functools import total_ordering
from pathlib import Path
from typing import List
from urllib.request import urlopen

import eyed3
import feedparser
import requests


@dataclass
@total_ordering
class FeedItem:
    title: str
    image_url: str
    mp3_url: str
    artist: str
    album: str
    track_num: int = 1
    total_tracks: int = 1
    disc_num: int = 1
    total_discs: int = 1

    @property
    def track_title(self) -> str:
        return f'{self.album}: {self.date:%B %-d, %Y}'

    @property
    def album_artist(self) -> str:
        return self.artist

    @property
    def month(self) -> int:
        return int(self.title.split('.')[1])

    @property
    def day(self) -> int:
        return int(self.title.split('.')[2])

    @property
    def year(self) -> int:
        y = int(self.title.split('.')[3])
        y += 2000 if y < 100 else 0
        return y

    @property
    def date(self) -> date:
        return date(self.year, self.month, self.day)

    @property
    def image_data(self):
        return urlopen(self.image_url).read() if self.image_url else None

    def __lt__(self, other: 'FeedItem') -> bool:
        return self.date < other.date

    def __eq__(self, other: 'FeedItem') -> bool:
        return self.date == other.date

    def download_and_save(self, destination_directory) -> Path:
        filename = (
            f'{self.artist} - {self.album} - {self.track_num:02} - {self.track_title}.mp3'
        )
        destination = Path(destination_directory) / filename

        logging.info(f'Downloading {self.mp3_url} to {destination}')

        r = requests.get(self.mp3_url)
        r.raise_for_status()

        with destination.open('wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        return destination

    def update_id3_tags(self, path: Path) -> None:
        mp3 = eyed3.load(path)
        mp3.initTag()
        logging.info(f'Setting tag: album={self.album}')
        mp3.tag.album = self.album
        logging.info(f'Setting tag: artist={self.artist}')
        mp3.tag.artist = self.artist
        mp3.tag.album_artist = self.album_artist
        logging.info(f'Setting tag: title={self.track_title}')
        mp3.tag.title = self.track_title
        logging.info(f'Setting tag: disc num={self.disc_num} of {self.total_discs}')
        mp3.tag.disc_num = (self.disc_num, self.total_discs)
        logging.info(f'Setting tag: track num={self.track_num} of {self.total_tracks}')
        mp3.tag.track_num = (self.track_num, self.total_tracks)
        logging.info(f'Setting tag: release date={self.year}')
        mp3.tag.release_date = self.year
        mp3.tag.recording_date = self.year
        image_data = self.image_data
        if image_data:
            logging.info(f'Setting image tag: {self.image_url}')
            mp3.tag.images.set(3, image_data, 'image/jpeg', 'Description')
        mp3.tag.save()

    @classmethod
    def from_rss_url(cls, rss_url: str, artist: str, album: str) -> List['FeedItem']:
        feed = feedparser.parse(rss_url)
        items = []

        for item in feed.entries:
            mp3_url = None
            for link in item.links:
                if link.type == 'audio/mpeg':
                    mp3_url = link.href
                    break
            items.append(
                FeedItem(item.itunes_title, item.image.href, mp3_url, artist, album)
            )

        items.sort()
        track_num = 1
        total_tracks = len(items)
        for item in items:
            item.track_num = track_num
            item.total_tracks = total_tracks
            track_num += 1

        return items
