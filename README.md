# Fallstudie1 - T(eam) HD

## Data Pipeline

## OneDrive Link
[THD OneDrive](https://srhk-my.sharepoint.com/:f:/g/personal/11010021_stud_hochschule-heidelberg_de/EsJ-yxpcI2BGk5ccB-yAlkMBkr0FEeI69z9Gz9BdiL1NCg?e=Udhkxj)

## Prerequistes
 1. Python 3.6
    - https://www.python.org/downloads/
 2. pip (should be included in python install bundle)
    - https://pip.pypa.io/en/stable/installing/
 3. ``` pip install --upgrade google-cloud-datastore ```
 4. ``` pip install --upgrade sqlalchemy ```
 5. ``` pip install --upgrade psycopg2 ```
 6. ``` pip install --upgrade requests ```
 7. ``` pip install --upgrade pandas ```
 8. ``` pip install --upgrade PyPDF2 ```
 9. ``` pip install --upgrade nltk ```
 10. ``` pip install --upgrade sklearn ```
 11. Tree Tagger
     - [Installation Guide](http://www.smo.uhi.ac.uk/~oduibhin/oideasra/interfaces/winttinterface.htm)
 12. ``` pip install --upgrade treetaggerwrapper ```
     - [Usage Guide](https://treetaggerwrapper.readthedocs.io/en/latest/)
     - [List of POS Tags (Deutsch)](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/stts_guide.pdf)
     - [List of POS Tags (English)](http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/Penn-Treebank-Tagset.pdf)
 13. ``` pip install --upgrade requests_oauthlib ```

## Useful Links
- https://www.yelp.de/developers/documentation/v3/business_search
- https://cloud.google.com/datastore/docs/concepts/entities#datastore-update-python
- https://github.com/Yelp/yelp-fusion/blob/master/fusion/python/sample.py
- https://opensource.com/article/17/9/python-logging
- http://ipv4.whatismyv6.com/
- http://docs.sqlalchemy.org/en/latest/core/type_basics.html
- https://www.suche-postleitzahl.org/downloads
- https://cloud.google.com/datastore/docs/concepts/queries
- https://github.com/mstamy2/PyPDF2
- Statistics Query Google Cloud Datastore
    https://cloud.google.com/appengine/docs/standard/python/ndb/admin

## How-To: Connect New Datasource

1. if needed create a new PostgreSQL Table in ```init_db.py``` script in folder ``` main.database```
    -  http://docs.sqlalchemy.org/en/latest/core/type_basics.html
2. Create a new collector. Inherits from ```Collector``` class. Implement at least ```_save()``` and ```collect()``` methods
3. Create a new transporter. Inherit from ```Transporter``` class. Implement only ```map()``` method
4. Create new methods in ```main.helper.creator.py```. For naming conventions and logic of these methods,  please take a look at already defined methods.
5. Update ```choices{}``` in ```main.py``` accordingly.
5. If you need to write some new methods for Database access (Google Datastore or PostgreSQL) please add them in the corresponding class of script ```db_helper.py```
6. Custom Exceptions must be created in script ```exception.py```
7. Please put methods with no relation to to Collector or Transporter into ```util.py```
8. For examples please take a look at already existing code!
9. It is very important to keep the naming convention for collector and transporter. <br>
<b>Filename</b>: ```'<any_string>_collector|transporter``` e.g.: ```plz_collector.py``` <br>
<b>Classname</b>: same as filename but in camel case starting with a capital letter  e.g.: ```PlzCollector```

## Cleaning

Protocol in [```main/cleaning/cleaning.md```](main/cleaning/cleaning.md)
