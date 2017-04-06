# -*- coding: utf-8 -*-
import json
import os
import re

from joblib import Parallel, delayed
import tqdm

from preprocessings.ja.tokenizer import MeCabTokenizer
from preprocessings.ja.normalization import normalize_unicode, normalize_number
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data/processed')


def cleaning(text):
    replaced_text = '\n'.join(s.strip() for s in text.splitlines()[2:] if s != '')  # skip header by [2:]
    replaced_text = replaced_text.lower()
    replaced_text = re.sub(r'\d+', '0', replaced_text)     # 数字の置き換え
    replaced_text = re.sub(r'[【】]', ' ', replaced_text)   # 【】の除去
    replaced_text = re.sub(r'[（）]', ' ', replaced_text)   # （）の除去
    replaced_text = re.sub(r'[［］]', ' ', replaced_text)   # ［］の除去
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    replaced_text = re.sub(r'https?:\/\/.*?[\r\n ]', '', replaced_text)  # URLの除去
    replaced_text = re.sub(r'　', '', replaced_text)  # 全角空白の除去
    return replaced_text


def normalization(text):
    normalized_text = normalize_unicode(text)
    normalized_text = normalize_number(normalized_text)
    return normalized_text


def process(text):
    text = cleaning(text)
    text = normalization(text)
    words = tokenizer.wakati_baseform(text)
    return words


if __name__ == '__main__':
    with open(os.path.join(DATA_DIR, 'livedoor.json')) as f:
        livedoor = json.load(f)

    tokenizer = MeCabTokenizer('/usr/local/lib/mecab/dic/mecab-ipadic-neologd/')
    data = Parallel(n_jobs=-1)([delayed(process)(text) for text in tqdm.tqdm(livedoor['data'])])
    #data = [doc[:600] for doc in data]  # 文章の長さを制限
    livedoor['data'] = data

    with open(os.path.join(DATA_DIR, 'livedoor_tokenized_neologd.json'), 'w') as f:
        json.dump(livedoor, f)
