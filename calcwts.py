"""
File: calcwts.py
Author: Joshua Hur
Date: 3/11/24
Email: jhur1@umbc.edu
Description: This program tokenizes and parses processed .txt files to calculate the term weights of
each token to be easier to compare.
"""

import sys
import os
import math
from collections import Counter

# Global counters for all words in all text files
global_token_counts = Counter()


def load_stoplist(stoplist_path):
    """
    Loads stopwords from a specific file and then creates a set of these words.
    :param stoplist_path: The file path to the stopwords list.
    :return: A set containing all the stopwords from the provided file.
             This set will be used to filter out the words from text files during the tokenization process.
    """
    with open(stoplist_path, 'r', encoding='utf-8') as file:
        return set(file.read().split())


def process_text_files(import_folder, excluded_tokens):
    """
    Processes text files located in the specified import folder.
    It cleans and tokenizes the content of each text file, excluding any tokens that appear in the imported stoplist.
    The function iterates through each file in the directory, ensuring it ends with ".txt" before processing.
    Each text file applies text cleaning and tokenizes the content, creating a count of each unique token
    in the document while excluding those found in the stoplist and tokens of length one.
    :param import_folder: The directory path containing the text files to be processed.
    :param excluded_tokens: A set of stopwords that will be excluded from the tokenization process.
    :return: A dictionary where each key is the name of a text file and the value is a 'Counter' object
             representing the count of each token in that document, excluding the stopwords and tokens of length one.
    """
    individual_file_count = {}

    for import_file_name in os.listdir(import_folder):
        if not import_file_name.endswith(".txt"):
            continue
        import_file_path = os.path.join(import_folder, import_file_name)
        token_count = Counter()
        with open(import_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                parts = line.strip().split(':')  # Split each line by ':'
                if len(parts) == 2:
                    token, count = parts[0].strip(), int(parts[1].strip())
                    if token not in excluded_tokens and len(token) > 1:
                        token_count[token] += count
        individual_file_count[import_file_name] = token_count
    return individual_file_count


def export_sorted_counts(export_folder, token_tf_idf, export_file_name):
    """
    Writes separate .wts files containing the term weight of cleaned tokens found in a single text file.
    Each line in the output files contains a token followed by its term weight.
    The tokens and their term weights are sorted by the term weight in descending order to ensure that
    the most significant terms appear first.
    :param export_folder: The directory path where the output files will be saved.
    :param token_tf_idf: A dictionary mapping each token to its term weight.
    :param export_file_name: The base name for the output files, derived from the original text file name.
    """

    # Sort a dictionary by term weight
    sorted_by_term_weight = sorted(token_tf_idf.items(), key=lambda item: item[1], reverse=True)
    term_weight_file_path = os.path.join(export_folder, f"{export_file_name}_Sort_by_Term_Weight.wts")

    with open(term_weight_file_path, 'w', encoding='utf-8') as weight_file:
        for token, count in sorted_by_term_weight:
            weight_file.write(f"{token}: {format(count, '.5f')}\n")


def calculate_document_frequencies(individual_text_data):
    """
    Calculates the document frequencies for each token in the set of text documents.
    Document Frequency is the number of documents that contain a specific token at least once.
    This function goes through the token counts for each document and increments
    the document frequency count for each unique token encountered.
    :param individual_text_data: A dictionary where each key is the name of a text file, and
                                 each value is a 'Counter' object representing the count of each token in that document.
    :return: A 'Counter' object containing the document frequencies for each token across all the text files.
             Each key in this counter will be a token, and the corresponding value will be the number of documents
             in which that token appears.
    """

    document_frequencies = Counter()

    for token_counts in individual_text_data.values():
        for token in token_counts:
            document_frequencies[token] += 1

    return document_frequencies


def calculate_tf_idf(individual_text_data, document_frequencies, total_documents):
    """
    Calculates the tf_idf scores for each token in each text document.
    :param individual_text_data: A dictionary where each key is the name of a text file, and each value is
                                 another dictionary containing a token and its counts for that file.
    :param document_frequencies: A Counter object containing the document frequencies of
                                 all tokens across all text files.
    :param total_documents: The total number of text documents processed.
    :return: A dictionary structured similarly to individual_text_data, but with tf_idf scores instead of
             token and its counts.
    """

    # Dictionary to stored final tf_idf scores for each file
    final_tf_idf_scores = {}

    for file_name, token_counts in individual_text_data.items():
        total_terms = sum(token_counts.values())

        # Store intermediate tf_idf scores before normalization
        intermediate_tf_idf_scores = {}
        sum_of_squares = 0

        # Calculate tf_idf for each token in the document
        for token, count in token_counts.items():
            tf = math.log(1 + (count / total_terms))

            # When there is only one import file, add 1 to avoid log(1), which is 0
            if total_documents == document_frequencies[token]:
                idf = math.log(total_documents / document_frequencies[token]) + 1
            else:
                idf = math.log(total_documents / document_frequencies[token])

            tf_idf = tf * idf
            intermediate_tf_idf_scores[token] = tf_idf
            sum_of_squares += (tf_idf ** 2)

        # Normalize the tf_idf scores
        norm = math.sqrt(sum_of_squares)
        normalized_tf_idf_scores = {token: (tf_idf / norm) for token, tf_idf in intermediate_tf_idf_scores.items()}
        final_tf_idf_scores[file_name] = normalized_tf_idf_scores

    return final_tf_idf_scores


def main_process_text_files(import_folder, export_folder, stoplist_file):
    """
    The main function that orchestrates the process of reading text files, tokenizing the text content,
    calculating tf_idf scores for each document, and exporting these scores to specified files in another directory.
    :param import_folder: The directory path containing the text files to be processed.
    :param export_folder: The directory path where the output files will be saved.
    :param stoplist_file: The file path to the stopwords list.
    """

    stoplist = load_stoplist(stoplist_file)
    individual_file_tokens = process_text_files(import_folder, stoplist)

    # Calculate document frequencies and tf_idf scores
    document_frequencies = calculate_document_frequencies(individual_file_tokens)
    total_documents = len(individual_file_tokens)
    tf_idf_scores = calculate_tf_idf(individual_file_tokens, document_frequencies, total_documents)

    # Export the tf_idf scores
    for file_name, token_counts in individual_file_tokens.items():
        filtered_tf_idf_scores = {token: tf_idf_scores[file_name][token] for token in token_counts}
        export_sorted_counts(export_folder, filtered_tf_idf_scores, file_name.split("_")[0])

    print(f"TXT files from {import_folder} are now tokenized and exported to {export_folder}")


if __name__ == '__main__':
    global_token_counts = Counter()

    # Check if the correct number of arguments are provided for a command,
    # inform the user of the correct usage, and exit the program if not
    import_dir = "Import"
    export_dir = "Export"

    stoplist_dir = "stoplist.txt"

    # Check if the stoplist file exists; if not, exit the program
    if not os.path.exists(stoplist_dir):
        print(f"Stoplist file {stoplist_dir} does not exist")
        sys.exit(1)

    # Check if the assigned import directory is available;
    # if not, exit the program
    if not os.path.exists(import_dir):
        print(f"Import directory {import_dir} does not exist")
        sys.exit(1)

    # Check if the assigned export directory is available;
    # if not, create a new export directory and proceed to tokenize
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        print(f"New directory {export_dir} is now created")
        main_process_text_files(import_dir, export_dir, stoplist_dir)

    # If both of the assigned import and export directories exist, run the regular program
    else:
        main_process_text_files(import_dir, export_dir, stoplist_dir)
