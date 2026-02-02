# 1行目: 縦H、横W
H, W = map(int, input().split())

# 2行目: ネズミの数N、使える罠の枚数T
N, T = map(int, input().split())

# マスごとのネズミ数を数える 2次元リストを用意 (全部0で初期化)
field = []
for _ in range(H):
    #0 が W 個並んだリストを作る
    row = [0] * W
    field.append(row)

# N匹それぞれの位置を読み込んでカウント
for _ in range(N):
    x, y = map(int, input().split())
    # 入力は 1 始まりなので、0 始まりに直す
    field[x - 1][y - 1] += 1

# すべてのマスのネズミ数を 1つのリストに集める
counts = []
for i in range(H):
    for j in range(W):
        counts.append(field[i][j])

# 多い順(降順)に並べ替える
counts.sort(reverse=True)

# 罠をT枚使って捕まえられるネズミの合計
# → ネズミ数が多いマスからT個ぶん足す
answer = 0
for i in range(T):
    answer += counts[i]

print(answer)
