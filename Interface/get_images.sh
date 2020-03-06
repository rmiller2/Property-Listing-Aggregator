#!/bin/bash

counter=0

while IFS= read -r url;do
    fileName="/Users/richardmiller/Documents/website_file_storage/"$2"_"$counter".jpg" 
    wget -O "$fileName" "$url"
    counter=$((counter+1))
done < $1




