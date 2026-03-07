import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.conf import settings


def send_bulk_sms(recipients, message):
    results = {'sent': 0, 'failed': 0, 'errors': []}
url = "https://api.africastalking.com/version1/messaging"    headers = {
        'apiKey': settings.AT_API_KEY,
        'Accept': 'application/json',
    }
    chunk_size = 100
    chunks = [recipients[i:i+chunk_size] for i in range(0, len(recipients), chunk_size)]
    for chunk in chunks:
        try:
            data = {
                'username': settings.AT_USERNAME,
                'to': ','.join(chunk),
                'message': message,
            }
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            print(f"AT Status: {response.status_code}")
            print(f"AT Response: {response.text}")
            if response.status_code == 201:
                resp_json = response.json()
                for recipient in resp_json.get('SMSMessageData', {}).get('Recipients', []):
                    if recipient.get('status') == 'Success':
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"{recipient.get('number')}: {recipient.get('status')}")
            else:
                results['failed'] += len(chunk)
                results['errors'].append(f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            results['failed'] += len(chunk)
            results['errors'].append(str(e))
    return results


def format_phone(phone):
    phone = str(phone).strip().replace(' ', '').replace('-', '')
    if phone.startswith('0'):
        phone = '+254' + phone[1:]
    elif phone.startswith('254'):
        phone = '+' + phone
    elif not phone.startswith('+'):
        phone = '+254' + phone
    return phone