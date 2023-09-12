import boto3
import logging
from decimal import Decimal
from datetime import datetime
import os
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
recurringTransactionsTable = dynamodb.Table(os.environ.get('RecurringTransactionsTable'))

def getRecurringTransaction(id):
    try:
        response = recurringTransactionsTable.get_item(
            Key={'id': id}
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {id} not found!')
    except Exception as e:
        logger.exception(f'Error getting element: {e}')


def getRecurringTransactions():
    try:       
        response = recurringTransactionsTable.scan()
        return response['Items']
    except Exception as e:
        logger.exception(f'Error getting all: {e}')
    
def loadRecurringTransactions(bodys):
    try:
        for t in bodys:
            createRecurringTransaction(t)
    except Exception as e:
        logger.exception(f'Error while loading batch: {e}')
    
    
def createRecurringTransaction(requestBody):
    try:
        requestBody['id'] = uuid.uuid4()
        requestBody['timestamp'] = datetime.now().isoformat()
        recurringTransactionsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during creation: {e}')
        
def updateRecurringTransaction(requestBody):
    try:
        item = recurringTransactionsTable.get_item(
            Key={ 'ref_date': requestBody['ref_date'] }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now().isoformat()
        recurringTransactionsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
            
def deleteRecurringTransaction(id):
    try:
        response = recurringTransactionsTable.delete_item(
            Key = { 'id': id },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return body
    except Exception as e:
        logger.exception(f'Error while deleting {id}: {e}')
        