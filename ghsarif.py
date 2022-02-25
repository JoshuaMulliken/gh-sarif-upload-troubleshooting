#!/usr/bin/python3
import gzip
import base64
import requests
import argparse

def upload(args, github_tkn):
    with open(args.fname, "rb") as f_in:
        gzipped = gzip.compress(f_in.read())
        base64d = base64.b64encode(gzipped)

    payload = {"commit_sha": args.sha,
               "ref": args.ref, "sarif": base64d.decode()}
    headers = {
        "Authorization": "token {}".format(github_tkn),
        "User-Agent": "Joshs-Sarif-Uploader",
        "Accept": "application/vnd.github.v3+json",
    }
    url = "https://api.github.com/repos/{}/{}/code-scanning/sarifs".format(args.owner, args.repo)

    r = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=20,
    )
    print(r.status_code)
    response = r.json()

    id = response["id"]
    print("Uploaded with id: {}".format(id))

    url = response["url"]
    print(url)


def check(args, github_tkn):
    url = "https://api.github.com/repos/{}/{}/code-scanning/sarifs/{}".format(args.owner, args.repo, args.id)

    headers = {
        "Authorization": "token {}".format(github_tkn),
        "User-Agent": "Joshs-Sarif-Uploader",
        "Accept": "application/vnd.github.v3+json",
    }

    r = requests.get(
        url,
        headers=headers,
        timeout=20,
    )
    print(r.status_code)
    print(r.json())


parser = argparse.ArgumentParser(prog="ghsarif")
parser.add_argument("owner", help="Organization or user")
parser.add_argument("repo", help="Repo")
subparsers = parser.add_subparsers()
upload_parser = subparsers.add_parser("upload", help="Upload a SARIF file")
upload_parser.add_argument("fname", help="Filename of SARIF file to upload")
upload_parser.add_argument("sha", help="Sha of commit")
upload_parser.add_argument("ref", help="Ref of branch/pr")
upload_parser.set_defaults(func=upload)
check_parser = subparsers.add_parser(
    "check", help="Check the status of a SARIF file")
check_parser.add_argument(
    "id", help="id of SARIF file given by the upload command")
check_parser.set_defaults(func=check)

args = parser.parse_args()

github_tkn = input("Github token: ")

args.func(args, github_tkn)
