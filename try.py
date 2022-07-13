from src import rls_umfrage_auswertung
import logging
import sys
import pprint

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    codebook_dict = rls_umfrage_auswertung.main_preprocessing_codebook()
    pprint.pprint(codebook_dict)
#rls_umfrage_auswertung.evaluating_with_codebook(answer_column_names)

if __name__ == '__main__':
    main()