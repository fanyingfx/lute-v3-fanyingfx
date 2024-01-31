import os
import shutil
from pathlib import Path

import yaml
from mdict_query.mdict_query import IndexBuilder

from lute.config.app_config import AppConfig
from lute.dict.mdx_util import MDXDict
from lute.dict.mdx_util import get_local_resource


def _create_prod_config_if_needed():
    """
    If config.yml is missing, create one from prod config.
    """
    config_file = os.path.join(AppConfig.configdir(), "config.yml")
    if not os.path.exists(config_file):
        prod_conf = os.path.join(AppConfig.configdir(), "config.yml.prod")
        shutil.copy(prod_conf, config_file)


def load_mdxdict_config():
    # if app_config_path is None:
    _create_prod_config_if_needed()
    app_conf_path = AppConfig.default_config_filename()
    dict_path = AppConfig(app_conf_path).dictpath
    with open(dict_path, "r") as f:
        conf = yaml.safe_load(f)
    return conf


mdxdict_conf = load_mdxdict_config()
rootfolder = mdxdict_conf["rootfolder"]
en_dict_conf = mdxdict_conf["dicts"]["English"]
jp_dict_conf = mdxdict_conf["dicts"]["Japanese"]


def get_local_paths(rootfolder, dict_conf):
    root_path = Path(rootfolder)
    dir_name = dict_conf["dir_name"]
    root_path = root_path / dir_name
    dictdir_list = dict_conf["dict_list"]
    if dict_conf.get("pronunciation"):
        dictdir_list.append(dict_conf["pronunciation"])
    return [root_path / dictdir for dictdir in dictdir_list]


en_local_paths = get_local_paths(rootfolder, en_dict_conf)
jp_local_paths = get_local_paths(rootfolder, jp_dict_conf)
dict_local = get_local_resource(en_local_paths + jp_local_paths)


def find_mdx_file(mdx_folder: Path):
    for file in mdx_folder.iterdir():
        if file.suffix == ".mdx":
            return str(file.absolute())


def get_mdxdicts(rootfolder, dict_conf, dict_local):
    dictdir_list = dict_conf["dict_list"]
    rootpath: Path = Path(rootfolder)
    dir_name = dict_conf["dir_name"]
    rootpath = rootpath / dir_name
    res = []
    for dictdir in dictdir_list:
        dir_path: Path = rootpath / dictdir
        mdx_file = find_mdx_file(dir_path)
        idxbd = IndexBuilder(mdx_file)
        res.append(MDXDict(idxbd, dict_local))
    pronunciation_mdxdict = None
    if dict_conf["pronunciation"]:
        pronun_path = rootpath / dict_conf["pronunciation"]
        mdx_file = find_mdx_file(pronun_path)
        pronunciation_builder = IndexBuilder(mdx_file)
        pronunciation_mdxdict = MDXDict(pronunciation_builder, dict_local)

    return res, pronunciation_mdxdict


en_bds, _ = get_mdxdicts(rootfolder, en_dict_conf, dict_local)
jp_bds, jp_pronun_bd = get_mdxdicts(rootfolder, jp_dict_conf, dict_local)
