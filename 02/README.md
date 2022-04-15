Example of test project to process large text data.


Steps to install and use the project locally.

1) Create a venv

2) Install requirements:
`pip install -r requirements.txt`

3) Apply migrations:
`./manage.py migrate`

4) Start debug Django server
`./manage.py runserver`

5) API endpoints:

The endpoint to handle text inputs:
`POST http://localhost:8000/words/word_counter`
- Plain text input
`Payload: {"type": "text", "value": "wordNumber1 wordComma, word-Hyphen- wordDot. wordNumber 1wordNumber"}`
- URL input
`Payload: {"type": "url", "value": "http://localhost:8000/words/test.txt"}`
- File path input
`Payload: {"type": "file_path", "value": "test1GB.txt"}`

The endpoint to check the number of times the word appeared:
`http://localhost:8000/words/word_statistics?input=UlySseS`
