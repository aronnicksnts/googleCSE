# About
Uses Google's Custom Search Engine to scrape images

# Prerequisites

## data.json
Add this file to the repository and add your own [google's custom search API](https://developers.google.com/custom-search/v1/introduction)
and your own [search engine](https://programmablesearchengine.google.com/controlpanel/create)

Afterwards, the ID and API into the *data.json* file as such
<pre><code>
{
    "customSearchAPI": "yourCustomSearchAPI",
    "searchEngineID": "yourSearchEngineID" 
    "imageQuery": "yourSearchQuery",
    "numberOfImages": 1000,
    "startingPageNumber": 1
}
</code></pre>