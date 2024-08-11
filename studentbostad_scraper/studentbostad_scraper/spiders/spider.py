import re
import scrapy
from scrapy_splash import SplashRequest
import json

class MySpider(scrapy.Spider):
    name = "spider"
    start_urls = ['https://www.studentbostader.se/soker-bostad/lediga-bostader/?pagination=1&paginationantal=100']  # Replace with your target URL

    previous_number_file = 'previous_number.json'

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 3})
    def parse(self, response):
        text_content = response.css('body').get()
        match = re.search(r'av\s+(\d+)\s+sökträffar', text_content)
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
                self.log(f"Number increased! Previous: {previous_number}, Current: {current_number}")
            else:
                self.log(f"Number did not increase. Previous: {previous_number}, Current: {current_number}")
        else:
            self.log("No previous data found, storing the current number.")

        # Save the current number for the next run
        self.save_current_number(current_number)

    def load_previous_number(self):
        try:
            with open(self.previous_number_file, 'r') as f:
                return json.load(f).get('number')
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_current_number(self, number):
        with open(self.previous_number_file, 'w') as f:
            json.dump({'number': number}, f)
