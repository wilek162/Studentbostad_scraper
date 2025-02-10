from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

        # Compare the numbers
        if previous_number is None:
            self.log(f"First run: Storing the current number {current_number}.")
            self.save_current_number(current_number)
            return

        if current_number != previous_number:
            self.log(
                f"Number changed! Previous: {previous_number}, Current: {current_number}. Sending email."
            )
            self.send_email_notification(previous_number, current_number)
        else:
            self.log("No new listings found. No email sent.")

        # Save the current number for the next run
        self.save_current_number(current_number)

    def send_email_notification(self, old_number, new_number):
        SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
        sender = "hello@demomailtrap.com"
        receiver = "pederburrstock@gmail.com"
        message = f"""\
        From: {sender}
        To: {receiver}
        Subject: Listings Updated

        The number of listings has changed from {old_number} to {new_number}.
        """
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "Listings Updated"
        msg.attach(MIMEText(message, "plain"))

        # Send Email
        with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            server.starttls()
            server.login("api", SMTP_PASSWORD)
            server.sendmail(sender, receiver, msg.as_string())
            print("✅ Email sent successfully!")

    def load_previous_number(self):
        try:
            with open(self.previous_number_file, "r") as f:
                return json.load(f).get("number")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_current_number(self, number):
        with open(self.previous_number_file, "w") as f:
            json.dump({"number": number}, f)
