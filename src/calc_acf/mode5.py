"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
from utility.handling_file_directory import read_file, make_directory
from utility.handling_data import inflated, read_index_quantity, read_sep
import os
import datetime
import glob
import re
import statsmodels.api as sm
import pandas as pd
from tqdm import tqdm

class method:
    # 変数
    mode = 5 # モード番号
    path = "" # 読み込み対象のファイルへのパス
    sep = "" # ファイルの区切り文字の種類

    def __init__(self, path):
        """
        ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
        相対パスと絶対パス、どちらでも可能。

        Input
        ------
        path : 読み込みたいのファイルへのパス(一括指定可)
        """

        self.sep = read_sep()
        self.path = path

    def write_settings(self, out_dir, start_time, end_time, quantity):
        """
        水増しの設定を出力する。

        Input
        ------
        out_dir : 保存先のディレクトリ
        start_time : 水増し期間、開始時間
        end_time : 水増し期間、終了時間
        quantity : 何個まで増やすか
        """

        path = out_dir + "settings.txt"

        with open(path, mode='w') as f:
            outline = "水増し 設定情報\n"
            start_text = "開始時間 : " + "{:.4f}".format(start_time) + "\n"
            end_text = "終了時間 : " + "{:.4f}".format(end_time) + "\n"
            quantity_text = "必要データ数 : " + str(quantity) + "\n"
            f.writelines([outline, start_text, end_text, quantity_text])

    def write_file(self, df, path, out_dir, quantity):
        """
        水増し結果を出力する。
        出力はindexの有無で、2種類存在する。

        Input
        ------
        df : 保存したい計算結果
        path : 元データのファイルパス
        out_dir : 保存先のディレクトリ
        start : 水増し期間、開始時間
        end : 水増し期間、終了時間
        quantity : 何個まで増やすか
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        # index有りのファイル名
        out_fname = ext[0] + "_" + str(quantity) + "_inflated" + ext[1]
        out_path = out_dir + out_fname

        # indexなしのファイル名
        out_fname_noindex = ext[0] + "_" + str(quantity) + "_inflated" + "_noindex" + ext[1]
        out_path_noindex = out_dir + out_fname_noindex

        df.to_csv(out_path, sep=" ", header=False, encoding="utf-8") # index有り
        df.to_csv(out_path_noindex, sep=" ", header=False, encoding="utf-8", index=False) # indexなし

    def calc(self, df_array, path_array, out_dir):
        """
        水増しを行う。

        Input
        ------
        df_array   : 読み込んだデータ群の配列
        path_array : 元データのファイルパス配列
        out_dir    : 水増しした結果を保存先するディレクトリへのパス
        """

        # 開始indexと終了index
        start_time, end_time, quantity = read_index_quantity()
        self.write_settings(out_dir, start_time, end_time, quantity) # 保存

        # プログレスバーの設定
        bar = tqdm(total=len(path_array))
        bar.set_description("inflated")

        for df, path in zip(df_array, path_array):
            df_data = pd.Series(df['data'], dtype='float') # 自己相関の計算のためにpd.Seriesに格納

            inflated_df = inflated(df_data, start_time, end_time, quantity)
            index = pd.Series([times*0.0002 for times in range(quantity)])
            out_pd = pd.Series(inflated_df, index=['{:.4f}'.format(i) for i in index])
            self.write_file(out_pd, path, out_dir, quantity)
            
            bar.update(1) # プログレスバーの更新
    
    def fit(self):
        """
        水増しの実行。
        """
        
        df_array, path_array = read_file(self.path, self.sep) # データの読み込み
        out_dir, _ = make_directory(self.mode) # 書き込みを行うディレクトリ
        self.calc(df_array, path_array, out_dir) # 水増しの実行と保存