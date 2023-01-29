import demoji
import re

# this for removing emoji in text and return text without emoji and normal text also


def find_emoji_in_text(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)

    if bool(emoji_pattern.search(string)):
        return emoji_pattern.sub(r'', string)
    else:
        return emoji_pattern.sub(r'', string)


# this function return text or emoji
def give_text_or_emoji(text):
    text_len = len(text)
    text = text.strip('\"')
    text = text.strip("\'")
    new_text = text
    bad_chars = ["[", "@", "_", "!", "$", "%", "^", "&", "*",
                 "(", ")", "<", ">", "?", "/", "|", "]", "#", "}", "{", "~", ":", "\"]"]
    test_string = ''.join(i for i in new_text if i not in bad_chars)
    emoji = demoji.findall(text)
    emoji = list(emoji.keys())

    test_string = re.sub(r'[,\s]+', ' ', test_string)
    test_string = re.sub(' +', '', test_string)
    test_string = re.sub(",", "", test_string)

    if text_len == 0:
        return "{}"
    elif (len(test_string) == len(emoji)):
        return None
    else:
        removed_emoji_text = find_emoji_in_text(text)
        return removed_emoji_text
