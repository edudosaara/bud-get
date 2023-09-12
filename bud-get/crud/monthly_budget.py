import boto3
import logging
from decimal import Decimal
from datetime import datetime
import os
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
monthlyBudgetTable = dynamodb.Table(os.environ.get('MonthlyBudgetTable'))

def getMonthlyBudget(ref_date):
    try:
        response = monthlyBudgetTable.get_item(
            Key={'ref_date': ref_date}
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {ref_date} not found!')
    except Exception as e:
        logger.exception(f'Error getting element: {e}')


def getMonthlyBudgets():
    try:       
        response = monthlyBudgetTable.scan()
        return response['Items']
    except Exception as e:
        logger.exception(f'Error getting all: {e}')
    
def loadMonthlyBudgets(bodys):
    try:
        for t in bodys:
            createMonthlyBudget(t)
    except Exception as e:
        logger.exception(f'Error while loading batch: {e}')
    
    
def createMonthlyBudget(requestBody):
    try:
        requestBody['ref_date'] = uuid.uuid4()
        requestBody['timestamp'] = datetime.now().isoformat()
        monthlyBudgetTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during creation: {e}')
        
def updateMonthlyBudget(requestBody):
    try:
        item = monthlyBudgetTable.get_item(
            Key={ 'ref_date': requestBody['ref_date'] }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now().isoformat()
        monthlyBudgetTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
            
def deleteMonthlyBudget(ref_date):
    try:
        response = monthlyBudgetTable.delete_item(
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
        