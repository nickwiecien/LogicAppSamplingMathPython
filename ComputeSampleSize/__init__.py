import logging
import random
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    SampleSize = float(req_body.get('SampleSize'))
    TotalNumberOfImages = int(req_body.get('TotalNumberOfImages'))

    NumberOfImagesToProcess = int(SampleSize * TotalNumberOfImages)
    IndexesToProcess = random.sample(range(0, TotalNumberOfImages-1), NumberOfImagesToProcess)

    return_obj = {'indexes': IndexesToProcess, 'numberOfImagesToProcess': NumberOfImagesToProcess}

    return func.HttpResponse(json.dumps(return_obj))
   
