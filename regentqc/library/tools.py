#!/usr/bin/env python3
'''
    These are various tools used by mediacurator
'''

import configparser
from gettext import translation
import os
import sys
import csv
import chardet
import shutil
import json
# from googletrans import Translator, constants
# from google_trans_new import google_translator  
# from translate import Translator
# import goslate
import argostranslate.package, argostranslate.translate


def load_arguments():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    arguments = {
        "task": None,
        "source": None,
    }

    for arg in sys.argv:
        if "-task:" in arg:
            arguments["task"] = arg[6:]
        elif "-source:" in arg:
            arguments["source"] = arg[8:]
        elif "-destination:" in arg:
            arguments["source"] = arg[13:]

    return arguments

def get_parent(filepath, level = 1):
    if level < 1:
        return os.path.dirname(filepath)
    return get_parent(os.path.dirname(filepath), level - 1)

def find_in_parents(file):
    if not os.path.exists(file):
        for x in range(3):
            tmpfile = os.path.join(get_parent(__file__, x), file)
            if os.path.exists(tmpfile):
                file = tmpfile
    if not os.path.exists(file): return False
    return os.path.abspath(file)

def load_config(file = "config.ini"):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    config = configparser.ConfigParser()
    find_in_parents(file)
    config.read(file)
    return config._sections

def load_csvs(source = "main"):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    csvs = {}
    datapath = find_in_parents('data')
    if not datapath: return False

    availables = {
        "continu_transfos"  : "ContinuationsTransformations.csv",
        "dom_valeurs"       : "DomaineValeur.csv",
        "entreprises"       : "Entreprise.csv",
        "etablissements"    : "Etablissements.csv",
        "fusions_scissions" : "FusionScissions.csv",
        "noms"              : "Nom.csv"
    }

    for key, value in availables.items():
        filepath = os.path.join(datapath, source, value)
        if os.path.isfile(filepath):
            if source == "originals":
                csvs[key] = csv.DictReader(open(filepath, encoding='utf-8-sig'))
            else:
                csvs[key] = csv.DictReader(open(filepath, encoding='utf-8'))

    return csvs

def init_argos(from_code, to_code):
    available_packages = argostranslate.package.get_available_packages()
    available_package = list(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )[0]
    download_path = available_package.download()
    argostranslate.package.install_from_path(download_path)
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = list(filter(
        lambda x: x.code == from_code,
        installed_languages))[0]
    to_lang = list(filter(
        lambda x: x.code == to_code,
        installed_languages))[0]
    return from_lang.get_translation(to_lang)

