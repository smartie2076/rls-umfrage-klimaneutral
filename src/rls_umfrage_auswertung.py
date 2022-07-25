import pandas as pd
import numpy as np
import logging
import pprint
import matplotlib.pyplot as plt

logging = logging.getLogger(__name__)

results = "./data"

codebook_file = "2022_06_RLI_Klimaneutrales Stromsystem_Codebook"

surveys = {
    "E-Mailverteiler": "2022_06_RLI_Klimaneutrales Stromsystem_E-Mailverteiler_Ergebnisse",
    "Internes Netzwerk": "2022_06_RLI_Klimaneutrales Stromsystem_internes-Netzwerk_Ergebnisse",
    "Pressemitteilung": "2022_06_RLI_Klimaneutrales Stromsystem_Pressemitteilung_Ergebnisse",
}

suffix = ".csv"

A = "A"
B = "B"
C = "C"
D = "D"
E = "E"
columns = "columns"
question = "question"
subquestion = "subquestion"
m_options = "multiple-choice-options"

# Define three characteristics
group_three_word_entries = [4, 11, 16, 21, 22, 26, 27, 34, 35]
# Multiple choice with 4 options
group_yes_rather_yes_rather_no_no = [5, 7, 9, 36]
# If you voted xy - why did you do that?
group_filter_follow_up_question = [6, 8, 10, 37, 39]
# Aufholbedarf
group_need_to_catch_up = [17, 18, 19, 20, 23, 24, 25, 28, 29, 30, 31, 32, 33]

EXCLUDE_CODES = [-77, -99, -66, 0, "0", "-66", "-99", "-77"]


def main_preprocessing_codebook():
    codebook_csv = pd.read_csv(
        f"{results}/{codebook_file}{suffix}",
        delimiter=";",
        encoding="ANSI",
        na_values=None,
    )
    codebook_csv = codebook_csv.replace({np.nan: None})

    codebook_dict = {}

    numbers = [i for i in range(4, 41)]

    for row in codebook_csv.index:
        try:
            value = float(codebook_csv.loc[row, A])
            question_number = int(codebook_csv.loc[row, A])
            two_below = codebook_csv.loc[row + 2, A]
            if isinstance(two_below, str):
                logging.debug(f"{question_number}: {codebook_csv.loc[row + 2, A]}")
                row, got_codebook = get_codebook_for_question(
                    codebook_csv, codebook_dict, question_number, row
                )
                if got_codebook is True:
                    numbers.remove(question_number)
        except:
            pass

    logging.info(f"Following questions are not assessed: {numbers}")

    pprint.pprint(codebook_dict)

    return codebook_dict


def evaluating_with_codebook(codebook_dict):
    for group in surveys.keys():
        numbers = [i for i in range(4, 41)]

        survey_data = pd.read_csv(
            f"{results}/{surveys[group]}{suffix}", delimiter=";", header=2
        )

        numbers = create_wordclouds(codebook_dict, survey_data, group, numbers)

        for question_number in (
            group_yes_rather_yes_rather_no_no + group_need_to_catch_up + [13, 14, 15]
        ):
            for subquestion_number in codebook_dict[question_number][
                subquestion
            ].keys():
                try:
                    values = survey_data[
                        [
                            codebook_dict[question_number][subquestion][
                                subquestion_number
                            ][columns]
                        ]
                    ]
                    message_data_received(codebook_dict, question_number)
                    numbers.remove(question_number)
                except:
                    logging.warning(f"Column {columns} not in {surveys[group]}")

        for question_number in group_filter_follow_up_question:
            string = survey_data[[codebook_dict[question_number][columns]]]
            message_data_received(codebook_dict, question_number)
            numbers.remove(question_number)

        logging.info(
            f"Following questions for {surveys[group]} are missing data evaluations: {numbers}."
        )

    return


from wordcloud import WordCloud


def plot_wordcloud(title, text):
    # Compare also: https://www.python-lernen.de/wordcloud-erstellen-python.htm
    # STOPWORDS.update(liste_der_unerwuenschten_woerter), now manually removed from string
    wordcloud = WordCloud(
        background_color="white", max_font_size=40, collocations=True
    ).generate(text)
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(title)
    plt.show()
    return


from HanTa import HanoverTagger as ht
import collections

hannover = ht.HanoverTagger("morphmodel_ger.pgz")

manual_lemmata = {
    "Sektorgekoppelt": "Sektorenkopplung",
    "Sektorkopplung": "Sektorenkopplung",
    "Flexibel": "Flexibilität",
    "effizient": "Effizienz",
    "Energien": "Energie",
    "Carbon": "Co2",
    "h2": "H2",
    "Nachkaltigkeit": "nachhaltig",
    "Wasserstoff": "H2",
    "erneuerbar": "Erneuerbare",
    "EE": "Erneuerbare",
    "versorgungssich": "Versorgungssicherheit",
    " re ": " regenerativ",
    " E ": "Energie",
    "pv": "PV",
    "-": "",
}

