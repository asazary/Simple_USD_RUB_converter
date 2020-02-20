### Simple USD to RUB converter
It's created for practice. The program launches server on 
specify port (8080 by default) and returns json with info:
- requested value (in USD)
- converted value (in RUB)
- course (in RUB)
- date of course
- valute charcode (3 chars)

### How to use
1. Run **Simple_USD_RUB_converter.py**
2. In your browser go to:
    1. localhost:8080 - for getting current USD course
    2. localhost:8080/usd_to_rub/<amount> - for getting
     json with converted value and other info.
     For example:
     localhost:8080/usd_to_rub/10
3. Press Ctrl + C in terminal to stop server.