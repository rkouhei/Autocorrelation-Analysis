"""
==============================
 2020/12/04
 Kohei Rikiishi
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

class calc_acf:
    # 変数
    df_array = [] # 読み込んだテキストの配列
    path_array = [] # ファイルへのパス格納用配列
    mode = 0 # 計算モード選択用変数
    iterations = [] # 計算回数指定用変数
    path = "" # 読み込み対象のファイルへのパス
    out_dir = "" # 書き込みを行うディレクトリ
    CONTINUOUS = 3 # mode3のとき、何回連続して計算をするか

    def __init__(self):
        """
        ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
        相対パスと絶対パス、どちらでも可能。

        Raises
        ------
        計算回数で、数字以外を入力した時。
        存在しないモードを選択したとき。
        連続してずらす際、後半のずらし回数が前半より多い時。
        """

        print("分析したいファイルへのパスを入力してください: ", end="")
        path = input()

        print("計算モードを選択してください(固定: 1, 任意: 2, 連続任意: 3): ", end="")
        mode = input()
        if mode == "2":
            print("計算回数を入力してください: ", end="")
            iteration = input()
            try:
                iteration = int(iteration) # 数字以外はexceptへ
                self.iterations.append(iteration)
            except:
                print("計算回数には、数字を入力してください。")
                exit()
        elif mode == "3":
            for i in range(1,self.CONTINUOUS+1):
                print(i, "回目の計算回数を入力してください: ", end="")
                iteration = input()
                try:
                    iteration = int(iteration) # 数字以外はexceptへ
                    self.iterations.append(iteration)
                except:
                    print("計算回数には、数字を入力してください。")
                    exit()
            sorted_iterations = sorted(self.iterations ,reverse=True)
            if sorted_iterations != self.iterations:
                    print("後半のずらし回数が前半より多くなっています。")
                    exit()
        elif mode != "1":
            print("存在しないモードです。")
            exit()
        
        self.path = path
        self.mode = mode

    def numericalSort(self, value):
        """
        複数ファイルの入力の際、ファイル名を昇順に並べる。
        """

        numbers = re.compile(r'(\d+)')
        parts = numbers.split(value)
        parts[1::2] = map(int, parts[1::2])
        return parts

    def read_file(self):
        """
        ファイルの読み込みを行う。一度に、複数ファイルの読み込みも可能。
        相対パスと絶対パス、どちらでも可能。

        Raises
        ------
        存在しないディレクトリやパスが指定された時。
        入力にテキストファイル以外のものが含まれている時。
        データ数よりずらす回数が多い時。
        """

        df_array = [] # 読み込んだテキストの配列
        path_array = sorted(glob.glob(self.path), key=self.numericalSort) # ファイルへのパス格納用配列
        self.path_array = [(x.replace("¥¥", "/")) for x in path_array] # windows対応

        # 読み込めていない場合
        if not self.path_array:
            print(self.path_array)
            print(self.path)
            print("指定したファイル、もしくはディレクトリが存在しません。")
            exit()

        # プログレスバーの設定
        bar = tqdm(total=len(self.path_array))
        bar.set_description("read_files")

        for file_path in self.path_array:
            ext = os.path.splitext(file_path)[1]
            if ext != ".txt":
                print("テキストファイル以外のものが含まれています。")
                exit()

            df = pd.read_table(
                file_path,
                header=None,
                sep=" ",
                names=("times", "data"),
                encoding="utf-8"
            )

            if self.mode == "2" or self.mode == "3":
                if len(df) < self.iterations[0]:
                    print("ずらす回数が、入力データ数より多いです。")
                    exit()

            df_array.append(df)

            bar.update(1)  # プログレスバーの更新

        self.df_array = df_array

    def make_directory(self):
        """
        出力するディレクトリを作成する。
        ディレクトリ名は、プログラムの実行時間に基づく。

        Raises
        ------
        出力ディレクトリが重複した場合。
        """

        dt_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )

        #日付をフォルダ名に整形
        year = str(dt_now.year)
        month = str(dt_now.month).zfill(2)
        day = str(dt_now.day).zfill(2)
        hour = str(dt_now.hour).zfill(2)
        minute = str(dt_now.minute).zfill(2)
        second = str(dt_now.second).zfill(2)
        dirname = year + month + day + "-" + hour + "." + minute + "." + second #フォルダ名を定義
        out_dir = os.path.dirname(__file__) + "/../out/" + dirname + "/" #生成フォルダのパス

        if os.path.isdir(out_dir):
            print("ディレクトリが既に存在しています。")
            exit()
        else:
            os.makedirs(out_dir) #フォルダを作成

        self.out_dir = out_dir

    def write_file(self, df, path, percentage=0, iteration=0):
        """
        計算結果を出力する。
        出力はindexの有無で、2種類存在する。
        """

        input_fname = re.split("/", path)[-1] # ファイルネームだけ取り出す
        ext = os.path.splitext(input_fname) # ファイル名と拡張子に分解

        if self.mode == "1":
            out_fname = ext[0] + "_" + str(int(percentage*100)) + ext[1]
            out_fname_noindex = ext[0] + "_" + str(int(percentage*100)) + "_noindex" + ext[1]

            out_path = self.out_dir + out_fname
            out_path_noindex = self.out_dir + out_fname_noindex
        elif self.mode == "2":
            out_fname = ext[0] + "_" + str(self.iterations[0]) + ext[1]
            out_fname_noindex = ext[0] + "_" + str(self.iterations[0]) + "_noindex" + ext[1]

            out_path = self.out_dir + out_fname
            out_path_noindex = self.out_dir + out_fname_noindex
        elif self.mode == "3":
            out_fname = ext[0] + "_iter" + str(iteration+1) + "_" + str(self.iterations[iteration]) + ext[1]
            out_fname_noindex = ext[0] + "_iter" + str(iteration+1) + "_" + str(self.iterations[iteration]) + "_noindex" + ext[1]

            out_path = self.out_dir + out_fname
            out_path_noindex = self.out_dir + out_fname_noindex

        df.to_csv(out_path, sep=" ", header=False, encoding="utf-8")
        df.to_csv(out_path_noindex, sep=" ", header=False, encoding="utf-8", index=False)

    def calc(self):
        """
        自己相関係数の計算を行う。
        """

        # プログレスバーの設定
        bar = tqdm(total=len(self.path_array))
        bar.set_description("calc_acf")

        for df, path in zip(self.df_array, self.path_array):
            df_data = pd.Series(df['data'], dtype='float') # 自己相関の計算のためにpd.Seriesに格納

            if self.mode == "1":
                iterations = len(df_data) # データ数の回数を計算の繰り返し回数とする

                for i in [i / 10 for i in range(5, 11)]: # 50%~100%で計算する
                    # deep copy
                    part_df = df_data.copy()
                    index = df.copy()

                    part_iterations = int(iterations * i) # 計算回数をint型で作成
                    part_df = part_df[:part_iterations] # dfの上からpart_iterations分だけ取り出す
                    acf = sm.tsa.stattools.acf(part_df, nlags=part_iterations, fft=True) # 自己相関の計算
                    index = index["times"][:part_iterations]*0.0002 # 出力用indexの作成準備
                    out_pd = pd.Series(acf, index=['{:.4f}'.format(i) for i in index]) # 出力用にデータをpdで成形
                    self.write_file(out_pd, path, percentage=i) # データの出力
            elif self.mode == "2":
                part_df = df_data.copy()
                index = df.copy()

                part_iterations = int(self.iterations[0])
                part_df = part_df[:part_iterations]
                acf = sm.tsa.stattools.acf(part_df, nlags=part_iterations, fft=True)
                index = index["times"][:part_iterations]*0.0002
                out_pd = pd.Series(acf, index=['{:.4f}'.format(i) for i in index])
                self.write_file(out_pd, path) 
            elif self.mode == "3":
                # deep copy(ずらした結果を再度使用するため、for文の外で)
                acf = df_data.copy()

                for i in range(self.CONTINUOUS):
                    index = df.copy()

                    part_iterations = int(self.iterations[i])
                    acf = sm.tsa.stattools.acf(acf, nlags=part_iterations, fft=True)
                    acf = acf[:part_iterations]
                    index = index["times"][:part_iterations]*0.0002
                    out_pd = pd.Series(acf, index=['{:.4f}'.format(i) for i in index])
                    self.write_file(out_pd, path, iteration=i)
            
            bar.update(1) # プログレスバーの更新

    def fit(self):
        """
        上記関数の実行。
        """

        self.read_file()
        self.make_directory()
        self.calc()

if __name__ == "__main__":
    calc_acf = calc_acf()
    calc_acf.fit()