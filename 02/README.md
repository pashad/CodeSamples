###### Example of test project to process large text data.


Steps to install and use the project locally.

1) Create a venv

2) Install requirements:
`pip install -r requirements.txt`

3) (Optional) Run script from inside root project directory to create 1GB file.
`./create_1GB_file`

4) Apply migrations:
`./manage.py migrate`

5) Start debug Django server
`./manage.py runserver`

6) API endpoints:

The endpoint to handle text inputs:

cURL:
```
curl -X POST -H 'Content-Type: application/json' -d '<YOUR_PAYLOAD_SEE_BELOW_EXAMPLES>' http://localhost:8000/words/word_counter
```

`POST http://localhost:8000/words/word_counter`
- Plain text input payload
`{"type": "text", "value": "wordNumber1 wordComma, word-Hyphen- wordDot. wordNumber 1wordNumber"}`
- URL input payload
`{"type": "url", "value": "http://localhost:8000/words/test.txt"}`
- File path input payload
`{"type": "file_path", "value": "ulysses.txt"} or 
{"type": "file_path", "value": "test1GB.txt"} # if the file is generated at step 3.
`

The endpoint to check the number of times the word appeared:

`GET http://localhost:8000/words/word_statistics`

`curl http://localhost:8000/words/word_statistics?input=UlySseS`
