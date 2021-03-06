# ARDJ で使用した文編集のツール文編集ツール
突然変異を模した文の変種生成スクリプト

基本的には標準入力で文を受け付けて，標準出力に返す．
入力には1行1文を想定．UTF-8エンコードが動作の条件．
入力文に “:” がある場合，それまでの部分文字列は header として扱う．従って，
次のような行があった場合，

abc-123:例えば，この文は文です．
abc-124:例えば，この文も文です．

処理 f の結果は，

abc-123:f(例えば，この文は文です．)
abc-124:f(例えば，この文も文です．)

となる．

% で始まる行はコメント行として処理しない．--commentchar X でコメント行の識別記号をXに変更可能．

## Python のバージョン

Python 3.x で動作する (Python 2.7 では動作しない)．

## 必要な Python パッケージ
- gensim [2.x以降]
- CaboCha
- MeCab

## 必要な word2vec データ
動作には gensim の word2vec が参照する単語類似度データが必要．データの獲得法は次の2つ:

1. 構築済みの [jawiki.pos.bin](https://www.dropbox.com/s/h9hy87hjqn5v3xj/jawiki.pos.bin?dl=1) データ (約200MB) を入手する．
2. 自作する: misc にあるスクリプトを使って Wikipedia の dump から構築する．
方法は misc/README.md を参照の事．モデルファイルの名称は jawiki.pos.bin とする．

なお，国立国語研究所が提供している [日本語書き言葉均衡コーパス (BCCWJ)](http://pj.ninjal.ac.jp/corpus_center/bccwj/) をライセンスを受けて利用している方には私たちが構築した単語類似度データの提供が可能．問い合わせ先は japanese#acceptability#ratings&gmail#com (# を . に，& を @ に変換)．

## 実行法の基本

    ```
    cat TEXT | ./changewords.py --pos 1 # 動詞をランダムに一つ選んで置換
    ```

か

    ```
    cat TEXT | python3 changewords.py --pos 1 # 動詞をランダムに一つ選んで置換
    ```

のいずれかの方法で実行．他のスクリプトも同様．

複数のバージョンの Python を使っている場合，CaboCha パッケージをインストール済みの Python3 を絶対パスで指定するのが確実．

## changewords.py

(突然変異とのアナロジーで) 入力文中の単語 1語をランダムに別の語に置き換える．
どの品詞の語を変異するかは --pos で指定する:
- 名詞 (形容動詞の語幹を含む) のみを変換させるには --pos 0 (形容動詞を除外したい場合には --exclude_Pred を追加)
- 動詞 (助動詞は含まない) のみを変換させるには --pos 1 (サ変名詞を取り入れたい場合には --extend_V を追加)
- 形容詞のみを変換させるには --pos 2
- 副詞のみを変換させるには --pos 3 (形容詞を含めたい場合には --extend_Adv を追加)
- 格助詞のみを変換させるには --pos 4
- 形容動詞のみを変換させるには --pos 5
とする．

使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./changewords.py --pos 1 # 動詞をランダムに一つ選んで置換
    ```
    ```
    cat TEXT | ./changewords.py --pos 2 # 形容詞をランダムに一つ選んで置換
    ```

ただし格助詞の変更のみ，類似度を使わないで疑似的に頻度を反映したランダム変異としている．

- 単語の置換は1度に1個だけだが，--repeat n で処理を非再帰的に n回反復する．変異を再帰的に実行したい場合，--nested を追加．

使用例:

    ```
    cat TEXT | ./changewords.py --pos 2 --repeat 10 # 形容詞をランダムに一つ選んで置換する処理を10回繰り返す
    ```


    ```
    cat TEXT | ./changewords.py --pos 1 --repeat 10 --nested # 動詞をランダムに一つ選んで置換する処理を再帰的に10回繰り返す
    ```

- --silent で入力文の表示を禁止 (デフォールトでは入力文を [original] のタグつきで再生)．

- --show_similars で置換の候補を一覧．

- どの語に置き換えるかは Wikipedia (か BCCWJ) から学習して構築した word2vec のモデルから選ぶ．
モデルファイルは --bin で指定 (デフォールトは jawiki.pos.bi)．使用例 (入力文の指定されたテキストを TEXT とする)::

    ```
    cat TEXT | ./changewords.py --bin bccwj.pos.bin
    ```

10回探して該当するものが見つからなかった場合は諦める．この場合:
    ```
    # Atempt failed, making no mutation.
    ```

の警告が出る．--try_until n で試行回数を変更できる．

- 置換する語は類似度の上限 (--ub m) と下限 (--lb n) の間にある候補の中からランダムに選択する．
- lb と ub のデフォールト値はそれぞれ 0.0 と 1.0．従って，類似度が 0.0 から1.0 の範囲の候補で置換．

使用例:

    ```
    cat TEXT | ./changewords.py --lb 0.3
    ```
    ```
    cat TEXT | ./changewords.py --ub 0.7
    ```
    ```
    cat TEXT | ./changewords.py --ub 0.7 --lb 0.5
    ```

- --no_hiragana でひらがなのみの語への置換を禁止 (意味の横滑りを抑制に効果がある)．

- 名詞の変異に関してのみ，[日本語 WordNet (WordNet-Ja)](http://compling.hss.ntu.edu.sg/wnja/index.en.html) を使って，同一 synset 内の別の語句に置換する処理を実装 (--use_WNJ オプション)．実行では
[ダウンロードページ](http://compling.hss.ntu.edu.sg/wnja/jpn/downloads.html) から SQLite3 データベースを入手し，'wnjpn.db' の名で changewords.py と同じディレクトリーに置く．
ただ，被覆率が (圧倒的に) 低く，変異がほとんど起きないので，期待している程使えない．

## swapphrases.py

文中の文節 (≒phrase) の順番を変え，かき混ぜ (scrambling) の効果をシミュレートする (文節の境界は CaboCha の判定による)．
最後の文節 (≒述語) に直接係っているものだけが入れ替えの対象となる．

入れ替え対象の節に係っている節はその節と一緒に移動する (なので，連体修飾など中の要素の順番は入れ替わらない) が --aggressive オプションで，分節へのまとめ上げを抑制 (これで相当に破壊的なかき混ぜを実行できる)．

- --repeat n でかき混ぜを n 回実行 (default 1)
- --degree d で一回辺りのかき混ぜ度 d を指定 (default 1)
- --start i, --end j オプションで入れ替えの範囲を i番目の分節から j番目の文節の範囲に限定する．使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./swapphrases.py --start 2 # 最初の文節 (≒phrase) をかき混ぜの対象から除く
    ```



## reducephrases.py

文中の節を段階的に再帰的に削除する．節の境界は CaboCha の判定によるもの．
最後の節に直接係っているものだけが削除の対象となる．

- --lb n で削除で残る文節数の下限 nを指定．使用例 (入力文の指定されたテキストを TEXT とする):

    ```
    cat TEXT | ./reducephrases.py --lb 3 # 少なくとも3つの文節を残す
    ```

- --exclude_wa で「は」で終わる節を削除対象から除外．

## 全体に共通する注意 (改良の必要な点)．

現状では，幾つかの処理が未実装．

- 入力に複文が来ることは想定していない (が，動作は一応する)．
- 1行に複数の文がある入力は全体で1文として扱う．
- 動詞を変換した場合に活用形がずれる場合があるが，正しい処理は未実装．文法性を保証したいなら，sed などを使った後処理が必要．
- 真性の名詞と UniDic で名詞扱いされている形容動詞語幹との区別ができていない [--exclude-PredN が少し動作を改善]．
- その他の幾つかのエラー処理は未実装．

## Copyrights

Copyright (C) 2016-2020 Kow Kuroda. All rights reserved.

スクリプトのライセンスは Apache License, Version 2.0 です．
