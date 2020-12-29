"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
import os
import datetime
import glob
import re
import statsmodels.api as sm
import pandas as pd
from tqdm import tqdm

def numericalSort(value):
    """
    複数ファイルの入力の際、ファイル名を昇順に並べる。

    Input
    ------
    value : 読み込みたいファイルへのパス

    Output
    ------
    parts : ファイル中の数字
    """

    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def read_file(path, sep):
    """
    ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
    相対パスと絶対パス、どちらでも可能。

    Input
    ------
    path : 読み込みたいファイルへのパス
    sep  : 読み込みたいファイルの区切り文字の指定

    Output
    ------
    df_array   : 読み込んだdfのリスト
    path_array : globで取得した、ファイルパスのリスト

    Raises
    ------
    存在しないディレクトリやパスが指定された時。
    入力にテキストファイル以外のものが含まれている時。
    ファイルの区切り文字を誤選択した時。
    """

    df_array = [] # 読み込んだテキストのdf配列
    path_array = sorted(glob.glob(path), key=numericalSort) # ファイルへのパス格納用配列
    path_array = [(x.replace("¥¥", "/")) for x in path_array] # windows対応

    # 読み込めていない場合
    if not path_array:
        print(path_array)
        print(path)
        print("指定したファイル、もしくはディレクトリが存在しません。")
        exit()

    # プログレスバーの設定
    bar = tqdm(total=len(path_array))
    bar.set_description("read_files")

    for file_path in path_array:
        ext = os.path.splitext(file_path)[1]
        if ext != ".txt":
            print("テキストファイル以外のものが含まれています。")
            exit()

        # データの読み込み
        if sep == "1": # スペースの場合
            df = pd.read_table(
                file_path,
                header=None,
                sep=" ",
                names=("times", "data"),
                encoding="utf-8"
            )
            df = df.dropna(how="all")
            df = df.reset_index()
        elif sep == "2": # タブの場合
            df = pd.read_table(
                file_path,
                header=None,
                sep="\t",
                names=("times", "data"),
                encoding="utf-8"
            )
            df = df.dropna(how="all")
            df = df.reset_index()
        else:
            print("1か2で選択してください。")
            exit()

        df_array.append(df)
        bar.update(1)  # プログレスバーの更新

    return df_array, path_array

# ディレクトリの作成
def make_directory(mode):
    """
    出力するディレクトリを作成する。
    ディレクトリ名は、プログラムの実行時間に基づく。

    Input
    ------
    mode : 計算モードの番号

    Output
    ------
    out_dir : 出力ディレクトリ名

    Raises
    ------
    出力ディレクトリが重複した場合。
    """

    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )

    # モード番号をstrで
    mode_name = "mode" + str(mode)

    #日付をフォルダ名に整形
    year = str(dt_now.year)
    month = str(dt_now.month).zfill(2)
    day = str(dt_now.day).zfill(2)
    hour = str(dt_now.hour).zfill(2)
    minute = str(dt_now.minute).zfill(2)
    second = str(dt_now.second).zfill(2)
    dirname = year + month + day + "-" + hour + "." + minute + "." + second #フォルダ名を定義
    out_dir = os.path.dirname(__file__) + "/../../out/" + mode_name + "/" + dirname + "/" #生成フォルダのパス

    if os.path.isdir(out_dir):
        print("ディレクトリが既に存在しています。")
        exit()
    else:
        os.makedirs(out_dir) #フォルダを作成

    return out_dir