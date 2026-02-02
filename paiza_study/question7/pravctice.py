# https://paiza.jp/works/mondai/b_rank_skillcheck_archive/3d_printer/edit?language_uid=python3

X,Y,Z = map(int.input().split())
# listを三次元配列にして、各行をsplitで受け取ってlistにappend
# その後三次元配列にappend
#最後に--をもらう用のインプットを作成

# 判別方法としては、yで回してzが1のyの列をまず見ていって＃が含まれているか、含まれていたら#を格納なかったら.を格納して
#二次元配列に追加していく
# 最後はその二次元配列を回してprint一次元が終わったら改行してprintを続ける


# X: 奥行き(前後), Y: 横(左右), Z: 高さ(上下)
X, Y, Z = map(int, input().split())

# 立体データを 3次元リストで持つ
# cube[x][z][y] という形で参照できるようにする
cube = []

for x in range(X):
    layer = []  # この x のときの Z×Y の平面
    for z in range(Z):
        row = list(input().strip())  # 例: "##." → ['#','#','.']
        layer.append(row)
    cube.append(layer)
    
    sep = input().strip()  # 実際には "--" が入っている

# ===== 正面(+x方向)から見たときの図を作る =====
# 結果は Z 行 Y 列
front = []
for z in range(Z):
    row = []
    for y in range(Y):
        row.append('.')
    front.append(row)


# z: 上から下, y: 左から右 を決めて、
# x 方向に「どこかに '#' があるか」を見る
for z in range(Z):
    for y in range(Y):
        for x in range(X):
            if cube[x][z][y] == '#':
                front[z][y] = '#'
                break  # 1つ見つかればそのマスは '#' で確定


# ===== 出力 =====
for z in range(Z):
    # front[z] は ['#', '.', '#'] みたいなリストなので
    # "".join(...) で "#.#" の文字列にして出力する
    print("".join(front[z]))

