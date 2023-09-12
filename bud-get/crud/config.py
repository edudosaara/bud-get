import boto3
import logging
from decimal import Decimal
from datetime import datetime
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
configTable = dynamodb.Table(os.environ.get('ConfigTable'))

def getConfig(config_id):
    try:
        response = configTable.get_item(
            Key={'config_id': config_id}
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {config_id} not found!')
    except Exception as e:
        logger.exception(f'Error getting element: {e}')


def getConfigs():
    try:       
        response = configTable.scan()
        return response['Items']
    except Exception as e:
        logger.exception(f'Error getting all: {e}')
    
def loadConfigs(bodys):
    try:
        for t in bodys:
            createConfig(t)
    except Exception as e:
        logger.exception(f'Error while loading batch: {e}')
    
    
def createConfig(requestBody):
    try:
        requestBody['timestamp'] = datetime.now().isoformat()
        configTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during creation: {e}')
        
def updateConfig(requestBody):
    try:
        item = configTable.get_item(
            Key={ 'config_id': requestBody['config_id'] }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now().isoformat()
        configTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
            
def deleteConfig(config_id):
    try:
        response = configTable.delete_item(
            Key = { 'config_id': config_id },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return body
    except Exception as e:
        logger.exception(f'Error while deleting {config_id}: {e}')
        