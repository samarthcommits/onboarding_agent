import nltk

import statistics
# nltk.download('punkt_tab')
# FileName = ("Path\GodFather.txt")
def count_tokens(docs):
    token_size = []
    c = 0
        #lines_in_file = file.read()
    for doc in docs:

        lines_in_file = doc.page_content
        nltk_tokens = nltk.word_tokenize(lines_in_file)
        token_size.append(len(nltk_tokens))
        c+=len(nltk_tokens)
    # print(len(nltk_tokens))
    return c

    # print('mean', statistics.mean(token_size))
    # print('median', statistics.median(token_size))
    # print('standard_deviation', statistics.stdev(token_size))
    # print('max', max(token_size))
    # print('min', min(token_size))
