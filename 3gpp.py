import os
import requests

# Create a folder to save PDFs
save_folder = "3gpp_specs"
os.makedirs(save_folder, exist_ok=True)


# List of 3GPP specifications (Release 17)
pdf_urls = [
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.321/38321-g50.zip",  # MAC Layer
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.331/38331-g50.zip",  # RRC
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.211/38211-g50.zip",  # PHY Channels & Modulation
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.212/38212-g50.zip",  # PHY Multiplexing & Coding
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.213/38213-g50.zip",  # PHY Layer Control
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.214/38214-g50.zip",  # PHY Data Procedures
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.300/38300-g50.zip",  # 5G Architecture
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.305/38305-g50.zip",  # NG-RAN Description
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.306/38306-g50.zip",  # UE Capabilities
    "https://www.3gpp.org/ftp/Specs/archive/38_series/38.323/38323-g50.zip"   # PDCP
]


def download_file(url, folder):
    """Download a file from a given URL."""
    filename = os.path.join(folder, url.split("/")[-1])
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed to download: {url}")


# Download all specified 3GPP PDFs
for url in pdf_urls:
    download_file(url, save_folder)
