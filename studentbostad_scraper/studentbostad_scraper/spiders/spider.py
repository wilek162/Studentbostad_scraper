import re
import scrapy
from scrapy_splash import SplashRequest
import json
import os
from mailjet_rest import Client

class MySpider(scrapy.Spider):
    name = "spider"
    start_urls = ['https://www.studentbostader.se/soker-bostad/lediga-bostader/?pagination=1&paginationantal=100']  # Replace with your target URL

    previous_number_file = 'previous_number.json'
    email_sent = False
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
        self.send_email_notification(previous_number, current_number)
        # Save the current number for the next run
        self.save_current_number(current_number)
        
    def send_email_with_mailjet(self, subject, body):
        # Get Mailjet API keys from environment variables (or set them directly here)
        api_key = os.getenv('MAILJET_API_KEY')  # Your Mailjet public API key
        api_secret = os.getenv('MAILJET_API_SECRET')  # Your Mailjet private API key

        if not api_key or not api_secret:
            self.log("API keys are missing.")
            return

        # Initialize the Mailjet client
        mailjet = Client(auth=(api_key, api_secret))

        # Create the email payload
        data = {
            'FromEmail': 'w05446795@gmail.com',
            'FromName': 'SENDER_NAME',
            'Subject': 'Your email flight plan!',
            'Text-part': 'Dear passenger, welcome to Mailjet! May the delivery force be with you!',
            'Html-part': '<h3>Dear passenger, welcome to <a href=\"https://www.mailjet.com/\">Mailjet</a>!<br />May the delivery force be with you!',
            'Recipients': [{'Email': 'pederburrstock@gmail.com'}]
            }
        self.log(data)
        # Send the email
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            self.log("Email sent successfully!")
            self.log("RESULT: ", str(result.json()))
        else:
            self.log(f"Failed to send email: {result.status_code} - {result.text}")
        
            
    def send_email_notification(self, old_number, new_number):
        if not self.email_sent:
            subject = "Scrapy Spider Update - Number of Listings"
            body = f"Old Number: {old_number}\nNew Number: {new_number}\n\nThe number of listings has been updated."

            # Send email using Mailjet API
            self.send_email_with_mailjet(subject, body)

            # Ensure we only send the email once per run
            self.email_sent = True        
    # def send_email_notification(self, old_number, new_number):
    #     if not self.email_sent:
    #         domain = os.getenv('DOMAIN')
    #         api_key = os.getenv('API_KEY')     
    #         response =  requests.post(
  	# 	f"https://api.mailgun.net/v3/{domain}/messages",
  	# 	auth=("api", api_key),
  	# 	data={"from": f"User <mailgun@{domain}>",
  	# 		"to": ["eboggeno@email1.io", f"YOU@{domain}"],
  	# 		"subject": "Hello",
  	# 		"text": "Testing!"})

    #         # Check if the email was sent successfully
    #         if response.status_code == 200:
    #             self.log("Email sent successfully!")
    #         else:
    #             self.log(f"Failed to send email: {response.text}")

    #         # Ensure we only send the email once per run
    #         self.email_sent = True

    def load_previous_number(self):
        try:
            with open(self.previous_number_file, 'r') as f:
                return json.load(f).get('number')
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_current_number(self, number):
        with open(self.previous_number_file, 'w') as f:
            json.dump({'number': number}, f)
