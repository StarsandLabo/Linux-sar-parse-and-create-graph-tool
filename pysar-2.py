from pathlib import Path
import argparse
import subprocess
import os
from pysar_simple_split import dir_save_result as TEXT_SAVE_DIR
from pysar_split_standard import dir_save_result as JSON_SAVE_DIR
from pysar_split_nest import dir_save_result as JSON_SAVE_DIR
from concurrent.futures import ThreadPoolExecutor

HTML_SAVE_DIR = Path('./').joinpath('result','html')



def main():
    parser = argparse.ArgumentParser(description='pysar-split-nest ver S.2022.10.23', exit_on_error=True, add_help=True)
    parser.add_argument('-i','--inputfile', nargs=1, help=f'Filepath by splitted sar result file', type=Path)
    """
    parser.add_argument('-j','--json',help='Create JSONfile', action='store_true')
    parser.add_argument('-t','--text',help='Create textfiles.', action='store_true')
    parser.add_argument('-H','--html',help='Create Graph on HTML', action='store_true')
    """

    inputfile = parser.parse_args().inputfile[0].resolve().as_posix()
    """
    create_text = parser.parse_args().text
    create_json = parser.parse_args().json
    create_html = parser.parse_args().html
    """
    
    def ExecCommandLineByOS(input_commandline: list):
        if not os.name == 'nt':
            subprocess.run( input_commandline, shell=False)
        else:
            subprocess.run( input_commandline, shell=True)
            
    #- Create plain texts
    SPLIT_SAR_MASTERFILE_TOOL_PATH = Path('./').glob('**/**/pysar_simple_split.py').__iter__().__next__().resolve()
    exec_command_line = ["python",f"{SPLIT_SAR_MASTERFILE_TOOL_PATH}","--inputfile", inputfile]
    ExecCommandLineByOS(exec_command_line)

    #- Split Json files
    #? ネストかどうかの判断をして適切なスクリプトに引数を渡す。
    # ディレクトリ配下のアイテムをすべて取得して最初の1行を見て判別する。
    textfile_paths = [ v.resolve() for v in TEXT_SAVE_DIR.glob('./*.txt') ]
    nested_headers = [ set([v for v in l if v.__len__() > 1]) for l in map(lambda x: x.split(" "),[
            'MBfsfree  MBfsused   %fsused  %ufsused     Ifree     Iused    %Iused FILESYSTEM',
            'CPU    wghMHz',
            'IN       inV       %in DEVICE',
            'TEMP      degC     %temp DEVICE',
            'FAN       rpm      drpm DEVICE',
            'CPU       MHz',
            'CPU   total/s   dropd/s squeezd/s  rx_rps/s flw_lim/s',
            'IFACE   rxerr/s   txerr/s    coll/s  rxdrop/s  txdrop/s  txcarr/s  rxfram/s  rxfifo/s  txfifo/s',
            'IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil ',
            'DEV       tps     rkB/s     wkB/s     dkB/s   areq-sz    aqu-sz     await     %util',
            'INTR    intr/s',
            'CPU      %usr     %nice      %sys   %iowait    %steal      %irq     %soft    %guest    %gnice     %idle'
        ]) if l.__len__() > 1
    ]
    SPLIT_NO_NESTED_FILE_TOOL_PATH = Path('./').glob('**/**/pysar_split_standard.py').__iter__().__next__().resolve()
    SPLIT_NESTED_FILE_TOOL_PATH = Path('./').glob('**/**/pysar_split_nest.py').__iter__().__next__().resolve()
    def SplitFilesForHTML(input_filepath: Path):
        with open(input_filepath.as_posix(), mode='r', encoding='utf-8') as fp:
            if set(fp.readline().split()[1:]) in nested_headers:
                ExecCommandLineByOS(["python", f"{SPLIT_NESTED_FILE_TOOL_PATH}", "--inputfile", filepath, '--no-indent'])
            else:
                ExecCommandLineByOS(["python", f"{SPLIT_NO_NESTED_FILE_TOOL_PATH}", "--inputfile", filepath, '--no-indent'])
                
    for filepath in textfile_paths:
        with ThreadPoolExecutor() as executor:
            executor.submit(SplitFilesForHTML, filepath)

    #- Create Graph on HTML(Thanks for Chartjs!)
    # HTMLを出力する。出力済みのJSONを参照する。
    CREATE_HTML_TOOL_PATH = Path('./').glob('**/**/pysar_create_graph.py').__iter__().__next__().resolve()
    jsonfile_paths = [ v.resolve() for v in JSON_SAVE_DIR.glob('./*.json') ]
    for filepath in jsonfile_paths:
        with ThreadPoolExecutor() as executor:
            executor.submit(ExecCommandLineByOS, ["python", f"{CREATE_HTML_TOOL_PATH}", "--inputfile", filepath])

if __name__ == '__main__':
    main()