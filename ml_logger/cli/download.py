from fnmatch import fnmatch
import os
from pathlib import Path

import requests
from params_proto import Flag, ParamsProto, Proto
from tqdm import tqdm


class DownloadArgs(ParamsProto, cli=True):
    """ Download Datasets from logging server.

    Usage:

        to download

        $ ml-download --prefix /instant-feature/datasets/rooms --source="*/processed/*" --target=rooms --exclude='*colmap'

        to list

        $ ml-download --list --prefix /instant-feature/datasets/rooms/whiteboard_v1 --source="processed/*"
        >
            processed/images_4
            processed/transforms.json
            processed/images
            processed/images_8
            processed/images_2

    """
    prefix = Proto(help="prefix on ML-Logger")

    source = Proto("*", help="Query pattern for the experiment directories. You need to "
                             "include the ** signs to search for child directories")
    target = Proto(env=".", help="cache directory")
    list = Flag("List all of the folders if set.")

    exclude = Proto(".git*", help="Exclude files matching this pattern when uploading")
    overwrite = Flag("overwrite existing folders in the cache directory")


def download(prefix: str, source: str, target: str = ".", overwrite=False):
    """download dataset from source to the target folder (local)

    Args:
        prefix (str): source folder. Example: "/fast_nerf/fast_nerf/panda_exp/2022"
        source (str, optional): child folder. Defaults to "source".
        target (str): target folder. Example: "$DATASETS/panda_exp/2022"
        overwrite (bool, optional): overwrite the target folder. Defaults to False.
            Other-wise it will skip the download if the target folder exists.
    """
    from ml_logger import logger

    _ = os.path.expandvars(f"{target}")
    target_image_folder = Path(_)

    if overwrite:
        pass
    elif target_image_folder.exists():
        print(f"{target_image_folder} folder already exists. set the --overwrite flag to overwrite it.")
        return target_image_folder

    with logger.Prefix(prefix):
        try:
            with logger.Sync():
                logger.make_archive(f"{source}", "tar", f"{source}")
                logger.download_dir(f"{source}.tar", f"{target}")
        except FileNotFoundError or requests.exceptions.JSONDecodeError:
            with logger.Sync():
                logger.download_file(f"{source}", to=f"{target}")

        # improves speed by 20% by switching to async remove.
        logger.remove(f"{source}.tar")

    return target_image_folder


def entrypoint():
    from ml_logger import logger

    exclude_patterns = DownloadArgs.exclude.split(';')

    with logger.Prefix(DownloadArgs.prefix):

        folders = logger.glob(DownloadArgs.source)

    if DownloadArgs.list:
        if folders:
            # show me the code for match the child string against a list of exclude patterns, step by step
            if exclude_patterns:
                folders = [f for f in folders if not any([fnmatch(f, e) for e in exclude_patterns])]

            print(*folders, sep="\n")
        else:
            from ml_logger import logger
            print(f"No folders found at '{DownloadArgs.prefix}' for source='{DownloadArgs.source}'")
            print(logger)
        return

    pbar = tqdm(folders)
    for child in pbar:
        if DownloadArgs.target:
            target = os.path.abspath(DownloadArgs.target)
        else:
            target = os.getcwd()

        target = os.path.join(target, child)
        pbar.write(f"Downloading {child} to {target}")
        local_path = download(
            DownloadArgs.prefix,
            f"{child}",
            target,
            overwrite=DownloadArgs.overwrite,
        )


if __name__ == "__main__":
    DownloadArgs.path = os.path.expandvars("/instant-feature/datasets/panda/open_ended/caterpillar")
    DownloadArgs.target = os.path.expandvars("$DATASETS/caterpillar/01-29")
    entrypoint()