def break_domval(source = None, destination = None):
    print("Breaking down DomaineValeur.")
    if not source: source = "main"
    if not destination  : destination = "results"
    dom_valeurs = load_csvs(source)["dom_valeurs"]
    datapath = find_in_parents('data')
    chunks = {}
    
    for domval in dom_valeurs:
        if domval['TYP_DOM_VAL'] not in chunks:
            chunks[domval['TYP_DOM_VAL']] = []
        chunks[domval['TYP_DOM_VAL']].append({
            "COD_DOM_VAL"   : domval["COD_DOM_VAL"],
            "VAL_DOM_FRAN"  : domval["VAL_DOM_FRAN"],
            "VAL_DOM_ENG"   : domval["VAL_DOM_ENG"]
        })
    
    for key in chunks.keys():
        with open(os.path.join(datapath, destination, f"{key.lower()}.csv"), 'w', newline = "", encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, chunks[key][0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(chunks[key])

def export_csv(source = None, destination = None):
    print("Exporting standalone csv files.")
    if not source: source = "main"
    if not destination  : destination = "results"
    dom_valeurs = load_csvs(source)["dom_valeurs"]
    datapath = find_in_parents('data')
    chunks = {}

    for domval in dom_valeurs:
        if domval['TYP_DOM_VAL'] not in chunks:
            chunks[domval['TYP_DOM_VAL']] = {}
        
        chunks[domval['TYP_DOM_VAL']][domval["VAL_DOM_FRAN"]] = {
            "name_french"   : domval["VAL_DOM_FRAN"],
            "name_english"  : domval["VAL_DOM_ENG"]
        }

        if domval['TYP_DOM_VAL'] in ['FORM_JURI', ]:
            chunks[domval['TYP_DOM_VAL']][domval["VAL_DOM_FRAN"]]['acronym_french'] = domval["COD_DOM_VAL"]

    for key in chunks.keys():
        with open(os.path.join(datapath, destination, f"{key.lower()}.csv"), 'w', newline = "", encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, chunks[key][next(iter(chunks[key]))].keys())
            dict_writer.writeheader()
            dict_writer.writerows(chunks[key].values())


def translate_domval(source = None, destination = None):
    print("Translating DomainValeur.")
    if not source       : source = "main"
    if not destination  : destination = "translated"
    translator = init_argos("fr", "en")
    dom_valeurs = load_csvs(source)["dom_valeurs"]
    dom_val_traduits = []
    
    for domval in dom_valeurs:
        translation = translator.translate(domval["VAL_DOM_FRAN"])

        ndomval = {
            "TYP_DOM_VAL"   : domval["TYP_DOM_VAL"],
            "COD_DOM_VAL"   : domval["COD_DOM_VAL"],
            "VAL_DOM_FRAN"  : domval["VAL_DOM_FRAN"],
            "VAL_DOM_ENG"   : translation
        }
        
        dom_val_traduits.append(ndomval)

    keys = dom_val_traduits[0].keys()

    datapath = find_in_parents('data')
    with open(os.path.join(datapath, destination, "DomaineValeur.csv"), 'w', newline = "", encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dom_val_traduits)


def print_csvs(source = None):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    if not source: source = "main"
    csvs = load_csvs(source)
    for continu_transfo in csvs["continu_transfos"]:
        print(json.dumps(continu_transfo, indent=2))
        break
    for dom_valeur in csvs["dom_valeurs"]:
        print(json.dumps(dom_valeur, indent=2))
        break
    for entreprise in csvs["entreprises"]:
        print(json.dumps(entreprise, indent=2))
        break
    for etablissement in csvs["etablissements"]:
        print(json.dumps(etablissement, indent=2))
        break
    for fusions_scission in csvs["fusions_scissions"]:
        print(json.dumps(fusions_scission, indent=2))
        break
    for nom in csvs["noms"]:
        print(json.dumps(nom, indent=2))
        break

def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    return chardet.detect(rawdata)['encoding']

def transcode(source = None, destination = None):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    print("Transcoding originals to utf-8.")
    if not source       : source = "originals"
    if not destination  : destination = "transcoded"

    availables = {
        "continu_transfos"  : "ContinuationsTransformations.csv",
        "dom_valeurs"       : "DomaineValeur.csv",
        "entreprises"       : "Entreprise.csv",
        "etablissements"    : "Etablissements.csv",
        "fusions_scissions" : "FusionScissions.csv",
        "noms"              : "Nom.csv"
    }
    
    datapath = find_in_parents('data')

    for key, value in availables.items():
        document = open(os.path.join(datapath, source, value), mode='r', encoding='utf-8-sig').read()
        document = document.encode(encoding = 'utf-8', errors = 'strict').decode(encoding = 'utf-8', errors = 'strict')
        open(os.path.join(datapath, destination, value), mode='w', encoding='utf-8').write(document)

def move_all_files(source, destination):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    for file_name in os.listdir(source):
        file_from = os.path.join(source, file_name)
        file_to = os.path.join(destination, file_name)
        if os.path.isfile(file_from):
            shutil.move(file_from, file_to)
            print('Moved:', file_name)

def build_workables():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    datapath = find_in_parents('data')

    paths = {
        "main": os.path.join(datapath, "main"),
        "transcoded": os.path.join(datapath, "transcoded"),
        "translated": os.path.join(datapath, "translated"),
        "results": os.path.join(datapath, "results"),
        "DomaineValeurs": os.path.join(datapath, "main", "DomaineValeurs"),
        "exports": os.path.join(datapath, "main", "exports"),
    }

    for path in paths.values():
        if not os.path.exists(path):
            os.makedirs(path)

    transcode("originals", "transcoded")
    move_all_files(paths['transcoded'], paths['main'])

    translate_domval("main", "translated")
    move_all_files(paths['translated'], paths['main'])
    
    break_domval("main", "results")
    move_all_files(paths['results'], paths['DomaineValeurs'])
    
    export_csv("main", "results")
    move_all_files(paths['results'], paths['exports'])

def test01(source = None, destination = None):
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    if not source       : source = "main"
    if not destination  : destination = "transcoded"

    availables = {
        "continu_transfos"  : "ContinuationsTransformations.csv",
        "dom_valeurs"       : "DomaineValeur.csv",
        "entreprises"       : "Entreprise.csv",
        "etablissements"    : "Etablissements.csv",
        "fusions_scissions" : "FusionScissions.csv",
        "noms"              : "Nom.csv"
    }
    
    datapath = find_in_parents('data')

    print(get_encoding_type(os.path.join(datapath, source, "exports", "act_econ.csv")))
    # for key, value in availables.items():
    #     # document = open(os.path.join(datapath, source, value), mode='r').read()
    #     print(get_encoding_type(os.path.join(datapath, source, value)))
    #     # open(os.path.join(datapath, destination, value), mode='w', encoding='utf-8').write(document)
