echo "Downloading geckodriver..."
wget https://github.com/mozilla/geckodriver/releases/download/v0.16.0/geckodriver-v0.16.0-linux64.tar.gz
tar zxvf geckodriver-v0.16.0-linux64.tar.gz
export PATH=$PATH:$(pwd)

echo "Check photos & captions..."
echo "Download first 10 photos and captions of account 'instagram'"
python instagramcrawler.py -q 'instagram' -n 20 -c

echo "Check hashtag..."
echo "Search for hashtag '#breakfast' and download 20 photos"
python instagramcrawler.py -q '#breakfast' -n 20
