from datetime import datetime, timedelta
from google.cloud import storage
from flask import escape
import requests
from bs4 import BeautifulSoup

def check_and_download(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    response = requests.get('https://www.justice.gov/eoir/foia-library-0')
    soup = BeautifulSoup(response.text, 'html.parser')
    # Search in the webpage for the element containing the last updated date.
   
    last_updated_element = soup.find("div", class_="last-updated") 
    last_updated_text = last_updated_element.text

    # Convert the text into a datetime object
    # The format depends on how the date is displayed on the website
    last_updated_date = datetime.strptime(last_updated_text, '%Y-%m-%d %H:%M:%S')

    # Check if the page was updated within the last 24 hours
    if last_updated_date > datetime.now() - timedelta(days=1):
        download_and_store()

    return f'Checked and downloaded data successfully!'


def download_and_store():
    response = requests.get('https://fileshare.eoir.justice.gov/FOIA-TRAC-Report.zip')

    # Make sure the request was successful
    response.raise_for_status()

    # Create a client to access the storage
    client = storage.Client(project='eoia-datapipeline')
    bucket = client.get_bucket('foia_zip')

    # Create a new blob and upload the file's content
    blob = bucket.blob('EOIA_Case_Data.zip')
    blob.upload_from_string(response.content)

    print('File uploaded to {}.'.format(bucket))
