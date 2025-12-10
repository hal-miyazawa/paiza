# 入力例
# 3 3 3
# 2 1
# FRB
# 3 6 2
# 0 4 1
# 5 0 7

# 出力例
# 3
# 6
# 4


# 1行目: N, H, W
#input().split()で
#入力値　3 3 3
#  ["3", "3", "3"]

# map(int,で[3, 3, 3]
# N, H, W =でN = 3,H = 3,W = 
N, H, W = map(int, input().split())

# 2行目: sy, sx（1-index）
sy, sx = map(int, input().split())

# 3行目: 移動経路
# strip()で文字列の 前後にある空白・改行を取り除く
S = input().strip()

# 座席のチョコ数を読み込む
choco = []
for _ in range(H):
    #input().split()の時点では文字列型のlist
    # map(int, ...) で文字列それぞれに int を適用する “map オブジェクト” になる
    #map は “順番に取り出せるけどリストではない”
    # list()で整数型のlistになる
    row = list(map(int, input().split()))
    choco.append(row)

# 現在位置（0-indexに変換）
y = sy - 1
x = sx - 1

# 移動と出力
for move in S:
    if move == "F":      # 上へ
        y -= 1
    elif move == "B":    # 下へ
        y += 1
    elif move == "L":    # 左へ
        x -= 1
    elif move == "R":    # 右へ
        x += 1

    # 移動先のチョコ数を出力
    print(choco[y][x])
