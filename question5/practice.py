# 「どのスーパーでどの野菜を買うか決める → 
# 合計金額が一番安くなるようにする → そのときに訪れるスーパーの数を最小にしたい」


# 入力
# 3(スーパーの数) 3(野菜の数)
# 100 200 300（スーパーごとの野菜の値段）
# 150 180 210
# 200 150 200

# 出力
# 2



N, K = map(int, input().split())

lista = []

for i in range(N):
    row = list(map(int, input().split()))
    lista.append(row)

used = [False] * N


# ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 各野菜 j について最安のスーパーを探す
for j in range(K):
    min_price = 10**18
    min_row = -1
    for i in range(N):
        if lista[i][j] < min_price:
            min_price = lista[i][j]
            min_row = i
    used[min_row] = True   # j の最安スーパーを記録

# 使ったスーパーの数を数える
ans = 0
for i in range(N):
    if used[i]:
        ans += 1

print(ans)

# --------------------------------------------------------
# for j in range(K):  # 各列を調べる
#     min_price = 10**18
#     min_row = -1
#     for i in range(N):
#         if prices[i][j] < min_price:
#             min_price = prices[i][j]
#             min_row = i
#     rows.append(min_row)

# # rows の重複を除いた個数が必要なスーパー数
#setでlist内の重複をなくす
#lenでlistの要素数を求める
# ans = len(set(rows))

# print(ans)
