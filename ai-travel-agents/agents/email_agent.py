from typing import Dict, Any
from .base_agent import BaseAgent
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from datetime import datetime


class EmailAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EmailAgent",
            instructions="""Create detailed travel itinerary emails.
            Include: flight details, hotel information, pricing, and booking links.
            Format content in clean, professional HTML with images and logos.
            Ensure all pricing and scheduling information is clearly presented.""",
            agent_type="email",
        )
        self.sendgrid_key = os.getenv("SENDGRID_KEY")

    async def run(self, messages: list) -> Dict[str, Any]:
        """Create and send travel itinerary email"""
        print("📧 EmailAgent: Creating and sending itinerary")

        email_data = eval(messages[-1]["content"])
        print(f"\n \n==> Email data: {email_data} \n \n")

        # Manually format the email content in HTML
        email_content = self._generate_email_content(email_data)

        # Send email
        success = self.send_email(email_data["to_email"], email_content)

        return {
            "success": success,
            "content": email_content,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient": email_data["to_email"],
        }

    def _generate_email_content(self, email_data: Dict[str, Any]) -> str:
        """Generate HTML content for the email"""

        flights_html = "<h2>Flights</h2><ol>"
        print(f"\n \n==> Email data: {email_data} \n \n")
        for flight in email_data["flights"]["recommended_flights"]:
            flights_html += f"""
            <li>
                <strong>{flight['airline']}</strong><br>
                <strong>Flight Number:</strong> {flight['flight_number']}<br>
                <strong>Departure:</strong> {flight['departure']}<br>
                <strong>Arrival:</strong> {flight['arrival']}<br>
                <strong>Duration:</strong> {flight['duration']}<br>
                <strong>Price:</strong> {flight['price']}<br>
                <img src="{flight['logo_url']}" alt="{flight['airline']}"><br>
                <a href="{flight['booking_url']}">Book Now</a>
            </li>
            """
        flights_html += "</ol>"

        hotels_html = "<h2>Hotels</h2><ol>"
        for hotel in email_data["hotels"]["recommended_hotels"]:
            hotels_html += f"""
            <li>
                <strong>{hotel['name']}</strong><br>
                <strong>Rating:</strong> {hotel['rating']}<br>
                <strong>Price per Night:</strong> {hotel['price_per_night']}<br>
                <strong>Total Price:</strong> {hotel['total_price']}<br>
                <strong>Location:</strong> {hotel['location']}<br>
                
                <img src="{hotel['image_url']}" alt="{hotel['name']}"><br>
                <a href="{hotel['booking_url']}">Book Now</a>
            </li>
            """
        hotels_html += "</ol>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Travel Itinerary</title>
        </head>
        <body>
            <h1>Your Travel Itinerary</h1>
            {flights_html}
            {hotels_html}
        </body>
        </html>
        """

    def send_email(self, to_email: str, content: str) -> bool:
        from_email = Email("paulo@vincimind.com")
        to_email = To(to_email)
        subject = "Your Travel Recommendations"
        content = Content("text/html", content)
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=content,
        )

        try:
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)
            print(f"Email sent to {to_email} with status code: {response.status_code}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
