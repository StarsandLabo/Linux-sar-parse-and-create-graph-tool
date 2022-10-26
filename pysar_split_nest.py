from pathlib import Path
import json
import re
from concurrent.futures import ThreadPoolExecutor
import argparse

dir_save_result = Path('./').joinpath('json')

def main():
    ORANGE,END,GREEN = "\033[38;5:172m","\033[0m",'\033[32m'
    parser = argparse.ArgumentParser(description='pysar-split-nest ver S.2022.10.23', exit_on_error=True, add_help=True)
    parser.add_argument('-i','--inputfile', nargs=1, help=f'Filepath by splitted sar result file', type=Path)
    parser.add_argument('-s','--silent',help='no output terminal', action='store_true')
    parser.add_argument('-d','--display-only',help='result no save. display only', action='store_true')
    parser.add_argument('-n','--no-indent',help='json indentation disable', action='store_true')

    inputfiles: Path = parser.parse_args().inputfile[0].resolve()
    no_output_terminal = parser.parse_args().silent
    no_file_save = parser.parse_args().display_only
    no_indent = parser.parse_args().no_indent

    def StoreMetrics(i_line, i_header, i_headers, i_key_object_stored_colmun_index):
        if (i_header == i_headers[i_key_object_stored_colmun_index]):
            return
        
        splitted_line, target_colmun = i_line.rstrip("\n").split("\t"), i_headers.index(i_header)
        return splitted_line[target_colmun]

    
    with open(
        file = inputfiles,
        mode = 'r',
        encoding='utf-8'
    ) as fp:
        RAW_CONTENT = fp.readlines()
    
    # 各CPUのIDなど、情報を取得したい主体が格納されている列番号。
    # 現状FILESYSTEMを除きすべて先頭に識別子が格納されていたのでこの値を取る。
    splitted_firstline = RAW_CONTENT[0].rstrip("\n").split("\t")
    key_object_stored_colmun_index = -1 if 'FILESYSTEM' in splitted_firstline else 1

    # 各CPUのIDなどを重複なく取得する集合
    DEVICE_ID_OR_DEVICEFILE_NAME = set( [ line.split("\t")[key_object_stored_colmun_index].rstrip("\n") for line in RAW_CONTENT[1:] ] )

    # 各CPUのIDなど毎にデータ種別毎に値を格納
    HEADERS = RAW_CONTENT[0].rstrip("\n").split("\t")

    # メトリクスごとの辞書を作成
    # グラフ描画の際に不要なのでCPU番号やFilesystem名などは不要
    MASTER_TABLE = {}
    for HEADER in HEADERS:
        if (HEADER == HEADERS[key_object_stored_colmun_index]): continue
        MASTER_TABLE[HEADER] = {}
        for DEVICE_ID in DEVICE_ID_OR_DEVICEFILE_NAME:#- CPUのIDなど、キーとなる情報
            MASTER_TABLE[HEADER][DEVICE_ID] = [] # CPUID等毎に辞書を作成する。データをわかりやすくしたい

    # 取得済みの行をループし、識別子の列に該当する辞書名に値を入れていく。
    content_lines = RAW_CONTENT[1:].__len__()
    for i, LINE in enumerate(RAW_CONTENT[1:]):
        for HEADER in HEADERS:
            if (HEADER == HEADERS[key_object_stored_colmun_index]): continue
            with ThreadPoolExecutor() as executor:
                key_selector = LINE.split("\t")[key_object_stored_colmun_index].rstrip("\n")
                MASTER_TABLE[HEADER][key_selector].append(
                    executor.submit(StoreMetrics, LINE, HEADER, HEADERS, key_object_stored_colmun_index).result()
                )
                print( "\033[2K","[ Splitting Content ] ",f"{inputfiles} ", i," / ", content_lines, end="\r", sep="" )

    # ファイルに書き出すセクション
    if no_file_save == False:
        dir_save_result.mkdir(exist_ok=True,parents=True)

        with open(f'{dir_save_result.joinpath(f"{Path(inputfiles).stem}")}.json', mode='w+', encoding='utf-8') as fp:
            if no_indent == False:
                fp.write(json.dumps(MASTER_TABLE, indent=4, ensure_ascii=False))
            else:
                fp.write(json.dumps(MASTER_TABLE))
                
            print(f'\033[2K{GREEN}JSON Result:{END}', Path(fp.name).resolve().as_posix()) if no_output_terminal == False else None
    else:
        if no_output_terminal == False:
            print(MASTER_TABLE) if no_indent == True else print(json.dumps(MASTER_TABLE, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()