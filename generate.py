import json
import os
import sys
import argparse

from helper.ModelGeneratorHelper import ModelGeneratorHelper


def main():
    parser = argparse.ArgumentParser(description="Json Schema to Marshmallow Models")
    parser.add_argument('json_schema_path', metavar='json_schema_path', type=str, help='Path to the json schema file')
    parser.add_argument('output_folder', metavar='model_output_folder', type=str, help='Path to the output folder')
    parser.add_argument('--namespace', dest='namespace', type=str, default='App', help='Namespace for the models')

    args = parser.parse_args()

    json_schema_path = args.json_schema_path

    output_folder = args.output_folder
    namespace = args.namespace

    # read json schema
    json_schema_file = open(json_schema_path, 'r')
    json_schema = json_schema_file.read()
    json_schema_file.close()

    json_schema = json.loads(json_schema)

    if(not "definitions" in json_schema):
        print("Missing definitions in json schema")
        sys.exit(1)

    # create output folder if not exists
    if(not os.path.exists(output_folder)):
        os.makedirs(output_folder)

    model_generator_helper = ModelGeneratorHelper()
    # generate models
    definitions = json_schema["definitions"]
    for key, definition in definitions.items():

        print("Generating " + key)
        model_generator_helper.generate_model(key, definition, output_folder, namespace, definitions)


if(__name__ == '__main__'):
    main()