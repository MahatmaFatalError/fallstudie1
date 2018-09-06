#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from config import constants
from main.helper.db_helper import SqlHelper, DatastoreHelper
from main.helper import util
import logging

logger = logging.getLogger(__name__)


def main():
    gcp_entity = None
    choices = {1: constants.GCP_ENTITY_RESTAURANT,
               2: constants.GCP_ENTITY_KAUFKRAFT,
               3: constants.GCP_ENTITY_RENT,
               4: constants.GCP_ENTITY_SPEISEKARTE,
               5: constants.SQL_TABLE_ZIP_CODE,
               6: constants.GCP_ENTITY_REVIEW
               }

    action_string = 'What do you want to reset?\n'

    for key in choices.keys():
        choice = '({0}){1}\n'.format(str(key), choices[key])
        action_string += choice

    action_string += "Answer by type in the number."

    util.setup_logging()

    action_number = int(input(action_string))

    gcp_entity = choices[action_number]

    if action_number not in [5]:
        reset_datastore(gcp_entity)
    # else:
    # reset_postgres()


def reset_datastore(gcp_entity):
    datastore = DatastoreHelper()

    ds_entities = datastore.fetch_entity(gcp_entity, None, None, False, None)
    for ds_entity in ds_entities:
        datastore.set_transported(ds_entity, False)


def reset_postgres():
    sql = SqlHelper(constants.SQL_DATABASE_NAME)

    sql.create_session()
    sql_entities = sql.fetch_entity_where('ZipCode', True)
    for sql_entity in sql_entities:
        sql_entity.requested = False

    sql.commit_session()
    sql.close_session()


if __name__ == '__main__':
    main()
