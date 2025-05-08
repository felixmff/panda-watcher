import json
import logging
from typing import List, Tuple

from app.hashing import compute_hashes, load_hashes, save_hashes, hash_single
from app.mailing import Mailer
from app.panda import PandaClient


class PandaWatcher:
    def __init__(self, config_path: str = "config/config.json") -> None:
        """
        Initializes the PandaWatcher with configuration data.

        Args:
            config_path (str): Path to the configuration JSON file.
        """
        with open(config_path, "r") as f:
            config = json.load(f)
            
        self.course_ids = config.get("course_ids", [])
        self.client = PandaClient()
        self.mailer = Mailer()
        
    def run(self) -> None:
        """
        Executes the full watcher routine:
        - logs in,
        - fetches resources,
        - compares hashes,
        - sends notification if new items found,
        - saves updated hashes.
        """
        self.client.login()
        logging.info("Logged in successfully")

        resources: List[Tuple[str, str, str, str]] = self.client.fetch_resources(self.course_ids)
        current_hashes = compute_hashes(resources)
        previous_hashes = load_hashes()

        new_items = [
            (course_id, course_name, resource_title, resource_url)
            for course_id, course_name, resource_title, resource_url in resources
            if hash_single(course_id, resource_title, resource_url) not in previous_hashes
        ]

        if new_items:
            logging.info(f"Found {len(new_items)} new resources")
            self.mailer.notify_recipients(new_items)
            logging.info("Notification sent to recipients")
        else:
            logging.info("No new resources found")

        save_hashes(current_hashes)
        logging.info("Hashes saved")