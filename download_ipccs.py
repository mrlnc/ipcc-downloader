#!/usr/bin/env python3
import re
import os
from pathlib import Path
import urllib.request
import zipfile
import argparse
from multiprocessing.pool import ThreadPool
from tqdm import tqdm

INDEX_URL = "https://itunes.com/version"

RESULT_SUCCESS = 0
RESULT_FILE_EXISTS = 1
RESULT_ERROR = 2

# thread worker function
def download_file(url: str):
    output_dir = "data/"

    # use file name and parent directory as file name
    filename = "_".join(url.split("/")[-2:])
    if Path(f"{output_dir}/{filename}").exists():
        return RESULT_FILE_EXISTS

    try:
        urllib.request.urlretrieve(url, f"{output_dir}/{filename}")
        return RESULT_SUCCESS
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return RESULT_ERROR

def unzip_file(ipcc_path):
    ipcc_dir = f"{ipcc_path}-dir"
    if Path(ipcc_dir).exists():
        # already unzipped, skipping
        return RESULT_FILE_EXISTS

    try:
        with zipfile.ZipFile(ipcc_path) as zip:
            zip.extractall(ipcc_dir)
        return RESULT_SUCCESS
    except zipfile.BadZipFile:
        print(f"Error unzipping {ipcc_path}: File is not a zip file")
        return RESULT_ERROR
    except Exception as e:
        print(f"Error unzipping {ipcc_path}: {e}")
        return RESULT_ERROR

def main(args):
    urls = []
    if args.input_file != None:
        print(f"Reading file: {args.input_file}")
        fh = open(args.input_file, "r")
    else:
        print(f"Reading Carrier Bundle index from: {INDEX_URL}")
        fh = urllib.request.urlopen(INDEX_URL)

    # extract URLs from the XML
    for line in fh.readlines():
        if type(line) != str:
            line = line.decode('utf-8')

        results = re.findall("(http[s]?://.*\.ipcc)", line)
        if results == None:
            continue

        for result in results:
            urls.append(result)

    # de-duplicate entries
    urls = set(urls)
    urls = sorted(urls)
    print(f"Found {len(urls)} URLs")

    try:
        os.mkdir(args.output_dir)
    except FileExistsError:
        pass

    # store URLs
    output_path = f"{args.output_dir}/ipcc_urls.txt"
    print(f"Writing URLs to file: {output_path}")
    with open(output_path, "w") as output_file:
        for url in urls:
            print(url, file=output_file)

    if args.download_all == False:
        print(f"Finished. To download IPCC files, re-run with arguments: '-i {args.output_dir}/ipcc_urls.txt -d'")
        return

    print(f"Starting download of {len(urls)} files.")

    with tqdm(total=len(urls), desc="Downloading Files") as pbar:
        def update_pbar(*args):
            pbar.update()

        pool = ThreadPool(6)
        results = pool.imap(download_file, urls)
        for _ in results:
            update_pbar()

    print(f"All files downloaded.")

    p = Path("data/")
    ipcc_files = list(p.glob('**/*ipcc'))

    with tqdm(total=len(ipcc_files), desc="Unzipping Files") as pbar:
        def update_pbar(*args):
            pbar.update()

        pool = ThreadPool(6)
        results = pool.imap(unzip_file, ipcc_files)
        for _ in results:
            update_pbar()

    print(f"All files unzipped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', default=None, type=str, help=f"Index file. If unspecified, downloads index from {INDEX_URL}")
    parser.add_argument('-o', '--output-dir', default="data", type=str, help="Output directory")
    parser.add_argument('-d', '--download-all', default=False, action="store_true", help="Download all IPCC files (may take some time)")
    args = parser.parse_args()

    main(args)
