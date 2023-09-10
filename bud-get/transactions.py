import boto3
import json
import logging
from decimal import Decimal
from datetime import datetime
from functools import reduce
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
transactionsTable = dynamodb.Table(os.environ.get('TransactionsTable'))

def getTransaction(refDate, index):
    try:
        response = transactionsTable.get_item(
            Key={
                'ref_date': refDate,
                'index': index
            }
        )
        if 'Item' in response:
            return response['Item']
        raise Exception(f'Primary key {refDate} and sort key {index} not found!')
    except Exception as e:
        logger.exception(f'Error: {e}')


def getTransactions(refDate=None):
    try:
        if refDate:
            transactionsOnDate = transactionsTable.scan(
                FilterExpression="#rd = :rd",
                ExpressionAttributeNames={ "#rd": "ref_date" },
                ExpressionAttributeValues={ ':rd': refDate }
            )
            if transactionsOnDate['Count'] == 0:
                return None
            return transactionsOnDate['Items']
        
        response = transactionsTable.scan()
        return response['Items']
    
    except Exception as e:
        logger.exception(f'Error: {e}')

    
def getNextIndexForRefDate(refDate):
    transactionsOnRefDate = getTransactions(refDate)
    if transactionsOnRefDate is None:
        return 1
    maxIndex = reduce(lambda acc, cur: max(acc, cur), [*map(lambda t: t['index'], transactionsOnRefDate)])
    return maxIndex+1
    
def loadTransactions(bodys):
    try:
        for t in bodys:
            createTransaction(t)
    except Exception as e:
        logger.exception(f'Error: {e}')
    
    
def createTransaction(requestBody):
    try:
        requestBody['index'] = getNextIndexForRefDate(requestBody['ref_date'])
        requestBody['timestamp'] = datetime.now().isoformat()
        transactionsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except:
        logger.exception('Log it here for now')
        
def updateTransaction(requestBody):
    try:
        item = transactionsTable.get_item(
            Key={
                'ref_date': requestBody['ref_date'],
                'index': requestBody['index']
            }
        )
        if item is None:
            raise Exception("Original item not found.")
        
        requestBody['timestamp'] = datetime.now()
        transactionsTable.put_item(Item=requestBody)
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return body
    except Exception as e:
        logger.exception(f'Error during update: {e}')
        
def loadFromJson(page):
    try:
        f = open(f'oldTransactions/transactions{str(page)}.json',)
        data = json.load(f, parse_float=Decimal)
        current_ref_date = ""
        counter = 1
        for t in data:
            if current_ref_date != t['ref_date']:
                current_ref_date = t['ref_date']
                counter = 1
            t['index'] = counter
            transactionsTable.put_item(Item=t)
            counter+=1
    except Exception as e:
        logger.exception(f'Error - {e}')
     
def deleteTransaction(refDate, index):
    try:
        response = transactionsTable.delete_item(
            Key = {
                'ref_date': refDate,
                'index': index
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return body
    except:
        logger.exception('Log it here for now')
        