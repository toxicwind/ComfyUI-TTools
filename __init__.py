import os
import spacy
import spacy.lang.en
import inspect
import textwrap
import nodes
import re
import random
import itertools
from functools import reduce
import unicodedata
import emoji
import logging
import json


class AnyType(str):

    def __ne__(self, __value: object) -> bool:
        return False


any_typ = AnyType("*")

nlp = spacy.load("en_core_web_sm")

# List of words to remove from stop words list
remove_stop_word_tokens = [
    'and', 'he', 'she', 'it', 'his',
    'its', 'with', 'without', 'before', 'after', 'during', 'around', 'among',
    'between', 'through', 'across', 'behind', 'below', 'beside', 'by', 'over',
    'under', 'into', 'onto', 'upon', 'along', 'above', 'near', 'from',
    'towards', 'to', 'up', 'down', 'in', 'on', 'off', 'out', 'at', 'of', 'not',
    'no', 'none', 'never', 'neither', 'nor', 'only', 'just', 'who', 'whose',
    'whom', 'what', 'where', 'any', 'all', 'each', 'every', 'either', 'both',
    'all', 'both', 'another', 'such', 'some', 'few', 'several', 'many', 'much',
    'most', 'more', 'less', 'eight', 'eleven', 'fifteen', 'fifty', 'five',
    'forty', 'four', 'hundred', 'nine', 'one', 'six', 'sixty', 'ten', 'third',
    'three', 'twelve', 'twenty', 'two', 'alone', 'against', 'down', "again",
    "almost", "already", "always", "anyone", "anything", "anywhere", "around",
    "back", "become", "becomes", "becoming", "beyond", "full", "further",
    "get", "give", "go", "here", "hereafter", "hereby", "herein", "hereupon",
    "mostly", "often", "once", "part", "put", "seem", "seemed", "seeming",
    "seems", "take", "together", "top", "toward", "until", "used", "using",
    "various", "via", "within", "about", "because", "but", "can",
    "cannot", "could", "do", "does", "doing", "done", "even", "for", "if",
    "is", "was", "were", "may", "might", "must", "or", "please", "really",
    "should", "since", "so", "that", "these", "this", "those", "though",
    "thus", "unless", "until", "while", "will", "would", "yet"
]

# Remove the words from the stop words list
for word in remove_stop_word_tokens:
    if word in nlp.Defaults.stop_words:
        nlp.Defaults.stop_words.remove(word)
    if nlp.vocab[word].is_stop:
        nlp.vocab[word].is_stop = False

# Print the remaining stop words
remaining_stop_words = list(nlp.Defaults.stop_words)
remaining_stop_words.sort()
print(", ".join(remaining_stop_words))

