"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
from utility.handling_file_directory import read_file, make_directory
import os
import datetime
import glob
import re
import statsmodels.api as sm
import pandas as pd
from tqdm import tqdm

class method:
    # 変数
    mode = 6 # モード番号
    path = "" # 読み込み対象のファイルへのパス
    sep = "" # ファイルの区切り文字の種類
    iteration = 0 # 計算回数指定用変数

    def __init__(self, path):
        """
        ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
        相対パスと絶対パス、どちらでも可能。

        Input
        ------
        path : 読み込みたいのファイルへのパス(一括指定可)

        Raises
        ------
        計算回数で、数字以外を入力した時。
        """

        print("分析したいファイルの区切り文字を入力してください(スペース: 1, タブ: 2): ", end="")
        self.sep = input()
        
        print("計算回数を入力してください: ", end="")
        iteration = input()
        try:
            iteration = int(iteration) # 数字以外はexceptへ
            self.iteration = iteration
        except:
            print("計算回数には、数字を入力してください。")
            exit()

        self.path = path

    def check_length(self, df_array, path_array):
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
            if len(df) < self.iteration:
                print(path)
                print("上記のファイルのデータ数より、ずらす回数が多くなっています。")
                exit()

        

    def write_file(self, df, path, out_dir):
        """
        計算結果を出力する。
        出力はindexの有無で、2種類存在する。

        Input
        ------
        df : 保存したい計算結果
        path : 元データのファイルパス
        out_dir : 保存先のディレクトリ
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        # index有りのファイル名
        out_fname = ext[0] + "_" + str(self.iteration) + ext[1]
        out_path = out_dir + out_fname

        # indexなしのファイル名
        out_fname_noindex = ext[0] + "_" + str(self.iteration) + "_noindex" + ext[1]
        out_path_noindex = out_dir + out_fname_noindex

        df.to_csv(out_path, sep=" ", header=False, encoding="utf-8") # index有り
        df.to_csv(out_path_noindex, sep=" ", header=False, encoding="utf-8", index=False) # indexなし

    def calc(self, df_array, path_array, out_dir):
        """
        自己相関係数の計算を行う。

        Input
        ------
        df_array   : 読み込んだデータ群の配列
        path_array : 元データのファイルパス配列
        out_dir    : 計算結果を保存先するディレクトリへのパス
        """

        # プログレスバーの設定
        bar = tqdm(total=len(path_array))
        bar.set_description("calc_acf")

        for df, path in zip(df_array, path_array):
            df_data = pd.Series(df['data'], dtype='float') # 自己相関の計算のためにpd.Seriesに格納
            part_df = df_data.copy()

            part_iterations = int(self.iteration)
            acf = sm.tsa.stattools.acf(part_df, nlags=part_iterations, fft=True)
            index = pd.Series([times*0.0002 for times in range(part_iterations)])
            out_pd = pd.Series(acf[part_iterations], index=['{:.4f}'.format(i) for i in index])
            self.write_file(out_pd, path, out_dir) 
            
            bar.update(1) # プログレスバーの更新
    
    def fit(self):
        """
        計算の実行。
        """
        df_array, path_array = read_file(self.path, self.sep) # データの読み込み
        self.check_length(df_array, path_array) # ずらす回数とデータ数を比較しておく
        out_dir = make_directory(self.mode) # 書き込みを行うディレクトリ
        self.calc(df_array, path_array, out_dir) # 計算の実行と保存