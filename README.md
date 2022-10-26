# Linux-sar-parse-and-create-graph-tool

# Video
[![video](https://user-images.githubusercontent.com/63001062/197391157-33e9250e-43ec-494e-b13c-3288dd7ad400.png)](https://youtu.be/5BfkWg0g4zc)

# Try it anyway.

```shell
# Python3.10 or later?
git clone https://github.com/StarsandLabo/Linux-sar-parse-and-create-graph-tool.git
cd ./Linux-sar-parse-and-create-graph-tool

python ./pysar-2.py --inputfile <sar-result-file>
```

# Overview

Sarコマンドの出力をそれぞれText(tsv),Json,グラフ(HTML Chart.js Graph)で出力します。  
Pythonはおそらく3.10(3.8?)以上が必要です。  

SarコマンドはKsarと同様に `env LANG=C sar -A` を想定していますが、単体の出力でも適用できるかもしれません。  
分類できなかった内容はunknownの名前が付きます。

Output the output of the Sar command in TSV, Json, HTML (Graph) respectively.  
Python probably requires 3.10(3.8?) or higher.  

The Sar command expects `env LANG=C sar -A` like Ksar, but it may also apply to single output.  
Content that could not be classified is named unknown.  

# Results are below

```shell
./result/<Start Processing Time>
├── html # Graphs On HTML
│   ├── sar-B
│   ├── sar-F
│   ├── sar-H
::
│   ├── sar-v
│   └── sar-w
├── json # JSON Results
└── tsv # TSV Results

40 directories
```

# Other

あくまで練習材料として良いなと思ったのが作成の動機です
+ 1つのファイルに雑多にいろいろな情報が詰め込まれているものをパースする
+ HTMLを用いたグラフ化（HTMLなので相手にわざわざKsar入れてもらう必要がない）  

すごく良く作り込んだ。というわけではないので使いづらいところはすみません。  

もともとはグラフだけ出力するように作ろうと考えていたのですが、うまくできなかったため  
text(tsv) > json > htmlと順を追って分割せざる得ませんでした。  

<details><summary>例えばグラフはいらないけどJSONはほしい。といった場合は</summary>

`python pysar_simple_split.py --inputfile <sar-result-file>`　でsar -Aコマンドの実行結果をテキストに分割します。  
その後は結果がネストされている場合は `python pysar_split_nest.py --inputfile <target-text>` とし、  
ネストされていない場合は `python pysar_split_standard.py --inputfile <target-text>` とすることでJSONを取得できます。

ネストされてるとかされてないとかよくわからないかもしれませんが、たとえばCPU使用率(sar -u ALL)などはCPUコア単位で出力がされるため、  
コア単位で使用率の推移を見る場合は多少加工が必要になってしまい、そういう出力がされているものをネストされているもの。としています。  
反対にメモリ(sar -r)は取得対象がメモリ総量（メモリスロット毎になにか情報が取得されるわけではない）なのでこういったものはネストされていない。となります。  

テキストだけExcelに取り込んでExcelのグラフを作る。というのもgoodなのですが、ほぼ生のSarで達成できるのでした…

</details>

正直面倒だと思うので全部出力が終わってから不要なディレクトリだけ削除してください。

# Changelog
+ 2022-10-26
  + Create directory named by processing start time because avoid overwrite result.
+ 2022-10-23
  + Release
