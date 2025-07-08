from ipa_lexicon import VALID_CHARS, VALID_NUMBERS, PUNCTUATIONS
import logging
from datetime import datetime
import pycountry
from babel import numbers
from num2words import num2words
import roman
from dateutil import parser
import re
from enum import StrEnum
from indic_numtowords import num2words as indic_num_to_words
from pydantic import BaseModel
import re 
import unicodedata
from schema import DeterministicPreTTSPreprocessingResponse, EntityType


class OrpheusTextCleaner:
    
    def __call__(self,text):
        text = self._unicode_normalize(text)
        text = self._remove_invisible_characters(text)
        text = self._handle_slashes(text)
        text = self._handle_quotes(text)
        text = self._replace_punctuation(text)
        text = self._filter_characters(text)
        text = self._normalize_whitespace(text)
        return text 
    
    def _unicode_normalize(self, text: str) -> str:
        return unicodedata.normalize('NFC', text)
    
    def _remove_invisible_characters(self, text: str) -> str:
        return re.sub(r'[\u200C\u200D\u00A0\u00AD]', '', text)
    
    def _handle_slashes(self, text: str) -> str:
        return re.sub(r'(?<!\d)/(?=\D)|(?<=\D)/(?=\d)|(?<=\D)/(?=\D)', ' ', text)

    
    def _handle_quotes(self, text: str) -> str:
        return re.sub(r"(?<=\s)['\"]|['\"](?=\s)|^['\"]|['\"]$", '', text)

    
    def _replace_punctuation(self, text: str) -> str:
        text = text.replace(':', ',').replace(';', ',')
        return re.sub(r'[-–—]', ' ', text)
    
    def _filter_characters(self, text: str) -> str:
        return ''.join(
            c for c in text
            if c.lower() in VALID_CHARS or c in VALID_NUMBERS or c in PUNCTUATIONS
        )
    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()
    

