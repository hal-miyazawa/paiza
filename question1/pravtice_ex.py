# 地図のサイズ
N = int(input())

# 高さのマップを読み込み
grid = []
for _ in range(N):
    row = list(map(int, input().split()))
    grid.append(row)

peaks = []

# すべてのマスを調べる
for i in range(N):
    for j in range(N):
        h = grid[i][j]

        # 周り4方向の高さ（範囲外は 0）
        up    = grid[i-1][j] if i-1 >= 0 else 0
        down  = grid[i+1][j] if i+1 < N else 0
        left  = grid[i][j-1] if j-1 >= 0 else 0
        right = grid[i][j+1] if j+1 < N else 0

        # 山頂判定（上下左右より高い）
        if h > up and h > down and h > left and h > right:
            peaks.append(h)

# リスト peaks を “大きい順（降順）に並べ替える”
# peaks.sort()だと小さい順
peaks.sort(reverse=True)

# 1行ずつ出力
for v in peaks:
    print(v)


