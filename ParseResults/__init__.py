import logging

import azure.functions as func

import os
import json
import tempfile
import pandas as pd
import uuid

from azure.storage.blob import BlobServiceClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    #Parse request body
    req_body = req.get_json()

    try:
        #Get custom vision/form recognizer results from body
        customVisionResults = req_body.get('customVisionResponse')
        formRecognizerResults = req_body.get('formsRecognizerResponse')
        PartitionKey = req_body.get('PartitionKey')
        RowKey = req_body.get('RowKey')

        #Store formatted results in a dictionary - will be converted to a Pandas dataframe
        results = {}

        #Add partition key and row key
        results['PartitionKey'] = PartitionKey
        results['RowKey'] = RowKey

        #Iterate over custom vision results - store highest scoring symbol
        #Optional: Implement symbol-specific thresholds
        for pred in customVisionResults['predictions']:
                if 'Symbol_{}'.format(pred['tagName']) not in results:
                    results['Symbol_{}'.format(pred['tagName'])] = pred['probability']
                else:
                    if results['Symbol_{}'.format(pred['tagName'])] < pred['probability']:
                        results['Symbol_{}'.format(pred['tagName'])] = pred['probability']

        #Iterate over Form Recognizer results to get tag values
        results['Form Recognizer Status'] = formRecognizerResults['status']

        for res in formRecognizerResults['analyzeResult']['readResults']:
            results['Form Recognizer Label'] = res['language']
            break 
            
        for doc in formRecognizerResults['analyzeResult']['documentResults']:
            for k,v in doc['fields'].items():
                if v is not None:
                    results[k] = v['valueString']

        spaceless_results = {}
        for k,v in results.items():
            if k=='3MID':
                spaceless_results['MMM_ID'] = v
            else:
                spaceless_results[k.replace(' ', '_')] = v

        #Retrun results json record with custom vision & form recognizer data
        return func.HttpResponse(json.dumps(spaceless_results), status_code=200)

        # Deprecated code for export results to Excel and uploading to Blob Storage
        # #Get temporary directory
        # tempdir = tempfile.gettempdir()

        # filename = '{}.xlsx'.format(str(uuid.uuid4()))

        # #Write blob data to temporary file
        # df = pd.DataFrame([results])
        # df.to_excel(os.path.join(tempdir, filename), index=False)

        # #Read data from excel file
        # upload_data = None
        # with open(os.path.join(tempdir, filename), 'rb') as file:
        #     upload_data = file.read()
        
        # #Upload updated file to blob storage
        # client = BlobServiceClient(os.environ.get('UPLOAD_STORAGE_ACCOUNT_URL'), os.environ.get('UPLOAD_STORAGE_ACCOUNT_KEY'))
        # container_client = client.get_container_client(os.environ.get('OUTPUT_CONTAINER'))
        # container_client.upload_blob(filename, upload_data, overwrite=True)

        # #Remove temporary excel files
        # os.remove(os.path.join(tempdir, filename))

        # return func.HttpResponse(json.dumps({'blobPath': '{}/{}'.format(os.environ.get('OUTPUT_CONTAINER'), filename)}), status_code=200)

    except Exception as e:
        return func.HttpResponse(status_code=500)
