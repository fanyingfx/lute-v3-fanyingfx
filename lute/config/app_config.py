"""
App configuration.
"""

import shutil
import yaml
from platformdirs import PlatformDirs
from pathlib import Path


class AppConfig:  # pylint: disable=too-many-instance-attributes
    """
    Configuration wrapper around yaml file.

    Adds various properties for lint-time checking.
    """

    def __init__(self, config_file_path):
        """
        Load the required configuration file.
        """
        self._load_config(config_file_path)

    def _load_config(self, config_file_path):
        """
        Load and validate the config file.
        """
        with open(config_file_path, "r", encoding="utf-8") as cf:
            config = yaml.safe_load(cf)

        if not isinstance(config, dict):
            raise RuntimeError(
                f"File at {config_file_path} is invalid or is not a yaml dictionary."
            )

        self.env = config.get("ENV", None)
        if self.env not in ["prod", "dev"]:
            raise ValueError(f"ENV must be prod or dev, was {self.env}.")

        self.is_docker = "IS_DOCKER" in config

        # Database name.
        self.dbname = config.get("DBNAME", None)
        if self.dbname is None:
            raise ValueError("Config file must have 'DBNAME'")

        # Various invoke tasks in /tasks.py check if the database is a
        # test_ db prior to running some destructive action.
        self.is_test_db = self.dbname.startswith("test_")

        # Path to user data.
        datapath = Path(config.get("DATAPATH", self._get_appdata_dir()))
        self.datapath = str(datapath)
        self.userimagespath = str(datapath / "userimages")
        self.useraudiopath = str(datapath / "useraudio")
        self.temppath = str(datapath / "temp")
        self.dbfilename = str(datapath / self.dbname)
        self.unidic_cwj_path = (datapath / "unidic-cwj").as_posix()
        self.unidic_csj_path = (datapath / "unidic-csj").as_posix()
        self.dicts_path = str(datapath / "dicts")

        # Path to db backup.
        # When Lute starts up, it backs up the db
        # if migrations are going to be applied, just in case.
        # Hidden directory as a hint to the the user that
        # this is a system dir.
        self.system_backup_path = str(datapath / ".system_db_backups")

        # Default backup path for user, can be overridden in settings.
        self.default_user_backup_path = config.get(
            "BACKUP_PATH", str(datapath / "backups")
        )

    def _get_appdata_dir(self):
        "Get user's appdata directory from platformdirs."
        dirs = PlatformDirs("Lute3", "Lute3")
        return dirs.user_data_dir

    @property
    def sqliteconnstring(self):
        "Full sqlite connection string."
        return f"sqlite:///{self.dbfilename}"

    @staticmethod
    def configdir():
        "Return the path to the configuration file directory."
        return Path(__file__).parent

    @staticmethod
    def default_config_filename():
        "Return the path to the default configuration file."
        thisdir = AppConfig.configdir()

        default_config = thisdir / "config.yml"
        if not default_config.exists():
            shutil.copy(thisdir / "config.yml.prod", default_config)
        return default_config
