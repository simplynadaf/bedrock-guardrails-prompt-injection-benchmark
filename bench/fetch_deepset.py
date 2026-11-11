"""Download deepset/prompt-injections (Apache-2.0) at run time; it is not redistributed in this repo."""
import pathlib, urllib.request
URL = "https://huggingface.co/datasets/deepset/prompt-injections/resolve/main/data/train-00000-of-00001-9564e8b05b4757ab.parquet"
DEST = pathlib.Path(__file__).resolve().parent.parent / "data" / "deepset.parquet"
if not DEST.exists():
    DEST.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve(URL, DEST)
print(DEST, DEST.stat().st_size, "bytes")
