#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2025
#            ✈ https://t.me/unneyon

# 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0
# + attribution
# + non-commercial
# + no-derivatives

import hashlib
import io
import json
import os
import re
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

config = json.loads(open("config.json", "r", encoding="utf-8").read())

def get_mod_names(dir: str = "code"):
    return [
        ".".join(x.split(".")[:-1]) for x in os.listdir(f"mods/{dir}")
    ]


def get_mods(dir: str = "code"):
    mod_names = get_mod_names()
    mods = []

    for mod in mod_names:
        code = open(f"mods/code/{mod}.py", "r").read()

        sha1 = hashlib.sha1()
        sha1.update(code.encode("utf-8"))

        try:
            pic = re.search(
                r"# ?meta pic: ?(https?://.*?)\n", code, re.S
            ).group(1)
        except Exception:
            pic = f"https://{config['url']}/basic_icon.png"

        try:
            description = re.search(
                r"# ?meta desc: ?(https?://.*?)\n", code, re.S
            ).group(1)
        except Exception:
            try:
                description = re.search(
                    r'class .+?Mod\(.*?Module\):.*?\n[ \t]*[\'"]{1,3}(.+?)[\'"]{1,3}',
                    code,
                    re.S,
                ).group(1)
            except Exception:
                description = "No description"

        commands = re.findall(r"async def ([^\n]+?)cmd\(self,", code, re.S)
        commands.sort()
        commands = [f".{i}" for i in commands]

        mods.append(
            {
                "sha": str(sha1.hexdigest()),
                "name": mod,
                "pic": pic,
                "desc": description,
                "link": f"https://{config['url']}/{mod}.py",
                "lines": code.count("\n") + 1,
                "chars": len(code),
                "cws": len(code) - sum(len(_) for _ in re.findall(r'(""".*?""")|(#.*)', code)),
                "file": mod+".py",
                "commands": commands
            }
        )

    return mods


@app.get("/banners/{mod}.png")
async def get_banner(request: Request, mod: str):
    file = f"mods/banners/{mod}.png"
    if mod not in get_mod_names("banners"):
        file = "static/basic_banner.png"

    return StreamingResponse(
        content=io.BytesIO(open(file, "rb").read()),
        status_code=200
    )


@app.get("/basic_icon.png")
async def get_icon(request: Request):
    return StreamingResponse(
        content=io.BytesIO(open("static/basic_icon.png", "rb").read()),
        status_code=200
    )


@app.get("/full.txt")
async def get_full(request: Request):
    return PlainTextResponse(
        content="\n".join(get_mod_names()),
        status_code=200
    )


@app.get("/{mod}.py")
async def get_raw_mod(request: Request, mod: str):
    if mod not in get_mod_names():
        return JSONResponse(
            content={
                "ok": False,
                "message": "Not found"
            },
            status_code=404
        )

    return PlainTextResponse(
        content=open(f"mods/code/{mod}.py", "r").read(),
        status_code=200
    )


@app.get("/view/{mod}.py")
async def get_mod(request: Request, mod: str):
    if mod not in get_mod_names():
        return JSONResponse(
            content={
                "ok": False,
                "message": "Not found"
            },
            status_code=404
        )

    return templates.TemplateResponse(
        "view.html",
        {
            "request": request,
            "mod_name": mod,
            "mod_code": open(f"mods/code/{mod}.py", "r").read(),
            "mod_icon": "https://" + config['url'] + f"/icon/{mod}.png",
            "url": config['url'],
            "sitename": config['sitename']
        }
    )


@app.get("/")
async def get_all_mods(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "mods": get_mods(),
            "url": config['url'],
            "sitename": config['sitename'],
            "description": config['description'],
            "site_icon": config['site_icon']
        }
    )


if __name__ == "__main__":
    print(f"\033[36m          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █\033[0m")
    print(f"\033[36m          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄\033[0m")
    print(f"\033[36m                © Copyright 2025\033[0m")
    print(f"\033[36m            ✈ https://t.me/unneyon\033[0m", end="\n\n")
    print(f"\033[36m 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.\033[0m")
    print(f"\033[36m 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0\033[0m")
    print(f"\033[36m + attribution\033[0m")
    print(f"\033[36m + non-commercial\033[0m")
    print(f"\033[36m + no-derivatives\033[0m", end="\n\n")
    print(f"\033[36mСайт [FTG WEB mods] успешно запущен!\033[0m")

    uvicorn.run(app, host="0.0.0.0", port=config['port'])