class TToolsRandomizeAndFormatString:
    """
    This class replaces specified characters and patterns in a string with commas,
    then randomizes the order of the resulting tokens, converts them to lowercase,
    and finally joins them back into a comma-separated string without extra spaces.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {
                    "multiline": True
                }),
                "and_string": ("STRING", {
                    "default": ",",
                    "multiline": False
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF
                }),
                "max_length": ("INT", {
                    "default": 1024,
                    "min": 0,
                    "max": 999999999
                }),
            },
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "doit"
    CATEGORY = "utils"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def recursive_replace(self, processed_string, words_to_replace):
        while True:
            old_processed_string = processed_string
            for word in words_to_replace:
                processed_string = re.sub(re.escape(word), ",",
                                          processed_string)
            if old_processed_string == processed_string:
                break
        processed_string = re.sub(",{2,}", ",", processed_string)
        words = processed_string.split(',')
        random.shuffle(words)
        processed_string = ','.join(words)
        return processed_string

    def remove_stop_words(self, text, and_string=","):
        AND_STRING = and_string
        text = text.replace(" - ", AND_STRING)
        text = text.replace(" -", AND_STRING)
        text = text.replace("- ", AND_STRING)
        text = text.replace(" -", AND_STRING)
        return text

    def remove_emoji(self, text: str) -> str:
        """
        Removes emoji characters from the input text.

        Args:
        text (str): The input text containing emoji characters.

        Returns:
        str: The input text with emoji characters removed.
        """
        return ''.join(char for char in text if not emoji.is_emoji(char))

    def doit(self, input_string, and_string, max_length=1024, seed=0):
        self.logger.debug("Initial input string: %s", input_string)
        random.seed(seed)
        input_string = input_string.lower()
        with open('words_to_replace.txt', 'r') as file:
            words_to_replace = file.read().splitlines()

        words_to_replace = [word.lower() for word in words_to_replace]
        words_to_replace.sort(key=len, reverse=True)
        self.logger.debug("Words to replace: %s", words_to_replace)
        input_string = self.recursive_replace(input_string, words_to_replace)
        self.logger.debug("After recursive_replace: %s", input_string)
        input_string = input_string.replace(",", "")
        self.logger.debug("After lowercase and comma replacement: %s",
                          input_string)
        preserved_periods = re.sub(r"\d+\.(?!\d)", ",", input_string)
        preserved_periods = re.sub(r"(?<!\d)\.|\.(?!\d)", ",",
                                   preserved_periods)
        preserved_periods = re.sub(r"(?<=\s):(?=\s)", ",", preserved_periods)
        preserved_periods = re.sub(r"(?<=[a-zA-Z]):(?!\d)", " ",
                                   preserved_periods)
        preserved_periods = preserved_periods.replace(":", ",")
        preserved_periods = preserved_periods.replace("s'", "s")
        preserved_periods = re.sub(r"(?<!\w)'(?!\w)", ",", preserved_periods)
        preserved_periods = re.sub(r"(?<!\w)-(?!\w)", ",", preserved_periods)
        preserved_periods = re.sub(r"(?<!\s)'(?!\s)", "", preserved_periods)
        processed_string = preserved_periods
        self.logger.debug("After period replacements: %s", processed_string)
        processed_string = self.remove_stop_words(processed_string, and_string)
        processed_string = self.remove_emoji(processed_string)
        self.logger.debug("After remove_stop_words: %s", processed_string)
        processed_string = processed_string.replace(";", ",")
        processed_string = processed_string.replace("!", ",")
        processed_string = processed_string.replace("?", ",")
        processed_string = processed_string.replace("“", ",")
        processed_string = processed_string.replace("”", ",")
        processed_string = processed_string.replace('"', ",")
        processed_string = processed_string.replace("‘", ",")
        processed_string = processed_string.replace("’", ",")
        processed_string = processed_string.replace("[", ",")
        processed_string = processed_string.replace("]", ",")
        processed_string = processed_string.replace("{", ",")
        processed_string = processed_string.replace("}", ",")
        processed_string = processed_string.replace("|", ",")
        processed_string = processed_string.replace("#", ",")
        processed_string = processed_string.replace("@", ",")
        processed_string = processed_string.replace("$", ",")
        processed_string = processed_string.replace("%", ",")
        processed_string = processed_string.replace("&", ",")
        processed_string = processed_string.replace("*", ",")
        processed_string = processed_string.replace(" - ", ",")
        processed_string = processed_string.replace("---", ",")
        processed_string = processed_string.replace("--", ",")
        processed_string = processed_string.replace("- ", ",")
        processed_string = processed_string.replace(" -", ",")
        processed_string = processed_string.replace("…", ",")
        processed_string = processed_string.replace("...", ",")
        processed_string = processed_string.replace("..", ",")
        processed_string = processed_string.replace(".", ",")
        processed_string = processed_string.replace("=>", ",")
        processed_string = processed_string.replace("->", ",")
        processed_string = processed_string.replace('\\n', ",")
        processed_string = processed_string.replace("' ", ",")
        processed_string = processed_string.replace(" '", ",")
        processed_string = processed_string.replace("/", "")
        processed_string = processed_string.replace('\\\\', "")
        processed_string = processed_string.replace("<", "")
        processed_string = processed_string.replace(">", "")
        processed_string = processed_string.replace("=", "")
        processed_string = processed_string.replace("+", "")
        processed_string = processed_string.replace("_", " ")
        processed_string = processed_string.replace("^", "")
        processed_string = re.sub(r" {2,}", " ", processed_string)
        processed_string = re.sub(r"\s+", " ", processed_string)
        self.logger.debug("After processed_string: %s", processed_string)
        initial_tokens = [
            token.strip().lower() for token in processed_string.split(",")
            if token.strip()
        ]
        self.logger.debug("Initial number of tokens: %s", len(initial_tokens))

        tokens = [
            self.remove_stop_words(token).strip() for token in initial_tokens
        ]
        self.logger.debug("Number of tokens after removing stop words: %s",
                          len(tokens))

        tokens = [token for token in tokens if 3 <= len(token) <= 75]
        self.logger.debug("Number of tokens after length filtering: %s",
                          len(tokens))

        total_tokens = len(tokens)
        selected_tokens = []
        for token in tokens:
            if total_tokens >= max_length:
                break
            selected_tokens.append(token)
            total_tokens += 1

        self.logger.debug("Number of selected tokens: %s",
                          len(selected_tokens))

        final_tokens = tokens + selected_tokens
        random.shuffle(final_tokens)

        output_string = ", ".join(token for token in final_tokens if token)
        output_string = output_string.strip(", ")

        self.logger.debug("Final output string: %s", output_string)

        return (output_string, )


class TToolsExtractJson:
    """
    This class extracts and processes JSON objects from a given string, 
    randomizes the extracted values, and outputs them as a comma-separated string.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {
                    "multiline": True
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFFFFFFFFFF
                }),
                "max_length": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 999999999
                }),
                "min_part_length": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 999999999
                }),
                "max_part_length": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 999999999
                }),
                "remove_stop_words": ("BOOLEAN", {
                    "forceInput": False
                })
            },
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "doit"
    CATEGORY = "utils"

    def remove_stop_words(self, text):
        return ' '.join(token.text for token in nlp(text) if not token.is_stop)

    def remove_emoji(self, text):
        return ''.join(char for char in text if not emoji.is_emoji(char))

    def extract_json_objects(self, text):
        json_pattern = re.compile(r'\{[^\}]*\}', re.DOTALL)
        json_objects = []
        for json_str in json_pattern.findall(text):
            if re.fullmatch(r'\{[^\}]*\}', json_str):
                try:
                    json_objects.append(
                        json.loads(re.sub(r'\\[n"\\]', '', json_str)))
                except json.JSONDecodeError:
                    print("Invalid JSON format, discarding entry: ", json_str)
        return json_objects

    def extract_values(self, json_objects):
        return [
            str(item) for obj in json_objects for k, v in obj.items()
            for item in (v if isinstance(v, list) else [v])
        ]

    def extract_and_process_json_from_string(self, text_content):
        json_objects = self.extract_json_objects(text_content)
        return self.extract_values(json_objects)

    def doit(self,
             input_string,
             max_length=10,
             min_part_length=14,
             max_part_length=100,
             seed=0,
             remove_stop_words=False):
        random.seed(seed)
        input_string = input_string.lower()
        print("Initial input string: ", input_string)
        values = self.extract_and_process_json_from_string(input_string)
        replacements = [
            ('_', ' '),
            ('/', ' and '),
            ('\\', ' and '),
            (':', ','),
            ('"', ','),
            ('.', ','),
            ('[', ','),
            (']', ','),
            ('{', ','),
            ('}', ','),
            ('&', ' and '),
            ('+', ' and '),
            ('$', 'currency value of '),
            ('%', ' percent'),
            ('@', ' at '),
            ('#', ' number '),
            ('<', ' less than '),
            ('>', ' greater than '),
            ('=', ' equals '),
            ('*', ' '),
            ('\n', ','),
        ]

        def apply_replacements(value):
            for old, new in replacements:
                value = value.replace(old, new)
            return value

        #Remove whitespace before after or multiple spaces within
        values = [re.sub(r" {2,}", " ", value.strip()) for value in values]
        values = sorted(set(values), key=len, reverse=True)
        values = [apply_replacements(v) for v in values]
        values = [re.sub(r" {2,}", " ", value.strip()) for value in values]
        values = sorted(set(values), key=len, reverse=True)
        values = sorted(set(
            itertools.chain.from_iterable(v.split(',') for v in values)),
                        key=len,
                        reverse=True)
        values = [re.sub(r" {2,}", " ", value.strip()) for value in values]
        print("Initial value count: ", len(values))
        print("Extracted values: ")
        for i, v in enumerate(values, start=1):
            print(f"{i}: {v}")
        if remove_stop_words:
            print("Values before removing stop words: ")
            for i, v in enumerate(values, start=1):
                print(f"{i}: {v}")
            values = [self.remove_stop_words(v) for v in values]
            print("Values after removing stop words: ")
            for i, v in enumerate(values, start=1):
                print(f"{i}: {v}")

        print("Value count after processing: ", len(values))

        print("Extracted values: ")
        for i, v in enumerate(values, start=1):
            print(f"{i}: {v}")
        #sort values
        values.sort(key=len, reverse=True)
        # remove duplicate values
        values = list(dict.fromkeys(values))

        print("Value count after removing duplicates: ", len(values))
        # Sort the values by length
        values.sort(key=len, reverse=False)
        # filter values based on length and remove "and " from the beginning
        values = [
            value[4:] if value.startswith("and ") else value
            for value in values
            if min_part_length <= len(value) <= max_part_length
        ]
        print("Value count after filtering by length: ", len(values))
        # Find the midpoint
        midpoint = len(values) // 2

        # Split the values into short and long
        short_values = values[:midpoint]
        long_values = values[midpoint:]

        # Determine the number of values to select from each list
        num_short = min(len(short_values), int(max_length * 0.8))
        num_long = min(len(long_values), max_length - num_short)

        # Randomly select values from each list
        selected_short_values = random.sample(short_values, num_short)
        selected_long_values = random.sample(long_values, num_long)

        # Combine the selected values
        selected_values = selected_short_values + selected_long_values
        #sort values
        values.sort(key=len, reverse=True)
        # remove duplicate values
        values = list(dict.fromkeys(values))

        print(
            "Value count after removing duplicates and filtering by length: ",
            len(values))
        print("Selected values: ")
        for i, v in enumerate(selected_values, start=1):
            print(f"{i}: {v}")
        output_string = ", ".join(str(v) for v in selected_values)
        print("Final output string: ", output_string)
        return (output_string, )


