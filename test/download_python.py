import argparse
from pathlib import Path
import requests

BASE_DIR = Path(__file__).absolute().parent.parent


def main(python_exe_name, python_version):
    print("Getting latest release information...")
    if python_version == "2.7":
        url = ("https://api.github.com/repos/masamitsu-murase"
               "/single_binary_stackless_python/releases/10437463")
    elif python_version == "3.6":
        url = ("https://api.github.com/repos/masamitsu-murase"
               "/single_binary_stackless_python/releases/19680526")
    elif python_version == "3.7":
        url = ("https://api.github.com/repos/masamitsu-murase"
               "/single_binary_stackless_python/releases/43930570")
    else:
        url = ("https://api.github.com/repos/masamitsu-murase"
               "/single_binary_stackless_python/releases/latest")
    response = requests.get(url)
    latest_release_info = response.json()

    print(f"Finding {python_exe_name}...")
    exe_url = next(x for x in latest_release_info["assets"]
                   if x["name"] == python_exe_name)["browser_download_url"]

    print(f"Downloading {python_exe_name}...")
    response = requests.get(exe_url,
                            headers={"Accept": "application/octet-stream"})

    with (BASE_DIR / python_exe_name).open("wb") as file:
        file.write(response.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("python_exe_name")
    parser.add_argument("python_version", type=str)
    args = parser.parse_args()
    main(args.python_exe_name, args.python_version)
