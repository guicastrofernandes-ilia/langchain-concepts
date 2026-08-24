"""Bulk-insert 1000 random vinyl records directly via SQLAlchemy."""

import asyncio
import random
from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from record_catalog.database import Base
from record_catalog.models import Record

DB_URL = "postgresql+asyncpg://record_store:record_store_pass@localhost:5432/record_store"

ARTISTS = [
    "The Beatles", "Pink Floyd", "Led Zeppelin", "Queen", "David Bowie",
    "The Rolling Stones", "Nirvana", "Radiohead", "Miles Davis", "John Coltrane",
    "Jimi Hendrix", "Fleetwood Mac", "Bob Dylan", "The Doors", "Joy Division",
    "Stevie Wonder", "Marvin Gaye", "Michael Jackson", "Prince", "Björk",
    "Caetano Veloso", "Tom Jobim", "Gilberto Gil", "Elis Regina", "Gal Costa",
    "Milton Nascimento", "Chico Buarque", "Jorge Ben", "Tim Maia", "Cartola",
    "João Gilberto", "Novos Baianos", "Os Mutantes", "Legião Urbana", "Titãs",
    "Metallica", "AC/DC", "Black Sabbath", "Deep Purple", "Iron Maiden",
    "Aphex Twin", "Massive Attack", "Portishead", "Depeche Mode", "New Order",
    "The Smiths", "R.E.M.", "Sonic Youth", "Pixies", "The Cure",
    "Frank Sinatra", "Ella Fitzgerald", "Duke Ellington", "Charles Mingus",
    "Thelonious Monk", "Louis Armstrong", "John Coltrane", "Miles Davis",
    "J Dilla", "Madlib", "MF DOOM", "DJ Shadow", "Wu-Tang Clan",
    "A Tribe Called Quest", "Nas", "Run-DMC", "Public Enemy",
    "Caetano Veloso", "Gilberto Gil", "Chico Buarque", "Tom Jobim",
]

ALBUMS = [
    "The Dark Side of the Moon", "Led Zeppelin IV", "Nevermind",
    "OK Computer", "Kind of Blue", "A Love Supreme",
    "Electric Ladyland", "Rumours", "Highway 61 Revisited",
    "Unknown Pleasures", "Remain in Light",
    "Songs in the Key of Life", "What's Going On",
    "Thriller", "Purple Rain",
    "Homogenic", "Transa", "Wave", "Clube da Esquina",
    "Construção", "África Brasil", "Acabou Chorare",
    "Dois", "Cabeça Dinossauro", "Sobrevivendo no Inferno",
    "Master of Puppets", "Back in Black", "Paranoid", "Machine Head",
    "Mezzanine", "Dummy", "Violator", "The Queen Is Dead",
    "Daydream Nation", "Doolittle", "Disintegration", "Hounds of Love",
    "Donuts", "Madvillainy", "Endtroducing.....",
    "Enter the Wu-Tang (36 Chambers)", "The Low End Theory", "Illmatic",
    "Abbey Road", "Revolver", "Rubber Soul", "Sgt. Pepper's",
    "Wish You Were Here", "The Wall", "Station to Station",
]

GENRES = ["rock", "jazz", "samba", "mpb", "bossa nova", "rap", "electronic",
           "punk", "metal", "pop", "soul", "funk", "indie", "alternative",
           "hip hop", "r&b", "experimental", "blues", "folk"]

LABELS = ["Apple Records", "EMI", "Columbia", "Blue Note", "Verve",
           "Atlantic", "Warner Bros.", "Capitol", "Decca", "RCA Victor",
           "Philips", "Motown", "Stax", "Sony Music", "Universal",
           "Som Livre", "Odeon", "Continental", "Island Records", "4AD"]

CONDITIONS = ["mint", "excellent", "very_good", "good", "fair", "poor"]

TRACK_NAMES = ["Intro", "Morning Light", "Chasing Shadows", "Midnight Run",
               "Prelude", "Waves", "Echoes", "The Fall", "Rising",
               "Opening", "Drift", "Surge", "Calm", "Finale",
               "Dawn", "Noon", "Dusk", "Twilight", "Nightfall",
               "Interlude", "Resolution", "Outro"]


def random_tracks():
    n = random.randint(1, 5)
    names = random.sample(TRACK_NAMES, n)
    return [{"title": t, "duration": f"{random.randint(2, 7)}:{random.randint(0, 59):02d}"} for t in names]


def random_record():
    return Record(
        artist=random.choice(ARTISTS),
        album=random.choice(ALBUMS) + (" " + chr(65 + random.randint(0, 5)) if random.random() < 0.3 else ""),
        year=random.randint(1940, 2024),
        genre=random.choice(GENRES),
        label=random.choice(LABELS),
        condition=random.choice(CONDITIONS),
        tracks=random_tracks() if random.random() < 0.7 else None,
    )


async def main():
    engine = create_async_engine(DB_URL, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    seen = set()
    records = []
    while len(records) < 1000:
        rec = random_record()
        key = (rec.artist, rec.album)
        if key not in seen:
            seen.add(key)
            records.append(rec)

    created = 0
    start = datetime.now()

    BATCH = 50
    for i in range(0, len(records), BATCH):
        batch = records[i:i + BATCH]
        async with factory() as session:
            session.add_all(batch)
            try:
                await session.commit()
                created += len(batch)
            except Exception:
                await session.rollback()
                for rec in batch:
                    async with factory() as s2:
                        s2.add(rec)
                        try:
                            await s2.commit()
                            created += 1
                        except Exception:
                            await s2.rollback()
        if created % 100 == 0:
            elapsed = (datetime.now() - start).total_seconds()
            print(f"  {created}/1000... ({elapsed:.1f}s)")

    elapsed = (datetime.now() - start).total_seconds()
    print(f"Inserted {created} records in {elapsed:.1f}s ({created/elapsed:.0f} records/s)")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())