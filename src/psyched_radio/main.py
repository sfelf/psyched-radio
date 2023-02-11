import logging
import sys

import click

from psyched_radio.feed_item import FeedItem

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)


@click.command()
@click.argument('rss_url')
@click.argument('album')
@click.argument('artist')
@click.argument('destination_directory', type=click.Path(exists=True))
def download_feed(rss_url, album, artist, destination_directory):
    feed_items = FeedItem.from_rss_url(rss_url, artist, album)

    for item in feed_items:
        path = item.download_and_save(destination_directory)
        item.update_id3_tags(path)
