import email
import imaplib
import config
import time
import requests
import json
from email.mime.text import MIMEText

def get_recent_orders():
    list = []
    url = 'https://rubysgardenboutique.myshopify.com/admin/orders.json?limit=5&fields=email,id,name,customer,tags'
    r = requests.get(url, auth=(config.API_KEY, config.API_PASSWORD))
    json_data = r.json()
    for order in json_data['orders']:
        if order['tags'] != 'thanks_email_generated'and order['customer']['orders_count'] == 1:
            list.append(order)
    return list

def compose_email(orders_list):
    list = []
    for order in orders_list:
        body = config.EMAIL_BODY.format(order['customer']['first_name'])
        msg = email.mime.text.MIMEText(body, 'html')
        msg['Subject'] = '''[Ruby's Garden Boutique] Order {} - A Big Thank You'''.format(order['name'])
        msg['From'] = 'sales@rubys-garden-boutique.co.uk'
        msg['To'] = order['customer']['email']
        list.append(msg)
    return list

def save_draft_email(message_list):
    host= "imap.gmail.com"
    mail= imaplib.IMAP4_SSL(host)
    mail.login(config.EMAIL, config.PASSWORD)
    mail.select('"[Gmail]/Drafts"')
    for message in message_list:
        current_time = imaplib.Time2Internaldate(time.time())
        mail.append('[Gmail]/Drafts','',
                    current_time,
                    str(message).encode('utf-8'))

def update_order_tags(orders_list):
    for order in orders_list:
        json_template = {"order": {"id": order['id'], "tags": "thanks_email_generated"}}
        payload = json.dumps(json_template)
        url = 'https://rubysgardenboutique.myshopify.com/admin/orders/{}.json'.format(order['id'])
        r = requests.put(url, data=payload, auth=(config.API_KEY, config.API_PASSWORD), headers={"Content-Type": "application/json"})

orders = get_recent_orders()
message_list = compose_email(orders)
save_draft_email(message_list)
update_order_tags(orders)