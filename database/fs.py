
import os

from .genesis import Genesis

def get_database_dir_path(data_dir: str) -> str:
    return os.path.join(os.path.expanduser(data_dir), "database")

def get_genesis_file_path(data_dir: str) -> str:
    return os.path.join(get_database_dir_path(data_dir), "genesis.json")

def get_blocks_db_file_path(data_dir: str) -> str:
    return os.path.join(get_database_dir_path(data_dir), "block.db")

def init_data_dir(data_dir: str):
    if os.path.exists(get_genesis_file_path(data_dir)):
        return

    os.makedirs(get_database_dir_path(data_dir), exist_ok=True)

    Genesis.write_to_disk(get_genesis_file_path(data_dir))

    with open(get_blocks_db_file_path(data_dir), 'w') as f:
        f.write('')
