# Cub-200-Scripts

Collection of all scripts / data used for gathering information about all 200 birds
listed in the CUB-200 Dataset

Since different naming patterns are used depending on the site, different text files
exist depending on the used API:

1. `en_names.txt`: This corresponds to xeno-cantos English names for all 200 birds and is used for all filename purposes
   across this repository
2. `xeno-canto-names.txt`: These are the names used for downloading from xeno-canto. Since the API does a partial
   matching on names, some birds are referenced by their scientific name
3. `botw-names.txt`: Mostly localization differenzes (e.g gray -> grey)
4. `CUB-200-names.txt`: The class labels as found in the CUB-200 dataset

## Additional Info

Additional infos regarding differences in species, ambiguous bird names etc can be found in `Additional Data/`

## Running the BOTW-Webscraper

1. Install all packages
2. Inside the working folder, create a .env with your login data (Required!)
3. Select whether to install pdfs, textfiles or both
4. Run the script

## Running the Xeno-Canto-Downloader

1. Install all packages
2. Run the script (This stores all audio files and meta-files inside the current working directory (separate folders)
   and also keeps track of bird_names which are ambiguous or have a limited number of recordings)