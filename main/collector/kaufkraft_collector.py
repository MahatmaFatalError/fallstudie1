# -*- coding: utf-8 -*-
import datetime
from main.collector.collector import Collector
import pandas as pd
import numpy as np
import PyPDF2
from main.helper.result import Result
from main.helper.util import parse


class KaufkraftCollector(Collector):

    pdf_path = None
    entity_id = None

    def __init__(self, entity_id, entity_name, test_mode, path):
        super(KaufkraftCollector, self).__init__(
            entity_name=entity_name,
            test_mode=test_mode
        )
        self.pdf_path = path
        self.entity_id = entity_id

    def _create_datastore_entity(self, content) -> dict:
        return {'updatedAt': datetime.datetime.now(), 'content': content, 'transported': False}

    def run(self):
        result = Result()
        pdf_file_obj = open(self.pdf_path, "rb")
        pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
        content = ""
        num_pages = pdf_reader.getNumPages()
        for x in range(num_pages):
            content += pdf_reader.getPage(x).extractText()
        last = "© Michael Bauer Research GmbH, Nürnberg \nTelefon: 0911 / 28 707 020\nE-Mail: info@mb-research.de\n"
        content = content.replace(last, "")
        content = content[:-1]  # delete last \n
        split = content.split("Euro pro Kopf\n")
        replace = "\nJahresdurchschnitt\nbezogen auf\nBevölkerung\nKaufkraft 2017\nWachstumsrate in %\nPrognose 2017\n2016 bis 2017"
        string = split[1].replace(replace, "")

        # split hole String on "/n" and put it into an array
        ar = np.array(string.split("\n"))

        # number of rows are 12
        # transform the array into a row with 12 columns
        n_rows = 12
        df = pd.DataFrame(np.reshape(ar, (-1, n_rows)))

        # split and rename city columns
        df_city = df[0].str.split(", ", expand=True).rename(columns={0: "city", 1: "city_type"})

        # parse and rename rest of columns
        df_values = df.iloc[:, 1:].applymap(parse).rename(columns={1: "pop_2016",
                                                                   2: "buyingpower_2016_buyingpowerindex",
                                                                   3: "pop_forecast_2017",
                                                                   4: "pop_forecast_2017_permille",
                                                                   5: "households_forecast_2017",
                                                                   6: "buyingpower_2017_euro",
                                                                   7: "buyingpower_2017_permille",
                                                                   8: "buyingpower_2017_euro_a_head",
                                                                   9: "buyingpower_2017_buyingpowerindex",
                                                                   10: "growthrate_2016_2017_percentage_euro",
                                                                   11: "growthrate_2016_2017_percentage_euro_a_head"})
        # match both dataframe df_city and df_values together
        df_result = pd.concat([df_city, df_values], axis=1)
        # transform row from mio euro to euro
        df_result.growthrate_2016_2017_percentage_euro = df_result.growthrate_2016_2017_percentage_euro.apply(
            lambda x: x * 1000000)
        result_json = df_result.to_json(orient='records')
        if not self.test_mode:
            datastore_entity = self._create_datastore_entity(result_json)
            success = self._save(self.entity_id, datastore_entity)
            result.set_success(success)
            self.logger.info(result)
        return result
