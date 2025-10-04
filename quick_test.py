import grpc
from sad_app.generated import wishlist_pb2 as pb
from sad_app.generated import wishlist_pb2_grpc as pb_grpc

def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb_grpc.DataAdminServiceStub(channel)

    # Ping
    stub.Ping(pb.Empty())
    print("Ping OK ✅")

    # Autocomplete ciudades (ej: CO + 'Bu')
    r = stub.AutocompleteCity(pb.AutocompleteCityRequest(pais="CO", query="Bu", limit=5))
    print("Autocomplete:", [{"pais": c.pais, "ciudad": c.ciudad} for c in r.items])

if __name__ == "__main__":
    main()
