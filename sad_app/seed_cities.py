import asyncio
from db import get_db

data = [
    {"pais": "CO", "ciudad": "Bogotá"},
    {"pais": "CO", "ciudad": "Bucaramanga"},
    {"pais": "CO", "ciudad": "Medellín"},
    {"pais": "CO", "ciudad": "Cali"},
    {"pais": "US", "ciudad": "New York"},
    {"pais": "US", "ciudad": "San Francisco"},
    {"pais": "ES", "ciudad": "Madrid"},
    {"pais": "ES", "ciudad": "Barcelona"},
]

async def run():
    db = await get_db()
    docs = []
    for c in data:
        docs.append({
            "pais": c["pais"],
            "ciudad": c["ciudad"],
            "ciudad_lc": c["ciudad"].strip().lower()
        })
    await db.cities.delete_many({})
    await db.cities.insert_many(docs)
    print("Ciudades sembradas.")

if __name__ == "__main__":
    asyncio.run(run())
