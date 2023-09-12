import boto3
import logging
from decimal import Decimal
from datetime import datetime
import os
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
balanceHistoryTable = dynamodb.Table(os.environ.get('BalanceHistoryTable'))

def getBalanceHistory(ref_date):
    try:
        response = balanceHistoryTable.get_item(
            Key={'ref_date': ref_date}
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {ref_date} not found!')
    except Exception as e:
        logger.exception(f'Error getting element: {e}')


def getBalanceHistorys():
    try:       
        response = balanceHistoryTable.scan()
        return response['Items']
    except Exception as e:
        logger.exception(f'Error getting all: {e}')
    
def loadBalanceHistorys(bodys):
    try:
        for t in bodys:
            createBalanceHistory(t)
    except Exception as e:
        logger.exception(f'Error while loading batch: {e}')
    
    
def createBalanceHistory(requestBody):
    try:
        requestBody['ref_date'] = uuid.uuid4()
        requestBody['timestamp'] = datetime.now().isoformat()
        balanceHistoryTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during creation: {e}')
        
def updateBalanceHistory(requestBody):
    try:
        item = balanceHistoryTable.get_item(
            Key={ 'ref_date': requestBody['ref_date'] }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now().isoformat()
        balanceHistoryTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
            
def deleteBalanceHistory(ref_date):
    try:
        response = balanceHistoryTable.delete_item(
            Key = { 'ref_date': ref_date },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return body
    except Exception as e:
        logger.exception(f'Error while deleting {ref_date}: {e}')
        