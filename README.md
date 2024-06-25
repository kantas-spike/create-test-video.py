# create-test-video.py

テンプレートSVG画像をもとに、指定された時間分のフレーム画像を作成し、そのフレーム画像からテストビデオを作成します。
フレーム画像作成時、テンプレートSVG画像のフレーム番号用テキスト要素に自動的にフレーム番号を挿入します。

## 前提

本ツールは、作成したSVG画像をインプットとして、[FFmpeg](https://ffmpeg.org/)によりテストビデオを作成します。

そのため、SVG画像入力に対応するため、 `--enable-librsvg` オプションを付けてビルドした **FFmpeg** を使用する必要があります。

私の環境はmacOS のため、以下の `--enable-librsvg`オプションを有効にした [Homebrew](https://brew.sh/) 用Formula を用意し、
FFmpegをビルド・インストールしています。

- [kantas-spike/homebrew-ffmpeg-with-librsvg](https://github.com/kantas-spike/homebrew-ffmpeg-with-librsvg)

## 使い方

```shell
$ python create-test-video.py -h
usage: create-test-video.py [-h] --template_svg SVG_FILE [--output OUTPUT_FILE] [--fps FPS] [--duration DURATION] [--workdir WORKDIR] [--frameno_id FRAMENO_ID] [--ffmpeg FFMPEG_PATH]

テンプレートSVG画像をもとに、指定された時間分のフレーム画像を作成し、そのフレーム画像からテストビデオを作成します。フレーム画像作成時、テンプレートSVG画像のフレーム番号用テキスト要素に自動的にフレーム番号を挿入します。

options:
  -h, --help            show this help message and exit
  -t SVG_FILE, --template_svg SVG_FILE
                        テンプレートSVG画像ファイルのパス
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        作成するテストビデオのパス(デフォルト値: output.mp4)
  --fps FPS             作成するテストビデオのFPS(デフォルト値: 60)
  -d DURATION, --duration DURATION
                        作成するテストビデオの長さ[単位:秒] (デフォルト値: 1)
  --workdir WORKDIR     フレーム画像生成用の作業ディレクトリのパス。未指定時は一時ディレクトリを採用
  --frameno_id FRAMENO_ID
                        SVG内でフレーム番号が記載されたtext要素のID(デフォルト値: frame_no)
  --ffmpeg FFMPEG_PATH  ffmpegコマンドのパス(デフォルト値: /usr/local/bin/ffmpeg)
  -v, --verbose         詳細なログを出力します。
```

## 使用例

### 60FPS 3秒のテストビデオ

```shell
python create-test-video.py -t ./sample_template/red_inkscape.svg -o sample_output/red.mp4 -d 3
```

[赤背景 180フレーム](./sample_output/red.mp4)

## テンプレートの作成方法

[サンプルのテンプレート](./sample_template/)は、[Inkscape - Draw Freely. | Inkscape](https://inkscape.org/)で作成しています。(Inkscape以外でも可能と思います。)

フレーム番号を自動挿入したい場所にText要素を配置し、Text要素の**id**として、**frame_no** を指定します。

**Inkscape** 利用時の、Text要素にIDを設定する方法は以下になります。

1. Text要素を右クリックし、**Object Properties** を選択
2. 表示される **Object Properties** ダイアログの **ID フィールド** に **frame_no** を設定
3. **Object Properties** ダイアログの **Set** ボタンをクリック
4. **Object Properties** ダイアログを閉じる

### 本ツールでの frame_no の更新ルール

**Inkscape** でテンプレートを作成した場合、**\<text/>** 要素の子要素の **\<tspan/>** に実際の文字が設定されます。

そのため、本ツールでは、以下のルールで **frame_no** を更新します。

1. テンプレートから **ID: frame_no** となる **\<text/>** 要素を検索
2. if **\<text/>** 要素がない:
   1. 何もしない
3. else:
   1. if **\<text/>** 要素の子要素に **\<tspan/>** がある
      1. 最初の **\<tspan/>** にフレーム番号を設定する
   2. else
      1. **\<text/>** 要素にフレーム番号を設定する

## メモ

- [xml.dom.minidom — Min... # xml.dom.minidom — Minimal DOM implementation — Python 3.12.4 documentation](https://docs.python.org/3/library/xml.dom.minidom.html#module-xml.dom.minidom)
- [XML DOM - Change Node Values](https://www.w3schools.com/xml/dom_nodes_set.asp)
- [homebrew-core/Formula/f/ffmpeg.rb at 34548975576ea25f2fb6fbd0b3d034f1edad2184 · Homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core/blob/34548975576ea25f2fb6fbd0b3d034f1edad2184/Formula/f/ffmpeg.rb)
- [homebrew-ffmpeg/homebrew-ffmpeg: A homebrew tap for an ffmpeg formula with lots of options](https://github.com/homebrew-ffmpeg/homebrew-ffmpeg)
