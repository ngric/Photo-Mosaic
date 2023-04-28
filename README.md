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
