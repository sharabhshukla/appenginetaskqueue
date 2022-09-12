from fastapi import FastAPI, status, Response
from create_app_engine_task import AppEngineTask
from data_models import UserData, ResponseData
from loguru import logger
from time import sleep
import redis

app = FastAPI()

PROJECT_ID = 'vocal-ceiling-278518'
QUEUE = 'pushq-default-app-engine'
LOCATION = 'us-central1'

HOST = '10.101.64.3'
PORT = 6379

r_client = redis.Redis(host=HOST, port=PORT, db=0)


@app.get('/', status_code=status.HTTP_200_OK)
def root_msg():
    return Response(content='Ok', status_code=status.HTTP_200_OK)


@app.post('/post_message_to_queue',
          status_code=status.HTTP_200_OK,
          response_model=ResponseData)
def post_msg_queue(message_to_post: UserData):
    logger.info('User data -> ')
    logger.info(message_to_post.json())
    r_client.set(message_to_post.user_id, 'task created')
    app_engine_task = AppEngineTask(project=PROJECT_ID, queue=QUEUE, location=LOCATION)
    task_response = app_engine_task.add_task(payload=message_to_post.dict(), in_seconds=5)
    response_data = ResponseData(**message_to_post.dict(), response=task_response.__str__())
    return response_data


@app.post("/post_message", response_model=ResponseData, status_code=status.HTTP_200_OK)
def read_message(user_data: UserData):
    r_client.set(user_data.user_id, 'task processing started')
    logger.info(f'user data ->')
    logger.info(f'{user_data}')
    sleep(300)
    response_data = ResponseData(**user_data.dict(), response='ok')
    r_client.set(user_data.user_id, 'task processing finished')
    return response_data


@app.get('/job_status/{job_id}')
def read_cache_status(job_id: str):
    job_status = r_client.get(job_id)
    return Response(content=job_status, status_code=status.HTTP_200_OK)
