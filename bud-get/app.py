import json
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics
from decimal import Decimal
from transactions import (
    getTransactions,
    getTransaction,
    loadTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction
)

app = APIGatewayRestResolver()
logger = Logger()
metrics = Metrics(namespace="Powertools")

@app.get("/")
def health():
    return {"response": "OK"}

@app.get("/transactions")
def transactionsGET():
    return getTransactions(app.current_event.query_string_parameters.get("ref_date") or None)
    
@app.post("/transactions")
def transactionsPOST():
    return loadTransactions(json.loads(app.current_event.body, parse_float=Decimal))

@app.get("/transaction")
def transactionGET():
    return getTransaction(
        refDate=app.current_event.query_string_parameters.get("ref_date"),
        index=int(app.current_event.query_string_parameters.get("index"))
    )

@app.post("/transaction")
def transactionPOST():
    return createTransaction(json.loads(app.current_event.body, parse_float=Decimal))

@app.put("/transaction")
def transactionPUT():
    return updateTransaction(json.loads(app.current_event.body, parse_float=Decimal))
    
@app.delete("/transaction")
def transactionDELETE():
    return deleteTransaction(
        refDate=app.current_event.query_string_parameters.get("ref_date"),
        index=int(app.current_event.query_string_parameters.get("index"))
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
