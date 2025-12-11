N,K,M = map(int,input().split())
# Nの数で人リストを作成する、TRUE*N を入れる。脱落でFalseにする
# Kの数でループを回してリストとして単語リストを作成

# Mの数でループを回してリストとしてしりとりリストを作成

# しりとりリストを回して条件
    # まず人数のカウント、１からスタートしてプラスしてNより大きくなるなら１に戻す。
    #　しりとりの発言が単語リストにあるか確認、なかったら脱落 or 発言の単語がzで終わっていたら脱落　→　その人リスト[カウント]をfalse
    #  発言した単語の最初の文字とその前の単語の最後の文字を比較する。一致してなかったら脱落（最初の判定をして最初だけこの条件は発動しない。）
    #  しりとりリストを回して発言をリストに入れていって重複したらそのカウントの人を脱落
# 出力としての人数→人リストのTrueの数を出力
# 人リストのtrueがある人リスト[n]のnを別配列に格納
# sortして小さい順にループして出力。printには改行をつける

# ---- 入力例の説明 ----
# N=3（3人でしりとり）
# K=6（単語リストに登録されているのは 6語）
# M=7（しりとりの発言が 7 回行われた）
#
# 単語リスト:
# a
# aloha
# app
# az
# paiza
# warp
#
# 発言ログ（順番に処理）:
# app
# paiza
# a
# aloha
# az
# warp
# paiza

# N: 人数, K: 単語リスト数, M: 発言回数
N, K, M = map(int, input().split())

# 単語リスト（セットにして高速に検索）
dict_words = set()
for _ in range(K):
    w = input().strip()
    dict_words.add(w)

# しりとりのログ
logs = []
for _ in range(M):
    s = input().strip()
    logs.append(s)

# 各人がゲームに残っているかどうか
alive = [True] * N

# すでに出た単語
used_words = set()

# 次に発言する人のインデックス（0-based）
cur = 0

# 直前の発言
prev_word = ""
# 直前の発言者がルール違反で脱落したかどうか
prev_broke_rule = True  # 最初の人はルール2を無視できるので True でスタート

for s in logs:
    # もし全員脱落してたらもう処理不要
    if not any(alive):
        break

    # 生きている人が出るまで cur を進める
    while not alive[cur]:
        cur = (cur + 1) % N

    invalid = False  # この発言がルール違反かどうか

    # ルール1: 単語リストにあるか
    if s not in dict_words:
        invalid = True

    # ルール2: 前の人がルール違反していない場合だけチェック
    if not prev_broke_rule:
        # 直前の単語の最後の文字と、今の単語の最初の文字
        if prev_word[-1] != s[0]:
            invalid = True

    # ルール3: すでに出た単語を言ってはいけない
    if s in used_words:
        invalid = True

    # ルール4: z で終わる単語はダメ
    if s.endswith('z'):
        invalid = True

    # その単語自体は「発言された」ので、ルール3用には記録する
    used_words.add(s)

    # 違反だったらこの人は脱落
    if invalid:
        alive[cur] = False
        prev_broke_rule = True
    else:
        prev_broke_rule = False

    # 今の単語を「直前の発言」として記録
    prev_word = s

    # 次の人へ（脱落してても次のループでスキップされる）
    cur = (cur + 1) % N

# 生き残った人の番号(1-based)を集める
survivors = []
for i in range(N):
    if alive[i]:
        survivors.append(i + 1)

# 小さい順に出力（すでに1..N順なのでそのままでもOK）
for num in survivors:
    print(num)
