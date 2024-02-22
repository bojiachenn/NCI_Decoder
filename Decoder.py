import sys
import Decoder_Main
import random
import os

__NFC_NCI_VER__ = "Ver 2.0" # 7 char
__DECODER_VERSION__ = "Ver 1.0" # 7 char

def clear_terminal():
    # 適用於 Windows
    if os.name == 'nt':
        os.system('cls')
    # 適用於 Unix/Linux
    else:
        os.system('clear')

def clear_below(row):
    print(f"\033[{row+1};0H\033[J", end="")

kaomoji=[
    "(o´∀`o)", "(o･ω･o)", "( ･ω･ )",
    "｡+(´ω`*)♪♪", "(๑˃ᴗ˂)ﻭ", "°˖✧◝(⁰▿⁰)◜✧˖°",
    "٩(ˊᗜˋ*)و ♡", "(๑•᎑•๑)", "٩( ᐛ )( ᐖ )۶"
]

def print_at(row, text):
    print(f"\033[{row};0H{text}", end="")
    # sys.stdout.write(f"\033[{row};0H{text}")
    # sys.stdout.flush()

def print_menu():
    ran = random.randint(0, len(kaomoji)-1)
    print_at(1,  "┌─────╮┌─────┐╭─────┐╭─────╮┌─────╮┌─────┐┌─────╮")
    print_at(2,  "│ ║   ││  ═══╡│ ┌───┘│ ║   ││ ║   ││  ═══╡│ ║   │")
    print_at(3,  "│ ║   ││  ═══╡│ └───┐│ ║   ││ ║   ││  ═══╡│ ┌┐ ┌╯")
    print_at(4, f"└─────╯└─────┘╰─────┘╰─────╯└─────╯└─────┘└─┘└─┘ \033[35;3;5m{__DECODER_VERSION__}\033[0m")
    print_at(5,   "┌──────────────────────────────────────────────┐")
    print_at(6,   "│                                              │")
    print_at(7,   "│   1: Read file                               │")
    print_at(8,   "│   2: Read raw data                           │")
    print_at(9,   "│   3: Exit              "+"{0:^20}".format(kaomoji[ran])+"  │")
    print_at(10, f"│                        \033[33mSupport NCI: \033[0m{__NFC_NCI_VER__}  │")
    print_at(11,  "└──────────────────────────────────────────────┘ \033[3;4;5mJimmy Chen\033[0m")

def main():
    clear_terminal()
    while True:
        print_menu()
        print("")
        print_at(12, " " * 80) # 清除第8行
        print_at(12, "Select Decoder Mode: ")
        select = input().strip()
        
        clear_below(12)

        if(select == "1"):
            while True:
                print_at(14, " " * 200)
                print_at(14, "Enter \033[33mfile Path\033[0m or \"\033[31m-1\033[0m\" back to Menu: ")
                # print("Enter \033[33mfile name\033[0m: ", end="")
                file_name = input().strip()
                if(file_name == "-1"):
                    clear_terminal()
                    break
                else:
                    try:
                        with open(file_name, mode='r', encoding='utf-8', errors='ignore') as file:
                            lines = file.readlines()
                    except FileNotFoundError:
                        print("\033[31mError:\033[0m File Not Found!\n")
                        continue

                    except UnicodeDecodeError:
                        print("\033[31mError:\033[0m Unicode Decode Error!\n")
                        continue

                    defult_search = "NxpNci"
                    print(f"Enter text to search (default is '\033[32m{defult_search}\033[0m'): ", end="")
                    search_string = input().strip() or defult_search
                    print(f"searching... \033[32m{search_string}\033[0m")
                        # Redirect standard output to a text file
                    original_stdout = sys.stdout
                    sys.stdout = open('output.txt', 'w')
                    print("File Path: "+file_name)
                    print("Searching Keyword: "+search_string)
                    print("")
                    i = 1
                    count = 0
                    for line in lines:
                        if ((search_string in line) & ("=>" in line)):
                            count = count + 1
                            print(str(i)+": ", end="")
                            print(line, end="")
                            print(" ↓", end="")
                            num_string = line.split("=>")[1].strip()

                        elif((search_string in line) & ("<=" in line)):
                            count = count + 1
                            print(str(i)+": ", end="")
                            print(line, end="")
                            print(" ↓", end="")
                            num_string = line.split("<=")[1].strip()

                        else:
                            i = i + 1
                            continue

                        try:
                            Decoder_Main.NFC_NCI_DECODER(num_string)
                            i = i + 1
                        except ValueError as e:
                            sys.stdout.flush()
                            sys.stdout = original_stdout
                            print("\n\033[31mError:\033[0m This text is not available for search\n")
                            # print(e)
                            sys.exit(0)

                    print("Total " + str(count) + " matche(s) in the file.")
                    sys.stdout.flush()
                    sys.stdout = original_stdout
                    print("\n\033[36mDone!!\033[0m\n")
                    os.system("PAUSE")
                    clear_below(12)
                    # sys.exit(0)
        
        elif(select == "2"):
            while True:
                # print_at(14, " " * 200)
                # print_at(14, "Input the \"\033[33mNCI raw data\033[0m\" or \"\033[31m-1\033[0m\" back to Menu: ")
                print("Input the \"\033[33mNCI raw data\033[0m\" or \"\033[31m-1\033[0m\" back to Menu: ", end="")
                raw = input().strip()

                if(raw == "-1"):
                    clear_terminal()
                    break

                else:
                    clear_below(14)
                    print(f"decoding... \033[32m{raw}\033[0m")
                    try:
                        Decoder_Main.NFC_NCI_DECODER(raw)
                    except ValueError:
                        clear_below(14)
                        print("\033[31mError: \033[33mNCI raw data\033[0m invalid. Try again!!\n")
        
        elif(select == "3"):
            print("\n\033[47;31mExiting...\033[0m")
            os.system("PAUSE")
            sys.exit(0)

        else:
            print("\033[31mInvalid\033[0m choice. Try again!!\n")

if __name__ == '__main__':
    main()
