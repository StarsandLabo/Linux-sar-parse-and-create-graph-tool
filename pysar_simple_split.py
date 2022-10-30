import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from traceback import format_exc
from collections import deque
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

dir_save_result = Path('./').joinpath('tsv')

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
    
    HEADERS_PROCESSED = set( [ RECORDING_TIME.sub("", v.group()).lstrip('\n\n').replace(" ","").rstrip("\n") for v in re.finditer(r'\n\n(?!Average:|Summary:).*$', RAW_CONTENT, flags=re.MULTILINE)] )
    HEADERS_HASHTABLE = {}
    
    for line in [ RECORDING_TIME.sub("", nominated_header.group()).lstrip('\n\n').rstrip("\n") for nominated_header in re.finditer(r'\n\n(?!Average:|Summary:).*$', RAW_CONTENT, flags=re.MULTILINE) ]:
        HEADERS_HASHTABLE[line.replace(" ","")] = list( [ v for v in line.split(" ") if len(v) > 0 ])# set してしまうと後ろの処理でもとの表示通りに並べ替えるのが非常に面倒になってしまう。TIMEをここで入れると変数名と内容に若干の食い違いのある印象となってしまう。
    # 悪下図 4

    #print( RAW_CONTENT_SPLITTED[0:])
    #times = 4 if os.cpu_count() > 8 else 2
    times = int(RAW_CONTENT_SPLITTED.__len__()/4 )
    datas = [ RAW_CONTENT_SPLITTED[idx:idx+times] for idx in range(0, len(RAW_CONTENT_SPLITTED), times)]
    
    # ヘッダを用いたハッシュテーブルが望ましいが、分割したリストをループにかける場合、一番最初のグループはヘッダが不明な可能性が高いため、
    # ヘッダが判明するものはもちろん別のリストとして格納するが、ヘッダの不明なグループを前のグループの末尾に連結する。
    # その後各配列に分散した同じグループを上から順番に結合していく
    # その際かその後にヘッダの名前は改める（どのタイミングで実施するかは未定）
    
    with ThreadPoolExecutor() as executor:
        def TrimTimeAndWhitespaceAndNewlinechar(x):
            return "".join( x.split(" ")[1:] ).rstrip("\n")
        
        def DisplayingConcurrently(input_lines):
            groups = []
            group = []
            for line in input_lines:
                
                if TrimTimeAndWhitespaceAndNewlinechar(line) in HEADERS_PROCESSED:
                    groups.append(group)
                    (group := []).append(TrimTimeAndWhitespaceAndNewlinechar(line))
                else:
                    if  line.__len__() > 0 and \
                        'Average:' not in line and\
                        'Summary:' not in line:
                            group.append(line)
            groups.append(group)
            return groups
        
        splitted_datas_with_header = {}
        for i, d in enumerate([ [i, executor.submit(DisplayingConcurrently, data)] for i, data in enumerate(datas)]) :
            splitted_datas_with_header[d[0]] = d[1].result()

    # 初回グループを除くすべてのグループの一番最初のグループを、前のIDの一番うしろの配列とつなぐ。
    for i in range(1, len(datas)):
        #? testcodes Check array statement.
        #? input(f"{Color.CYAN}{splitted_datas_with_header[i-1][-1]}{Color.END}")
        #? input(f"{Color.YELLOW}{splitted_datas_with_header[i][0]}{Color.END}")
        splitted_datas_with_header[i-1][-1] = splitted_datas_with_header[i-1][-1] + splitted_datas_with_header[i].pop(0)
        #? input(f"{Color.RED}{splitted_datas_with_header[i-1][-1]}{Color.END}")
        #? input(f"{Color.GREEN}{splitted_datas_with_header[i][0]}{Color.END}")
    
    # 各配列に散っているヘッダ毎の内容を結合する。
    # ヘッダ毎の連想配列を用意する。
    
    JOINTED_RESULTS = {}
    
    for header in HEADERS_PROCESSED:
        JOINTED_RESULTS[header] = []
    
    # ここで連結する際、splitted_datas_with_header[i]の中には同じヘッダーを持つ秒違いの情報があり、
    # それをまとめる必要がある。
    # headerをキーにしてrecord[0] == headerの時はappendする。
    headers_len = HEADERS_PROCESSED.__len__()
    for i in range(datas.__len__()):
        for header in HEADERS_PROCESSED:
            for record in splitted_datas_with_header[i]:
                if header in record:
                    JOINTED_RESULTS[header] += record[1:]
                    continue
            print( "\033[2K","[ Splitting by Content ] ", i," / ",headers_len, end="\r", sep="" )    

    for i, header in enumerate(list(HEADERS_PROCESSED), start=1):
        l = []
        HEADERS_HASHTABLE[header].insert(0,'TIME')
        l.append( "\t".join( HEADERS_HASHTABLE[header] ) )
        
        for v in JOINTED_RESULTS[header]:
            l.append( "\t".join( [x for x in v.split(" ") if x.__len__() > 0] ) )

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

        if no_file_save == False:
            dir_save_result.mkdir(exist_ok=True,parents=True)            
            with open(f'{dir_save_result.joinpath(f"sar-{filename_prefix}")}.tsv', mode='w+', encoding='utf-8') as fp:
                fp.write('\n'.join(l))
            print(f"{COLOR.CYAN}TSV Result:{COLOR.END}", Path(fp.name).resolve().as_posix()) if no_output_terminal == False else None
        else:
            print('\n'.join(l)) if no_output_terminal == False else None
if __name__ == '__main__':
    main()