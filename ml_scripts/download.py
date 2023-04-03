import os
from pathlib import Path

from params_proto import Flag, ParamsProto, Proto
from tqdm import tqdm


class DownloadArgs(ParamsProto):
    """Download Datasets from logging server."""

    prefix: str = Proto(help="prefix on ML-Logger")
    output = Proto(env=".", help="cache directory")

    query = Proto(
        "**",
        help="""
            Query pattern for the experiment directories. 
            You need to include the ** signs to search for 
            child directories
            """,
    )
    list = Flag("List all of the folders if set.")

    source = Proto(
        help="""
            source folder, parent of the image folder. We do
            not list experiments when this is set.
            """,
    )
    image_folder: str = Proto("source", help="The name of the image folder under each experiment")
    overwrite = Flag("overwrite existing folders in the cache directory")


def list(prefix, query):
    from ml_logger import logger

    with logger.Prefix(prefix):
        exps = logger.get_exps(query)
        if len(exps.axes[0]) == 0:
            return []
        return [p.replace("/parameters.pkl", "") for p in exps["prefix"]]


def download(source: str, target: str, image_folder: str = "source", overwrite=False):
    """download dataset from source to the target folder (local)

    Args:
        source (str): source folder. Example: "/fast_nerf/fast_nerf/panda_exp/2022"
        target (str): target folder. Example: "$DATASETS/panda_exp/2022"
        image_folder (str, optional): child folder. Defaults to "source".
        overwrite (bool, optional): overwrite the target folder. Defaults to False.
            Other-wise it will skip the download if the target folder exists.
    """
    from ml_logger import logger

    _ = os.path.expandvars(f"{target}/{image_folder}")
    target_image_folder = Path(_)

    if overwrite:
        pass
    elif target_image_folder.is_dir():
        print(f"{target_image_folder} folder already exists. set the --overwrite flag to overwrite it.")
        return target_image_folder

    with logger.Prefix(source), logger.Sync():
        logger.make_archive(f"{image_folder}", "tar", f"{image_folder}")
        logger.download_dir(f"{image_folder}.tar", f"{target}/{image_folder}")

        # improves speed by 20% by switching to async remove.
        logger.remove(f"{image_folder}.tar")
        return target_image_folder


def entrypoint():
    if DownloadArgs.source is not None:
        print("Downloading folder", DownloadArgs.source)
        t = download(
            f"{DownloadArgs.source}",
            f"{DownloadArgs.output}",
            image_folder=DownloadArgs.image_folder,
            overwrite=DownloadArgs.overwrite,
        )
        if t:
            print("Downloading complete.")
        return

    folders = list(DownloadArgs.prefix, DownloadArgs.query)

    if DownloadArgs.list:
        print(*folders, sep="\n")
        return
    pbar = tqdm(folders)
    for folder in pbar:
        pbar.set_description(f"Downloading {folder}")
        download(
            f"{DownloadArgs.prefix}/{folder}",
            f"{DownloadArgs.output}/{folder}",
            image_folder=DownloadArgs.image_folder,
            overwrite=DownloadArgs.overwrite,
        )


if __name__ == "__main__":
    DownloadArgs.prefix = os.path.expandvars("/instant-feature/datasets/panda/open_ended/caterpillar")
    DownloadArgs.output = os.path.expandvars("$DATASETS/caterpillar/01-29")
    entrypoint()
