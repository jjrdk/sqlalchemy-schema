def get_reference(schema, root_schema):
    ref = schema["$ref"]
    if not ref.startswith("#/"):
        raise NotImplementedError(ref)
    target = root_schema
    for k in ref.split("/")[1:]:
        target = target[k]
    return target
