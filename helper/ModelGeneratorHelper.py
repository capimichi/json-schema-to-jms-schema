from model.ModelProperty import ModelProperty


class ModelGeneratorHelper:

    def get_mappings(self):
        mappings = {
            "string": "string",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "array",
            "object": "object"
        }

        return mappings

    def get_type_mapped(self, type):
        type_map = self.get_mappings()

        if (type in type_map):
            return type_map[type]

        return type

    def get_definition_type(self, definition, definitions):

        type = None
        if ("type" in definition):
            type = definition["type"]

        object = ""
        many = False
        if (type == "array"):
            many = True

            type, object, tmp = self.get_definition_type(definition["items"], definitions)

        if (type == "object"):
            object = definition["title"]

        if ("$ref" in definition):
            object = definition["$ref"].split("/")[-1]

        return type, object, many

    def get_model_content_getter(self, model_property):
        var_type = model_property.get_var_type(self.get_mappings())

        content = ""
        content += "\t/**\n"
        content += "\t * @return " + var_type + "\n"
        content += "\t */\n"
        content += "\tpublic function get" + model_property.get_pascal_case_name() + "()\n"
        content += "\t{\n"
        content += "\t\treturn $this->" + model_property.get_camel_case_name() + ";\n"
        content += "\t}\n\n"

        return content

    def get_model_content(self, model_name, model_properties, namespace):
        content = "<?php\n\n"
        content += "namespace " + namespace + ";\n\n"
        content += "use JMS\Serializer\Annotation as Serializer;\n\n"
        content += "/**\n"
        content += "* Class " + model_name + "\n"
        content += "*\n"
        content += "* @package " + namespace + "\n"
        content += "* @Serializer\ExclusionPolicy(\"none\")\n"
        content += "*/\n"
        content += "class " + model_name + "\n"
        content += "{\n"

        for model_property in model_properties:

            var_type = model_property.get_var_type(self.get_mappings())
            serialized_type = model_property.get_serialized_type(self.get_mappings())

            content += "\t/**\n"
            content += "\t * @var " + var_type + "\n"
            content += "\t * @Serializer\Type(\"" + serialized_type + "\")\n"
            content += "\t * @Serializer\SerializedName(\"" + model_property.name + "\")\n"
            content += "\t */\n"
            content += "\tprotected $" + model_property.get_camel_case_name() + ";\n\n"

        for model_property in model_properties:
            full_type = model_property.get_full_type(self.get_mappings())
            var_type = model_property.get_var_type(self.get_mappings())
            serialized_type = model_property.get_serialized_type(self.get_mappings())

            getter_content = self.get_model_content_getter(model_property)
            content += getter_content

            setter_content = self.get_model_content_setter(model_property)
            content += setter_content

        content += "}\n"

        return content

    def generate_model(self, model_name, definition, output_folder, namespace, definitions):

        path = output_folder + "/" + model_name + ".php"

        if (not "properties" in definition):
            return False

        properties = definition["properties"]
        model_properties = []

        for property_key, property in properties.items():

            if ("type" in property):
                type = property["type"]
                type = self.get_type_mapped(type)
            elif ("$ref" in property):
                type = property["$ref"].split("/")[-1]
                real_type = self.get_definition_real_type(type, definitions)
                if (len(real_type) > 0):
                    type = real_type
            else:
                raise Exception("Missing type in property " + property_key + " in model " + model_name)

            many = False

            if (type == "object"):
                if ("title" in property):
                    type = property["title"]
                else:
                    if ("additionalProperties" in property):
                        additional_properties = property["additionalProperties"]
                        if ("type" in additional_properties):
                            type = additional_properties["type"]
                            type = self.get_type_mapped(type)
            elif (type == "array"):
                many = True
                items = property["items"]
                if ("$ref" in items):
                    type = items["$ref"].split("/")[-1]
                    real_type = self.get_definition_real_type(type, definitions)
                    if (len(real_type) > 0):
                        type = real_type
                elif ("type" in items):
                    type = items["type"]
                    type = self.get_type_mapped(type)

            if (len(type) > 0):
                model_property = ModelProperty(name=property_key, type=type, many=many, namespace=namespace)
                model_properties.append(model_property)

        if (len(model_properties) == 0):
            return False

        model_content = self.get_model_content(model_name, model_properties, namespace)

        model_file = open(path, 'w')
        model_file.write(model_content)
        model_file.close()

    def get_definition_real_type(self, key, definitions):
        if(not key in definitions):
            return ""
        definition = definitions[key]
        if ("type" in definition):
            type = definition["type"]
            if(type == "object"):
                return ""
            elif(type in self.get_mappings()):
                return self.get_mappings()[type]
        return ""


    def get_model_content_setter(self, model_property):
        var_type = model_property.get_var_type(self.get_mappings())

        content = ""
        content += "\t/**\n"
        content += "\t * @param " + var_type + " $" + model_property.get_camel_case_name() + "\n"
        content += "\t * @return $this\n"
        content += "\t */\n"
        content += "\tpublic function set" + model_property.get_pascal_case_name() + "(" + var_type + " $" + model_property.get_camel_case_name() + ")\n"
        content += "\t{\n"
        content += "\t\t$this->" + model_property.get_camel_case_name() + " = $" + model_property.get_camel_case_name() + ";\n"
        content += "\t\treturn $this;\n"
        content += "\t}\n\n"

        return content
