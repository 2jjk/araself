import logging
import re 
import html

import pyarabic.araby as araby

class Preprocessor:
    def __init__(
        self,
        remove_html_markup: bool = True,
        replace_urls_emails_mentions: bool = True,
        insert_white_spaces: bool = True,
        strip_tashkeel: bool = True,
        strip_tatweel: bool = True,
        remove_non_digit_repetition: bool = True,
        keep_emojis: bool = True,
        # apply_farasa_segmentation: bool = None,
        language: str = 'ar'
    ) -> None:

        if language != 'ar' or language is None:
            logging.warning("Language must be set to 'ar'. Preprocessor will default back to Arabic language.")
            language = 'ar'

        self.keep_emojis = keep_emojis   
        if self.keep_emojis:
            import emoji

            self.emoji = emoji
            # if self.apply_farasa_segmentation:
            #     logging.warning(
            #         "Keeping tweets with Farasa Segmentation is 10 times slower"
            #     )
        
        # self.apply_farasa_segmentation = apply_farasa_segmentation
        # if self.apply_farasa_segmentation:
        #     try:
        #         from farasa.segmenter import FarasaSegmenter

        #         self.farasa_segmenter = FarasaSegmenter(interactive=True)
        #     except ModuleNotFoundError:
        #         logging.error(
        #             "farasapy is not installed, you want be able to process text for AraBERTv1 and v2. Install it using: pip install farasapy"
        #         )

        self.language = language
        self.remove_html_markup = remove_html_markup
        self.replace_urls_emails_mentions = replace_urls_emails_mentions
        self.insert_white_spaces = insert_white_spaces
        self.strip_tashkeel = strip_tashkeel
        self.strip_tatweel = strip_tatweel
        self.remove_non_digit_repetition = remove_non_digit_repetition


    def preprocess(self, text: str) -> str:
        text = str(text)
        text = html.unescape(text)

        if self.strip_tashkeel:
            text = araby.strip_tashkeel(text) # removes text diacritization
        if self.strip_tatweel:
            text = araby.strip_tatweel(text) # addresses text elongation

        if self.replace_urls_emails_mentions:
            # replace all possible URLs with [رابط]
            for reg in url_regexes:
                text = re.sub(reg, " [رابط] ", text)
            # replace all e-mails with [بريد]
            for reg in email_regexes:
                text = re.sub(reg, " [بريد] ", text)
            # replace mentions with [مستخدم]
            text = re.sub(user_mention_regex, " [مستخدم] ", text)

        if self.remove_html_markup:
            # remove html line breaks (<:? />)
            text = re.sub("<br />", " ", text)
            # remove html markup
            text = re.sub("</?[^>]+>", " ", text)

        if self.remove_non_digit_repetition:
            text = multiple_char_pattern.sub(r"\1\1", text)

        if self.insert_white_spaces:
            text = re.sub(
                "([^0-9\u0621-\u063A\u0641-\u064A\u0660-\u0669a-zA-Z ])",
                r" \1 ",
                text,
            )

            text = text.replace("[ رابط ]", "[رابط]")
            text = text.replace("[ بريد ]", "[بريد]")
            text = text.replace("[ مستخدم ]", "[مستخدم]")

            # insert whitespace between words and numbers or numbers and words
            text = re.sub(
                "(\d+)([\u0621-\u063A\u0641-\u064A\u066A-\u066C\u0654-\u0655]+)",
                r" \1 \2 ",
                text,
            )
            text = re.sub(
                "([\u0621-\u063A\u0641-\u064A\u066A-\u066C\u0654-\u0655]+)(\d+)",
                r" \1 \2 ",
                text,
            )

        if self.keep_emojis:
            emoji_regex = "".join(list(self.emoji.UNICODE_EMOJI["en"].keys()))
            rejected_chars_regex2 = "[^%s%s]" % (chars_regex, emoji_regex)
            text = re.sub(rejected_chars_regex2, " ", text)
        else:
            text = re.sub(rejected_chars_regex, " ", text)

        text = " ".join(text.replace("\uFE0F", "").split())

        # if self.apply_farasa_segmentation:
        #     if self.keep_emojis:
        #         new_text = []
        #         for word in text.split():
        #             if word in list(self.emoji.UNICODE_EMOJI["en"].keys()):
        #                 new_text.append(word)
        #             else:
        #                 new_text.append(self.farasa_segmenter.segment(word))
        #         text = " ".join(new_text)
        #     else:
        #         text = self.farasa_segmenter.segment(text)
        #     return self._farasa_segment(text)

        return text


multiple_char_pattern = re.compile(r"(\D)\1{2,}", re.DOTALL)
        
url_regexes = [
    r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
    r"@(https?|ftp)://(-\.)?([^\s/?\.#-]+\.?)+(/[^\s]*)?$@iS",
    r"http[s]?://[a-zA-Z0-9_\-./~\?=%&]+",
    r"www[a-zA-Z0-9_\-?=%&/.~]+",
    r"[a-zA-Z]+\.com",
    r"(?=http)[^\s]+",
    r"(?=www)[^\s]+",
    r"://",
]

email_regexes = [r"[\w-]+@([\w-]+\.)+[\w-]+", r"\S+@\S+"]
user_mention_regex = r"@[\w\d]+"

chars_regex = r"0-9\u0621-\u063A\u0640-\u066C\u0671-\u0674a-zA-Z\[\]!\"#\$%\'\(\)\*\+,\.:;\-<=·>?@\[\\\]\^_ـ`{\|}~—٪’،؟`୍“؛”ۚ»؛\s+«–…‘/"
rejected_chars_regex = r"[^0-9\u0621-\u063A\u0641-\u066C\u0671-\u0674a-zA-Z\[\]!\"#\$%\'\(\)\*\+,\.:;\-<=·>?@\[\\\]\^_ـ`{\|}~—٪’،؟`୍“؛”ۚ»؛\s+«–…‘/]"
