import argparse
import subprocess
import json
import requests


def getRawGameByUrl(url):
    r = requests.get(url)
    content = r.text
    data_start = "<script>var data ={"
    data_end = "</script>"
    d = content.find(data_start)
    e = content[d:].find(data_end)  - 1
    raw_data = content[d:d+e][len(data_start) - 1:]
    return raw_data


def getRawGameByHash(hash):
    url = "https://shogidb2.com/games/" + hash
    return getRawGameByUrl(url)


class KifBuilder():
    def __init__(self):
        self.kif_content = ""
        self.errors = []
    def tryBuildTag(self, tag, value):
        build_tags = ["開始日時", "終了日時", "棋戦詳細", "棋戦",
         "手合割", "戦型" ,"後手", "場所", "先手", "time_consumed", 
         "time", "strategy", "result", "provider"]
        if tag in build_tags and value != None and isinstance(value, str):
            try:
                self.kif_content +=  f"{tag}:{value}\n"
            except:
                self.errors.append(f"Error when making tag {tag}")

    def buildHeader(self, json_data):
        for key in json_data.keys():
            self.tryBuildTag(key, json_data[key])
        self.kif_content += f"手数----指手---------消費時間--\n"

    #buildMove can be expanded to include shogidb2 comments if desired
    def buildMove(self, move, move_number):
        try:
            kifu_move = move["move"]
            self.kif_content += f'{move_number:>4}   {kifu_move:<}\n'
        except:
            self.errors.append(f"Critical | Error when adding kifu move {move_number}")

    def getResult(self):
        return (self.kif_content, self.errors)


class FormatProcessor():
    def __init__(self, game_json):
        self.game_json = game_json

    def construct(self, format_builder):
        format_builder.buildHeader(self.game_json)
        move_number = 2
        for move in self.game_json["moves"]:
            format_builder.buildMove(move, move_number)
            move_number += 1



parser = argparse.ArgumentParser(description=r'Example: python convert_shogidb2_to_kif.py -i fea78d295d14bf6d667cad2985304c0969b9213f -o 志沢春吉vs樋口義雄1929.kif -p' )

parser.add_argument('-u', '--url', action='store', dest='game_url', help='Url of the shogidb2 game')
parser.add_argument('-i', '--hash', action='store', dest='game_hash', help='Hash of the shogidb2 game')
parser.add_argument('-o', '--output', action='store', dest='output', help='File to save the kif in')
parser.add_argument('-p', '--print', action='store_true', dest="print_kif", help="Print the game to the terminal")
args = parser.parse_args()


if args.game_hash == None and args.game_url == None:
    print("Please use '-i' ('--hash') or '-u' ('--url') to specify the shogidb2 game. Use '-h' argument to get help")
    exit()

raw_game = ""
if args.game_hash != None:
    raw_game = getRawGameByHash(args.game_hash)
if args.game_url != None and raw_game == "":
    raw_game = getRawGameByUrl(args.game_url)

game_json = json.loads(raw_game)

kif_builder = KifBuilder()
processor = FormatProcessor(game_json)
processor.construct(kif_builder)
kif_content, errors = kif_builder.getResult()

if args.print_kif:    
    print(kif_content)

if args.output != None:
    try:
        f = open(args.output, "w")
        f.write(kif_content)
        f.close()
    except:
        print("Error, could not write kif file to disk")

if len(errors) > 0:
    print("Errors:")
    for error in errors:
        print(f"    {error}")



def convertJsonToKIF(game_as_json):
    kifu_file = ""
    kifu_file += f"開始日時：{game_as_json['開始日時']}\n"
    kifu_file += f"終了日時：{game_as_json['終了日時']}\n"
    kifu_file += f"棋戦：{game_as_json['棋戦']}\n"
    kifu_file += f"棋戦詳細：{game_as_json['棋戦詳細']}\n"
    kifu_file += f"持ち時間：{game_as_json['time']}\n"
    kifu_file += f"手合割：{game_as_json['手合割']}\n"
    kifu_file += f"先手：{game_as_json['先手']}\n"
    kifu_file += f"後手：{game_as_json['後手']}\n"
    kifu_file += f"場所：{game_as_json['場所']}\n"
    kifu_file += f"result：{game_as_json['result']}\n"
    kifu_file += f"place：{game_as_json['place']}\n"
    kifu_file += f"strategy：{game_as_json['strategy']}\n"
    kifu_file += f"time_consumed：{game_as_json['time_consumed']}\n"
    kifu_file += f"手数----指手---------消費時間--\n"
    moves = game_as_json["moves"]
    for i in range(len(moves)):
        kifu_file += f"{i + 1:>4}   {moves[i]['move']:<}\n"
    return kifu_file

