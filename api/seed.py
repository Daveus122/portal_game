import requests
import time
import os
from datetime import datetime
from models import SessionLocal, Game, Tag, engine, Base
from sqlalchemy import text

STEAM_KEY = os.environ.get("STEAM_KEY", "")

APP_LIST_URL = (
    f"https://api.steampowered.com/IStoreService/GetAppList/v1/"
    f"?key={STEAM_KEY}&max_results=50000&include_games=true&include_dlc=false"
)

APPDETAIL_URL = "https://store.steampowered.com/api/appdetails"


# =========================
# TAGS
# =========================
def get_or_create_tag(session, name):
    if not name:
        return None

    name = name.lower().strip()

    tag = session.query(Tag).filter_by(name=name).first()

    if tag is None:
        tag = Tag(name=name)
        session.add(tag)
        session.flush()

    return tag


# =========================
# FECHA
# =========================
def parse_date(text):
    formatos = [
        "%d %b, %Y",
        "%b %Y",
        "%Y",
        "%d de %b. de %Y"
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(text, fmt).date()
        except:
            pass

    return None


# =========================
# PLATAFORMAS
# =========================
def get_platforms(p):
    plats = []

    if p.get("windows"):
        plats.append("Windows")

    if p.get("mac"):
        plats.append("Mac")

    if p.get("linux"):
        plats.append("Linux")

    if len(plats) == 0:
        return "PC"

    return ", ".join(plats)


# =========================
# DETAIL GAME
# =========================
def fetch_detail(appid):
    try:
        r = requests.get(
            APPDETAIL_URL,
            params={
                "appids": appid,
                "l": "spanish"
            },
            timeout=15
        )

        data = r.json().get(str(appid), {})

        if data.get("success") == False:
            return None

        return data.get("data")

    except:
        return None


# =========================
# SEED
# =========================
def seed(max_games=5000):

    Base.metadata.create_all(engine)

    session = SessionLocal()

    try:

        total_actual = session.query(Game).count()

        print(f"🎮 Juegos actuales en DB: {total_actual}")

        if total_actual > 0:
            print("🧹 Limpiando juegos antiguos...")

            session.execute(text("DELETE FROM game_tags"))
            session.execute(text("DELETE FROM games"))
            session.execute(text("DELETE FROM tags"))

            session.commit()

        if STEAM_KEY == "":
            print("❌ NO HAY STEAM_KEY")
            print("👉 Crea una aquí:")
            print("https://steamcommunity.com/dev/apikey")
            return

        print("🌐 Descargando lista gigante de Steam...")

        r = requests.get(APP_LIST_URL, timeout=60)

        apps = r.json().get("response", {}).get("apps", [])

        print(f"📦 Apps encontradas: {len(apps)}")

        count = 0

        for app in apps:

            if count >= max_games:
                break

            appid = app.get("appid")

            if appid is None:
                continue

            existe = session.query(Game).filter_by(id=appid).first()

            if existe:
                continue

            detail = fetch_detail(appid)

            if detail is None:
                continue

            if detail.get("type") != "game":
                continue

            nombre = detail.get("name", "")

            if nombre == "":
                continue

            print(f"🎮 [{count+1}/{max_games}] {nombre}")

            price_data = detail.get("price_overview")

            if price_data:
                price = price_data.get("final_formatted", "Free")
            else:
                price = "Free"

            genres = []

            for g in detail.get("genres", []):
                genres.append(g.get("description", ""))

            genre_text = ", ".join(genres[:3])

            game = Game(
                id=appid,
                title=nombre,
                thumbnail=detail.get("header_image", ""),
                short_description=detail.get("short_description", ""),
                game_url=f"https://store.steampowered.com/app/{appid}",
                genre=genre_text,
                platform=get_platforms(detail.get("platforms", {})),
                publisher=", ".join(detail.get("publishers", [])[:1]),
                developer=", ".join(detail.get("developers", [])[:1]),
                release_date=parse_date(
                    detail.get("release_date", {}).get("date", "")
                ),
                price=price,
            )

            session.add(game)
            session.flush()

            # =========================
            # TAGS
            # =========================
            tag_names = set()

            for g in detail.get("genres", []):
                tag_names.add(g.get("description", "").lower())

            for c in detail.get("categories", []):
                tag_names.add(c.get("description", "").lower())

            for plat in ["windows", "mac", "linux"]:

                if detail.get("platforms", {}).get(plat):

                    if plat == "windows":
                        tag_names.add("windows")

                    if plat == "mac":
                        tag_names.add("mac")

                    if plat == "linux":
                        tag_names.add("linux")

            for name in tag_names:

                if name != "":

                    t = get_or_create_tag(session, name)

                    if t not in game.tags:
                        game.tags.append(t)

            count += 1

            # guardar cada 50
            if count % 50 == 0:
                session.commit()
                print(f"💾 Guardados {count} juegos")

            time.sleep(0)

        session.commit()

        print("")
        print("===================================")
        print(f"✅ TERMINADO")
        print(f"🎮 Juegos insertados: {count}")
        print("===================================")

    except Exception as e:

        session.rollback()

        print("")
        print("❌ ERROR:")
        print(e)

    finally:
        session.close()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    seed(max_games=200)