import requests as rq
from typing import Self
import random


class MMBot:
    words = [word.strip() for word in open("5letters.txt")]
    mm_url = "https://we6.talentsprint.com/wordle/game/"
    register_url = mm_url + "register"
    creat_url = mm_url + "create"
    guess_url = mm_url + "guess"
    SINGLETON = True

    def __init__(self: Self, name: str):
        if MMBot.SINGLETON:
            MMBot.SINGLETON = False
            self.session = rq.session()
        register_dict = {"mode": "mastermind", "name": name}
        reg_resp = self.session.post(MMBot.register_url, json=register_dict)
        self.me = reg_resp.json()['id']

    def setup_game(self: Self):
        def is_unique(w: str) -> bool:
            return len(w) == len(set(w))
        self.attempts = 0
        creat_dict = {"id": self.me, "overwrite": True}
        self.session.post(MMBot.creat_url, json=creat_dict)
        self.choices = [w for w in MMBot.words if is_unique(w)]
        random.shuffle(self.choices)

    def play(self: Self) -> dict:
        def post(choice: str) -> tuple[int, bool]:
            guess = {"id": self.me, "guess": choice}
            response = self.session.post(MMBot.guess_url, json=guess)
            rj = response.json()
            right = int(rj["feedback"])
            status = "win" in rj["message"]
            return right, status

        choice = random.choice(self.choices)
        self.choices.remove(choice)
        right, won = post(choice)
        tries = [f'{choice}:{right}']

        while not won:
            if DEBUG:
                print(choice, right, self.choices[:10])
            self.update(choice, right)
            choice = random.choice(self.choices)
            self.choices.remove(choice)
            right, won = post(choice)
            tries.append(f'{choice}:{right}')
        return {"Secret": choice, "Attempts": len(tries), "Route": " => ".join(tries)}

    def update(self: Self, choice: str, right: int):
        def common(choice: str, word: str):
            return len(set(choice) & set(word))
        self.choices = [w for w in self.choices if common(choice, w) == right]

DEBUG = False
bot = MMBot("CodeShifu")
for _ in range(10):
    bot.setup_game()
    print(bot.play())
