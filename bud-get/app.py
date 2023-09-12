import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics
from decimal import Decimal
from crud.transactions import *
from crud.accounts import *
from crud.balance_history import *
from crud.monthly_budget import *
from crud.recurring_transactions import *
from crud.config import *

app = APIGatewayRestResolver()
logger = Logger()
metrics = Metrics(namespace="Powertools")

def queryParam(app, name):
    return app.current_event.query_string_parameters.get(name) or None

def parseBody(app):
    return json.loads(app.current_event.body, parse_float=Decimal) or {}

@app.get("/")
def health(): return {"response": "OK"}

##################
#  TRANSACTIONS  #
##################
@app.get("/transactions")
def transactionsGET():
    return getTransactions(queryParam(app, "ref_date"))
    
@app.post("/transactions")
def transactionsPOST():
    return loadTransactions(parseBody(app))

@app.get("/transaction")
def transactionGET():
    return getTransaction(queryParam(app, "ref_date"), int(queryParam(app, "index")))

@app.post("/transaction")
def transactionPOST():
    return createTransaction(parseBody(app))

@app.put("/transaction")
def transactionPUT():
    return updateTransaction(parseBody(app))
    
@app.delete("/transaction")
def transactionDELETE():
    return deleteTransaction(queryParam(app, "ref_date"), int(queryParam(app, "index")))

################
#   ACCOUNTS   #
################
@app.get("/accounts")
def accountsGET():
    return getAccounts()
    
@app.post("/accounts")
def accountsPOST():
    return loadAccounts(parseBody(app))

@app.get("/account")
def accountGET():
    return getAccount(queryParam(app, "account_id"))

@app.post("/account")
def accountPOST():
    return createAccount(parseBody(app))

@app.put("/account")
def accountPUT():
    return updateAccount(parseBody(app))
    
@app.delete("/account")
def accountDELETE():
    return deleteAccount(queryParam(app, "account_id"))

#######################
#   BALANCE HISTORY   #
#######################
@app.get("/balanceHistorys")
def balanceHistorysGET():
    return getBalanceHistorys()
    
@app.post("/balanceHistorys")
def balanceHistorysPOST():
    return loadBalanceHistorys(parseBody(app))

@app.get("/balanceHistory")
def balanceHistoryGET():
    return getBalanceHistory(queryParam(app, "ref_date"))

@app.post("/balanceHistory")
def balanceHistoryPOST():
    return createBalanceHistory(parseBody(app))

@app.put("/balanceHistory")
def balanceHistoryPUT():
    return updateBalanceHistory(parseBody(app))
    
@app.delete("/balanceHistory")
def balanceHistoryDELETE():
    return deleteBalanceHistory(queryParam(app, "ref_date"))

#######################
#   MONTHLY BUDGET    #
#######################
@app.get("/monthlyBudgets")
def monthlyBudgetsGET():
    return getMonthlyBudgets()
    
@app.post("/monthlyBudgets")
def monthlyBudgetsPOST():
    return loadMonthlyBudgets(parseBody(app))

@app.get("/monthlyBudget")
def monthlyBudgetGET():
    return getMonthlyBudget(queryParam(app, "ref_date"))

@app.post("/monthlyBudget")
def monthlyBudgetPOST():
    return createMonthlyBudget(parseBody(app))

@app.put("/monthlyBudget")
def monthlyBudgetPUT():
    return updateMonthlyBudget(parseBody(app))
    
@app.delete("/monthlyBudget")
def monthlyBudgetDELETE():
    return deleteMonthlyBudget(queryParam(app, "ref_date"))

##########################
# RECURRING TRANSACTIONS #
##########################
@app.get("/recurringTransactions")
def recurringTransactionsGET():
    return getRecurringTransactions()
    
@app.post("/recurringTransactions")
def recurringTransactionsPOST():
    return loadRecurringTransactions(parseBody(app))

@app.get("/recurringTransaction")
def recurringTransactionGET():
    return getRecurringTransaction(queryParam(app, "id"))

@app.post("/recurringTransaction")
def recurringTransactionPOST():
    return createRecurringTransaction(parseBody(app))

@app.put("/recurringTransaction")
def recurringTransactionPUT():
    return updateRecurringTransaction(parseBody(app))
    
@app.delete("/recurringTransaction")
def recurringTransactionDELETE():
    return deleteRecurringTransaction(queryParam(app, "id"))

##########################
#         CONFIGS        #
##########################
@app.get("/configs")
def configsGET():
    return getConfigs()
    
@app.post("/configs")
def configsPOST():
    return loadConfigs(parseBody(app))

@app.get("/config")
def configGET():
    return getConfig(queryParam(app, "config_id"))

@app.post("/config")
def configPOST():
    return createConfig(parseBody(app))

@app.put("/config")
def configPUT():
    return updateConfig(parseBody(app))
    
@app.delete("/config")
def configDELETE():
    return deleteConfig(queryParam(app, "config_id"))

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
