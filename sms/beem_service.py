import requests
import base64
import logging
from .models import SentSMS
from django.conf import settings

API_KEY = "8a12eab677d132d0"
SECRET_KEY = "ZTlkMzAxNmIzZDg4MzUwMzdlMWUzZTFkYWYzNDI5ZWRiNzFjMjk5YTQ4ZmQwOTRhZWI4ZjBjNDQxNjQ0Mjk5Nw=="
BASE_URL = "https://apisms.beem.africa"
SOURCE_ADDR = "MANUS-DEI"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_auth_header():
    print("Generating auth header")
    token = f"{API_KEY}:{SECRET_KEY}"
    encoded_token = base64.b64encode(token.encode()).decode()
    auth_header = f"Basic {encoded_token}"
    print(f"Auth header: {auth_header}")
    return auth_header

def send_sms(recipients):
    print("Entering send_sms function")
    print(f"Recipients received: {recipients}")
    url = f"{BASE_URL}/v1/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    print(f"Headers: {headers}")

    # Process each recipient individually to send customized messages
    responses = []
    for recipient in recipients:
        print(f"Processing recipient: {recipient['dest_addr']}")
        formatted_recipient = [{"recipient_id": 1, "dest_addr": recipient["dest_addr"]}]
        message = recipient.get("message", "")
        print(f"Message to send: {message}")
        data = {
            "source_addr": SOURCE_ADDR,
            "schedule_time": "",
            "encoding": 0,
            "message": message,
            "recipients": formatted_recipient
        }
        print(f"Request data: {data}")

        try:
            print(f"Sending request to {url}")
            response = requests.post(url, json=data, headers=headers)
            print(f"Response status code: {response.status_code}")
            response_json = response.json()
            print(f"Response JSON: {response_json}")
            responses.append(response_json)

            if response.status_code == 200 and response_json.get('successful'):
                print("SMS sent successfully, saving to SentSMS model")
                SentSMS.objects.create(
                    dest_addr=recipient['dest_addr'],
                    first_name=recipient.get('first_name'),
                    last_name=recipient.get('last_name'),
                    message=message,
                    network=response_json.get('network', 'Unknown'),
                    length=len(message),
                    sms_count=(len(message) // 160) + 1,
                    status='Sent'
                )
                print("Saved to SentSMS model")
            else:
                print("Failed to send SMS for this recipient")
        except Exception as e:
            print(f"Error sending SMS to {recipient['dest_addr']}: {e}")
            responses.append({"error": str(e)})
    
    print(f"All responses: {responses}")
    # Aggregate responses; return success if all succeeded, otherwise return first error
    if all(resp.get('successful', False) for resp in responses if 'successful' in resp):
        return {"successful": True, "message": "All SMS sent successfully"}
    else:
        first_error = next((resp for resp in responses if 'error' in resp), {"error": "Unknown error"})
        return first_error

def check_balance():
    print("Entering check_balance function")
    url = f"{BASE_URL}/public/v1/vendors/balance"
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    print(f"Headers: {headers}")
    try:
        print(f"Sending request to {url}")
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        response_json = response.json()
        print(f"Response JSON: {response_json}")
        return response_json
    except ValueError as e:
        print(f"Error parsing response: {e}")
        logger.error(f"check_balance error: {response.text}")
        return {"error": "Invalid response from server"}

def get_sms_history():
    print("Entering get_sms_history function")
    url = f"{BASE_URL}/public/v1/sms/history"
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    print(f"Headers: {headers}")
    try:
        print(f"Sending request to {url}")
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        response_json = response.json()
        print(f"Response JSON: {response_json}")
        return response_json
    except ValueError as e:
        print(f"Error parsing response: {e}")
        logger.error(f"get_sms_history error: {response.text}")
        return {"error": "Invalid response from server"}