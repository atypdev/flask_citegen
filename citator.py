from flask import Flask
from flask import request
from datetime import date
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

app = Flask(__name__)
PARSER = "html.parser"


@app.route("/")
def index():
    link = str(request.args.get("link", ""))
    format = int(request.args.get("format", 1))
    generated = ""
    if link and format != 4:
        generated = generate(link, format)
    return f"""
    <head>
        <link rel="stylesheet" href="static/style.css">
    </head>
    <h1>Citation Generator</h1>
    <br>
    <form action="" method="get">
        <b>1. Insert Your Link: </b>
        <input type="text" placeholder="https://example.com" name="link"><br>
        <b>2. Select a Format: </b>
        <select name="format" id="format">
            <option value="1">1: author (published_date). title. site_name. publisher. url.</option>
            <option value="2">2: author (published_date). title. site_name. publisher. Retrieved access_date, from url.</option>
            <option value="3">3: author (published_date). title. site_name. publisher. url. Accessed access_date.</option>
            <option value="4">Debug Mode</option>
        </select>
        <input type="submit" value="Generate"><br>
    </form>
    """ + (
        f"""
        <b>Provided Link:</b> {link}<br>
        <b>Selected Mode: </b>{format}<br>
        <h2>Your Citation:</h2>
        <p class='container'>{generated}</p>
        <footer>flask_citegen v0.1</footer>
        """
        if link
        else ""
    )


def generate(url, format):
    # get page
    try:
        page = requests.get(url)
    except requests.exceptions.MissingSchema:
        return "<span style='color:red'>Invalid URL: please try again with a valid URL.</span>"
    soup = BeautifulSoup(page.content, PARSER)

    # get title
    title = soup.find("title").string

    # get site name
    link = urlparse(url)
    try:
        site_name = link.netloc.split("@")[-1].split(":")[0].capitalize()
    except (TypeError, KeyError):
        site_name = "Unknown"

    # get author
    try:
        author = soup.find("meta", {"name": "author"})["content"]
    except (TypeError, KeyError):
        author = site_name

    # get date
    try:
        published_date = soup.find("meta", {"name": "date"})["content"]
    except (TypeError, KeyError):
        published_date = "n.d."

    # get publisher
    try:
        publisher = soup.find("meta", {"name": "publisher"})["content"] + ". "
    except (TypeError, KeyError):
        publisher = ""

    # get access date
    access_date = date.today().strftime("%B %d, %Y")

    # get citation
    # 1: author (published_date). title. site_name. publisher. url.
    if format == 1:
        return f"{author} ({published_date}). <i>{title}</i>. {site_name}. {publisher} {url}."
    # 2: author (published_date). title. site_name. publisher. Retrieved access_date, from url.
    elif format == 2:
        return f"{author} ({published_date}). <i>{title}</i>. {site_name}. {publisher} Retrieved {access_date}, from <a href='{url}'>{url}</a>."
    # 3: author (published_date). title. site_name. publisher. url. Accessed access_date.
    elif format == 3:
        return f"{author} ({published_date}). <i>{title}</i>. {site_name}. {publisher} {url}. Accessed {access_date}."
    # debug mode
    elif format == 4:
        return f"Author: {author}<br>Published Date: {published_date}<br>Title: {title}<br>Site Name: {site_name}<br>Publisher: {publisher}<br>URL: {url}<br>Accessed: {access_date}"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
