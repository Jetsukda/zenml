import base64
import json
import os
from typing import Dict, Text

import boto3

from zenml.utils.constants import ZENML_BASE_IMAGE_NAME, AWS_ENTRYPOINT

AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
AWS_REGION = 'AWS_REGION'


def _get_container_params(config, region):
    config_encoded = base64.b64encode(json.dumps(config).encode())
    return f'python -m {AWS_ENTRYPOINT} run_pipeline --config_b64 ' \
           f'{config_encoded.decode()} --region {region}'


def get_startup_script(config: Dict,
                       region: Text,
                       zenml_image: Text = ZENML_BASE_IMAGE_NAME):
    c_params = _get_container_params(config, region)
    return f'#!/bin/bash\n' \
           f'mkdir aws_config\n' \
           f'touch aws_config/config\n' \
           f'echo "[default]">>config\n' \
           f'echo "region = {region}">>config\n"' \
           f'sudo HOME=/home/root docker run --net=host ' \
           f'--env AWS_REGION={region} -v aws_config:/home/.aws '\
           f'{zenml_image} {c_params}'


def setup_session():
    session = boto3.Session()
    credentials = session.get_credentials()
    os.environ[AWS_ACCESS_KEY_ID] = credentials.access_key
    os.environ[AWS_SECRET_ACCESS_KEY] = credentials.secret_key
    return session


def setup_region(region):
    if region is None:
        if AWS_REGION in os.environ:
            pass
        else:
            session = boto3.Session()
            if session.region_name is None:
                os.environ[AWS_REGION] = 'eu-central-1'
            else:
                os.environ[AWS_REGION] = session.region_name
    else:
        os.environ[AWS_REGION] = region
    return os.environ[AWS_REGION]