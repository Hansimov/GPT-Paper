import shutil


def rmtree_and_mkdir(path, overwrite=False):
    if overwrite:
        shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
