pip install -r requirements.txt

python -m grpc_tools.protoc -I SAD-proto/proto `
  --python_out=sad_app\generated --grpc_python_out=sad_app\generated `
  SAD-proto/proto/wishlist.proto

New-Item -ItemType File sad_app\generated\__init__.py -Force | Out-Null

python .\sad_app\seed_cities.py

python -m sad_app.seed_cities.py

python .\sad_app\server.py

python -m sad_app.server
