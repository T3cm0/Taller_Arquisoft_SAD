import asyncio
import os
import time
import uuid
import uvloop
import grpc

from generated import wishlist_pb2 as pb
from generated import wishlist_pb2_grpc as pb_grpc
from db import get_db

class DataAdminService(pb_grpc.DataAdminServiceServicer):
    async def Ping(self, request, context):
        return pb.Empty()

    async def CreateUser(self, request: pb.CreateUserRequest, context):
        db = await get_db()
        user_id = str(uuid.uuid4())
        doc = {
            "_id": user_id,
            "nombre": request.nombre,
            "apellido": request.apellido,
            "extra": dict(request.extra)
        }
        await db.users.insert_one(doc)
        return pb.UserResponse(user=pb.User(
            id=user_id, nombre=doc["nombre"], apellido=doc["apellido"], extra=doc["extra"]
        ))

    async def UpsertUser(self, request: pb.UpsertUserRequest, context):
        db = await get_db()
        if request.id:
            # update
            to_set = {
                "nombre": request.nombre,
                "apellido": request.apellido,
                "extra": dict(request.extra)
            }
            await db.users.update_one({"_id": request.id}, {"$set": to_set}, upsert=True)
            user_id = request.id
        else:
            # create (sin id)
            user_id = str(uuid.uuid4())
            await db.users.insert_one({
                "_id": user_id,
                "nombre": request.nombre,
                "apellido": request.apellido,
                "extra": dict(request.extra)
            })
        doc = await db.users.find_one({"_id": user_id}) or {}
        return pb.UserResponse(user=pb.User(
            id=user_id, nombre=doc.get("nombre",""), apellido=doc.get("apellido",""),
            extra=doc.get("extra", {})
        ))

    async def GetUser(self, request: pb.GetUserRequest, context):
        db = await get_db()
        doc = await db.users.find_one({"_id": request.id})
        if not doc:
            await context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
        return pb.UserResponse(user=pb.User(
            id=str(doc["_id"]), nombre=doc["nombre"], apellido=doc["apellido"], extra=doc.get("extra", {})
        ))

    async def CreateWish(self, request: pb.CreateWishRequest, context):
        db = await get_db()
        # valida que user exista
        if not await db.users.find_one({"_id": request.user_id}):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "user_id inválido")

        # (opcional) valida ciudad exista
        city_doc = await db.cities.find_one({
            "ciudad_lc": request.ciudad.strip().lower(),
            **({"pais": request.pais} if request.pais else {})
        })
        if not city_doc:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Ciudad no está registrada")

        wish_id = str(uuid.uuid4())
        now_ms = int(time.time() * 1000)
        doc = {
            "_id": wish_id,
            "user_id": request.user_id,
            "titulo": request.titulo,
            "descripcion": request.descripcion,
            "pais": request.pais,
            "ciudad": request.ciudad,
            "creado_en": now_ms
        }
        await db.wishes.insert_one(doc)
        return pb.WishResponse(wish=pb.Wish(
            id=wish_id, user_id=doc["user_id"], titulo=doc["titulo"], descripcion=doc["descripcion"],
            pais=doc["pais"], ciudad=doc["ciudad"], creado_en=doc["creado_en"]
        ))

    async def ListWishesByUser(self, request: pb.ListWishesByUserRequest, context):
        db = await get_db()
        cursor = db.wishes.find({"user_id": request.user_id}).sort("creado_en", -1)
        items = []
        async for w in cursor:
            items.append(pb.Wish(
                id=str(w["_id"]), user_id=w["user_id"], titulo=w["titulo"],
                descripcion=w.get("descripcion",""), pais=w.get("pais",""),
                ciudad=w.get("ciudad",""), creado_en=w["creado_en"]
            ))
        return pb.ListWishesResponse(items=items)

    async def AutocompleteCity(self, request: pb.AutocompleteCityRequest, context):
        db = await get_db()
        q = request.query.strip().lower()
        limit = request.limit or 10
        filt = {"ciudad_lc": {"$regex": f"^{q}"}}
        if request.pais:
            filt["pais"] = request.pais
        cursor = db.cities.find(filt).limit(limit)
        items = []
        async for c in cursor:
            items.append(pb.City(pais=c["pais"], ciudad=c["ciudad"]))
        return pb.AutocompleteCityResponse(items=items)

async def serve():
    server = grpc.aio.server()
    pb_grpc.add_DataAdminServiceServicer_to_server(DataAdminService(), server)
    port = os.getenv("SAD_PORT", "50051")
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    print(f"[SAD] gRPC escuchando en {port}")
    await server.wait_for_termination()

if __name__ == "__main__":
    uvloop.run(serve())
