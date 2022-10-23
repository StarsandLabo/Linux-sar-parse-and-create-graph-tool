# Linux-sar-parse-and-create-graph-tool

# Try it anyway.

```shell
# Python3.10 or later?
git clone https://github.com/StarsandLabo/Linux-sar-parse-and-create-graph-tool.git
cd ./Linux-sar-parse-and-create-graph-tool

python ./pysar-2.py --inputfile <sar-result-file>
```

# Overview

Sarコマンドの出力をそれぞれText,Json,HTML(Graph)で出力します。  
Pythonはおそらく3.10(3.8?)以上が必要です。  

SarコマンドはKsarと同様に `env LANG=C sar -A` を想定していますが、単体の出力でも適用できるかもしれません。  
分類できなかった内容はunknownの名前が付きます。

Output the output of the Sar command in Text, Json, HTML (Graph) respectively.  
Python probably requires 3.10(3.8?) or higher.  

The Sar command expects `env LANG=C sar -A` like Ksar, but it may also apply to single output.  
Content that could not be classified is named unknown.  

# Youtube
[![video](https://user-images.githubusercontent.com/84756197/173222007-3aefa245-4c0e-45e6-9855-91f0e3be89ed.png)](https://youtu.be/5BfkWg0g4zc)




# Results are below

```shell
./result/
├── html # Graphs On HTML
│   ├── sar-B
│   ├── sar-F
│   ├── sar-H
::
│   ├── sar-v
│   └── sar-w
├── json # JSON Results
└── text # Text Results

40 directories
```
