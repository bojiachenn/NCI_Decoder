import sys, os, random
import json
from nci_decoder import Decoder_Main
import log_profiles

__NFC_NCI_VER__ = "2.0" # 3 char
__DECODER_VERSION__ = "2.0" # 3 char

kaomoji=[
    "(o´∀`o)", "(o･ω･o)", "( ･ω･ )",
    "｡+(´ω`*)♪♪", "(๑˃ᴗ˂)ﻭ", "°˖✧◝(⁰▿⁰)◜✧˖°",
    "٩(ˊᗜˋ*)و ♡", "(๑•᎑•๑)", "٩( ᐛ )( ᐖ )۶"
]

config = {}

def load_config(file_path):
    global config
    try:
        with open(file_path, mode='r') as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        return 0
    except json.JSONDecodeError as e:
        print("JSON 解析失败:", e)
        return 0
    return 1

def decode_and_print(prefix, hex_str, vendor, chip_model):
    print(prefix, end="")
    try:
        Decoder_Main.NFC_NCI_DECODER(int(len(hex_str)/2), hex_str, vendor, chip_model, 1)
    except KeyError as e1:
        print(f"Error: {e1} control code not found, please check the documentation.")
        print("#end")
    except ValueError as e2:
        print(f"Error: {e2}")
        print("#end")
    except Exception as e:
        print("Error: Unexpected error!!")
        print("type:", type(e))
        print("message:", str(e))
        print("#end")

def clear_terminal():
    # 適用於 Windows
    if os.name == 'nt':
        os.system('cls')
    # 適用於 Unix/Linux
    else:
        os.system('clear')

def clear_below(row):
    print(f"\033[{row+1};0H\033[J", end="")

def print_at(row, text):
    print(f"\033[{row};0H{text}", end="")
    # sys.stdout.write(f"\033[{row};0H{text}")
    # sys.stdout.flush()

def print_menu(status):
    ran = random.randint(0, len(kaomoji)-1)
    if status:
        print("\033[32m")
    else:
        print("\033[31m")

    print_at(6, "{0:>70}".format("")+"  Json\033[0m")
    print_at(7, "{0:>70}".format("")+"Vendor: "+config.get("vendor", "None"))
    print_at(8, "{0:>70}".format("")+"Model:  "+config.get("chip_model", "None"))
    print_at(9, "{0:>70}".format("")+"Filter: "+config.get("filter", "None"))
    # print_at(1, "{0:>70}".format("")+"r: Reload json file")

    print_at(1,  "┌─────╮┌─────┐╭─────┐╭─────╮┌─────╮┌─────┐┌─────╮")
    print_at(2,  "│ ║   ││  ═══╡│ ┌───┘│ ║   ││ ║   ││  ═══╡│ ║   │")
    print_at(3,  "│ ║   ││  ═══╡│ └───┐│ ║   ││ ║   ││  ═══╡│ ┌┐ ┌╯")
    print_at(4, f"└─────╯└─────┘╰─────┘╰─────╯└─────╯└─────┘└─┘└─┘ \033[35;3;5mVer {__DECODER_VERSION__}\033[0m")
    print_at(5,   "┌──────────────────────────────────────────────┐")
    print_at(6,   "│                                              │")
    print_at(7,   "│   1: Read file                               │")
    print_at(8,   "│   2: Read raw data                           │")
    print_at(9,   "│   3: Exit              "+"{0:^20}".format(kaomoji[ran])+"  │")
    print_at(10, f"│                        \033[33mSupport NCI: \033[0mVer {__NFC_NCI_VER__}  │")
    print_at(11,  "└──────────────────────────────────────────────┘ \033[3;4;5mJimmy Chen\033[0m")

