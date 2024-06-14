import requests
import json
import os
from dotenv import load_dotenv
from skyflow.errors import SkyflowError
from skyflow.service_account import generate_bearer_token, is_expired
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

def send_prompt_to_server(text):
    load_dotenv(override=True) 
    url = os.getenv("DETECT_API_URL")
    token = os.getenv("Token")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'X-SKYFLOW-ACCOUNT-ID':os.getenv("X-SKYFLOW-ACCOUNT-ID")
    }
    requestData = {
        "text": text,
        "return_entities": True,
        "deidentify_option": "ENTITY_UNQ_COUNTER",
        "restrict_entity_types" : ["all"],
        "vault_id": os.getenv("vault_id"),
        "store_entities": True,
        "advanced_options": {
            "schema": {
                "table_name": "table1",
                "mapping": {
                    "session_id": "session_id",
                    "default": "text"
                }
            }
        },  
        "session_id": "1" 
    }
    try:
        response = requests.post(url, headers=headers, json=requestData)
        response.raise_for_status()
        return response.json() 
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        if response.status_code in [403, 404, 500]:
            logger.info("Fetching new bearer token...")
            headers['Authorization'] =f'Bearer {os.getenv("Token")}',
            try:
                response = requests.post(url, headers=headers, json=requestData)
                response.raise_for_status()
                return response.json()  # Convert the response body to JSON
            except requests.RequestException as e:
                logger.error(f"Error during retry: {e}")
                return None
        else:
            logger.error(f"Error during fetch operation: {e}")
            return None
    
def skyflow_detect(text):
    # Example usage
    response = send_prompt_to_server(text)
    return response

def skyflow_identify(text):
    load_dotenv(override=True) 
    url = os.getenv("IDENTIFY_API_URL")
    token = os.getenv("Token")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    requestData = {
        "text": text,
        "vault_id": os.getenv("vault_id")
    }
    try:
        response = requests.post(url, headers=headers, json=requestData)
        response.raise_for_status()
        return response.json()  # Convert the response body to JSON
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        if response.status_code in [403, 404, 500]:
            logger.info("Fetching new bearer token...")
            headers['Authorization'] = f'Bearer {os.getenv("Token")}',
            try:
                response = requests.post(url, headers=headers, json=requestData)
                response.raise_for_status()
                return response.json()  # Convert the response body to JSON
            except requests.RequestException as e:
                logger.error(f"Error during retry: {e}")
                return None
        else:
            logger.error(f"Error during fetch operation: {e}")
            return None