import pandas as pd
import numpy as np
import logging
import pprint

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


def main_preprocessing_codebook():
    codebook = pd.read_csv(
        f"{results}/{codebook_file}{suffix}", delimiter=";", encoding="ANSI", na_values=None
    )
    codebook = codebook.replace({np.nan: None})

    answer_column_names = {}

    numbers = [i for i in range(4, 41)]

    for row in codebook.index:
        try:
            value = float(codebook.loc[row, A])
            question_number = int(codebook.loc[row, A])
            two_below = codebook.loc[row + 2, A]
            if isinstance(two_below, str):
                logging.debug(f"{question_number}: {codebook.loc[row + 2, A]}")
                row, got_codebook = get_codebook_for_question(codebook,
                    answer_column_names, question_number, row
                )
                if got_codebook is True:
                    numbers.remove(question_number)
        except:
            pass

    logging.info(f"Following questions are not assessed: {numbers}")

    pprint.pprint(answer_column_names)

    return answer_column_names

def evaluating_with_codebook(answer_column_names):
    for group in surveys.keys():
        numbers = [i for i in range(4, 41)]

    data = pd.read_csv(
        f"{results}/{surveys[group]}{suffix}", delimiter=";", header=2
    )

    for question_number in group_three_word_entries:
        for field in range(0, len(answer_column_names[question_number][columns])):
            string = data[[answer_column_names[question_number][columns][field]]]

        message_data_received(answer_column_names, question_number)
        numbers.remove(question_number)

    for question_number in group_yes_rather_yes_rather_no_no + group_need_to_catch_up + [13, 14, 15]:
        for subquestion_number in answer_column_names[question_number][subquestion].keys():
            try:
                values = data[[answer_column_names[question_number][subquestion][subquestion_number][columns]]]
                message_data_received(answer_column_names, question_number)
                numbers.remove(question_number)
            except:
                logging.warning(f"Column {columns} not in {surveys[group]}")

    for question_number in group_filter_follow_up_question:
        string = data[[answer_column_names[question_number][columns]]]
        message_data_received(answer_column_names, question_number)
        numbers.remove(question_number)

    logging.info(f"Following questions for {surveys[group]} are missing data evaluations: {numbers}.")

    return

def get_codebook_for_question(codebook, answer_column_names, question_number, row):
    logging.debug(f"Checking for codebook to question {question_number}.")
    got_codebook = True
    if question_number in group_three_word_entries:
        row = three_word_entries(codebook, answer_column_names, question_number, row)
    elif question_number in group_yes_rather_yes_rather_no_no:
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options=4)
        #row = yes_rather_yes_rather_no_no(answer_column_names, question_number, row)
    elif question_number in group_filter_follow_up_question:
        row = filter_follow_up_question(codebook, answer_column_names, question_number, row)
    elif question_number in group_need_to_catch_up:
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options = 8)
    elif question_number == 12:
        row = single_subquestions(codebook, answer_column_names, question_number, row)
    elif question_number == 13:
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options = 6)
    elif question_number == 14:
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options = 5)
    elif question_number == 15:
        row += 7
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options= 5)
    elif question_number == 38:
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options= 7)
    elif question_number == 40:
        row_buffer = row
        row = multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options = 6)
        column_buffer = answer_column_names[question_number][subquestion][1][columns]
        question_buffer = answer_column_names[question_number][subquestion][1][question]

        answer_column_names[question_number][subquestion].update({2: {columns: column_buffer,
                                                                     question: question_buffer}})

        row = row_buffer + 12

        answer_column_names[question_number][subquestion].update({3: {columns: codebook.loc[row+2,A],
                                                                  question: codebook.loc[row+1,A]}})
        logging.info(f"Codebook for question {question_number} and the 3 subquestions recieved.")
    elif question_number == 41:
        logging.info(f"Question {question_number} is related to data rights and has to be evaluated seperately.")
    else:
        got_codebook = False
        logging.warning(f"Codebook for question {question_number} not found.")

    return row, got_codebook

def single_subquestions(codebook, answer_column_names, question_number, row):
    answer_column_names.update(
        {question_number: {question: codebook.loc[row + 2, A], subquestion: {}}}
    )
    row += 2
    number_of_subquestions = 0
    end_of_aspects = False
    while end_of_aspects is False:
        number_of_subquestions += 1
        answer_column_names[question_number][subquestion].update(
            {number_of_subquestions: {
                question: codebook.loc[row + 0, A],
                columns: [codebook.loc[row + 1, A], codebook.loc[row + 5, A]],
                m_options: ["Value", "1: Keine Angabe"],
            }}
        )
        row += 9
        if "v_" not in codebook.loc[row + 1, A]:
            end_of_aspects = True

    logging.info(
        f"Codebook to question {question_number} and its {number_of_subquestions} subquestions parsed: Follow up question with text"
    )
    return

def multiple_choice(codebook, answer_column_names, question_number, row, multiple_choice_options):
    logging.debug(f"Decoding question {question_number}")
    answer_column_names.update(
        {question_number: {question: codebook.loc[row + 2, A], subquestion: {}}}
    )
    row += 2
    number_of_subquestions = 0
    end_of_aspects = False
    while end_of_aspects is False:
        number_of_subquestions += 1
        answer_column_names[question_number][subquestion].update(
            {number_of_subquestions: {
                question: codebook.loc[row + 1, D],
                columns: codebook.loc[row + 1, A],
                m_options: {
                },
            }}
        )
        for option_number in range(1,multiple_choice_options+1):
            answer_column_names[question_number][subquestion][number_of_subquestions][m_options].update({codebook.loc[row + 1 + option_number, C]: codebook.loc[row + 1+ option_number, D]})

        row += option_number + 1

        if "v_" not in codebook.loc[row + 1, A] or question_number==40:
            end_of_aspects = True

    logging.info(
        f"Codebook to question {question_number} and its {number_of_subquestions} subquestions parsed: Follow up question with text"
    )
    return row

def filter_follow_up_question(codebook, answer_column_names, question_number, row):
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

    answer_column_names.update(
        {question_number: {columns: column, question: question_string}}
        )

    logging.info(
        f"Codebook to question {question_number} parsed: Follow up question with text"
    )
    return row

def three_word_entries(codebook, answer_column_names, question_number, row):
    answer_column_names.update(
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

def message_data_received(answer_column_names, question_number):
    logging.debug(
        f"Got the data to process answers for question {question_number}: {answer_column_names[question_number][question]}"
    )