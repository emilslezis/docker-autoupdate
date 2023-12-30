import logging
import os
import sys

import requests
import json


# TODO use JSON SCHEMA

def docker_autoupdate():
    file = open("config.json")
    data = json.load(file)

    # TODO handle update_task
    # TODO schedule update_task to certain time
    update_task(data)


def update_task(params: dict) -> None:
    # Get specified image tag digest
    # API reference - https://docs.docker.com/docker-hub/api/latest/
    request = requests.get(
        'https://hub.docker.com/v2/namespaces/%s/repositories/%s/tags/%s'
        % (params['namespace'], params['repository'], params['tag'])
    )

    # Handle request response
    if request.status_code == 200:
        # Request successful
        latest_digest = request.json()['digest']

        # Check if there is need to update
        if not params['last_digest'] == latest_digest:
            container_update(params)

            # Update digest to latest
            # TODO redo - only when successful update
            with open('test.json', 'w') as file:
                params['last_digest'] = latest_digest
                json.dump(params, file)

        else:
            logging.info('UPDATE SKIPPED - latest and current version matches')

    elif request.status_code == 404:
        # Incorrect data
        # TODO handle 404 better
        logging.error('UPDATE FAILED - Incorrect entry data (404)')
    elif request.status_code == 500:
        logging.error('UPDATE FAILED - docker hub api server error (500)')
    else:
        logging.error('UPDATE FAILED - undocumented error while getting latest image')


def container_update(params: dict) -> None:
    # TODO delete old/unused image
    # TODO handle unsuccessful commands

    logging.info('Update process has started')

    # Install image by specified parameters
    os.system('sudo docker pull %s/%s:%s' % (params['namespace'], params['repository'], params['tag']))
    # Stop & Drop existing container
    os.system('sudo docker stop %s' % params['container_name'])
    os.system('sudo docker rm %s' % params['container_name'])
    # Create new container with command from json
    os.system(params['run_command'])

    logging.info('Update process successful')


if __name__ == "__main__":
    # TODO add info command
    # TODO add stop command
    # TODO add restart command
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        docker_autoupdate()

    else:
        print("Invalid option. Use 'info' to get information about commands.")
