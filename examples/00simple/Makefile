default: swagger2 jsonschema

swagger2:
	sqlalchemy_schema models.py:Group --out dst/default.json
	sqlalchemy_schema models.py:Group --out dst/default.yaml

jsonschema:
	sqlalchemy_schema models.py:Group --layout=jsonschema --out dst/jsonschema.json

openapi3:
	sqlalchemy_schema models.py:Group --layout=openapi3.0 --out dst/openapi3.json
