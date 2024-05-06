from functools import cache
from pathlib import Path

from mdict_query.mdict_utils import MDXDict
from lute.config.app_config import AppConfig

config_file = AppConfig.default_config_filename()
ac = AppConfig(config_file)
DICTS_PATH = Path(ac.dicts_path)
if not DICTS_PATH.exists():
    raise FileNotFoundError(f"请将词典文件 dicts 放在: {DICTS_PATH.parent} 目录")
EN_MDX_FILE = (
    DICTS_PATH / "Eng" / "olad10/Oxford Advanced Learner's Dictionary 10th.mdx"
)
en_mdx_dict = MDXDict(EN_MDX_FILE)


JP_PROUN_FILE = DICTS_PATH / "ja" / "nhk" / "NHK日本語発音アクセント辞書.mdx"
jp_proun_mdx = MDXDict(JP_PROUN_FILE)

JP_MDX_FILE = DICTS_PATH / "ja" / "Shogakukanjcv3/Shogakukanjcv3.mdx"
jp_mdx_dict = MDXDict(JP_MDX_FILE)


@cache
def en_query(word: str) -> bytes:
    return en_mdx_dict.lookup(word)  # type: ignore[no-any-return]


@cache
def jp_query(word: str) -> bytes:
    proun = jp_proun_mdx.lookup(word)
    return proun + b"\n" + jp_mdx_dict.lookup(word)  # type: ignore[no-any-return]
