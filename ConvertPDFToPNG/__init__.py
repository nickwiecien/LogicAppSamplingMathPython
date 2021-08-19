import logging
import tempfile 
import fitz
from typing import Tuple
import os
import json
import azure.functions as func
import base64


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    req_body = req.get_json()
    pdf_bytes = base64.b64decode(req_body.get('data'))
    tempdir = tempfile.gettempdir()
    temp_pdf = os.path.join(tempdir, 'upload.pdf')
    temp_png = os.path.join(tempdir, 'download.png')

    with open(temp_pdf, 'wb') as file:
        file.write(pdf_bytes)

    # Adapted from https://www.thepythoncode.com/article/convert-pdf-files-to-images-in-python
    # Leverages https://github.com/pymupdf/PyMuPDF
    pages = None
    pdfIn = fitz.open(temp_pdf)
    output_files = []
    # Iterate throughout the pages
    for pg in range(pdfIn.pageCount):
        if str(pages) != str(None):
            if str(pg) not in str(pages):
                continue
        # Select a page - asumed single page
        page = pdfIn[pg]
        rotate = int(0)
        zoom_x = 2
        zoom_y = 2
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        output_file = temp_png
        pix.writePNG(output_file)
        output_files.append(output_file)
    pdfIn.close()
        
    out_bytes = None
    with open(temp_png, 'rb') as file:
        out_bytes = file.read()
        
    os.remove(temp_pdf)
    os.remove(temp_png)

    return func.HttpResponse(json.dumps({'png_content': base64.b64encode(out_bytes).decode()}))