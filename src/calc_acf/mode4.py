"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
from utility.handling_file_directory import read_file, make_directory
from utility.handling_data import inflated, read_iteration, read_index_quantity, read_sep
import os
import glob
import re
import statsmodels.api as sm
import pandas as pd
from tqdm import tqdm

class method:
    # 変数
    mode = 4 # モード番号
    path = "" # 読み込み対象のファイルへのパス
    sep = "" # ファイルの区切り文字の種類
    CONTINUOUS = 3 # 何回連続して計算をするか

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

    def remove_midway_files(self, out_base_dir):
        path = out_base_dir + "midway_cal/*.txt" # 削除するファイル群
        path_array = sorted(glob.glob(path)) # ファイルへのパス格納用配列
        path_array = [(x.replace("¥¥", "/")) for x in path_array] # windows対応

        if not path_array:
            return
        
        for p in path_array:
            os.remove(p)

    def write_settings(self, out_dir, path, start_time, end_time, quantity, iteration):
        """
        水増しの設定を出力する。

        Input
        ------
        out_dir : 保存先のディレクトリ
        start_time : 水増し期間、開始時間
        end_time : 水増し期間、終了時間
        quantity : 何個まで増やすか
        iteration: 何回目の計算か
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        path = out_dir + "settings_" + ext[0] + "_cal" + str(iteration+1) + ".txt"

        with open(path, mode='w') as f:
            outline = "水増し 設定情報\n"
            start_text = "開始時間 : " + "{:.4f}".format(start_time) + "\n"
            end_text = "終了時間 : " + "{:.4f}".format(end_time) + "\n"
            quantity_text = "必要データ数 : " + str(quantity) + "\n"
            iteration_text = "何回目の計算か : " + str(iteration+1) + "\n"
            f.writelines([outline, start_text, end_text, quantity_text, iteration_text])
        
    def write_midway_settings(self, out_base_dir, start_time, end_time, quantity, iteration):
        """
        水増しの設定を、途中結果のディレクトリへ出力する。

        Input
        ------
        out_base_dir : 保存先のディレクトリ
        start_time : 水増し期間、開始時間
        end_time : 水増し期間、終了時間
        quantity : 何個まで増やすか
        iteration: 何回目の計算か
        """

        path = out_base_dir + "midway_cal/" + "settings_cal" + str(iteration+1) + ".txt"

        with open(path, mode='w') as f:
            outline = "水増し 設定情報\n"
            start_text = "開始時間 : " + "{:.4f}".format(start_time) + "\n"
            end_text = "終了時間 : " + "{:.4f}".format(end_time) + "\n"
            quantity_text = "必要データ数 : " + str(quantity) + "\n"
            iteration_text = "何回目の計算か : " + str(iteration+1) + "\n"
            f.writelines([outline, start_text, end_text, quantity_text, iteration_text])

    def write_file(self, df, path, out_dir, iteration):
        """
        計算結果を出力する。
        出力はindexの有無で、2種類存在する。

        Input
        ------
        df : 保存したい計算結果
        path : 元データのファイルパス
        out_dir : 保存先のディレクトリ
        iteration: 何回目の計算か
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        # index有りのファイル名
        out_fname = ext[0]  + "_cal" + str(iteration+1) + ext[1]
        out_path = out_dir + out_fname

        # indexなしのファイル名
        out_fname_noindex = ext[0] + "_cal" + str(iteration+1) + "_noindex" + ext[1]
        out_path_noindex = out_dir + out_fname_noindex

        df.to_csv(out_path, sep=" ", header=False, encoding="utf-8") # index有り
        df.to_csv(out_path_noindex, sep=" ", header=False, encoding="utf-8", index=False) # indexなし

    def write_midway_file(self, df, path, out_base_dir, iteration):
        """
        計算結果を、途中結果のディレクトリへ出力する。
        出力はindexの有無で、2種類存在する。

        Input
        ------
        df : 保存したい計算結果
        path : 元データのファイルパス
        out_base_dir : 保存先のディレクトリ
        iteration: 何回目の計算か
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        # index有りのファイル名
        out_fname = "mode4_cal" + str(iteration+1) + ext[1]
        out_path = out_base_dir + "midway_cal/" + out_fname

        # indexなしのファイル名
        out_fname_noindex = "mode4_cal" + str(iteration+1) + "_noindex" + ext[1]
        out_path_noindex = out_base_dir + "midway_cal/" + out_fname_noindex

        df.to_csv(out_path, sep=" ", header=False, encoding="utf-8") # index有り
        df.to_csv(out_path_noindex, sep=" ", header=False, encoding="utf-8", index=False) # indexなし

    def calc(self, df_array, path_array, out_dir, out_base_dir):
        """
        水増し計算を行う。

        Input
        ------
        df_array     : 読み込んだデータ群の配列
        path_array   : 元データのファイルパス配列
        out_dir      : 水増しした結果を保存する先のディレクトリのパス
        out_base_dir : 水増し計算の途中結果を保存する先のディレクトリのパス
        """

        # プログレスバーの設定
        bar = tqdm(total=len(path_array))
        bar.set_description("inflated")

        for df, path in zip(df_array, path_array):
            df_data = pd.Series(df['data'], dtype='float') # 自己相関の計算のためにpd.Seriesに格納
            inflated_df = df_data.copy()
            
            for i in range(self.CONTINUOUS):
                if i > 0:
                    # 開始indexと終了index
                    start_time, end_time, quantity = read_index_quantity()
                    self.write_settings(out_dir, path, start_time, end_time, quantity, iteration=i) # 保存
                    inflated_df = pd.Series(inflated_df)
                    inflated_df = inflated(inflated_df, start_time, end_time, quantity) # 水増しdf
                
                if 0 < i < self.CONTINUOUS-1:
                    self.write_midway_settings(out_base_dir, start_time, end_time, quantity, iteration=i) # 保存
                
                iteration = int(read_iteration()) # ずらす回数

                inflated_df = sm.tsa.stattools.acf(inflated_df, nlags=iteration, fft=True)
                index = pd.Series([times*0.0002 for times in range(iteration)])
                out_pd = pd.Series(inflated_df[:iteration], index=['{:.4f}'.format(i) for i in index])

                if i < self.CONTINUOUS-1:
                    self.write_midway_file(out_pd, path, out_base_dir, iteration=i)
                self.write_file(out_pd, path, out_dir, iteration=i)
            
            bar.update(1) # プログレスバーの更新
    
    def fit(self):
        """
        水増しの実行。
        """
        
        df_array, path_array = read_file(self.path, self.sep) # データの読み込み
        out_dir, out_base_dir = make_directory(self.mode) # 書き込みを行うディレクトリ
        self.remove_midway_files(out_base_dir)
        self.calc(df_array, path_array, out_dir, out_base_dir) # 水増しの実行と保存