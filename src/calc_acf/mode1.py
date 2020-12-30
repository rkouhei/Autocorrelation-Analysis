"""
==============================
 2020/12/30
 rkouhei
==============================
"""

# ライブラリのインポート
from utility.handling_file_directory import read_file, make_directory
import os
import re
import statsmodels.api as sm
import pandas as pd
from tqdm import tqdm

class method:
    # 変数
    mode = 1 # モード番号
    path = "" # 読み込み対象のファイルへのパス
    sep = "1" # ファイルの区切り文字の種類

    def __init__(self, path):
        """
        ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
        相対パスと絶対パス、どちらでも可能。

        Input
        ------
        path : 読み込みたいのファイルへのパス(一括指定可)
        """
        self.path = path

    def write_file(self, df, path, out_dir, percentage):
        """
        計算結果を出力する。
        出力はindexの有無で、2種類存在する。

        Input
        ------
        df : 保存したい計算結果
        path : 元データのファイルパス
        out_dir : 保存先のディレクトリ
        percentage : 計算に使用したデータの割合
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        # index有りのファイル名
        out_fname = ext[0] + "_" + str(int(percentage*100)) + ext[1]
        out_path = out_dir + out_fname

        # indexなしのファイル名
        out_fname_noindex = ext[0] + "_" + str(int(percentage*100)) + "_noindex" + ext[1]
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
            iterations = len(df_data) # データ数の回数を計算の繰り返し回数とする

            for i in [i / 10 for i in range(5, 11)]: # 50%~100%で計算する
                # deep copy
                part_df = df_data.copy()

                part_iterations = int(iterations * i) # 計算回数をint型で作成
                part_df = part_df[:part_iterations] # dfの上からpart_iterations分だけ取り出す
                acf = sm.tsa.stattools.acf(part_df, nlags=part_iterations, fft=True) # 自己相関の計算
                index = pd.Series([times*0.0002 for times in range(part_iterations)]) # 出力用indexの作成準備
                out_pd = pd.Series(acf, index=['{:.4f}'.format(i) for i in index]) # 出力用にデータをpdで成形
                self.write_file(out_pd, path, out_dir, percentage=i) # データの出力
            
            bar.update(1) # プログレスバーの更新
    
    def fit(self):
        """
        計算の実行。
        """
        
        df_array, path_array = read_file(self.path, self.sep)
        out_dir, _ = make_directory(self.mode) # 書き込みを行うディレクトリ
        self.calc(df_array, path_array, out_dir)