class TToolsSD3ResolutionSolver:
    """
    Provides a resolution close to 1 megapixel with dimensions as multiples of 64.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x": ("INT", {"display": "number"}),
                "y": ("INT", {"display": "number"}),
                "format": (["Portrait", "Landscape"], {"default": "Portrait"}),
            },
        }

    RETURN_TYPES = ("INT","INT",)
    RETURN_NAMES = ("Width","Height",)
    FUNCTION = "solve"
    CATEGORY = "utils"

    def solve(self, x, y, format):
        scale = (1000000 / (x * y)) ** 0.5
        x_adjusted, y_adjusted = (int(x * scale) // 64) * 64, (int(y * scale) // 64) * 64
        return (max(x_adjusted, y_adjusted), min(x_adjusted, y_adjusted)) if format == 'Landscape' else (min(x_adjusted, y_adjusted), max(x_adjusted, y_adjusted))


NODE_CLASS_MAPPINGS = {
    "TTools SD3 Resolution Solver": TToolsSD3ResolutionSolver,
    "TTools Randomize And Format String": TToolsRandomizeAndFormatString,
    "TTools Extract JSON": TToolsExtractJson
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TToolsSD3ResolutionSolver": "TTools SD3 Resolution Solver",
    "TToolsRandomizeAndFormatString": "TTools Randomize And Format String",
    "TToolsExtractJson": "TTools Extract JSON",
}
