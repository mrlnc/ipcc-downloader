#!/usr/bin/python3
import re
import os
import urllib.request
import argparse
import threading
from queue import Queue

# thread function
def download_file(queue: Queue, output_dir: str):
    while True:
        try:
            url = queue.get(block=False)
        except:
            break
        if url is None:
            break

        # use file name and parent directory as file name
        filename = "_".join(url.split("/")[-2:])
        print("Downloading %s" % url)
        try:
            urllib.request.urlretrieve(url, f"{output_dir}/{filename}")
        except:
            print(f"Error downloading {url}")
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

    if args.download_all == True:
        print(f"Starting download of {len(urls)} files.")

        queue = Queue()
        # each URL is a job
        for i, url in enumerate(urls):
            queue.put(url)
        # start some workers
        for i in range(args.workers):
            threading.Thread(target=download_file, args=(queue, args.output_dir)).start()

        # wait until all tasks are done
        queue.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', default="ipcc_index.xml", type=str, help="Input file")
    parser.add_argument('-o', '--output-dir', default="data", type=str, help="Output directory")
    parser.add_argument('-d', '--download-all', default=False, action="store_true", help="Download all IPCC files (may take some time)")
    parser.add_argument('-w', '--workers', default="8", type=int, help="Number of parallel download threads")

    args = parser.parse_args()
    main(args)