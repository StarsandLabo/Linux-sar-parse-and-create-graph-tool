
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from traceback import format_exc
from collections import deque
from time import perf_counter
import argparse

class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'

dir_save_result = Path('./').joinpath('result','tsv')

def main():
    COLOR = Color()
    ORANGE,END = "\033[38;5:172m","\033[0m"
    parser = argparse.ArgumentParser(description='pysar-split-nest ver S.2022.10.23', exit_on_error=True, add_help=True)
    parser.add_argument('-i','--inputfile', nargs=1, help=f'Filepath by splitted sar result file', type=Path)
    parser.add_argument('-s','--silent',help='no output terminal', action='store_true')
    parser.add_argument('-d','--display-only',help='result no save. display only', action='store_true')

    inputfile: Path = parser.parse_args().inputfile[0].resolve()
    no_output_terminal = parser.parse_args().silent
    no_file_save = parser.parse_args().display_only
    #inputfile = Path('sar-A3.txt')
    
    with open(inputfile.resolve().as_posix(), mode='r', encoding='utf-8')as fp: RAW_CONTENT = fp.read()

    # 時間ごとにグルーピングする？
    #  ->時間はタイトルを記録した時点とメトリクスを取得した時点でずれていることがあり、信用できない。
        # multilineの正規表現で\n\n~と続く跡の値が項目名。
    # 時間（ポイントする数）がどのくらいあるかは確認する
    
    RECORDING_TIME = re.compile(r'((\d+.?).?:?){3}')
    
    RAW_CONTENT_SPLITTED = RAW_CONTENT.split("\n")
    for line in RAW_CONTENT_SPLITTED:
        try:
            sar_exec_times_count_key = re.search(r'^((\d+.?).?:?){3}.*$', line).group()
            break
        except:
            continue
    sar_exec_times_count_key = RECORDING_TIME.sub("",sar_exec_times_count_key)
    RECORD_COUNT = ([ _ for _ in RAW_CONTENT_SPLITTED if ( (sar_exec_times_count_key in _) and not (re.search(r'^[a-zA-Z]', _[0])) ) ]).__len__()
    
    HEADERS = set( [  RECORDING_TIME.sub("", v.group()).lstrip('\n\n') for v in re.finditer(r'\n\n(?!Average:|Summary:).*$', RAW_CONTENT, flags=re.MULTILINE)] )

    # %などの文字はファイル名に使いづらいので１６進数に変換する用のライン
    #[[ print(x,end="") for x in map(lambda x: hex(ord(x)) if not re.match(r'[a-zA-Z,\t]', x ) else x, re.sub(r'\s+',"\t",v) )] for v in HEADERS]
    
    def LineAppend(header: str):
        target_content, skipped_content_raw = [],""
        
        for line in RAW_CONTENT_SPLITTED:
            #if header ==  RECORDING_TIME.sub("",line): print(line, header,sep="\n"); input()
            try:
                if ('Average:' in line) or ('Summary:' in line): raise ValueError()
            except ValueError:
                skipped_content_raw += line+"\n"; continue
            
            if header in line:
                if header ==  RECORDING_TIME.sub("",line):
                    #print(header,RECORDING_TIME.sub("",line),sep="\n")
                    #input()
                    catchflg = True
                    continue
            elif  RECORDING_TIME.sub("",line) in HEADERS:
                catchflg = False
                continue
            else:
                pass
            
            try:
                if catchflg == True: target_content.append(line)
                """
                if catchflg == True: print(line, f"\033[45;5m'{catchflg}'\033[m")
                if catchflg == True: input()
                """
            except:
                continue
        return target_content, skipped_content_raw
        
    RAW_BY_CONTENT,skipped_content = {},{}
    headers_len = HEADERS.__len__()
    for i, HEADER in enumerate(HEADERS,start=1):
        with ThreadPoolExecutor() as executor_create_by_content:
            RAW_BY_CONTENT[HEADER],skipped_content[HEADER] = executor_create_by_content.submit(LineAppend, HEADER).result()
            print( "\033[2K","[ Splitting by Content ] ", i," / ",headers_len, end="\r", sep="" )

    for i, header in enumerate(list(HEADERS), start=1):
        match header:
            case x if 'pgpgin/s'  in x : filename_prefix = 'B'
            case x if 'bread/s'   in x : filename_prefix = 'b'
            case x if 'aqu-sz'    in x : filename_prefix = 'd'
            case x if 'FILESYSTEM'in x : filename_prefix = 'F'
            case x if 'kbhugfree' in x : filename_prefix = 'H'
            case x if 'INTR'      in x : filename_prefix = 'I'
            case x if 'runq-sz'   in x : filename_prefix = 'q'
            case x if 'kbmemfree' in x : filename_prefix = 'r'
            case x if 'kbswpfree' in x : filename_prefix = 'S'
            case x if r'%usr'     in x : filename_prefix = 'u-ALL'
            case x if 'dentunusd' in x : filename_prefix = 'v'
            case x if 'pswpin/s'  in x : filename_prefix = 'W'
            case x if 'cswch'     in x : filename_prefix = 'w'
            
            #? -m options
            case x if 'MHz'       in x and      'wghMHz' in x : filename_prefix = 'm-FREQ'
            case x if 'MHz'       in x and not  'wghMHz' in x : filename_prefix = 'm-CPU'
            case x if 'FAN'       in x : filename_prefix = 'm-FAN'
            case x if 'inV'       in x : filename_prefix = 'm-IN'
            case x if 'TEMP'      in x : filename_prefix = 'm-TEMP'
            case x if 'idvendor'  in x : filename_prefix = 'm-USB'
            
            #? -n options
            case x if 'rxpck/s'   in x : filename_prefix = 'n-DEV'
            case x if 'rxerr/s'   in x : filename_prefix = 'n-EDEV'
            case x if 'getatt/s'  in x : filename_prefix = 'n-NFS'
            case x if 'badcall/s' in x : filename_prefix = 'n-NFSD'
            case x if 'totsck'    in x : filename_prefix = 'n-SOCK'
            case x if 'irec/s'    in x : filename_prefix = 'n-IP'
            case x if 'ihdrerr/s' in x : filename_prefix = 'n-EIP'
            case x if 'itmr'      in x : filename_prefix = 'n-ICMP'
            case x if 'idstunr'   in x : filename_prefix = 'n-EICMP'
            case x if 'active/s'  in x : filename_prefix = 'n-TCP'
            case x if 'ihdrerr/s' in x : filename_prefix = 'n-ETCP'
            case x if 'odgm/s'    in x : filename_prefix = 'n-UDP'
            case x if 'tcp6sck'   in x : filename_prefix = 'n-SOCK6'
            case x if 'irec6/s'   in x : filename_prefix = 'n-IP6'
            case x if 'ihdrer6/s' in x : filename_prefix = 'n-EIP6'
            case x if 'imsg6/s'   in x : filename_prefix = 'n-ICMP6'
            case x if 'ierr6/s'   in x : filename_prefix = 'n-EICMP6'
            case x if 'idgm6/s'   in x : filename_prefix = 'n-UDP6'
            case x if 'dropd/s'   in x : filename_prefix = 'n-SOFT'
            
            case _: filename_prefix = f'unknown{i}'

        (single_element := []).append( 'TIME' + "\t".join( re.sub(r'\s+','\t', (" " + header) ).split("\t") ) )
        [ single_element.append( re.sub(r'\s+|\t+','\t', line) ) for line in RAW_BY_CONTENT[header] if line.__len__() > 1 ]

        if no_file_save == False:
            dir_save_result.mkdir(exist_ok=True,parents=True)            
            with open(f'{dir_save_result.joinpath(f"sar-{filename_prefix}")}.tsv', mode='w+', encoding='utf-8') as fp:
                fp.write('\n'.join(single_element))
            print(f"{COLOR.CYAN}Text Result:{COLOR.END}", Path(fp.name).resolve().as_posix()) if no_output_terminal == False else None
        else:
            print('\n'.join(single_element)) if no_output_terminal == False else None
if __name__ == '__main__':
    main()
