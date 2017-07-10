import requests
import json
import csv
import datetime
import json
from datetime import timedelta
from random import randint

server = 'https://prod-api.dgdeepai.com'
username = 'activision_prod@digitalgenius.com'
password = '3tcSC7YaK6UdUpzZmNv1AcA54tE'
model_group_id = 'bb7841ca-3c97-4e4d-95c2-aa6e4ae3bc11'


LANGUAGE = 'English'
CHANNEL = 'Chat'


def getToken():
    url = '{server}/api/v1/auth0/login'.format(server=server)
    headers = {
        'content-type': "application/json"
    }
    data = {
        'username': username,
        'password': password
    }
    resp = requests.request(
        'POST', url, data=json.dumps(data), headers=headers)
    token = resp.headers['Set-Authorization']
    return token


# def createModelGroup():

#     token = getToken()

#     url = '{server}/api/v1/qa/modelgroup'.format(server=server)

#     headers = {
#         'content-type': "application/json",
#         'authorization': "Bearer {token}".format(token=token)
#     }

#     data = {
#         'name': 'Activision_1',
#         'description': 'Activision_1'
#     }

#     resp = requests.request(
#         'POST', url, data=json.dumps(data), headers=headers)
#     print(resp.text)


# def createModelVersion():

#     token = getToken()

#     url = '{server}/api/v1/qa/modelgroup/{model_group_id}/modelversion'.format(
#         server=server, model_group_id=model_group_id)
#     headers = {
#         'content-type': "application/json",
#         'authorization': "Bearer {token}".format(token=token)
#     }

#     data = {
#         'languages': [
#             LANGUAGE
#         ],
#         'channels': [
#             CHANNEL
#         ],
#         'startTraining': False
#     }

#     resp = requests.request(
#         'POST', url, data=json.dumps(data), headers=headers)
#     print(resp.text)


class BodyWrapper (object):

    def __init__(self, externalId=None, createdAt=None, messages=[]):
        self.externalId = externalId
        self.createdAt = createdAt
        self.messages = messages


class Message (object):

    def __init__(self, externalId=None, createdAt=None, fromMessage=None, language=None, channel=None, content=None):
        self.externalId = externalId
        self.createdAt = createdAt
        self.fromMessage = fromMessage
        self.language = language
        self.channel = channel
        self.content = content


def readMessagesFile(file):

    messagesArray = []

    with open(file, 'r', encoding='utf-8') as f:
        content = csv.reader(f, delimiter=',')
        next(content)

        firstLine = next(content)

        current = firstLine[0]

        date = ''
        if firstLine[2] is '':
            date = (datetime.datetime.now()).isoformat()
        else:
            date = (datetime.datetime.strptime(
                firstLine[2], '%Y-%m-%d %H:%M:%S')).isoformat()

        wrapper = BodyWrapper(current, date)
        messages = [Message(current + '-1', date, firstLine[3],LANGUAGE, CHANNEL, firstLine[6])]

        for i, line in enumerate(content, 2):
            logExternalId = line[0]
            currDate = ''

            if line[2] is '':
                currDate = (datetime.datetime.now()).isoformat()
            else:
                currDate = (datetime.datetime.strptime(
                    line[2], '%Y-%m-%d %H:%M:%S')).isoformat()

            if logExternalId == current:
                messages.append(Message(logExternalId + '-' + str(i),
                                        currDate, line[3], LANGUAGE, CHANNEL, line[6]))
            else:
                wrapper.messages = messages
                messagesArray.append(wrapper)

                messages = [Message(
                    logExternalId + '-' + str(i), currDate, line[3], LANGUAGE, CHANNEL, line[6])]

                wrapper = BodyWrapper(logExternalId, currDate)
                current = logExternalId

        f.close()

    createMessagesJson(messagesArray)


def createMessagesJson(messagesArray):

    answers = []

    for item in messagesArray:

        messages = []

        for message in item.messages:
            tmp = {
                "externalId": message.externalId,
                "createdAt": message.createdAt,
                "from": message.fromMessage,
                "language": message.language,
                "channel": message.channel,
                "content": message.content
            }

            messages.append(tmp)

        if len(messages) > 1:
            data = {
                "externalId": item.externalId,
                "createdAt": item.createdAt,
                "messages": messages
            }

            answers.append(data)

    # saveMessagesToFiles(answers)
    sendMessagesJsonToAPI(answers)


# def saveMessagesToFiles(answers):
#     """Split full chat log to json files"""
#     n = 1000

#     matrix = [answers[i:i + n] for i in range(0, len(answers), n)]

#     for i, line in enumerate(matrix, 1):
#         with open(str(i) + '.json', 'w') as outfile:
#             json.dump(line, outfile)
#         outfile.close()


def sendMessagesJsonToAPI(answers):
    """Sends entire chat log to server"""

    errors = []

    token = getToken()
    url = '{server}/api/v1/qa/modelgroup/{model_group_id}/chatlog'.format(server=server, model_group_id=model_group_id)

    headers = {
        'content-type': "application/json",
        'authorization': "Bearer {token}".format(token=token)
    }

    for index, answer in enumerate(answers):
        print('\n\n---' + str(index))

        if answer['externalId'] is '':
            answer['externalId'] = str(randint(11111111, 99999999))

        resp = requests.request('POST', url, data=json.dumps(answer), headers=headers)
        if resp.status_code is not 201:
            errors.append(answer.externalId)

        print(resp.text)

    print('\n\n\nerrors ' + str(errors))


# def sendMessagesJSON(file):
#     """Sends JSON with part of chat log to server"""

#     errors = []

#     token = getToken()
#     url = '{server}/api/v1/qa/modelgroup/{model_group_id}/chatlog'.format(
#         server=server, model_group_id=model_group_id)

#     headers = {
#         'content-type': "application/json",
#         'authorization': "Bearer {token}".format(token=token)
#     }

#     arr = json.loads(open(file).read())

#     for i, line in enumerate(arr):
#         print('\n\n---' + str(i))

#         if line['externalId'] is '':
#             line['externalId'] = str(randint(11111111, 99999999))

#         resp = requests.request(
#             'POST', url, data=json.dumps(line), headers=headers)

#         if resp.status_code is not 201:
#             errors.append(line.externalId)

#         print(resp.text)

#     print('\n\n\n' + str(errors))


readMessagesFile('chat_log.csv')
