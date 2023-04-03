from contextlib import ExitStack

from params_proto import ParamsProto, Proto, Flag


class UploadArgs(ParamsProto):
    """
    ML-Logger upload command

    Example:
        ff-upload --list  # to see all files in the current directory for upload
        ff-upload --target /fast_nerf/fast_nerf/panda_exp/2022  # uploads to this folder
        ff-upload --target /$USER/sratch/tmp --overwrite  # overwrite existing files
        ff-upload --target /$USER/scratch/tmp --archive  # upload the files as a tar file

    """

    target: str = Proto(help="The target prefix on the logging server")  # , required=True)
    source = Proto(".", help="cache directory")
    query = Proto(
        "**",
        help="""
        Query pattern for the files to be tarred 
        """,
    )
    archive = Flag("Use archive to upload the files")

    list = Flag("List all of the folders if set.")
    overwrite = Flag("overwrite existing folders in the cache directory")


def list(source, query):
    """list the current directory into a tree"""
    from glob import glob

    return glob(source + "/" + query, recursive=True)


def upload(source, target, image_folder="source", overwrite=False):
    """download dataset from source to the target folder (local)

    Args:
        source (str): source folder. Example: "/fast_nerf/fast_nerf/panda_exp/2022"
        target (str): target folder. Example: "$DATASETS/panda_exp/2022"
        child_folder (str, optional): child folder. Defaults to "source".
        overwrite (bool, optional): overwrite the target folder. Defaults to False.
            Other-wise it will skip the download if the target folder exists.
    """
    from ml_logger import logger

    raise NotImplementedError("This is a snippet. You need to implement this function.")


def entrypoint():
    from ml_logger import logger
    from pathlib import Path

    folders = list(UploadArgs.source, UploadArgs.query)

    if UploadArgs.list:
        print(*folders, sep="\n")
        return

    if UploadArgs.target is None:
        logger.print("setting the upload target to ", logger.prefix)
        PCntx = ExitStack()
    else:
        PCntx = logger.Prefix(UploadArgs.target)

    with logger.Sync(), PCntx:  # use synchronous mode to make sure the upload finished

        dirname = Path(UploadArgs.source).absolute().name
        filename = dirname + ".tar"

        print(f"Uploading the {dirname} to", logger.get_dash_url(), dirname)
        remote_files = logger.glob(filename)
        if remote_files and filename in remote_files:
            if UploadArgs.overwrite:
                print("File alread exists, removing it first")
                logger.remove(filename)
            else:
                print("File alread exists. Set the --overwrite flag to overwrite it.")

        logger.upload_dir(UploadArgs.source, filename, excludes=tuple(), archive="tar")
        print("Uploading completed")

        if not UploadArgs.archive:
            logger.shell(f"mkdir -p {dirname} && tar -xvf {filename} --directory {dirname}")
            logger.remove(filename)
            print("Decompressed the archive on the server")


if __name__ == "__main__":
    # UploadArgs.list = True
    # UploadArgs.overwrite = True
    # UploadArgs.archive = False
    # UploadArgs.target = "/fast_nerf/fast_nerf/panda_exp/2023/ge_upload_example/"
    # UploadArgs.prefix = os.path.expandvars("/fast_nerf/fast_nerf/panda_exp/2022")
    # UploadArgs.output = os.path.expandvars("$DATASETS/panda_exp/2022")
    entrypoint()
