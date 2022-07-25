from src import rls_umfrage_auswertung
import logging
import sys
import pandas as pd
import pprint


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    codebook_dict = rls_umfrage_auswertung.main_preprocessing_codebook()
    # rls_umfrage_auswertung.evaluating_with_codebook(codebook_dict)
    survey_data = pd.read_csv(
        "data/2022_06_RLI_Klimaneutrales Stromsystem_E-Mailverteiler_Ergebnisse.csv",
        delimiter=";",
        header=2,
    )
    rls_umfrage_auswertung.create_stacked_bar_chart_percent(
        survey_data, codebook_dict, question_number=31b
    )


if __name__ == "__main__":
    main()
