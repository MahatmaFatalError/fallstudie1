# Fallstudie1 - T(eam) HD

## Data Pipeline

## OneDrive Link
[THD OneDrive](https://srhk-my.sharepoint.com/:f:/g/personal/11010021_stud_hochschule-heidelberg_de/EsJ-yxpcI2BGk5ccB-yAlkMBkr0FEeI69z9Gz9BdiL1NCg?e=Udhkxj)

## Prerequistes
 1. Python 3.6
    - https://www.python.org/downloads/
 2. Google Cloud SDK (with bundled Python)
    - https://cloud.google.com/sdk/docs/?hl=de
 3. pip (should be included in python install bundle)
    - https://pip.pypa.io/en/stable/installing/
 4. ``` pip install --upgrade google-cloud ```
 5. ``` pip install --upgrade sqlalchemy ```
 6. ``` pip install --upgrade psycopg2 ```

## How-To: Start a Proxy for PostreSQL Connection (not working for JWEBER :-))
1. ``` gcloud auth login ```
2. ``` gcloud auth application-default login ```
3. ``` cd <folder with cloud_sql_proxy.exe> ```
3. ``` cloud_sql_proxy -instances=ace-ripsaw-200308:europe-west1:t3am-thd=tcp:5432 ```

## Useful Links
- https://www.yelp.de/developers/documentation/v3/business_search
- https://cloud.google.com/datastore/docs/concepts/entities#datastore-update-python
- https://github.com/Yelp/yelp-fusion/blob/master/fusion/python/sample.py
- https://opensource.com/article/17/9/python-logging
- http://ipv4.whatismyv6.com/
