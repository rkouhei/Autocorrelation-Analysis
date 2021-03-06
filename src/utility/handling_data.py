"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
import pandas as pd

def read_sep():
    """
    読み込み対象のデータの区切り文字が、タブかスペースか指定。
    """

    print("分析したいファイルの区切り文字を入力してください(スペース: 1, タブ: 2): ", end="")
    sep = input()
    return sep

def read_iteration():
    """
    自己相関係数の計算で使用する、「ずらす回数」を読み込む。

    Output
    ------
    iteration : ずらす回数

    Raises
    ------
    iterationに数字以外が入力されたとき。
    """
    
    print("計算回数を入力してください: ", end="")
    iteration = input()
    try:
        iteration = int(iteration) # 数字以外はexceptへ
    except:
        print("計算回数には、数字を入力してください。")
        exit()

    return iteration

def read_iterations(CONTINUOUS):
    """
    自己相関係数の計算で使用する、「ずらす回数」を読み込む。

    Input
    ------
    CONTINUOUS: iterationを入力する回数

    Output
    ------
    iterations : ずらす回数の配列

    Raises
    ------
    後半のずらし回数が前半より多くなったとき。
    """
    
    iterations = [] # ずらす回数

    for i in range(1, CONTINUOUS+1):
        print(i, "回目の", end="")
        iterations.append(read_iteration())
    sorted_iterations = sorted(iterations, reverse=True)
    if sorted_iterations != iterations:
        print("後半のずらし回数が前半より多くなっています。")
        exit()

    return iterations

def read_index_quantity():
    """
    水増しのindexとquantityを読み込む。

    Output
    ------
    start_time : 水増し期間、開始時間
    end_time   : 水増し期間、終了時間
    quantity   : 何個まで増やすか

    Raises
    ------
    indexに小数点以外を入れたとき。
    indexに0.0002の倍数以外を入れたとき。
    end_timeがstart_timeよりも遅いとき。
    quantityに数字以外を入れたとき。
    """

    print("水増しの基準となる時間を入力してください: ")
    print("開始時間: ", end="")
    start_time = input()
    print("終了時間: ", end="")
    end_time = input()
    try:
        start_time = float(start_time) # 0.0002の倍数で無いものはexceptへ
        end_time = float(end_time)
    except:
        print("時間は、小数点で指定してください。")
        exit()
    if (round(start_time*10000) % 2) != 0 or (round(end_time*10000) % 2) != 0:
        print("時間は、0.0002s刻みで指定してください。")
        exit()
    elif start_time > end_time:
        print("開始時間が終了時間よりも遅い時間となっています。")
        exit()

    # 何個までデータを水増しするか
    print("水増ししたいデータ数を入力してください: ", end="")
    quantity = input()
    try:
        quantity = int(quantity)
    except:
        print("水増しデータ数には、数字を入力してください。")
        exit()

    return start_time, end_time, quantity

def check_length(df_array, path_array, iteration):
    """
    ずらす回数がデータ数より多ければアラートする。

    Input
    ------
    df_array   : 読み込んだデータ群の配列
    path_array : 元データのファイルパス配列

    Raises
    ------
    ずらす回数が、データ数よりも多い時。
    """

    for df, path in zip(df_array, path_array):
        if len(df) < iteration:
            print(path)
            print("上記のファイルのデータ数より、ずらす回数が多くなっています。")
            exit()

def inflated(df, start, end, quantity):
    """
    dfのデータを一部切り取り、それを指定の個数まで増やす。

    Input
    ------
    df : 水増し対象のデータ
    start : 水増し期間、開始時間
    end : 水増し期間、終了時間
    quantity : 何個まで増やすか

    Output
    ------
    inflated_list : 水増ししたデータのlist

    Raises
    ------
    endのindexが、dfに存在しない場合
    """

    # 時間のindexを行数に変更
    start_line = int((start * 10000) / 2)
    end_line = int((end * 10000) / 2)

    # indexがdf内であるか調べる
    if len(df)+1 < end_line:
        print("indexの時間が、読み込みファイルのデータに含まれていません。")
        exit()
    
    # 水増し対象区間
    part_df = df[start_line:end_line]

    # 何回水増し(コピー)が必要か
    iterate_num = int(quantity / len(part_df))

    inflated_df = part_df.copy()
    for _ in range(iterate_num):
        inflated_df = pd.concat([inflated_df, part_df])
    inflated_list = list(inflated_df[:quantity])

    return inflated_list