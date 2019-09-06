import json

list = [[{'Time': '16:04:33', 'Type': 'Router', 'Host': 'Akagi', 'IP': '10.10.10.1', 'CPU%': 1.0, 'Memory%': 76.59, 'Bandwidth': 0.009708740533333333}, {'Time': '16:04:33', 'Type': 'Router', 'Host': 'Zuikaku', 'IP': '10.10.10.2', 'CPU%': 0.0, 'Memory%': 67.45}, {'Time': '16:04:33', 'Type': 'Router', 'Host': 'Kaga', 'IP': '10.10.10.14', 'CPU%': 0.0, 'Memory%': 67.45}, {'Time': '16:04:34', 'Type': 'Router', 'Host': 'Shoukaku', 'IP': '10.10.10.18', 'CPU%': 0.0, 'Memory%': 67.45, 'Bandwidth': 0.005146711866666666}, {'Time': '16:04:34', 'Type': 'PC', 'Host': 'MONITORED', 'IP': '148.204.2.2', 'CPU%': 0.0, 'Memory%': 45.06, 'HDD%': 31, 'Bandwidth': 8.690634666666667e-05}]]
with open('person.txt', 'a') as fout:
    fout.write("\n")
    json.dump(list , fout)