liste_der_unerwuenschten_woerter = [
    "sind",
    "und",
    "der",
    "die",
    "das",
    "gleich" "oder",
    "aber",
    "für",
    "ist",
    "auf",
    "bei",
    "des",
    "eine",
    "um",
    "bis",
    "mit",
    "von",
    "durch",
    "aus",
    "werden",
    "den",
    "zur",
    "als",
    "in",
    "im",
    "zu",
    "dass",
    "auch",
    "aus",
    "vor",
    "es",
    "kann",
    "sich",
    "sein",
    "bzw",
    "wie",
    "wird",
    "welche",
    "ggf",
    "zum",
    "z.",
    "b.",
    "z B",
    "bsp",
    "können",
    "haben",
    "müssen",
    "so",
    "ein",
    "mich",
    "nur",
    "oder",
    "ich",
    "wir",
    "vom",
    "sollen",
    "an",
]

liste_der_unerwuenschten_woerter += [
    key.capitalize() for key in liste_der_unerwuenschten_woerter
]


def get_lemma(string_answers, number_of_most_common_words_displayed):
    for key in [";", ",", ".", ":", "!", "%", "(", ")", "'", "=", "“"]:
        string_answers = string_answers.replace(key, "")

    for i in range(0, 6):
        string_answers.replace("  ", " ")

    wordlist = string_answers.split(" ")
    wordlist = [ele for ele in wordlist if ele != []]

    lemma_string = ""
    # Find lemma, eg. Erneuerbare = Erneuerbar
    for item in range(0, len(wordlist)):
        wordlist[item] = hannover.analyze(wordlist[item])[0]
        lemma_string += hannover.analyze(wordlist[item])[0] + " "

    for key in manual_lemmata.keys():
        lemma_string = lemma_string.replace(key, manual_lemmata[key])

    for key in liste_der_unerwuenschten_woerter:
        lemma_string = lemma_string.replace(f" {key} ", " ")

    data = collections.Counter(
        [ele for ele in lemma_string.split(" ") if ele != ""]
    ).most_common(number_of_most_common_words_displayed)
    data = pd.DataFrame.from_records(data, columns=["word", "count"])
    data.plot.barh(x="word", y="count")
    return lemma_string[:-1]


def create_stacked_bar_chart_percent(data, codebook, question_number):
    data_to_plot = {}

    codes_identical = True
    for sub in codebook[question_number][subquestion]:
        if sub == 1:
            codes = codebook[question_number][subquestion][sub][m_options]
        # Make sure you always have the same options
        if codebook[question_number][subquestion][sub][m_options] != codes:
            codes_identical = False
        try:
            data_to_plot.update(
                {
                    codebook[question_number][subquestion][sub][question]: [
                        np.nan if x in EXCLUDE_CODES else x
                        for x in data[
                            codebook[question_number][subquestion][sub][columns]
                        ].values
                    ]
                }
            )
        except:
            print(
                f"Values for '{codebook[question_number][subquestion][sub][question]}' could not be fetched from {codebook[question_number][subquestion][sub][columns]}."
            )
            pass

    # Count number of occurrences of multiple-choice options
    data_to_plot = pd.DataFrame(data_to_plot).apply(pd.value_counts)
    # Calculate percentage of votes
    data_to_plot = data_to_plot.div(data_to_plot.sum(axis=0), axis=1)
    # Only change index if the labels are actually identical
    if codes_identical is True:
        as_list = data_to_plot.index.tolist()
        as_list = [str(int(x)) for x in as_list]
        data_to_plot.index = as_list
        data_to_plot.rename(index=codes, inplace=True)
        data_to_plot = data_to_plot.sort_values(by=codes["1"], axis=1, ascending=True)
        print(data_to_plot)
        data_to_plot = data_to_plot.T
        data_to_plot.plot.barh(
            stacked=True, title=codebook[question_number][question], mark_right=True
        )
        plt.show()
    else:
        print(codes)
        print(data_to_plot)


def create_wordclouds(
    codebook_dict,
    survey_data,
    survey_group,
    numbers=[],
    question_number_list=group_three_word_entries,
    number_of_most_common_words_displayed=20,
):
    for question_number in question_number_list:
        string_answers = ""
        # Merge all string answers for seperate answer fields into one single string
        for field in range(0, len(codebook_dict[question_number][columns])):
            list_answers = survey_data[
                [codebook_dict[question_number][columns][field]]
            ].values
            for x in list_answers:
                if x not in EXCLUDE_CODES:
                    string_answers += " " + str(x[0])

        title = f"{survey_group}:\n {codebook_dict[question_number][question][:-20]}"

        lemma_string = get_lemma(string_answers, number_of_most_common_words_displayed)

        plot_wordcloud(title, lemma_string)

        message_data_received(codebook_dict, question_number)

        if numbers != []:
            numbers.remove(question_number)

    return numbers


