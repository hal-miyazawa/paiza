# 園児の人数 N、じゃんけん回数 M を読み込む
N, M = map(int, input().split())

# 各園児の列車を管理するための辞書 trains を作る
# たとえば、園児1 → [1], 園児2 → [2] のように初期化する
trains = {}
for i in range(1, N + 1):
    trains[i] = [i]

# M 回のじゃんけん結果を順番に処理する
for _ in range(M):
    x, y = map(int, input().split())   # x が y に勝つ

    # x の列の末尾に、y の列を連結する（勝った列が伸びる）
    trains[x] = trains[x] + trains[y]

    # y の列は先頭じゃなくなるため空にする
    trains[y] = []

# すべての列の中で、最大の長さを調べる
max_len = 0
for key in trains:
    current_length = len(trains[key])
    if current_length > max_len:
        max_len = current_length

# 最大長の列を持つ園児番号（列の先頭）を winners に入れる
winners = []
for key in trains:
    if len(trains[key]) == max_len and max_len > 0:
        winners.append(key)

# winners を小さい順に並べ替える
winners.sort()

# winners の値を1行ずつ出力
for w in winners:
    print(w)