def mode_1():
    while True:
        # print_at(14, " " * 115)
        print("Enter \033[33mPath\033[0m or \"\033[31m-1\033[0m\" back to Menu: ", end="")
        file_path = input().strip()

        if(file_path == "-1"):
            clear_terminal()
            break

        else:
            if not os.path.exists(file_path):
                print("\033[31mError:\033[0m File or Directory Not Found!\n")
                continue

            file_paths = []
            
            if os.path.isfile(file_path):
                # print(f"The path '{file_path}' is a file.")
                file_paths.append(file_path)

            elif os.path.isdir(file_path):
                # print(f"The path '{file_path}' is a directory.")
                files = os.listdir(file_path)
                for f_name in files:
                    f_path = os.path.join(file_path, f_name)
                    if(os.path.isfile(f_path)):
                        file_paths.append(f_path)

            print("")

            decode_key = config.get("vendor", "None")
            print(f"Enter keyword to search raw data: ", end="")
            if(decode_key == "None"):
                decode_key = input().strip()
            else:
                print("\033[32m"+decode_key+"\033[0m")
            
            filter_key = config.get("filter", "None")
            defult_filter_key = "remain_all"
            print(f"Enter filter keyword(s) for other messages (default is '\033[32m{defult_filter_key}\033[0m'): ", end="")
            if(filter_key == "None"):
                filter_key = input().strip() or defult_filter_key
            else:
                print("\033[32m"+filter_key+"\033[0m")
            filter_key_list = filter_key.split()
            print("")

            for file_path in file_paths:
                with open(file_path, mode='r', encoding='utf8', errors='ignore') as file: # 
                    lines = file.readlines()

                print(f"searching \033[32m{decode_key}\033[0m in file: \033[33m{file_path}\033[0m...")
                           
                file_name = os.path.basename(file_path)    # 取得輸入檔檔名
                output_folder = 'NCI_output'    # 輸出資料夾
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)    # 如果資料夾不存在則建立
                output_path = os.path.join(output_folder, file_name+'_d.txt')    # 加入路徑

                original_stdout = sys.stdout
                sys.stdout = open(output_path, 'w')    # Redirect standard output to a text file

                print("File Path: "+file_path)
                print("Searching Keyword: "+decode_key)
                print("Filter: ", end="")
                print(filter_key_list)
                print("")
                count = 0
                profile = log_profiles.get_profile(decode_key)
                pending = {}   # ST-style sequence number -> accumulated fragment (dict has "sequence")

                for line in lines:
                    cand = log_profiles.extract_candidate(line, profile)

                    if cand is None:
                        if((filter_key_list[0] == "remain_all") or (any(key.lower() in line.lower() for key in filter_key_list))):
                            line = line.rstrip().encode("utf8").decode("cp950", "ignore") #
                            print(line)
                        continue

                    if profile.get("sequence") is None:
                        # 沒有分段機制（例如 NXP）：一行就是一個完整封包
                        arrow = "DH --> NFCC" if cand["direction"] == "TX" else "DH <-- NFCC"
                        tag = decode_key + ("NciX" if cand["direction"] == "TX" else "NciR")
                        if cand["kind"] == "redacted":
                            print(f"{cand['ts']}  {arrow}  {tag}  [REDACTED: payload hidden by HAL]")
                            count = count + 1
                            continue
                        if len(cand["hex"]) < 6:
                            continue
                        count = count + 1
                        decode_and_print(f"{cand['ts']}  {arrow}  {tag}", cand["hex"], config.get("vendor", "None"), config.get("chip_model", "None"))
                        continue

                    # 有分段機制（例如 ST）：依序號累積 hex，湊滿宣告長度才解碼
                    seq = cand["seq"]
                    if cand["kind"] == "redacted":
                        pending[seq] = {"redacted": True}
                        continue

                    if cand["is_start"] or seq not in pending:
                        pending[seq] = {"direction": cand["direction"], "ts": cand["ts"], "hex": cand["hex"]}
                    elif cand["is_continue"] and seq in pending and not pending[seq].get("redacted"):
                        pending[seq]["hex"] += cand["hex"]

                    entry = pending.get(seq)
                    if entry and not entry.get("redacted") and len(entry["hex"]) >= 6:
                        declared_total_bytes = 3 + int(entry["hex"][4:6], 16)
                        if len(entry["hex"]) >= declared_total_bytes * 2:
                            arrow = "DH --> NFCC" if entry["direction"] == "TX" else "DH <-- NFCC"
                            count = count + 1
                            decode_and_print(f"{entry['ts']}  {arrow}", entry["hex"], config.get("vendor", "None"), config.get("chip_model", "None"))
                            del pending[seq]

                for seq, entry in pending.items():
                    count = count + 1
                    if entry.get("redacted"):
                        print(f"[REDACTED: packet #{seq} payload hidden by HAL]")
                    else:
                        print(f"[INCOMPLETE: packet #{seq} never reached its declared length]")

                print("\nTotal " + str(count) + " matche(s) in the file.")
                sys.stdout.flush()
                sys.stdout.close()
                sys.stdout = original_stdout
                # clear_below(18)
                print("Output File:", f"\033[33m{output_path}\033[0m")
                print("")
            print("\033[36mDone!!\033[0m\n")
            # os.system("PAUSE")
            # clear_below(12)
            # sys.exit(0)

def mode_2():
    while True:
        # print_at(14, " " * 200)
        # print_at(14, "Input the \"\033[33mNCI raw data\033[0m\" or \"\033[31m-1\033[0m\" back to Menu: ")
        print("Input the \"\033[33mNCI raw data\033[0m\" or \"\033[31m-1\033[0m\" back to Menu: ", end="")
        raw = input().strip()
        raw = raw.replace("0x", "")
        raw = raw.replace(",", "")
        raw = raw.replace(" ", "")
        raw = raw.upper()

        if(raw == "-1"):
            clear_terminal()
            break

        else:
            # clear_below(14)
            print(f"decoding... \033[32m{raw}\033[0m\n")
            try:
                Decoder_Main.NFC_NCI_DECODER(int(len(raw)/2), raw, config.get("vendor", "None"), config.get("chip_model", "None"), 2)
            except KeyError as e1:
                print(f"\033[31mError:\033[0m \033[33m{e1}\033[0m control code not found, please check the documentation.\n")
            except ValueError as e2:
                # clear_below(14)
                # print(e)
                print("\033[31mError: \033[33mNCI raw data\033[0m invalid. Try again!!")
                print(f"\033[31mError: \033[0m{e2}\n")
            except Exception as e:
                print("\033[31mError: \033[0mUnexpected error!!")
                print("type:", type(e))
                print("message:", str(e))
            print("")

def main():
    status = load_config("config.json")
    clear_terminal()
    while True:
        print_menu(status)
        print_at(12, " " * 110) # 清除第12行
        print_at(12, "                              (\"\033[31mr\033[0m\" reload json)")
        print_at(12, "Select Decoder Mode: ")
        select = input().strip()
        
        clear_below(12)

        if(select == "1"):
            mode_1()
        
        elif(select == "2"):
            mode_2()
        
        elif(select == "3"):
            print("\n\033[31mExiting...\033[0m")
            os.system("PAUSE")
            sys.exit(0)

        elif(select == "r"):
            clear_terminal()
            status = load_config("config.json")

        else:
            print("\033[31mInvalid\033[0m choice. Try again!!\n")

if __name__ == '__main__':
    main()
