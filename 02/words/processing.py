import re
from collections import defaultdict, Counter
from multiprocessing import Pool, cpu_count

import requests

from test_project.settings import BASE_DIR
from words.models import Word


def process_text_input(text):
    """
    Handle raw text input.
    """
    mapping = prepare_text_input(text)
    persist_to_db(mapping)


def prepare_text_input(text):
    """
    Convert raw text input into a mapping dict
    that contains word as a key and count increment as a value.
    Hyphens and commas should be considered as part of the word,
    other characters (including digits) can be removed.
    """
    mapping = defaultdict(int)
    text = re.sub(r'[^a-zA-Z\-,\s]', '', text).lower()
    for word in text.split():
        mapping[word] += 1

    return mapping


def persist_to_db(mapping):
    """
    Perform bulk save/update into DB for the processed data.
    """
    bulk_create_input = []
    bulk_update_input = []
    for key, value in mapping.items():
        try:
            obj = Word.objects.get(text_input=key)
            obj.count += value
            bulk_update_input.append(obj)
        except Word.DoesNotExist:
            bulk_create_input.append(Word(text_input=key, count=value))

    if bulk_update_input:
        Word.objects.bulk_update(bulk_update_input, ['count'])
    if bulk_create_input:
        Word.objects.bulk_create(bulk_create_input)


def process_url_input(url):
    """
    Handle URL input.
    Assuming valid text response to be received from the URL.
    Chunk size is set to 10MB.
    """
    results = []
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=1024*1024*10):
            results.append(prepare_text_input(chunk.decode()))
    sum_mapping = sum((Counter(mapping) for mapping in results), Counter())
    persist_to_db(dict(sum_mapping))


def process_file_path_input(file_path):
    """
    Handle file path input.
    Assuming text file that exists in `file_inputs` folder.
    Read chunk size is set to 10MB.
    """
    with open(f"{BASE_DIR}/file_inputs/{file_path}") as f:
        with Pool(cpu_count() - 1) as pool:
            results = pool.map(prepare_text_input, read_in_chunks(f))

    sum_mapping = sum((Counter(mapping) for mapping in results), Counter())
    persist_to_db(dict(sum_mapping))


def read_in_chunks(file_object, chunk_size=1024*1024*10):
    """
    Read a file piece by piece. Default chunk size: 10MB.
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
