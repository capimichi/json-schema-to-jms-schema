import json
import os
import sys
import argparse

def get_property_marshmallow_type(property):

    type = ""
    many = False

    if ("type" in property):
        type = property["type"]

        # replace integer with int
        if (type == "integer"):
            type = "Int"
        elif type == "array":
            type = "List"
            if("items" in property and "$ref" in property["items"]):
                ref = property["items"]["$ref"]
                type = ref.split("/")[-1]
            many = True
        elif type == "string":
            type = "Str"
    elif "$ref" in property:
        type = property["$ref"].split("/")[-1]

    return type, many

def get_property_type(property):
    type = "str"

    if ("type" in property):
        type = property["type"]

        # replace integer with int
        if (type == "integer"):
            type = "int"
        elif type == "array":
            type = "list"
        elif type == "string":
            type = "str"
    elif "$ref" in property:
        type = property["$ref"].split("/")[-1]

    return type

def generate_model(model_name, properties, model_namespace):
    model_content = ""

    # clear properties with name __typename
    if ("__typename" in properties):
        del properties["__typename"]

    for propertyKey, property in properties.items():
        type = get_property_type(property)
        if(not type in ["int", "str", "list"]):
            model_content += "from " + model_namespace + "." + type + " import " + type + "\n"

    model_content += "\n"

    model_content += "class " + model_name + ":\n"
    model_content += "\tdef __init__(self"

    for propertyKey, property in properties.items():
        type = get_property_type(property)
        model_content += ", " + propertyKey + ": " + type

    model_content += "):\n"

    for propertyKey, property in properties.items():
        model_content += "\t\tself." + propertyKey + " = " + propertyKey + "\n"

    return model_content

def generate_schema(schema_name, properties, schema_namespace):
    schema_content = "from marshmallow import Schema, fields\n"

    # clear properties with name __typename
    if("__typename" in properties):
        del properties["__typename"]

    for propertyKey, property in properties.items():
        type, many = get_property_marshmallow_type(property)
        if(not type in ["Int", "Str", "List"]):
            schema_content += "from " + schema_namespace + "." + type + "Schema import " + type + "Schema\n"

    schema_content += "\n"

    schema_content += "class " + schema_name + "(Schema):\n"

    for propertyKey, property in properties.items():
        type, many = get_property_marshmallow_type(property)
        if(type in ["Int", "Str", "List"]):
            schema_content += "\t" + propertyKey + " = fields." + type + "()\n"
        else:
            many_string = "True" if many else "False"
            schema_content += "\t" + propertyKey + " = fields.Nested(" + type + "Schema, many=" + many_string + ")\n"

    return schema_content

def main():
    parser = argparse.ArgumentParser(description="Json Schema to Marshmallow Models")
    parser.add_argument('json_schema_path', metavar='json_schema_path', type=str, help='Path to the json schema file')
    parser.add_argument('model_output_folder', metavar='model_output_folder', type=str, help='Path to the output folder')
    parser.add_argument('schema_output_folder', metavar='schema_output_folder', type=str, help='Path to the output folder')
    parser.add_argument('--model_namespace', metavar='model_namespace', type=str, help='Namespace for the models', default="models")
    parser.add_argument('--schema_namespace', metavar='schema_namespace', type=str, help='Namespace for the schemas', default="schemas")

    args = parser.parse_args()

    json_schema_path = args.json_schema_path
    model_output_folder = args.model_output_folder
    schema_output_folder = args.schema_output_folder

    model_namespace = args.model_namespace
    schema_namespace = args.schema_namespace

    # read json schema
    json_schema_file = open(json_schema_path, 'r')
    json_schema = json_schema_file.read()
    json_schema_file.close()

    json_schema = json.loads(json_schema)

    if(not "definitions" in json_schema):
        print("Missing definitions in json schema")
        sys.exit(1)

    # create output folder if not exists
    if(not os.path.exists(model_output_folder)):
        os.makedirs(model_output_folder)

    if(not os.path.exists(schema_output_folder)):
        os.makedirs(schema_output_folder)

    # generate models
    for key, value in json_schema["definitions"].items():

        model_path = os.path.join(model_output_folder, key + ".py")
        schema_path = os.path.join(schema_output_folder, key + "Schema.py")

        print("Generating " + key)

        if ("properties" in value):
            model_content = generate_model(key, value["properties"], model_namespace)

        model_file = open(model_path, 'w')
        model_file.write(model_content)
        model_file.close()

        if("properties" in value):
            schema_content = generate_schema(key + "Schema", value["properties"], schema_namespace)

        schema_file = open(schema_path, 'w')
        schema_file.write(schema_content)
        schema_file.close()


if(__name__ == '__main__'):
    main()