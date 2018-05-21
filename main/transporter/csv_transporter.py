import json
import logging
from main.transporter.transporter import Transporter
from main.database.DBHelper import SqlHelper, DatastoreHelper

logger = logging.getLogger(__name__)


class Csv(Transporter):

    def transport(self):
        source_db = DatastoreHelper()
        target_db = SqlHelper(self.database)
        source_entities = source_db.fetch_all_entities(self.source_entity)
        target_db_columns = target_db.get_table_column_names(self.target_table)
        logger.debug(target_db_columns)
        for message in source_entities:
            content = json.loads(message['content'])
            db_entry = self.map(content, target_db_columns)
            logger.info("Saving from Datastore %s into DB Table %s...", source_db, target_db)
            # target_db.insert(db_entry, self.target_table)

    def map(self, source_entity, target_fields):
        db_entry = {}
        logger.debug(source_entity)
        for item in source_entity:
            ...
            # TODO Mapping

        return db_entry
