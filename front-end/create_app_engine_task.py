"""Create a task for a given queue with an arbitrary payload."""
from typing import Union
from loguru import logger
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import json


class AppEngineTask:
    def __init__(
            self,
            project: str,
            queue: str, location: str):
        self.project = project
        self.queue = queue
        self.location = location
        # Create a client.
        self.client = tasks_v2.CloudTasksClient()

        # Construct the fully qualified queue name.
        self.parent = self.client.queue_path(self.project, self.location, self.queue)

        # Construct the request body.
        self.task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': tasks_v2.HttpMethod.POST,
                'relative_uri': '/post_message'
            }
        }

    def add_task(self, in_seconds: float, payload: dict):
        if payload is not None:
            if isinstance(payload, dict):
                # Convert dict to JSON string
                payload = json.dumps(payload)
                # specify http content-type to application/json
                self.task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
                # The API expects a payload of type bytes.
            converted_payload = payload.encode()

            # Add the payload to the request.
            self.task['app_engine_http_request']['body'] = converted_payload

            if in_seconds is not None:
                # Convert "seconds from now" into an rfc3339 datetime string.
                d = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=in_seconds)

                # Create Timestamp protobuf.
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(d)

                # Add the timestamp to the tasks.
                self.task['schedule_time'] = timestamp

        # Use the client to build and send the task.
        response = self.client.create_task(parent=self.parent, task=self.task)

        logger.info('Created task')
        return response
