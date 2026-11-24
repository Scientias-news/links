#!/usr/bin/env python3
"""Linkpagina (link in bio) bijwerken: zet een post bovenaan posts.json en maakt een kleine afbeelding.

  python3 linkpagina.py toevoegen --id 267860 --titel "..." --rubriek Psychologie \
      --url https://scientias.nl/... --beeld pad/naar/01.jpg [--datum 2026-11-24T21:30]
  python3 linkpagina.py lijst

Houdt de nieuwste 60 posts. Een artikel-ID dat er al in staat, wordt bijgewerkt en naar boven gezet.
Daarna: git add posts.json img/ && git commit && git push (GitHub Pages publiceert automatisch).
"""
import argparse, json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(HIER, "posts.json")
MAX = 60


def laad():
    return json.load(open(POSTS)) if os.path.exists(POSTS) else []


def bewaar(posts):
    json.dump(posts[:MAX], open(POSTS, "w"), ensure_ascii=False, indent=1)
    houden = {p["beeld"] for p in posts[:MAX]}
    for f in os.listdir(os.path.join(HIER, "img")):
        if f"img/{f}" not in houden:
            os.remove(os.path.join(HIER, "img", f))


def toevoegen(a):
    os.makedirs(os.path.join(HIER, "img"), exist_ok=True)
    im = Image.open(a.beeld).convert("RGB")
    im.thumbnail((720, 960))
    naam = f"img/{a.id}.jpg"
    im.save(os.path.join(HIER, naam), quality=80, optimize=True, progressive=True)
    datum = a.datum or datetime.now(ZoneInfo("Europe/Amsterdam")).strftime("%Y-%m-%dT%H:%M")
    post = {"id": str(a.id), "datum": datum, "titel": a.titel, "rubriek": a.rubriek, "url": a.url, "beeld": naam}
    posts = [p for p in laad() if p["id"] != str(a.id)]
    posts.insert(0, post)
    posts.sort(key=lambda p: p["datum"], reverse=True)
    bewaar(posts)
    print(f"OK linkpagina: {a.titel[:60]} ({len(posts[:MAX])} posts)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    t = sub.add_parser("toevoegen")
    for k in ("id", "titel", "rubriek", "url", "beeld"):
        t.add_argument("--" + k, required=True)
    t.add_argument("--datum")
    sub.add_parser("lijst")
    a = p.parse_args()
    if a.cmd == "toevoegen":
        toevoegen(a)
    elif a.cmd == "lijst":
        for x in laad():
            print(x["datum"], x["id"], x["titel"][:70])
    else:
        p.print_help()
