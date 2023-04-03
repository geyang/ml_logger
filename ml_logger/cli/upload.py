from contextlib import ExitStack, contextmanager

from params_proto import ParamsProto, Proto, Flag


class UploadArgs(ParamsProto):
    """ ML-Logger upload command

    Example:
        ml-upload --list  # to see all files in the current directory for upload
        ml-upload --target /fast_nerf/fast_nerf/panda_exp/2022  # uploads to this folder
        ml-upload --target /$USER/sratch/tmp --overwrite  # overwrite existing files
        ml-upload --target /$USER/scratch/tmp --archive  # upload the files as a tar file

    """
    list = Flag("List all of the folders if set.")

    target: str = Proto(help="The target prefix on the logging server")  # , required=True)
    workdir = Proto(".", help="cache directory")
    source = Proto("*", help="""Query pattern for the files to be tarred.""")
    archival = Flag("Use archive to upload the files")

    overwrite = Flag("overwrite existing folders in the cache directory")


@contextmanager
def WorkDir(path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """
    import os

    origin = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def list(source, query):
    """list the current directory into a tree"""
    from glob import glob
    with WorkDir(source):
        return glob(query, recursive=True)


def upload(source, target, overwrite=False):
    """download dataset from source to the target folder (local)

    Args:
        source (str): source folder. Example: "/fast_nerf/fast_nerf/panda_exp/2022"
        target (str): target folder. Example: "$DATASETS/panda_exp/2022"
        overwrite (bool, optional): overwrite the target folder. Defaults to False.
            Other-wise it will skip the download if the target folder exists.
    """
    from ml_logger import logger

    raise NotImplementedError("This is a snippet. You need to implement this function.")


def entrypoint():
    from ml_logger import logger
    from pathlib import Path

    folders = list(UploadArgs.workdir, UploadArgs.source)

    if UploadArgs.list:
        print(UploadArgs.workdir + ":", *folders, sep="\n")
        return

    if UploadArgs.target is None:
        logger.print("setting the upload target to ", logger.prefix)
        PCntx = ExitStack()
    else:
        PCntx = logger.Prefix(UploadArgs.target)

    with logger.Sync(), PCntx, WorkDir(UploadArgs.workdir):  # use synchronous mode to make sure the upload finished
        from tqdm import tqdm

        pbar = tqdm(folders)
        for local_name in pbar:
            desc = f"Uploading the {local_name} to {logger.get_dash_url()}/{local_name}"
            pbar.write(desc)

            tar_filename = local_name + ".tar"

            if tar_filename in logger.glob(tar_filename):
                if UploadArgs.overwrite:
                    pbar.write(f"overwriting {tar_filename} on the server")
                    logger.remove(tar_filename)
                else:
                    pbar.write(f"{tar_filename} alread exists on the server"
                               "Set the --overwrite flag to overwrite it.")
                    continue

            logger.upload_dir(local_name, tar_filename, excludes=tuple(), archive="tar")

            if local_name in logger.glob(local_name):
                if UploadArgs.overwrite:
                    pbar.write(f"overwriting {local_name} on the server")
                    logger.remove(local_name)
                else:
                    pbar.write(f"{local_name} alread exists on the server"
                               "Set the --overwrite flag to overwrite it.")
                    continue

            if not UploadArgs.archival:
                logger.shell(f"mkdir -p {local_name} && tar -xvf {tar_filename} --directory {local_name}")
                logger.remove(tar_filename)
                pbar.write("Decompressed the archive on the server")

        print("Uploading completed")


if __name__ == "__main__":
    # UploadArgs.list = True
    # UploadArgs.overwrite = True
    # UploadArgs.archive = False
    # UploadArgs.target = "/fast_nerf/fast_nerf/panda_exp/2023/ge_upload_example/"
    # UploadArgs.prefix = os.path.expandvars("/fast_nerf/fast_nerf/panda_exp/2022")
    # UploadArgs.output = os.path.expandvars("$DATASETS/panda_exp/2022")
    entrypoint()
