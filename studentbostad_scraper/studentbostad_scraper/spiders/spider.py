from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import scrapy
from scrapy_splash import SplashRequest
import os


class MySpider(scrapy.Spider):
    name = "spider"
    start_urls = [
        "https://www.studentbostader.se/soker-bostad/lediga-bostader/?pagination=1&paginationantal=100"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={"wait": 3})

    def parse(self, response):
        text_content = response.css("body").get()
        match = re.search(r"av\s+(\d+)\s+sökträffar", text_content)
        if match:
            current_number = int(match.group(1))
            self.log(f"Found {current_number} listings.")
            self.send_email_notification(current_number)
        else:
            self.log("Number not found")

    def send_email_notification(self, current_number):
        page_url = "https://www.studentbostader.se/soker-bostad/lediga-bostader/?pagination=1&paginationantal=100"
        SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
        sender = "hello@demomailtrap.com"
        receiver = "pederburrstock@gmail.com"
        message = f"""\
    From: {sender}
    To: {receiver}
    Subject: Listings Update

    The current number of listings is {current_number}.

    Link to page:
    {page_url}
    """
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "Listings Update"
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            server.starttls()
            server.login("api", SMTP_PASSWORD)
            server.sendmail(sender, receiver, msg.as_string())
            print("✅ Email sent successfully!")
