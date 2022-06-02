#!/usr/bin/python3
import re
import os
from pathlib import Path
import urllib.request
import argparse
import threading
from queue import Queue

DL_RESULT_SUCCESS = 0
DL_RESULT_FILE_EXISTS = 1
DL_RESULT_ERROR = 2

# thread function
def download_file(queue: Queue, output_dir: str, results: Queue):
    while True:
        try:
            url = queue.get(block=False)
        except:
            break
        if url is None:
            # we're done
            break

        # use file name and parent directory as file name
        filename = "_".join(url.split("/")[-2:])
        if Path(f"{output_dir}/{filename}").exists():
            # file exists, skipping
            queue.task_done()
            results.put(DL_RESULT_FILE_EXISTS)
            continue

        try:
            urllib.request.urlretrieve(url, f"{output_dir}/{filename}")
            results.put(DL_RESULT_SUCCESS)
        except:
            print(f"Error downloading {url}")
            results.put(DL_RESULT_ERROR)

        queue.task_done()

def main(args):
    urls = []
    print(f"Reading file: {args.input_file}")
    # extract URLs from the XML file
    with open(args.input_file, "r") as fh:
        for line in fh.readlines():
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
        return

    print(f"Starting download of {len(urls)} files.")
    queue = Queue()
    results = Queue()
    # each URL is a job
    for i, url in enumerate(urls):
        queue.put(url)

    # start some workers
    for i in range(args.workers):
        threading.Thread(target=download_file, args=(queue, args.output_dir, results)).start()

    # wait until all tasks are done
    queue.join()

    r = {}
    r[DL_RESULT_SUCCESS] = 0
    r[DL_RESULT_FILE_EXISTS] = 0
    r[DL_RESULT_ERROR] = 0
    while True:
        try:
            result = results.get(block=False)
        except:
            break
        if result == None:
            break
        r[result] += 1

    print(f"{r[DL_RESULT_SUCCESS]} files downloaded, {r[DL_RESULT_FILE_EXISTS]} already on disk, {r[DL_RESULT_ERROR]} errors")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', default="ipcc_index.xml", type=str, help="Input file")
    parser.add_argument('-o', '--output-dir', default="data", type=str, help="Output directory")
    parser.add_argument('-d', '--download-all', default=False, action="store_true", help="Download all IPCC files (may take some time)")
    parser.add_argument('-w', '--workers', default="8", type=int, help="Number of parallel download threads")

    args = parser.parse_args()
    main(args)
