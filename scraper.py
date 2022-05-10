import re
import json
import time
import requests

def getMangaData(mangaLink):
    res = requests.get(mangaLink)
    html = res.text
    data = {}
    
    def getDataFromExpression(expression):
        match = re.search(expression, html)
        return match.group(1).strip()

    title = getDataFromExpression(r'<div class="post-title">[\s\S]+<h1>\s+([^<]+)')
    summary = getDataFromExpression(r'<div class="summary__content ">[\s\S]+?<p>([\s\S]+?)<\/p>')
    cover = getDataFromExpression(r'<div class="summary_image">[\s\S]+?src="([^"]+)')
    author = getDataFromExpression(r'<div class="author-content">[\s\S]+?>([^<]+)')

    data['title'] = title
    data['volume'] = 1
    data['author'] = author
    data['artist'] = author
    data['description'] = summary
    data['cover'] = cover
    data['chapters'] = {}
    
    chapterExpr = r'<li class="wp-manga-chapter\s*">[^<]+<a\shref="([^"]+)'
    chapters = re.findall(chapterExpr, html)

    for chapterLink in chapters:
        res = requests.get(chapterLink)
        html = res.text
        chapterData = {}
        
        chapterIndexExpr = r'(\d+)[^\/]*\/$'
        match = re.search(chapterIndexExpr, chapterLink)
        chapterIndex = match.group(1)
        
        imageDataExpr = r'<img id="image-(\d+)" src="[^h]+([^"]+)'
        imageMatches = re.findall(imageDataExpr, html)
        images = []

        for imgMatch in imageMatches:
            index = int(imgMatch[0])
            imgLink = imgMatch[1]
            images.insert(index, imgLink)

        chapterData["groups"] = {}
        chapterData["groups"]["Colored Council"] = images
        chapterData['last_updated'] = str(int(time.time())) # TODO: scrape time
        data['chapters'][chapterIndex] = chapterData

    return data

if __name__ == "__main__":   
    mangaData = getMangaData("https://coloredmanga.com/manga/kingdom/")

    with open("kingdom_metadata.json", "w") as file:
        json.dump(mangaData, file, indent=4)

#https://cubari.moe/gist/raw.githubusercontent.com/<rest of the url...>