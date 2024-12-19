import atexit
import logging
import os
import time

import requests
import runpod

runpod.api_key = os.environ['RUNPOD_API_KEY']

logging.basicConfig(level=logging.DEBUG)

class RunPodChatBot:

    def __init__(self, prompt, id=None, terminate=True):
        self.api_token = os.environ["RUNPOD_API_KEY"]

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        self.id = None
        self.prompt = prompt

        if terminate:
            atexit.register(self.terminate_pod)

        if id is None:
            self._create_pod()
        else:
            self.id = id

        self.base_url = f"https://{self.id}-8000.proxy.runpod.net/v1"
        self._wait_for_vllm()

        self.API_URL = f"{self.base_url}/chat/completions"  # Replace with the actual URL of your vLLM server.
#
        self.message = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": ""},
        ]

        logging.info('init done')


    def __del__(self):
        pass

    def terminate_pod(self):
        if self.id is not None:
            logging.info(f'Terminating pod {self.id}')
            runpod.terminate_pod(self.id)
            self.id = None

    def _create_pod(self):
        logging.info('Creating runpod')
        response = runpod.create_pod('title-suggester-llm',
                                     image_name=os.environ['IMAGE_NAME'],
                                     #gpu_type_id="NVIDIA A40",  # Replace with the appropriate GPU type ID
                                     gpu_type_id=os.environ['GPU_TYPE'],  # Replace with the appropriate GPU type ID
                                     gpu_count=int(os.environ['GPU_COUNT']),
                                     container_disk_in_gb=int(os.environ['CONTAINER_SIZE']),
                                     volume_in_gb=int(os.environ['VOLUME_SIZE']),
                                     volume_mount_path="/root/.cache/huggingface",
                                     docker_args=os.environ['DOCKER_ARGS'],
                                     ports="8000/http",
                                     min_download=2000
                                     )

        if response['id']:
            logging.info(f"Pod created successfully with ID: {response['id']}")
        else:
            logging.error(f"Error creating pod: {response}")
        self.id = response['id']
        self._wait_for_runtime()

    def _wait_for_runtime(self):
        while True:
            logging.info('checking for runtime')
            pod = runpod.get_pod(self.id)
            if pod['runtime'] is not None:
                break
            time.sleep(2)

        logging.info('Runtime up')

    def _wait_for_vllm(self):
        while True:
            logging.info('checking models API call')
            if self.get_models() is not None:
                break

            time.sleep(2)

    def _add_prompt(self, text):
        return self.prompt + text

    def _assemble_payload(self, message):

        self.message[1]["content"] = self._add_prompt(message)

        # Define the payload
        return {
            "model": os.environ['MODEL_NAME'],
            "messages": self.message,
            "max_tokens": 50,
            "temperature": 0.7,
            "n": 1
        }

    def get_models(self):
        models_url = f"{self.base_url}/models"
        response = requests.get(models_url, headers=self.headers)

        if response.status_code == 200:
            #logging.info("Available models:", response.json())
            return response.json()

        logging.error(f"Failed to connect to {models_url}. Status code: {response.status_code}")

    def get_response(self, message):

        payload = self._assemble_payload(message)

        logging.info(f'Payload is {payload}')
        logging.info(f'URL is {self.API_URL}')
        logging.info(f'headers are {self.headers}')
        response = requests.post(self.API_URL, headers=self.headers, json=payload)

        # Print the response
        if response.status_code == 200:
            logging.debug(response.json())
            titles = list(ch['message']['content'] for ch in response.json()['choices'])
            for t in titles:
                logging.info(f"Suggested title: {t}")
            return titles
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            print(response)



if __name__ == "__main__":
    bot = RunPodChatBot(terminate=True)

    bot.get_response('This is a short text talking about LLMs. They are awesome.')
