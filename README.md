# Photo Mosaic Generator
CS445 Final Project

## Scraper

``` shell
usage: scraper.py [-h] (-q QUERY | -f FILE)
```

To download ~400 images for each us president, you can use the `queries` file provided, and images will be saved to the `images` directory:
``` shell
python scraper.py -f queries
```

alternatively, if you don't want to download all 18400 images:
``` shell
python scraper.py -q "George Washington"
```

#### Results of above operation available [here](https://drive.google.com/drive/folders/1HODufez2f0zsSry19U79UyZYS7hi9iIn?usp=sharing)

## Cloud Function

The cloud function can be accessed via curl. Required variables are search_query: What mosaic should be composed of, target_url: what mosaic should look like, and receiver: email address that mosaic should be sent to.


``` shell
curl --location 'https://gis-search-anfpnmc32a-uc.a.run.app' \
--header 'Content-Type: application/json' \
--data-raw '{
  "target_image": "YOUR TARGET IMAGE URL HERE",
  "search_query": "YOUR QUERY HERE",
  "receiver": "YOUR EMAIL HERE"
}'
```
