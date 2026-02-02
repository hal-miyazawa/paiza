# 盤面の行数 H と列数 W を読み込む
H, W = map(int, input().split())

# 盤面を読み込む
mas = []
for _ in range(H):
    line = input().strip()   # 例: "...", "#.."
    row = list(line)         # 1文字ずつのリストにする
    mas.append(row)

# 書き換えるマスの y, x 座標
y, x = map(int, input().split())

# マスの文字を反転させる
if mas[y][x] == "#":
    mas[y][x] = "."
else:
    mas[y][x] = "#"

# 盤面を出力
for i in range(H):
    #join は リストの中身を結合して 1 つの文字列にする関数。
    #"abc"こんな感じになる
    print("".join(mas[i]))
