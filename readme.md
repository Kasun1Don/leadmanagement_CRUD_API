# How to use the JSON API for Lead Signal Tracking app

## This API can CRUD

### header: application/json

### Ensure Correct Content-Type in Insomnia

When you make the PUT request in Insomnia, make sure to set the Content-Type header to application/json.

Example Steps in Insomnia:

* Set the Request Method: Select PUT.
* Set the URL: http://localhost:5000/lead/3 (replace 1 with the actual id of the lead you want to update).

Set the Headers:
* Click on the "Headers" tab.

Add a new header:
* Key: Content-Type
* Value: application/json

Set the Body:
* Click on the "Body" tab.
* Select JSON from the dropdown.
* Enter your JSON payload (column_id & lead id are different - check url):

```py
{
  "company_name": "ACME",
  "description": "Updated Description", #option
  "lead_owner": "Updated Owner", #option
  "column_id": 1
}
or
{
  "company_name": "ACME",
  "column_id": 1
}

```

## Roadmap of Features

1. Flask Migrations to preserve new data instead of dropping all tables
2. Front end (resolving javascript issues - run in firefox) 
