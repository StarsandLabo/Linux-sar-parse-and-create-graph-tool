from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from pathlib import Path
import json
from threading import Thread

import html_template
import re
from pprint import pprint
import argparse

def main():
    ORANGE,END = "\033[38;5:172m","\033[0m"
    parser = argparse.ArgumentParser(description='pysar-split-nest ver S.2022.10.23', exit_on_error=True, add_help=True)
    parser.add_argument('-i','--inputfile', nargs=1, help=f'Filepath by splitted sar result file', type=Path)
    parser.add_argument('-s','--silent',help='no output terminal', action='store_true')

    inputfile: Path = parser.parse_args().inputfile[0].resolve()
    no_output_terminal = parser.parse_args().silent

    #? for test####################
    #input_nested_file = Path('./').glob('./**/sar-u-ALL.json').__next__().resolve().as_posix()
    #input_no_nested_file = Path('./').glob('./**/sar-B.json').__next__().resolve().as_posix()
    #inputfile = input_nested_file
    #inputfile = input_no_nested_file
    #? ############################
    
    with open(inputfile, mode='r', encoding='utf-8') as fp:
        RAW_JSON = json.load(fp)

    # ネストされているかの判断は、取り込んだJSONファイルの2段めが配列なのかオブジェクトなのかで判別する。
    #? htmlのタイトル...ネストされている場合はTIMEや%USRといった項目から取得する。
    isNested = True if RAW_JSON[RAW_JSON.__iter__().__next__()].__class__ == dict else False

    def CreateDataset(input_records: dict):
        internal_datasets = []
        DATASET = html_template.Dataset()

        for key, value in input_records.items():
            if key == 'TIME': continue
            
            DATASET.label = key
            DATASET.data = value
            DATASET.pointRadius = 3
            DATASET.borderColor = html_template.GetLineColorsRandom()
            
            internal_datasets.append(DATASET.CreateDataset())
        #print(internal_datasets)
        return internal_datasets
    
    def CreateHTML(input_dataset, input_title):
        base_chart_part = html_template.CHART_PART
        base_html_format = html_template.BASE_HTML
        
        tag_matching_details = re.compile(r'\<details\>.+\</details\>',re.MULTILINE+re.DOTALL)
        processed_chart_part = \
            tag_matching_details.sub('',base_chart_part) \
            .replace('!!!labels!!!', labels.__str__()) \
            .replace('!!!datasets!!!', json.dumps(input_dataset)) \
            .replace('!!!targetmetrics!!!', input_title)
        
        processed_base_html = base_html_format \
            .replace('!!!title!!!',input_title) \
            .replace('!!!ChartPlaceholder!!!', processed_chart_part)

        #ファイルに出力するセクション    
        dir_save_result = Path('./').joinpath('result','html',f'{Path(inputfile).stem}')
        dir_save_result.mkdir(exist_ok=True,parents=True)
        validated_input_title = "".join( [ v for v in map(lambda S: S if re.match(r'[a-z,A-Z,0-9]',S) else "_", input_title)] )
        with open(f'{dir_save_result.joinpath(f"{validated_input_title}.html")}', mode='w+', encoding='utf-8') as fp:
            fp.write(processed_base_html)
                
            print(f'{ORANGE}HTML Result:{END}', Path(fp.name).resolve().as_posix()) if no_output_terminal == False else None
            #print('microsoft-edge ', Path(fp.name).resolve().as_posix()) if no_output_terminal == False else None
            #from subprocess import Popen
            #Popen(["microsoft-edge", Path(fp.name).resolve().as_posix()])
        
    if isNested == True:
        labels = [""] * RAW_JSON['TIME'][RAW_JSON['TIME'].__iter__().__next__()].__len__()
        DATASETS = {}
        for k in RAW_JSON.keys():
            if k == 'TIME': continue
            # ここでExecutor呼びたい
            with ThreadPoolExecutor() as executor:
                DATASETS[k]=executor.submit(CreateDataset, RAW_JSON[k]).result()
                #executor.submit( CreateHTML, CreateDataset(RAW_JSON[k]), k)
            
        for k in RAW_JSON.keys():
            if k == 'TIME': continue
            with ThreadPoolExecutor() as executor:
                executor.submit( CreateHTML,DATASETS[k], Path(inputfile).stem + " " + k)
    else:
        labels = [""] * RAW_JSON['TIME'].__len__()
        DATASETS = CreateDataset(input_records=RAW_JSON)
        CreateHTML(DATASETS, Path(inputfile).stem)
        #print(json.dumps(DATASETS)); quit()
    # html テンプレートの全体的な整形とあたいのはめ込み

if __name__ == '__main__':
    main()