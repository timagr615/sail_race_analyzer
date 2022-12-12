sudo rm -rf postgres_data
sudo rm -rf storage
# shellcheck disable=SC2164
cd migrations
sudo rm -rf versions
mkdir versions