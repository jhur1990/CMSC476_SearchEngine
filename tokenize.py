"""
File: tokenize.py
Author: Joshua Hur
Date: 2/23/24
Email: jhur1@umbc.edu
Description: This program tokenize and lowercase all words in a collection of HTML documents.
"""

import sys
import os
import re
import html
from collections import Counter

# Global counters for all words in all HTML files
global_token_counts = Counter()

# Remove all content within HTML tags
TAG_RE = re.compile(r'<[^>]+>')

# Remove trailing apostrophes or single quotation marks after words
APOSTROPHE_RE = re.compile(r"\b(\w+)(['’])(?=\s|$)")

# Remove possessive endings "'s", "’s"
POSSESSIVE_RE = re.compile(r"\b(\w+)(['’]s)\b")

# Remove commas from numbers
NUMBER_COMMA_RE = re.compile(r'(?<=\d),(?=\d)')

# Replace non-alphanumeric characters with space
NON_ALPHANUMERIC_RE = re.compile(r"[^\w\s\u2019\u2018\u201B\u02BC\u02BB]")


def process_html_files(import_folder, export_folder):
    """
    Processes each HTML file located in the specified import directory independently.
    :param import_folder: The directory path containing the HTML files to be processed.
    :param export_folder: The directory path where the output files will be saved.
    """
    for import_file_name in os.listdir(import_folder):
        # Access only HTML files
        if import_file_name.endswith(".html"):
            file_path = os.path.join(import_folder, import_file_name)
            process_html_file(file_path, export_folder)


def process_html_file(import_file_path, export_folder):
    """
    Processes HTML files located in the specified import directory, extracts text content
    by removing HTML tags and other specified characters, then calculates and records
    the frequency of each unique word.
    :param import_file_path: The directory path containing the HTML files to be processed.
    :param export_folder: The directory path where the output files will be saved.
    """

    # Initialize a counter for all words in all files
    try:
        with open(import_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            html_content = file.read()

        # Clean the HTML content to extract tokens and count their frequency
        text_content = strip_tags(html_content)
        token_counts = Counter(text_content)

        # Update the global token counts with counts from this file
        global_token_counts.update(token_counts)

        # Once all files are processed, sort and write the results
        sorted_by_token, sorted_by_count = sort_word_counts(token_counts)
        export_file_name = os.path.basename(import_file_path).replace('.html', '')  # Remove .html extension
        export_sorted_counts(export_folder, sorted_by_token, sorted_by_count, export_file_name)

    # Notify if one of the input files can't be accessed
    except Exception as error_file:
        print(f"Failed to process {import_file_path}: {error_file}")


def strip_tags(html_content):
    """
    Takes a string containing HTML content and performs operations to remove all HTML tags
    and the content enclosed within them.
    This function is designed to extract only the textual data outside of HTML tag boundaries,
    decoding HTML entities to their corresponding characters.
    The resulting text is then cleaned of specific punctuations and non-alphanumeric characters,
    converted to lowercase, and split into individual tokens.
    :param html_content: A string containing HTML content to be cleaned and tokenized.
    :return: A list of tokens extracted from the cleaned HTML content, with all HTML tag contents removed.
    """

    # Decode HTML entities first
    text = html.unescape(html_content)

    # Replace various quotation marks with different Unicode to single quotes for the future use
    text = re.sub(r'[\u2019\u2018\u201B\u02BC\u02BB]', "'", text)

    # Insert spaces around HTML tags before removing them
    text = re.sub(r'<', ' <', text)
    text = re.sub(r'>', '> ', text)

    # Perform regular expression operations
    text = TAG_RE.sub('', text)
    text = APOSTROPHE_RE.sub(r'\1', text)
    text = POSSESSIVE_RE.sub(r'\1', text)
    text = NUMBER_COMMA_RE.sub('', text)
    text = NON_ALPHANUMERIC_RE.sub(' ', text)

    # Convert text to lower case and split into words
    tokens = text.lower().split()
    return tokens


def sort_word_counts(token_counts):
    """
    Sorts the given dictionary of cleaned token counts into two separate lists.
    :param token_counts: A dictionary where each key is a token and each value is the count
                        of how many times that  token appears.
    :return: A tuple containing two lists:
             1. The first list contains tuples of (token, count), sorted alphabetically by token.
             2. The second list contains tuples of (token, count), sorted by count in descending order.
    """

    # Sort by token in alphabetical order first
    sorted_by_token = sorted(token_counts.items(), key=lambda item: item[0])

    # Create a new list sorted by count, based on the already sorted list
    sorted_by_count = sorted(sorted_by_token, key=lambda item: item[1], reverse=True)

    return sorted_by_token, sorted_by_count


def export_sorted_counts(export_folder, sorted_by_token, sorted_by_count, export_file_name):
    """
    Writes two separate text files containing the frequencies of cleaned tokens found in a single HTML file.
    The first file lists the tokens sorted alphabetically, and
    the second file lists the tokens sorted by their frequency in descending order.
    Each line in the output files contains a token followed by its frequency count.
    :param export_folder: The directory path where the output files will be saved.
    :param sorted_by_token: A list of tuples where each tuple contains a token and its frequency count.
                            This list should be sorted alphabetically by token.
    :param sorted_by_count: Another list of tuples where each tuple contains a token and its frequency count.
                            This list should be sorted in descending order by the frequency count.
    :param export_file_name: The base name for the output files, derived from the original HTML file name.
    """

    # Write sorted by frequency
    frequency_file_path = os.path.join(export_folder, f"{export_file_name}_Sort_by_Frequency.txt")
    with open(frequency_file_path, 'w', encoding='utf-8') as file:
        for token, count in sorted_by_count:
            file.write(f"{token}: {count}\n")


# New function to export combined counts
def export_combined_counts(export_folder, combined_token_counts):
    sorted_by_token, sorted_by_count = sort_word_counts(combined_token_counts)

    # Export combined sorted by frequency
    combined_frequency_file_path = os.path.join(export_folder, "Combined_Sort_by_Frequency.txt")
    with open(combined_frequency_file_path, 'w', encoding='utf-8') as file:
        for token, count in sorted_by_count:
            file.write(f"{token}: {count}\n")


if __name__ == '__main__':

    import_dir = "Import"
    export_dir = "Export"

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

        process_html_files(import_dir, export_dir)
        export_combined_counts(export_dir, global_token_counts)
        print(f"HTML files from {import_dir} are now tokenized and exported to {export_dir}")

    # If both of the assigned import and export directories exist, run the regular program
    else:
        process_html_files(import_dir, export_dir)
        export_combined_counts(export_dir, global_token_counts)
        print(f"HTML files from {import_dir} are now tokenized and exported to {export_dir}")
