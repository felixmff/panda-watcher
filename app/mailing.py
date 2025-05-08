import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Optional, List, Tuple, Dict

import boto3


class Mailer:
    def __init__(self) -> None:
        """Initializes the Mailer with SES credentials from environment variables."""
        self.client = boto3.client(
            "ses",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.from_address = os.getenv("SES_FROM_ADDRESS")
        self.from_name = os.getenv("SES_FROM_NAME")

    def send(
        self,
        recipients: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
    ) -> Dict:
        """
        Sends an email via AWS SES.

        Args:
            recipients (list): List of recipient email addresses.
            subject (str): Subject of the email.
            body_html (str): HTML content of the email.
            body_text (Optional[str]): Fallback plain text content.

        Returns:
            dict: The response from the SES client.
        """
        if not body_text:
            body_text = "This is a html-only email."

        message = {
            "Subject": {
                "Data": subject,
                "Charset": "UTF-8",
            },
            "Body": {
                "Html": {
                    "Data": body_html,
                    "Charset": "UTF-8",
                },
                "Text": {
                    "Data": body_text,
                    "Charset": "UTF-8",
                },
            },
        }

        destination = {
            "ToAddresses": recipients,
        }

        return self.client.send_email(
            Source=f"{self.from_name} <{self.from_address}>",
            Destination=destination,
            Message=message,
        )

    def load_recipients(self) -> List[str]:
        """
        Loads recipient email addresses from the config file.

        Returns:
            list: A list of recipient email addresses.
        """
        with open("config/config.json", "r") as f:
            config = json.load(f)
        return config.get("notify_emails", [])

    def notify_recipients(self, new_items: List[Tuple[str, str, str, str]]) -> None:
        """
        Sends a notification email to all recipients about new items.

        Args:
            new_items (list): A list of tuples containing course and resource data.
        """
        subject = "New Resources available on PANDA"
        template_path = Path("templates/notification.html")
        body_html = template_path.read_text(encoding="utf-8")

        grouped = defaultdict(list)
        for course_id, course_name, resource_name, resource_url in new_items:
            grouped[(course_id, course_name)].append((resource_name, resource_url))

        rows = ""
        for (course_id, course_name), resources in grouped.items():
            rows += f"""
    <div style="margin-bottom: 2em;">
      <h3 style="margin-bottom: 0.5em; color: white">{course_name}</h3>
      <ul style="list-style-type: none; padding-left: 0;">
"""
            for resource_name, resource_url in resources:
                rows += f"""
        <li style="margin-bottom: 1em; padding: 1em; background-color: #2a2c2c; border-radius: 8px;">
          <a href="{resource_url}" style="color: #4fc3f7; text-decoration: none;">📄 {resource_name}</a>
        </li>
"""
            rows += "</ul></div>"

        body_html = body_html.format(count=len(new_items), rows=rows)

        self.send(
            recipients=self.load_recipients(),
            subject=subject,
            body_html=body_html,
        )
