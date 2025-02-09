import re
import smtplib
import scrapy
from scrapy_splash import SplashRequest
import json
import os


class MySpider(scrapy.Spider):
    name = "spider"
    start_urls = [
        "https://www.studentbostader.se/soker-bostad/lediga-bostader/?pagination=1&paginationantal=100"
    ]  # Replace with your target URL

    previous_number_file = "previous_number.json"
    email_sent = False

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={"wait": 3})

    def parse(self, response):
        text_content = response.css("body").get()
        match = re.search(r"av\s+(\d+)\s+sökträffar", text_content)
        if match:
            current_number = int(match.group(1))
        else:
            self.log("Number not found")
            return

        # Load the previous number from a file
        previous_number = self.load_previous_number()

        # Compare the numbers and log the result
        if previous_number is not None:
            if current_number > previous_number:
                self.log(
                    f"Number increased! Previous: {previous_number}, Current: {current_number}"
                )
            else:
                self.log(
                    f"Number did not increase. Previous: {previous_number}, Current: {current_number}"
                )
        else:
            self.log("No previous data found, storing the current number.")
        self.send_email_notification(previous_number, current_number)
        # Save the current number for the next run
        self.save_current_number(current_number)

    def send_email_notification(self, old_number, new_number):
        if not self.email_sent:
            sender = "Private Person <hello@demomailtrap.com>"
            receiver = "A Test User <pederburrstock@gmail.com>"
            message = f"""\
            Subject: Hi Mailtrap
            To: {receiver}
            From: {sender}
            This is a test e-mail message."""
            with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
                server.starttls()
                server.login("smtp@mailtrap.io", "50f0cf40cbfb792bfe8d2b9d6d39ad8a")
                server.sendmail(sender, receiver, message)
            #         # Ensure we only send the email once per run
            self.email_sent = True

    def load_previous_number(self):
        try:
            with open(self.previous_number_file, "r") as f:
                return json.load(f).get("number")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_current_number(self, number):
        with open(self.previous_number_file, "w") as f:
            json.dump({"number": number}, f)
