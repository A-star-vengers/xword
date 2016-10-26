import requests

def main():

    with requests.Session() as s:

        r = s.post("http://127.0.0.1:5000/login", data={
                "username" : "test",
                "password" : "test"
                 }
              )

        print(r.text)

        for x in range(20, 100):

            r = s.post("http://127.0.0.1:5000/create_puzzle", data={
                    "title" : "The best puzzle " + str(x),
                    "hint_1" : "one",
                    "answer_1" : "two",
                    "hint_2" : "three",
                    "answer_2" : "four",
                    "hint_3" : "five",
                    "answer_3" : "six",
                    "hint_4" : "seven",
                    "answer_4" : "eight",
                    "hint_5" : "nine",
                    "answer_5" : "ten",
                    "hint_6" : "eleven",
                    "answer_6" : "twelve",
                    "hint_7" : "thirteen",
                    "answer_7" : "fourteen",
                    "hint_8" : "fifteen",
                    "answer_8" : "sixteen",
                    "hint_9" : "seventeen",
                    "answer_9" : "eighteen",
                    "hint_10" : "nineteen",
                    "answer_10" : "twenty"
                })


    

if __name__ == "__main__":
    main()
