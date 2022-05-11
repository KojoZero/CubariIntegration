import os
import re
import json
import time
import requests
import html

def getMangaData(mangaLink, ref=None):
    res = requests.get(mangaLink)
    htmlvar = res.text
    data = {}
    
    def getDataFromExpression(expression):
        match = re.search(expression, htmlvar)
        return match.group(1).strip()

    title = html.unescape(getDataFromExpression(r'<div class="post-title">[\s\S]+<h1>\s+([^<]+)'))
    summary = getDataFromExpression(r'<div class="summary__content ">[\s\S]+?<p>([\s\S]+?)<\/p>')
    cover = getDataFromExpression(r'<div class="summary_image">[\s\S]+?src="([^"]+)')
    
    try:
        author = getDataFromExpression(r'<div class="author-content">[\s\S]+?>([^<]+)')
    except:
        author = ""

    data['title'] = title
    data['volume'] = 1
    data['author'] = author
    data['artist'] = author
    data['description'] = summary
    data['cover'] = cover
    data['chapters'] = {}
    
    chapterExpr = r'<li class="wp-manga-chapter\s*">[^<]+<a\shref="([^"]+)'
    chapters = re.findall(chapterExpr, htmlvar)

    for chapterLink in chapters:
        chapterData = {}
        
        chapterIndexExpr = r'(\d+(?:\.\d+)*)[^\/]*\/$'
        match = re.search(chapterIndexExpr, chapterLink)
        chapterIndex = match.group(1)
        
        if ref:
            chapterData = ref['chapters'].get(chapterIndex) or {}

        if not chapterData:
            res = requests.get(chapterLink)
            htmlvar = res.text
            
            chapterHeaderExpr = r'id="chapter-heading">([^<]+)</h'
            match = re.search(chapterHeaderExpr, htmlvar)
            chapterHeader = match.group(1)

            chapterNameExpr = r'[\s\S]+-(.+)'
            match = re.search(chapterNameExpr, chapterHeader)
            chapterName = match.group(1).strip()

            imageDataExpr = r'<img id="image-(\d+)" src="[^h]+([^"]+)'
            imageMatches = re.findall(imageDataExpr, htmlvar)
            images = []

            for imgMatch in imageMatches:
                index = int(imgMatch[0])
                imgLink = imgMatch[1]
                images.insert(index, imgLink)

            chapterData["title"] = chapterName
            chapterData["groups"] = {}
            chapterData["groups"]["Colored Council"] = images
        
        chapterData['last_updated'] = str(int(time.time())) # TODO: scrape time
        data['chapters'][chapterIndex] = chapterData

    return data

if __name__ == "__main__":   
    res = requests.get("https://coloredmanga.com/")
    htmlvar = res.text
    seriesExpr = r'<h3[^>]+>[^<]*<a\s+href="(https:\/\/coloredmanga.com\/manga\/[^"\/]+)["\/]'
    seriesMatches = set(re.findall(seriesExpr, htmlvar))

    for series in seriesMatches:
        print("LOADING MANGA DATA FOR", series)

        seriesNameExpr = r'.+\/(.+)'
        match = re.search(seriesNameExpr, series)
        seriesName = match.group(1)

        ref = None
        outputPath = "./json/" + seriesName + ".json"

        if os.path.exists(outputPath):
            with open(outputPath) as file:
                ref = json.load(file)

        try:
            mangaData = getMangaData(series, ref)
            print("LOADED MANGA DATA FOR", series)

            with open(outputPath, "w") as file:
                json.dump(mangaData, file, indent=4)

            print("EXPORTED TO", outputPath)
        except Exception as e:
            print("FAILED TO LOAD MANGA FOR", series)
            print("EXCEPTION:", e)
            print()

        
        
    # https://cubari.moe/gist/https://raw.githubusercontent.com/KojoZero/CubariIntegration/master/json/kingdom_metadata.json