# Autocorrelation-Analysis
時系列データに対して、自己相関係数を計算する。

## 実行環境
- Python Version
  - Python 3.6.3 :: Anaconda, Inc.

- Library Version
  - requirements.txtを参照のこと

pipをインストールしている場合は、
```
$ pip install -r requirements.txt
```

## 実行上の注意事項
### 実行方法
プログラムの実行は、以下のコマンドで行う。  
実行する際には、プログラムまでのパスに注意する。
```
$ python3 main.py
```

### 入力
分析したいファイルへのパスの入力では、絶対パス・相対パス、どちらでも可能。
```
絶対パス: /Users/username/Autocorrelation-Analysis/data/sample.txt
相対パス: ./data/sample.txt
```

複数ファイルの入力をしたい場合は、以下のように入力する。  
拡張子をしていすれば、その拡張子のファイルのみ読み込む。指定がない場合は、ディレクトリ下のファイルをすべて読み込む。  
こちらも絶対パス・相対パス、どちらでも可能。
```
絶対パス: /Users/username/Autocorrelation-Analysis/data/*.txt
相対パス: ./data/*.txt
```

計算モードでは、ずらす回数の指定ができる。  
3000回(データ数の回数)ずらしたい場合は`1`を、任意の回数をずらしたい場合は`2`を入力する。

### 出力
出力は、`out`ディレクトリに行う。  
出力ディレクトリ名は、プログラムの実行時間になる。  

計算モード`1`の場合は、1つの入力ファイルにつき、12個のファイルが出力される。(データ数の50%~100%だけずらしたファイル(6個) × インデックスの有無(2個))  
計算モード`2`の場合は、1つの入力ファイルにつき、2個のファイルが出力される。(インデックスの有無(2個))

## License
"Autocorrelation-Analysis" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).