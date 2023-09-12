import boto3
import logging
from decimal import Decimal
from datetime import datetime
import os
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
accountsTable = dynamodb.Table(os.environ.get('AccountsTable'))

def getAccount(account_id):
    try:
        response = accountsTable.get_item(
            Key={'account_id': account_id}
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {account_id} not found!')
    except Exception as e:
        logger.exception(f'Error getting element: {e}')


def getAccounts():
    try:       
        response = accountsTable.scan()
        return response['Items']
    except Exception as e:
        logger.exception(f'Error getting all: {e}')
    
def loadAccounts(bodys):
    try:
        for t in bodys:
            createAccount(t)
    except Exception as e:
        logger.exception(f'Error while loading batch: {e}')
    
    
def createAccount(requestBody):
    try:
        requestBody['account_id'] = str(uuid.uuid4())
        requestBody['timestamp'] = datetime.now().isoformat()
        accountsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during creation: {e}')
        
def updateAccount(requestBody):
    try:
        item = accountsTable.get_item(
            Key={ 'account_id': requestBody['account_id'] }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now().isoformat()
        accountsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
            
def deleteAccount(account_id):
    try:
        response = accountsTable.delete_item(
            Key = { 'account_id': account_id },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return body
    except Exception as e:
        logger.exception(f'Error while deleting {account_id}: {e}')
        