class OrpheusTextNormalizer:
    """
    A comprehensive text preprocessing class for converting various text entities 
    to their spoken word equivalents across multiple languages.
    """
    
    def __init__(self):
        self.lang_mapping = {
            'od': 'or',
        }
        self.currency_mapping = self._get_currency_mapping()
        self.text_cleaner=OrpheusTextCleaner()
        
    def process_text(self, text: str, to_lang: str = "en") -> DeterministicPreTTSPreprocessingResponse:
        """
        Main method to process text and convert entities to spoken format.
        
        Args:
            text (str): Input text to process
            to_lang (str): Target language code (default: "en")
            
        Returns:
            DeterministicPreTTSPreprocessingResponse: Processed text with replacement entities
        """
        all_replaced_entities = []
        
        # Define processing functions for English
        process_fns_en = [
            (self._process_dates, EntityType.DATE),
            (self._process_time_and_duration, EntityType.TIME),
            (self._process_currency_entities, EntityType.CURRENCY),
            (self._process_numbers_to_words, EntityType.NUM_WITH_WORDS),
            (self._process_phone_numbers_with_hyphens, EntityType.PHONE_NUMBERS),
            (self._process_decimal_to_spoken, EntityType.DECIMAL),
            (self._process_ordinal_to_word, EntityType.ORDINAL),
            (self._process_vehicle_number, EntityType.VEHICLE_NUMBER),
            (self._process_alphanumerics, EntityType.ALPHANUMERICS),
            (self._process_non_comma_numbers, EntityType.NON_COMMA_NUMBERS),
            (self._process_acronyms_read_out, EntityType.ACRONYMS_READ_OUT),
        ]
        
        # Define processing functions for other languages
        process_fns_others = [
            (self._process_dates, EntityType.DATE),
            (self._process_time_and_duration, EntityType.TIME),
            (self._process_currency_entities, EntityType.CURRENCY),
            (self._process_numbers_to_words, EntityType.NUM_WITH_WORDS),
            (self._process_phone_numbers_with_hyphens, EntityType.PHONE_NUMBERS),
            (self._process_vehicle_number, EntityType.VEHICLE_NUMBER),
            (self._process_decimal_to_spoken, EntityType.DECIMAL),
            (self._process_non_comma_numbers, EntityType.NON_COMMA_NUMBERS), 
            (self._process_alphanumerics, EntityType.ALPHANUMERICS),
            (self._process_acronyms_read_out, EntityType.ACRONYMS_READ_OUT),
        ]

        try:
            #text=self._clean_text(text)
            process_fns = process_fns_en if to_lang == "en" else process_fns_others

            for process_fn, entity_type in process_fns:
                text, replaced_entities = process_fn(text, to_lang=to_lang)
                replaced_entities = [
                    (r[0], r[1], entity_type) for r in replaced_entities
                ]
                all_replaced_entities.extend(replaced_entities)
            
            text=self.text_cleaner(text)
            
        except Exception as e:
            logging.error(
                f"Error during text preprocessing pipeline. Original text: '{text[:100]}...'. Error: {str(e)}",
                exc_info=True,
            )
            return DeterministicPreTTSPreprocessingResponse(
                formatted_text=text, replaced_entities=all_replaced_entities
            )
        
        return DeterministicPreTTSPreprocessingResponse(
            formatted_text=text, replaced_entities=all_replaced_entities
        )

    
    def _indic_num_to_words_wrapper(self, number, lang):
        """Convert numbers to words in Indic languages with decimal support."""
        number_str = str(number)
        
        if '.' not in number_str:
            return indic_num_to_words(number, lang=self.lang_mapping.get(lang, lang))
        
        whole_part, decimal_part = number_str.split('.')
        whole_words = indic_num_to_words(int(whole_part), lang=self.lang_mapping.get(lang, lang))
        
        if all(digit == '0' for digit in decimal_part):
            return whole_words
        
        decimal_words = [indic_num_to_words(int(digit), lang=self.lang_mapping.get(lang, lang)) for digit in decimal_part]
        
        point_word = {
            "hi": "दशमलव",       # Hindi
            "ta": "புள்ளி",         # Tamil
            "te": "దశాంశం",        # Telugu
            "ml": "പത്താംശം",     # Malayalam
            "kn": "ದಶಾಂಶ",        # Kannada
            "mr": "दशांश",        # Marathi
            "gu": "દશાંશ",         # Gujarati
            "or": "ଦଶମିକ",         # Odia
            "bn": "দশমিক",         # Bengali
            "pa": "ਦਸ਼ਮਲਵ" 
        }.get(lang, "point")
        
        return f"{whole_words} {point_word} {' '.join(decimal_words)}"

    def _num_to_words_wrapper(self, number, to_lang='en', **kwargs):
        """Universal number to words converter supporting multiple languages."""
        if to_lang == 'en':
            return num2words(number, **kwargs)
        elif to_lang == 'en_IN':
            return num2words(number, lang=to_lang, **kwargs)
        else:
            return self._indic_num_to_words_wrapper(number, lang=to_lang)

    def _process_ordinal_to_word(self, text, to_lang='en'):
        """Convert ordinal numbers (1st, 2nd, etc.) to words."""
        if to_lang != 'en':
            return text, []
        
        entities_replaced = []

        def replace_ordinal(match):
            num = int(match.group(1))
            original = match.group(0)
            replaced = self._num_to_words_wrapper(num, to="ordinal", to_lang=to_lang)
            entities_replaced.append((original, replaced))
            return replaced

        pattern = r"\b(\d+)(st|nd|rd|th)\b"
        modified_text = re.sub(pattern, replace_ordinal, text)
        return modified_text, entities_replaced

    def _process_dates(self, text, to_lang='en'):
        """Convert date formats to spoken words."""
        extracted_entities = []

        def year_to_words(year):
            if year < 2000:
                return (
                    self._num_to_words_wrapper(year // 100, to_lang=to_lang).replace("-", " ")
                    + " "
                    + self._num_to_words_wrapper(year % 100, to_lang=to_lang).replace("-", " ")
                )
            else:
                return self._num_to_words_wrapper(year, to_lang=to_lang, to="year").replace("-", " ")

        def date_to_words(date, original, date_after_month=False, to_lang=to_lang):
            parts = []
            day_representation = self._num_to_words_wrapper(date.day, to="ordinal", to_lang=to_lang).replace("-", " ")
            month_representation = date.strftime("%B")
            
            if date_after_month:
                parts.append(month_representation)
                parts.append(day_representation)
            else:
                parts.append(day_representation)
                parts.append(month_representation)

            if date.year != 1900 and str(date.year) in original:
                parts.append(year_to_words(date.year))
            
            return " ".join(parts)

        def is_likely_measurement(text, start, end):
            measurements = {
                "watts", "ohms", "volts", "amperes", "kg", "lbs",
                "meters", "feet", "liters", "gallons",
            }
            after = text[end:].strip().lower().split()
            return after and after[0] in measurements

        def replace_date(match):
            original = match.group()
            start, end = match.span()
            if is_likely_measurement(text, start, end):
                return original
            
            try:
                ordinal_match = re.match(r"(\d+)(st|nd|rd|th)\s+(\w+)", original)
                if ordinal_match:
                    day = int(ordinal_match.group(1))
                    month_name = ordinal_match.group(3)
                    if day < 1 or day > 31:
                        return original

                    month = datetime.strptime(month_name, "%B").month
                    if (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
                        return original

                time_info = re.search(r"\d{4}\s*hours", original)
                if time_info:
                    original = original.replace(time_info.group(), "").strip()

                if re.match(r"\d{4}-\d{2}-\d{2}", original):
                    date = datetime.strptime(original, "%Y-%m-%d")
                else:
                    date = parser.parse(original, dayfirst=True)
                
                date_after_month = True if to_lang in ['ta', 'kn', 'te', 'ml'] else False
                if 1000 <= date.year <= 2100:
                    replacement = date_to_words(date, original, date_after_month, to_lang=to_lang)
                    extracted_entities.append((original, replacement))
                    return replacement
            except ValueError:
                pass
            return original

        date_pattern = (
            r"\b(\d{1,2}(?:st|nd|rd|th)?[-/.]\d{1,2}[-/.]\d{4}|"
            r"\d{4}[-/.]\d{2}[-/.]\d{2}|"
            r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
            r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}|"
            r"\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
            r"Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{4})?)\b"
        )

        replaced_text = re.sub(date_pattern, replace_date, text, flags=re.IGNORECASE)
        return replaced_text, extracted_entities

    def _time_to_words(self, time, to_lang='en'):
        """Convert time format to spoken words."""
        time_suffix_mapping = {
            'am': 'a m',
            'pm': 'p m',
            'बजे': ''
        }

        am_pm_match = re.match(r"(?<!\w)(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*(am|pm|बजे)(?!\w)", time.lower())
        if am_pm_match:
            hours = int(am_pm_match.group(1))
            minutes = int(am_pm_match.group(2) or 0)
            am_pm = am_pm_match.group(3)
            am_pm = time_suffix_mapping.get(am_pm, am_pm)
        else:
            hours, minutes = map(int, time.split(":"))
            am_pm = ""

        hour_word = self._num_to_words_wrapper(hours, to_lang=to_lang)
        oh_word = "oh" if to_lang == "en" else ""

        if minutes == 0:
            return f"{hour_word} {am_pm}"
        else:
            if minutes < 10:
                minute_word = f"{oh_word} {self._num_to_words_wrapper(minutes, to_lang=to_lang)}"
            else:
                minute_word = self._num_to_words_wrapper(minutes, to_lang=to_lang)
            return f"{hour_word} {minute_word} {am_pm}"

    def _duration_to_words(self, duration):
        """Convert duration format to spoken words."""
        hours, minutes = map(int, duration.split(":"))
        result = []
        if hours > 0:
            result.append(f"{self._num_to_words_wrapper(hours)} hour{'s' if hours > 1 else ''}")
        if minutes > 0:
            result.append(f"{self._num_to_words_wrapper(minutes)} minute{'s' if minutes > 1 else ''}")
        return " and ".join(result)

    def _process_time_and_duration(self, text, to_lang='en'):
        """Process time and duration entities in text."""
        extracted_entities = []

        def replace_time(match):
            original = match.group()
            replaced = self._time_to_words(original, to_lang=to_lang)
            extracted_entities.append((original, replaced))
            return replaced

        def replace_duration(match):
            original = match.group()
            if 0 <= int(match.group(1)) <= 23 and 0 <= int(match.group(2)) <= 59:
                replaced = self._duration_to_words(original)
                extracted_entities.append((original, replaced))
                return replaced
            return original

        time_patterns = [
            r"(?<!\w)(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*(am|pm|बजे)(?!\w)",
            r"\b([01]?[0-9]|2[0-3]):[0-5][0-9]\b",
        ]
        
        for pattern in time_patterns:
            text = re.sub(pattern, replace_time, text, flags=re.IGNORECASE)

        text = re.sub(r"\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b", replace_duration, text)
        return text, extracted_entities

    def _number_to_spoken(self, number):
        """Convert phone number digits to spoken words."""
        digit_to_word = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
        }

        spoken = []
        if number.startswith("+"):
            spoken.append("plus")
            number = number[1:]

        number = re.sub(r"\D", "", number)
        for i in range(0, len(number), 4):
            chunk = number[i:i + 4]
            spoken_chunk = " ".join(digit_to_word[d] for d in chunk)
            spoken.append(spoken_chunk)

        return ", ".join(spoken)
    
    def _process_phone_numbers_with_hyphens(self, text, to_lang='en'):

        def num_to_words(num):
            words = []
            current_group = []

            for char in num:
                if char == "+":
                    words.append("plus")
                elif char.isdigit():
                    current_group.append(self._num_to_words_wrapper(char, to_lang=to_lang))
                elif char in "-() ":
                    if current_group:
                        words.extend(self._process_group(current_group))
                        current_group = []
                    # Comma removed here

            if current_group:
                words.extend(self._process_group(current_group))

            return " ".join(words)

        phone_pattern = re.compile(
            r"""
            (?:
                (?:\+?\d{1,3}[-\s]?)?
                (?:\d{1,4}[-\s]?)?
                (?:\(\d{2,4}\)|\d{2,4})
                (?:[-\s]?\d{1,4}){0,4}
            )
            """, re.VERBOSE
        )

        date_pattern = re.compile(
            r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b"
        )

        replacements = []

        def replace_func(match):
            match_text = match.group(0)
            if len(match_text) < 8 or date_pattern.match(match_text):
                return match_text
            spoken = num_to_words(match_text)
            replacements.append((match_text, spoken))
            return spoken

        formatted_text = phone_pattern.sub(replace_func, text)
        return formatted_text, tuple(replacements)

    def _process_group(self, group):
        """Helper method for processing phone number groups."""
        if len(group) <= 4:
            return group
        result = []
        for i, word in enumerate(group):
            #if i > 0 and i % 3 == 0:
             #   result.append(",")
            result.append(word)
        return result

    def _get_currency_mapping(self):
        """Get currency symbol to code mapping."""
        currency_mapping = {}
        for currency in pycountry.currencies:
            currency_mapping[currency.alpha_3] = currency.alpha_3
            if hasattr(currency, "numeric"):
                symbol = numbers.get_currency_symbol(currency.alpha_3, locale="en_US")
                if symbol != currency.alpha_3:
                    currency_mapping[symbol] = currency.alpha_3
        return currency_mapping

    def _word_to_number(self, word):
        """Convert scale words to numbers."""
        scale = {
            "hundred": 100, "thousand": 1000, "k": 1000, "lakh": 100000,
            "million": 1000000, "m": 1000000, "crore": 10000000,"crores":10000000,
            "billion": 1000000000, "b": 1000000000,
        }
        return scale.get(word.lower(), 1)

    # def _process_currency_entities(self, text, to_lang='en'):
    #     """Normalize currency expressions into spoken format."""
    #     extracted_replacements = []

    #     def replace_currency(match):
    #         full_match = match.group(0)
    #         leading_whitespace = re.match(r"^\s*", full_match).group(0)
    #         core_match = full_match[len(leading_whitespace):]

    #         # Extract number and optional suffix like k/m/b
    #         amount_str = re.search(r"([\d,]+(?:\.\d+)?)([kmb])?", core_match, re.IGNORECASE)
    #         if not amount_str or not amount_str.group(1):
    #             return full_match

    #         amount_without_commas = amount_str.group(1).replace(",", "")
    #         try:
    #             amount = float(amount_without_commas)
    #         except ValueError:
    #             return full_match

    #         # Apply short suffix scaling (k/m/b)
    #         if amount_str.group(2):
    #             amount *= self._word_to_number(amount_str.group(2))

    #         # Apply scale words like crore, lakh
    #         scale_words = re.findall(r"\b(hundred|thousand|lakh|million|crore|billion)s?\b", core_match, re.IGNORECASE)
    #         if scale_words:
    #             amount *= self._word_to_number(scale_words[0])  # Only take the first one

    #         # Determine currency code
    #         currency = next((cur for cur in self.currency_mapping if cur in core_match), None)
    #         if not currency:
    #             currency_match = re.match(r"([A-Z]{3})\s", core_match)
    #             if currency_match and currency_match.group(1) in self.currency_mapping:
    #                 currency = currency_match.group(1)
    #             elif "Rs." in core_match or "₹" in core_match:
    #                 currency = "INR"

    #         if not currency:
    #             return full_match

    #         # Language-specific formatting
    #         to_pass_lang = to_lang if to_lang != "en" else "en_IN"
    #         amount_words = self._num_to_words_wrapper(amount, to="cardinal", to_lang=to_pass_lang).replace("-", " ")
    #         amount_words = amount_words.capitalize()

    #         if "hundred" in amount_words and re.search(r"\b(\d+)\b", amount_words.split("hundred")[-1].strip()):
    #             amount_words = re.sub(r"hundred", "hundred and", amount_words)

    #         # Get currency name
    #         currency_code = self.currency_mapping[currency]

    #         if currency_code == "INR":
    #             currency_name = "rupee" if amount == 1 else "rupees"
    #         else:
    #             try:
    #                 currency_name = numbers.get_currency_name(currency_code, count=amount, locale="en_US")
    #             except:
    #                 currency_name = currency_code.lower()

    #         # Build replacement
    #         replaced_text = f"{amount_words} {currency_name}".strip()

    #         # Fix overpluralization bug
    #         replaced_text = re.sub(r"\brupees s\b", "rupees", replaced_text)

    #         # Preserve trailing punctuation
    #         punctuation_match = re.search(r"([^\w\s]+)(\s*)$", core_match)
    #         if punctuation_match:
    #             replaced_text += punctuation_match.group(1) + punctuation_match.group(2)
    #         else:
    #             replaced_text += " " if match.end() < len(text) and text[match.end()].isalnum() else ""

    #         replaced_text = leading_whitespace + replaced_text
    #         extracted_replacements.append((full_match, replaced_text))
    #         return replaced_text

    #     # currency_pattern = r"([₹$£€¥]?\s*[\d,.]+(?:\s*[kmb])?(?:\s*(hundred|thousand|lakh|million|crore|crores|billion))?\s*(?:USD|EUR|INR|GBP|JPY|CAD|AUD)?)"
    #     # rs_pattern = r"Rs\.?\s*[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundred|thousand|lakh|million|crore|crores|billion))?"
    #     # currency_code_prefix_pattern = r"\b(USD|EUR|INR|GBP|JPY|CAD|AUD)\s+[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundred|thousand|lakh|million|crore|crores|billion))?"
        
    #     #currency_pattern = r"([₹$£€¥]?\s*[\d,.]+(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?\s*(?:USD|EUR|INR|GBP|JPY|CAD|AUD)?)"
    #     currency_pattern = r"([₹$£€¥]?\s*[\d,.]+(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?|rupees?|rupee))?\s*(?:USD|EUR|INR|GBP|JPY|CAD|AUD)?)"

    #     #rs_pattern = r"Rs\.?\s*[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?"
    #     rs_pattern = r"Rs\.?\s*[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?"

    #     currency_code_prefix_pattern = r"\b(USD|EUR|INR|GBP|JPY|CAD|AUD)\s+[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?"

    #     # Combined currency regex pattern
    #     combined_pattern = f"{currency_pattern}|{rs_pattern}|{currency_code_prefix_pattern}"

    #     replaced_text = re.sub(combined_pattern, replace_currency, text, flags=re.IGNORECASE)
    #     return replaced_text, extracted_replacements

    def _process_currency_entities(self, text, to_lang='en'):
        """Normalize currency expressions into spoken format."""
        extracted_replacements = []

        def replace_currency(match):
            full_match = match.group(0)
            leading_whitespace = re.match(r"^\s*", full_match).group(0)
            core_match = full_match[len(leading_whitespace):]

            # Extract number and optional suffix like k/m/b
            amount_str = re.search(r"([\d,]+(?:\.\d+)?)([kmb])?", core_match, re.IGNORECASE)
            if not amount_str or not amount_str.group(1):
                return full_match

            amount_without_commas = amount_str.group(1).replace(",", "")
            try:
                amount = float(amount_without_commas)
            except ValueError:
                return full_match

            # Apply short suffix scaling (k/m/b)
            if amount_str.group(2):
                amount *= self._word_to_number(amount_str.group(2))

            # Apply scale words like crore, lakh, etc.
            scale_words = re.findall(r"\b(hundred|thousand|lakh|million|crore|billion)s?\b", core_match, re.IGNORECASE)
            if scale_words:
                amount *= self._word_to_number(scale_words[0])  # Only take the first one

            # Determine currency code
            currency = next((cur for cur in self.currency_mapping if cur in core_match), None)
            if not currency:
                currency_match = re.match(r"([A-Z]{3})\s", core_match)
                if currency_match and currency_match.group(1) in self.currency_mapping:
                    currency = currency_match.group(1)
                elif "Rs." in core_match or "₹" in core_match or re.search(r"\brupees?\b", core_match, re.IGNORECASE):
                    currency = "INR"

            if not currency:
                return full_match

            # Language-specific formatting
            to_pass_lang = to_lang if to_lang != "en" else "en_IN"
            amount_words = self._num_to_words_wrapper(amount, to="cardinal", to_lang=to_pass_lang).replace("-", " ")
            amount_words = amount_words.capitalize()

            # Insert 'and' for numbers like 1200 -> one thousand and two hundred
            if "hundred" in amount_words and re.search(r"\b(\d+)\b", amount_words.split("hundred")[-1].strip()):
                amount_words = re.sub(r"hundred", "hundred and", amount_words)

            # Get currency name
            currency_code = self.currency_mapping[currency]

            if currency_code == "INR":
                currency_name = "rupee" if amount == 1 else "rupees"
            else:
                try:
                    currency_name = numbers.get_currency_name(currency_code, count=amount, locale="en_US")
                except:
                    currency_name = currency_code.lower()

            # Build replacement
            replaced_text = f"{amount_words} {currency_name}".strip()

            # Fix overpluralization bug
            replaced_text = re.sub(r"\brupees s\b", "rupees", replaced_text)

            # Preserve trailing punctuation
            punctuation_match = re.search(r"([^\w\s]+)(\s*)$", core_match)
            if punctuation_match:
                replaced_text += punctuation_match.group(1) + punctuation_match.group(2)
            else:
                replaced_text += " " if match.end() < len(text) and text[match.end()].isalnum() else ""

            replaced_text = leading_whitespace + replaced_text
            extracted_replacements.append((full_match, replaced_text))
            return replaced_text

        # Patterns
        currency_pattern = r"([₹$£€¥]?\s*[\d,.]+(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?|rupees?|rupee))?\s*(?:USD|EUR|INR|GBP|JPY|CAD|AUD)?)"
        rs_pattern = r"Rs\.?\s*[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?"
        currency_code_prefix_pattern = r"\b(USD|EUR|INR|GBP|JPY|CAD|AUD)\s+[\d,]+(?:\.\d+)?(?:\s*[kmb])?(?:\s*(hundreds?|thousands?|lakhs?|millions?|crores?|billions?))?"

        # Combined pattern
        combined_pattern = f"{currency_pattern}|{rs_pattern}|{currency_code_prefix_pattern}"

        replaced_text = re.sub(combined_pattern, replace_currency, text, flags=re.IGNORECASE)
        return replaced_text, extracted_replacements



    
    def _process_numbers_to_words(self, text, to_lang='en'):
        """Process numbers with commas and convert to words."""
        extracted_replacements = []

        def replace_number(match):
            number_str = match.group()
            if ',' in number_str:
                cleaned_str = number_str.replace(",", "")
                try:
                    number = float(cleaned_str)
                    to_pass_lang = to_lang if to_lang != "en" else "en_IN"
                    
                    if number < 0:
                        word = " minus " + self._num_to_words_wrapper(abs(number), to_lang=to_pass_lang).replace("-", " ")
                    else:
                        word = self._num_to_words_wrapper(number, to_lang=to_pass_lang).replace("-", " ")
                        
                    extracted_replacements.append((number_str, word))
                    return word
                except ValueError:
                    return number_str
            else:
                return number_str

        pattern = r"-?\b\d+(?:,\d+)*(?:\.\d+)?\b"
        replaced_text = re.sub(pattern, replace_number, text)
        return replaced_text, extracted_replacements

    def _process_decimal_to_spoken(self, text, to_lang='en'):
        """Process decimal numbers and convert to spoken format."""
        extracted_entities = []

        def replace_decimal(match):
            integer_part, decimal_part = match.group().split(".")
            to_pass_lang = to_lang if to_lang != "en" else "en_IN"  
            spoken_decimal = self._num_to_words_wrapper(float(match.group()), to_lang=to_pass_lang)
            extracted_entities.append((match.group(), spoken_decimal))
            return spoken_decimal

        replaced_text = re.sub(r"\b\d+\.\d+\b", replace_decimal, text)
        return replaced_text, extracted_entities

    def _replace_roman_numerals(self, text):
        """Replace Roman numerals with word equivalents."""
        entities_extracted_replaced = []

        def replace(match):
            roman_numeral = match.group(0)
            try:
                integer = roman.fromRoman(roman_numeral)
                word_representation = self._num_to_words_wrapper(integer)
                entities_extracted_replaced.append((roman_numeral, word_representation))
                return word_representation
            except roman.InvalidRomanNumeralError:
                return roman_numeral

        pattern = r"\b[IVXLCDM]+\b"
        replaced_text = re.sub(pattern, replace, text)
        return replaced_text, entities_extracted_replaced

    """def _process_alphanumerics(self, sentence, to_lang='en'):
        extracted_entities = []

        def process_match(match):
            s = match.group(0)
            if re.match(r"^[A-Z]{2}\s\d{2}\s[A-Z]{2}\s\d{4}$", s):
                words = s.split()
                replaced_words = []
                for word in words:
                    replaced_words.extend([
                        char if char.isalpha() else self._num_to_words_wrapper(int(char), to_lang=to_lang)
                        for char in word
                    ])
                replaced_value = self._add_commas(replaced_words)
                extracted_entities.append((s, replaced_value))
                return replaced_value

            if any(char.isalpha() for char in s) and any(char.isdigit() for char in s):
                if re.match(r"^\d+[A-Za-z]{1,3}$", s):
                    return s

                replaced_words = [
                    char if char.isalpha() else self._num_to_words_wrapper(int(char), to_lang=to_lang)
                    for char in s if char.isalnum()
                ]
                replaced_value = self._add_commas(replaced_words)
                extracted_entities.append((s, replaced_value))
                return replaced_value
            return s

        pattern = r"\b[A-Z]{2}\s\d{2}\s[A-Z]{2}\s\d{4}\b|(?<!\w)[A-Z0-9-]+(?!\w)"
        replaced_text = re.sub(pattern, process_match, sentence)
        return replaced_text, tuple(extracted_entities)"""
    
    def _process_alphanumerics(self, sentence, to_lang='en'):
        """Process alphanumeric entities like vehicle numbers and IDs."""
        extracted_entities = []

        def process_match(match):
            s = match.group(0)

            # Case 1: Specific format like vehicle numbers (e.g., KA 05 AB 1234)
            if re.match(r"^[A-Z]{2}\s\d{2}\s[A-Z]{2}\s\d{4}$", s):
                words = s.split()
                replaced_words = []
                for word in words:
                    for char in word:
                        if char.isalpha():
                            replaced_words.append(char)
                        else:
                            replaced_words.append(self._num_to_words_wrapper(int(char), to_lang=to_lang))
                replaced_value = self._add_commas(replaced_words)
                extracted_entities.append((s, replaced_value))
                return replaced_value

            # Case 2: General alphanumerics like AMZ9900876, PNR567
            if any(char.isalpha() for char in s) and any(char.isdigit() for char in s):
                # Skip digit+letters like 123ABC if needed
                if re.match(r"^\d+[A-Za-z]{1,3}$", s):
                    return s

                # Split into letter and digit groups
                groups = re.findall(r'[A-Za-z]+|\d+', s)
                replaced_words = []
                for group in groups:
                    if group.isalpha():
                        replaced_words.extend(list(group))
                    else:
                        replaced_words.extend([
                            self._num_to_words_wrapper(int(d), to_lang=to_lang)
                            for d in group
                        ])
                replaced_value = self._merge_with_spaces(replaced_words)
                extracted_entities.append((s, replaced_value))
                return replaced_value

            return s

        # Pattern: Vehicle numbers or uppercase alphanumerics
        pattern = r"\b[A-Z]{2}\s\d{2}\s[A-Z]{2}\s\d{4}\b|(?<!\w)[A-Z0-9-]+(?!\w)"
        replaced_text = re.sub(pattern, process_match, sentence)
        return replaced_text, tuple(extracted_entities)

    def _add_commas(self, words):
        """Add commas to word lists for better readability."""
        result = ""
        for i, word in enumerate(words):
            if i > 0 and i % 3 == 0:
                result = result.rstrip() + ","
            result += " " + word
        return result.strip()

    def _merge_with_spaces(self, words):
        """Add commas to word lists for better readability."""
        result = ""
        for i, word in enumerate(words):
            if i > 0 and i % 3 == 0:
                result = result.rstrip()
            result += " " + word
        return result.strip()

    def _process_vehicle_number(self, text, to_lang='en'):
        """Process vehicle number plates."""
        def add_space_between_letters(text):
            return " ".join(text)

        def replace_format(match):
            parts = match.group(0).replace(" ", "")
            state = add_space_between_letters(parts[:2])
            district = " ".join(self._num_to_words_wrapper(int(digit), to_lang=to_lang) for digit in parts[2:4])
            series = add_space_between_letters(parts[4:-4])
            number = " ".join(self._num_to_words_wrapper(int(digit), to_lang=to_lang) for digit in parts[-4:])
            return f"{state} {district} {series} {number}"

        pattern = r"\b([A-Z]{2})\s?([0-9]{2})\s?([A-Z]{1,2})\s?([0-9]{4})\b"
        replaced_entities = []

        def replacement_func(match):
            original = match.group(0)
            replaced = replace_format(match)
            replaced_entities.append((original, replaced))
            return replaced

        new_text = re.sub(pattern, replacement_func, text)
        return new_text, replaced_entities
    
    def _process_non_comma_numbers(self, text, to_lang='en'):
        def replace_number(match):
            num_str = match.group()

            def convert_and_format(n):
                return self._num_to_words_wrapper(n, to_lang=to_lang).replace("-", " ")

            def add_commas_to_words(words):
                if len(words.split()) > 4:
                    word_groups = [
                        words.split()[i : i + 3]
                        for i in range(0, len(words.split()), 3)
                    ]
                    return ", ".join(" ".join(group) for group in word_groups)
                return words

            # Check if it's a pin code format (e.g., 400 001)
            if re.match(r"^\d{3}\s\d{3}$", num_str):
                digits = "".join(digit for digit in num_str if digit.isdigit())
                worded = " ".join(
                    convert_and_format(int(digit)) for digit in digits
                )
                return add_commas_to_words(worded)

            # For numbers with leading zeros or all zeros, read digit by digit
            if num_str.startswith("0") or all(digit == "0" for digit in num_str):
                worded = " ".join(
                    convert_and_format(int(digit)) for digit in num_str
                )
                replacement = add_commas_to_words(worded)
            else:
                # For all other cases, convert to int
                num = int(num_str.replace(" ", ""))

                # Check if it's a year (4 digits between 1980 and 2050)
                if len(num_str) == 4 and 1980 <= num <= 2050:
                    replacement = convert_and_format(num)

                # For numbers with more than 4 digits, add commas and read out digit-wise
                elif len(num_str) > 4:
                    worded = " ".join(
                        convert_and_format(int(digit))
                        for digit in num_str
                        if digit.isdigit()
                    )
                    replacement = add_commas_to_words(worded)

                # For binary, octal, or hexadecimal representations
                elif re.search(r"\b(0b|0o|0x)", match.string[: match.start()]):
                    replacement = " ".join(
                        convert_and_format(int(digit)) for digit in num_str
                    )

                # For numbers 1000-9999 (excluding years in the specified range)
                elif 1000 <= num <= 9999:
                    replacement = " ".join(
                        convert_and_format(int(digit)) for digit in num_str
                    )

                # For all other numbers
                else:
                    replacement = convert_and_format(num)

            replacements.append((num_str, replacement))
            return replacement

        replacements = []
        pattern = r"\b(?<!\d,)(\d{3}\s\d{3}|\d+)(?!,\d)\b"
        processed_text = re.sub(pattern, replace_number, text)

        return (processed_text, tuple(replacements))

    def _process_acronyms_read_out(self, input_string, to_lang='en'):
        words_to_replace = [
            "AADHAAR",
            "AADHAR",
            "NITI Aayog",
            "ISRO",
            "NABARD",
            "NASSCOM",
            "SEBI",
            "NIFT",
            "NIMHANS",
            "AIIMS",
            "BARC",
            "TRAI",
            "BHEL",
            "SAIL",
            "GAIL",
            "NHAI",
            "CREDAI",
            "ASSOCHAM",
            "NASSCOM",
            "UIDAI",
            "NITI",
            "NABI",
            "BITS",
            "TERI",
            "HUDCO",
            "NALCO",
            "BALCO",
            "CIDCO",
            "ICAR",
            "AMUL",
            "HAL",
            "e-NACH",
            "NASDAQ",
            "SENSEX",
            "CIBIL",
            "NIFTY",
            "PAN",
        ]

        extracted_replaced = []
        modified_string = input_string

        for word in words_to_replace:
            # Replace word + "'s"
            pattern = rf"\b{re.escape(word)}\'s\b"
            if re.search(pattern, modified_string):
                replacement = f"{word.lower()}s"
                modified_string = re.sub(pattern, replacement, modified_string)
                extracted_replaced.append((f"{word}'s", replacement))

            # Replace word + "s"
            pattern = rf"\b{re.escape(word)}s\b"
            if re.search(pattern, modified_string):
                replacement = f"{word.lower()}s"
                modified_string = re.sub(pattern, replacement, modified_string)
                extracted_replaced.append((f"{word}s", replacement))

            # Replace the word itself
            pattern = rf"\b{re.escape(word)}\b"
            if re.search(pattern, modified_string):
                replacement = word.lower()
                modified_string = re.sub(pattern, replacement, modified_string)
                extracted_replaced.append((word, replacement))

        return (modified_string, tuple(extracted_replaced))




