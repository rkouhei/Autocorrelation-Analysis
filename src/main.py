"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
from calc_acf import mode1, mode2, mode3, mode6

def select_mode():
    """
    計算モードの選択とファイルのパスの入力をする。
    一度に、複数ファイルの読み込みも可能。
    相対パスと絶対パス、どちらでも可能。

    Raises
    ------
    存在しないモードを選択したとき。
    モードで数字以外を使用したとき。
    """

    print("分析したいファイルへのパスを入力してください: ", end="")
    path = input()

    print("計算モードを選択してください(固定: 1, 任意(part data): 2, 連続任意: 3, 水増し計算: 4, 水増しのみ: 5, 任意(all data): 6): ", end="")
    mode = input()
    try:
        mode = int(mode)
    except:
        print("数字を入力してください")
        exit()

    if mode == 1:
        acf = mode1.method(path)
    elif mode == 2:
        acf = mode2.method(path)
    elif mode == 3:
        acf = mode3.method(path)
    elif mode == 6:
        acf = mode6.method(path)
    else:
        print("存在しないモードです。")
        exit()
    
    acf.fit() # 自己相関係数の計算・保存

if __name__ == "__main__":
    select_mode()