import logging
import os
import re
import time
import requests
import RunPodChatBot

def fetch_documents(response, tag='inbox'):
    headers = {"Authorization": f"Token {os.environ['PAPERLESS_API_KEY']}"}

    if response and response['next']:
        url = response['next']
    else:
        if tag:
            url = f"{os.environ['PAPERLESS_URL']}/documents/?tags__name__iexact={tag}"
        else:
            url = f"{os.environ['PAPERLESS_URL']}/documents/"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f"Error fetching documents: {response.status_code} {response.text}")
        return []

    return response.json()

def update_document_title(doc_id, new_title):
    url = f"{os.environ['PAPERLESS_URL']}/documents/{doc_id}/"
    headers = {
        "Authorization": f"Token {os.environ['PAPERLESS_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {"title": new_title}

    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code != 200:
        logging.error(f"Error updating document title: {response.status_code}")
    else:
        logging.info(f"Successfully updated document {doc_id} title to '{new_title}'")

def main():
    check_interval = int(os.environ.get('CHECK_INTERVAL', 60)) * 60

    prompt_file = os.environ['PROMPT_FILE']
    with open(prompt_file, 'r') as f:
        prompt = f.read()

    
    while True:
        print("Fetching documents...")

        results = list()
        response = None

        while True:
            response = fetch_documents(response)

            if not response:
                break

            results.extend(response['results'])

            if response['next'] is None:
                break

        if not response:
            logging.debug('No documents available')
            time.sleep(60)
            continue

        matches = [d for d in results if re.match(os.environ['TITLE_REGEX'], d['title'])]

        if len(matches) > 0:
            logging.info(f"Need to process {len(matches)} documents.")

            bot = RunPodChatBot.RunPodChatBot(prompt)
            new_title = dict()

            for i, doc in enumerate(matches):
                logging.info(f"Processing document ID {doc['id']} ({i}/{len(matches)}) with title: {doc['title']}")
                content = doc.get('content', '')
                new_title[doc['id']] = bot.get_response(content)

            bot.terminate_pod()
            del bot

            logging.info('Updating titles')
            for id, title in new_title.items():
                logging.info(f'Updating document {id}, new title: {title}')
                if title:
                    update_document_title(id, title[0] + os.environ['AUTO_TITLE_SUFFIX'])


        logging.info(f"Sleeping for {check_interval} seconds...")
        time.sleep(check_interval)


if __name__ == "__main__":
    main()

