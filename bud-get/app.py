from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics
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
    return loadTransactions(bodys=app.current_event.body)

@app.get("/transaction")
def transactionGET():
    return getTransaction(
        refDate=app.current_event.query_string_parameters.get("ref_date"),
        index=int(app.current_event.query_string_parameters.get("index"))
    )

@app.post("/transaction")
def transactionPOST():
    return createTransaction(app.current_event.body)

@app.put("/transaction")
def transactionPUT():
    return updateTransaction(app.current_event.body)
    
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