def get_codebook_for_question(codebook, codebook_dict, question_number, row):
    logging.debug(f"Checking for codebook to question {question_number}.")
    got_codebook = True
    if question_number in group_three_word_entries:
        row = three_word_entries(codebook, codebook_dict, question_number, row)
    elif question_number in group_yes_rather_yes_rather_no_no:
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=4
        )
        # row = yes_rather_yes_rather_no_no(codebook_dict, question_number, row)
    elif question_number in group_filter_follow_up_question:
        row = filter_follow_up_question(codebook, codebook_dict, question_number, row)
    elif question_number in group_need_to_catch_up:
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=8
        )
    elif question_number == 12:
        row = single_subquestions(codebook, codebook_dict, question_number, row)
    elif question_number == 13:
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=6
        )
    elif question_number == 14:
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=5
        )
    elif question_number == 15:
        row += 7
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=5
        )
    elif question_number == 38:
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=7
        )
    elif question_number == 40:
        row_buffer = row
        row = multiple_choice(
            codebook, codebook_dict, question_number, row, multiple_choice_options=6
        )
        column_buffer = codebook_dict[question_number][subquestion][1][columns]
        question_buffer = codebook_dict[question_number][subquestion][1][question]

        codebook_dict[question_number][subquestion].update(
            {2: {columns: column_buffer, question: question_buffer}}
        )

        row = row_buffer + 12

        codebook_dict[question_number][subquestion].update(
            {3: {columns: codebook.loc[row + 2, A], question: codebook.loc[row + 1, A]}}
        )
        logging.info(
            f"Codebook for question {question_number} and the 3 subquestions recieved."
        )
    elif question_number == 41:
        logging.info(
            f"Question {question_number} is related to data rights and has to be evaluated seperately."
        )
    else:
        got_codebook = False
        logging.warning(f"Codebook for question {question_number} not found.")

    return row, got_codebook


def single_subquestions(codebook, codebook_dict, question_number, row):
    codebook_dict.update(
        {question_number: {question: codebook.loc[row + 2, A], subquestion: {}}}
    )
    row += 2
    number_of_subquestions = 0
    end_of_aspects = False
    while end_of_aspects is False:
        number_of_subquestions += 1
        codebook_dict[question_number][subquestion].update(
            {
                number_of_subquestions: {
                    question: codebook.loc[row + 0, A],
                    columns: [codebook.loc[row + 1, A], codebook.loc[row + 5, A]],
                    m_options: ["Value", "1: Keine Angabe"],
                }
            }
        )
        row += 9
        if "v_" not in codebook.loc[row + 1, A]:
            end_of_aspects = True

    logging.info(
        f"Codebook to question {question_number} and its {number_of_subquestions} subquestions parsed: Follow up question with text"
    )
    return


def multiple_choice(
    codebook, codebook_dict, question_number, row, multiple_choice_options
):
    logging.debug(f"Decoding question {question_number}")
    codebook_dict.update(
        {question_number: {question: codebook.loc[row + 2, A], subquestion: {}}}
    )
    row += 2
    number_of_subquestions = 0
    end_of_aspects = False
    while end_of_aspects is False:
        number_of_subquestions += 1
        codebook_dict[question_number][subquestion].update(
            {
                number_of_subquestions: {
                    question: codebook.loc[row + 1, D],
                    columns: codebook.loc[row + 1, A],
                    m_options: {},
                }
            }
        )
        for option_number in range(1, multiple_choice_options + 1):
            codebook_dict[question_number][subquestion][number_of_subquestions][
                m_options
            ].update(
                {
                    codebook.loc[row + 1 + option_number, C]: codebook.loc[
                        row + 1 + option_number, D
                    ]
                }
            )

        row += option_number + 1

        if "v_" not in codebook.loc[row + 1, A] or question_number == 40:
            end_of_aspects = True

    logging.info(
        f"Codebook to question {question_number} and its {number_of_subquestions} subquestions parsed: Follow up question with text"
    )
    return row


def filter_follow_up_question(codebook, codebook_dict, question_number, row):
    # Sadly, the codebook is not consistent here.
    # I think filter rules are sometimes written in a single condensed row, and sometimes over multiple lines.

    if "v_" in codebook.loc[row + 3, A]:
        question_string = codebook.loc[row + 2, A]
        column = codebook.loc[row + 3, A]
        row += 3
    elif "v_" in codebook.loc[row + 10, A]:
        question_string = codebook.loc[row + 9, A]
        column = codebook.loc[row + 10, A]
        row += 10
    else:
        question_string = codebook.loc[row + 10, A]
        column = codebook.loc[row + 11, A]
        row += 11

    codebook_dict.update(
        {question_number: {columns: column, question: question_string}}
    )

    logging.info(
        f"Codebook to question {question_number} parsed: Follow up question with text"
    )
    return row


def three_word_entries(codebook, codebook_dict, question_number, row):
    codebook_dict.update(
        {
            question_number: {
                columns: [
                    codebook.loc[row + 3, A],
                    codebook.loc[row + 4, A],
                    codebook.loc[row + 5, A],
                ],
                question: codebook.loc[row + 2, A],
            }
        }
    )
    row += 5
    logging.info(
        f"Codebook to question {question_number} parsed: Composed of three word entries"
    )
    return row


def message_data_received(codebook_dict, question_number):
    logging.debug(
        f"Got the data to process answers for question {question_number}: {codebook_dict[question_number][question]}"
    )
