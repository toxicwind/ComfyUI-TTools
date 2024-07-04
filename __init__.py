import spacy
import spacy.lang.en
import re
import random
import itertools
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
print("TTools - Stop Words: " + ", ".join(remaining_stop_words))


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
        #print("Initial input string: ", input_string)
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
        # print("Initial value count: ", len(values))
        # print("Extracted values: ")
        if remove_stop_words:
            # print("Values before removing stop words: ")
            values = [self.remove_stop_words(v) for v in values]
            # print("Values after removing stop words: ")


        # print("Value count after processing: ", len(values))
        #sort values
        values.sort(key=len, reverse=True)
        # remove duplicate values
        values = list(dict.fromkeys(values))

        # print("Value count after removing duplicates: ", len(values))
        # Sort the values by length
        values.sort(key=len, reverse=False)
        # filter values based on length and remove "and " from the beginning
        values = [
            value[4:] if value.startswith("and ") else value
            for value in values
            if min_part_length <= len(value) <= max_part_length
        ]
        # print("Value count after filtering by length: ", len(values))
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

        output_string = ", ".join(str(v) for v in selected_values)
        # print("Final output string: ", output_string)
        return (output_string, )


class TToolsSD3ResolutionSolver:
    """
    Provides a resolution close to 1 megapixel with dimensions as multiples of 64.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x": ("INT", {"display": "number", "default": 1024}),
                "y": ("INT", {"display": "number", "default": 1024}),
                "max_long_side": ("INT", {"display": "number", "default": 1280}),
                "format": (["Portrait", "Landscape"], {"default": "Portrait"}),
                "skip_if_mulof64": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("INT","INT",)
    RETURN_NAMES = ("Width","Height",)
    FUNCTION = "solve"
    CATEGORY = "utils"

    def solve(self, x, y, format, max_long_side, skip_if_mulof64):
        if skip_if_mulof64 and x % 64 == 0 and y % 64 == 0:
            return x, y

        scale = (1000000 / (x * y)) ** 0.5
        x_adjusted, y_adjusted = (int(x * scale) // 64) * 64, (int(y * scale) // 64) * 64
        width, height = (max(x_adjusted, y_adjusted), min(x_adjusted, y_adjusted)) if format == 'Landscape' else (min(x_adjusted, y_adjusted), max(x_adjusted, y_adjusted))
        if max(width, height) > max_long_side:
            scale = max_long_side / max(width, height)
            width, height = int(width * scale), int(height * scale)
        return width, height

NODE_CLASS_MAPPINGS = {
    "TTools SD3 Resolution Solver": TToolsSD3ResolutionSolver,
    "TTools Extract JSON": TToolsExtractJson
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TToolsSD3ResolutionSolver": "TTools SD3 Resolution Solver",
    "TToolsExtractJson": "TTools Extract JSON",
}
