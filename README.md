## Title-Suggester-LLM

This code is indended to run as da docker container together with an installation of [paperless-ngx](https://docs.paperless-ngx.com/). 

The code will use the paperless-ngx API to check for documents with the tag `inbox`. It will try to match the titles of the resulting documents with the provided regex `TITLE_REGEX`. 

If there are any matches, it will start a Pod hosted at [https://www.runpod.io/](runpod.io) with the given GPUs and GPU count and starting a LLM there. (For this to work, you need a runpod account, an API key, and prepaid credits). 
*THIS WILL COST MONEY*.

Warning: While this Pod is running, everybody can connect to the LLM and use it.

It will then send the ncontent from the document OCR to the LLM and generate titles for documents and update the docuemnts using the paperless-ngx api.

After all documents are processed, it will sleep for one hour and start over again.

To run, set the following environmental variables:

```
PAPERLESS_API_KEY=<your key>
RUNPOD_API_KEY=<your key>
PAPERLESS_URL=http://<your ip>:8000/api
TITLE_REGEX=scanned.*
CHECK_INTERVAL=60
PROMPT_FILE=config/prompt
IMAGE_NAME=vllm/vllm-openai:latest
MODEL_NAME=neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8
DOCKER_ARGS=--model neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8 --max-model-len 16384 --port 8000
GPU_TYPE=Nvidia GeForce RTX 4090
GPU_COUNT=2
CONTAINER_SIZE=20
VOLUME_SIZE=30
AUTO_TITLE_SUFFIX= (auto-generated title)
```
