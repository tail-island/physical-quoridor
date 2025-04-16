import json
import sys


class Player:
    def run(self):
        while True:
            request = json.loads(input())

            match request["command"]:
                case "get_action":
                    action = self.get_action(request["observation"])
                    print(json.dumps(action))
                    sys.stdout.flush()

                case "end_game":
                    self.end_game()
                    print(json.dumps("OK"))
                    sys.stdout.flush()
                    break

    def get_action(self, observation):
        return (0, [0, 0], (0, 0, 0))

    def end_game(self):
        pass
