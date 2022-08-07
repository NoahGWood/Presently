import string
from utils import GetText

SKIP_WORDS=[
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'i', 'it', 'for',
    'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by',
    'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
    'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
    'which', 'go', 'me', 'when', 'make', 'can', 'like', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back',
    'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new',
    'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
]

def word_count_file(filepath, words={}):
    lines = GetText(filepath).split()
    txt = [x for x in lines]
    words = words
    total = 0
    for word in txt:
        word = word.lower()
        word = word.strip()
        word = word.strip(string.punctuation)
        total += 1
        if word.lower() in words and word.lower() not in SKIP_WORDS and not word.isdigit() and len(word) > 3:
            words[word.lower()] += 1
        else:
            words[word.lower()] = 1
    return total, words

def StatsByUser(presentations):
    words = {}
    total = 0
    for presentation in presentations:
        subtotal = 0
        for f in presentation.files:
            sub, words = word_count_file(f.filepath)
            subtotal += sub
        total += subtotal
    word_list = []
    for key, value in words.items():
        word_list.append((value, key))
    word_list.sort(reverse=True)
    # Top ten
    return total, [x[1] for x in word_list[:9]]