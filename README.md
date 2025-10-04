pip install -r requirements.txt

python -m grpc_tools.protoc -I SAD-proto/proto `
  --python_out=sad_app\generated --grpc_python_out=sad_app\generated `
  SAD-proto/proto/wishlist.proto

New-Item -ItemType File sad_app\generated\__init__.py -Force | Out-Null
Test-Path .\sad_app\generated\wishlist_pb2.py

Test-Path .\sad_app\generated\wishlist_pb2_grpc.py

New-Item -ItemType File .\sad_app\__init__.py -Force | Out-Null

New-Item -ItemType File .\sad_app\generated\__init__.py -Force | Out-Null

Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force

python .\sad_app\seed_cities.py

python -m sad_app.seed_cities.py

python .\sad_app\server.py

python -m sad_app.server
