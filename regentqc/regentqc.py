#!/usr/bin/env python3

# Normal import
try:
    from regentqc.library.tools import load_arguments, load_config, print_csvs, break_domval, translate_domval, transcode, export_csv, build_workables, test01
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, print_csvs, break_domval, translate_domval, transcode, export_csv, build_workables, test01

def main():
    arguments = load_arguments()
    source = arguments['source']
    destination = arguments['source']
    if arguments['task'] == "print":
        print_csvs(source)
    elif arguments['task'] == "break_domval":
        break_domval(source, destination)
    elif arguments['task'] == "export":
        export_csv(source)
    elif arguments['task'] == "translate_domval":
        translate_domval(source, destination)
    elif arguments['task'] == "transcode":
        transcode(source, destination)
    elif arguments['task'] == "build":
        build_workables()
    elif arguments['task'] == "test":
        test01(source, destination)
        
if __name__ == '__main__':
    main()
