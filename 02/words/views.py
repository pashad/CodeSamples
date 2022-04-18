import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from test_project.settings import BASE_DIR
from words.models import Word
from words.processing import process_file_path_input, process_text_input, process_url_input


@require_POST
@csrf_exempt
def word_counter(request):
    """
    Process the input and persist the results into DB.

    Expected input payload:
        {
            "type": "text"|"url"|"file_path"
            "value":  text string/URL string/file path string (assume test_project/file_inputs/{file_path})
        }

    Eg. POST http://localhost:8000/words/word_counter
        Payload: {"type": "text", "value": "wordNumber1 wordComma, word-Hyphen- wordDot. wordNumber 1wordNumber"}
    """
    request_json = json.loads(request.body)  # assume JSON payload input with the appropriate encoding
    if not (input_type := request_json.get("type", "").lower()) or not (input_value := request_json.get("value")):
        return HttpResponse("Invalid payload", status=HTTPStatus.BAD_REQUEST)

    if input_type == "text":
        process_text_input(input_value)
    elif input_type == "url":
        process_url_input(input_value)
    elif input_type == "file_path":
        process_file_path_input(input_value)
    else:
        return HttpResponse("Invalid input type", status=HTTPStatus.BAD_REQUEST)

    return HttpResponse("OK")


def test_txt(request):
    """
    Endpoint to test URL string

    Eg. POST http://localhost:8000/words/word_counter
        Payload: {"type": "url", "value": "http://localhost:8000/words/test.txt"}
    """

    f = open(f"{BASE_DIR}/file_inputs/ulysses.txt")
    return HttpResponse(f.read(), content_type="text/plain")


@require_GET
def word_statistics(request):
    """
    Get the number of occurrences of the word.

    Eg. GET http://localhost:8000/words/word_statistics?input=LoRem
    """
    word_input = request.GET.get("input", "").lower()
    try:
        count = Word.objects.get(text_input=word_input).count
    except Word.DoesNotExist:
        count = 0
    return HttpResponse(count)
