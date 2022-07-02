#!/usr/bin/env python3
'''
    These are various tools used by mediacurator
'''

import configparser
from gettext import translation
import os
import sys
import csv
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
    }

    for arg in sys.argv:
        if "-task:" in arg:
            arguments["task"] = arg[6:]

    return arguments

def get_parent(filepath, level = 1):
    if level < 1:
        return os.path.dirname(filepath)
    return get_parent(os.path.dirname(filepath), level - 1)

def find_in_parents(file):
    if not os.path.exists(file):
        print("Here")
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

def load_csvs():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    datapath = find_in_parents('data')
    if not datapath: return False
    return {
        "continu_transfos"  : csv.DictReader(open(os.path.join(datapath, "ContinuationsTransformations.csv"), encoding='utf-8-sig')),
        "dom_valeurs"       : csv.DictReader(open(os.path.join(datapath, "DomaineValeur.csv"), encoding='utf-8-sig')),
        "entreprises"       : csv.DictReader(open(os.path.join(datapath, "Entreprise.csv"), encoding='utf-8-sig')),
        "etablissements"    : csv.DictReader(open(os.path.join(datapath, "Etablissements.csv"), encoding='utf-8-sig')),
        "fusions_scissions" : csv.DictReader(open(os.path.join(datapath, "FusionScissions.csv"), encoding='utf-8-sig')),
        "noms"              : csv.DictReader(open(os.path.join(datapath, "Nom.csv"), encoding='utf-8-sig'))
    }

    print(noms)
    # print(f"Hello {datapath}!")

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


def translate_domval():
    translator = init_argos("fr", "en")


    datapath = find_in_parents('data')
    # translator = Translator(from_lang = "fr", to_lang="en")
    # gs = goslate.Goslate()

    dom_valeurs = load_csvs()["dom_valeurs"]
    dom_val_traduits = []
    # count = 0
    for domval in dom_valeurs:        
        # print(f"*******{domval['COD_DOM_VAL']}*******")
        # print(f"TYP_DOM_VAL: {domval['TYP_DOM_VAL']}")
        # print(f"COD_DOM_VAL: {domval['COD_DOM_VAL']}")
        # print(f"VAL_DOM_FRAN: {domval['VAL_DOM_FRAN']}")
        translation = translator.translate(domval["VAL_DOM_FRAN"])

        # print(f"VAL_DOM_ENG: {translation}")
        # break
        ndomval = {
            "TYP_DOM_VAL"   : domval["TYP_DOM_VAL"],
            "COD_DOM_VAL"   : domval["COD_DOM_VAL"],
            "VAL_DOM_FRAN"  : domval["VAL_DOM_FRAN"],
            "VAL_DOM_ENG"   : translation
        }
        # print(json.dumps(ndomval, indent=2))
        # break
        dom_val_traduits.append(ndomval)

        # count += 1
        # if count > 100: break

    keys = dom_val_traduits[0].keys()

    with open(os.path.join(datapath, "DomaineValeur_ml.csv"), 'w', newline = "", encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dom_val_traduits)


def print_csvs():
    '''Get/load command parameters

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    csvs = load_csvs()
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