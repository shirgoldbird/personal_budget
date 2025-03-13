#!/usr/bin/env python
import os
import sys
import argparse
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

def setup_google_sheet(creds_path, sheet_id=None, sheet_name=None):
    """
    Sets up a Google Sheet for transaction tracking.
    If sheet_id is provided, adds a new sheet to an existing spreadsheet.
    If sheet_id is not provided, creates a new spreadsheet.
    """
    # Load credentials
    try:
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

    # Build the Sheets API client
    service = build('sheets', 'v4', credentials=creds)
    sheets = service.spreadsheets()
    
    # Create a new spreadsheet or use existing one
    if not sheet_id:
        try:
            # Create a new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': sheet_name or 'Personal Budget Tracker'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Transactions',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            result = sheets.create(body=spreadsheet).execute()
            sheet_id = result['spreadsheetId']
            print(f"Created new spreadsheet with ID: {sheet_id}")
            print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    else:
        # Add a transactions sheet to existing spreadsheet if it doesn't exist
        try:
            metadata = sheets.get(spreadsheetId=sheet_id).execute()
            sheet_exists = False
            
            for sheet in metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == 'Transactions':
                    sheet_exists = True
                    break
            
            if not sheet_exists:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': 'Transactions',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                }
                
                body = {'requests': [request]}
                response = sheets.batchUpdate(spreadsheetId=sheet_id, body=body).execute()
                print("Added 'Transactions' sheet to existing spreadsheet")
        
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    # Add headers to the Transactions sheet
    headers = [
        'Transaction ID', 'Date', 'Account ID', 'Description', 
        'Amount', 'Category', 'Notes', 'Timestamp'
    ]
    
    try:
        body = {
            'values': [headers]
        }
        
        result = sheets.values().update(
            spreadsheetId=sheet_id,
            range='Transactions!A1:H1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Added headers to Transactions sheet: {result.get('updatedCells')} cells updated")
        
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
    
    return sheet_id

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Set up Google Sheets for budget tracking')
    parser.add_argument('--creds', type=str, help='Path to Google service account credentials JSON file')
    parser.add_argument('--sheet-id', type=str, help='Existing Google Sheet ID (optional)')
    parser.add_argument('--sheet-name', type=str, help='Name for new spreadsheet (optional)')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials path
    creds_path = args.creds or os.environ.get('GOOGLE_CREDS_PATH')
    if not creds_path:
        print("Error: Google credentials path not provided")
        print("Please specify with --creds or set GOOGLE_CREDS_PATH environment variable")
        return 1
    
    # Get or create sheet ID
    sheet_id = args.sheet_id or os.environ.get('GOOGLE_SHEET_ID')
    sheet_name = args.sheet_name
    
    # Setup the sheet
    result_id = setup_google_sheet(creds_path, sheet_id, sheet_name)
    
    if result_id:
        print(f"\nSetup complete! Add this to your .env file:")
        print(f"GOOGLE_SHEET_ID={result_id}")
        return 0
    else:
        print("Setup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())