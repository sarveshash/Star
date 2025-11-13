import requests

url = "https://files.catbox.moe/491yle.mp4"
filename = "491yle.mp4"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0 Safari/537.36"
}

try:
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print("Download success:", filename)

except Exception as e:
    print("Download failed:", e)
