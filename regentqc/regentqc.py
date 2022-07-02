#!/usr/bin/env python3

# Normal import
try:
    from regentqc.library.tools import load_arguments, load_config, print_csvs, translate_domval
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, print_csvs, translate_domval

def main():
    arguments = load_arguments()
    if arguments['task'] == "print":
        print_csvs()
    elif arguments['task'] == "translate_domval":
        translate_domval()
        
if __name__ == '__main__':
    main()
