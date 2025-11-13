import requests

def download_file(url: str, local_filename: str):
    try:
        # streaming to avoid loading entire file into memory if large
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # will raise HTTPError for bad responses
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        print(f"Downloaded successfully: {local_filename}")
    except Exception as e:
        print(f"Failed to download. Error: {e}")

if __name__ == "__main__":
    url = "https://files.catbox.moe/491yle.mp4"
    local_filename = "491yle.mp4"
    download_file(url, local_filename)
