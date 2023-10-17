
class ModelProperty:

    def __init__(self, name, type, many=False, namespace="App"):
        self.name = name
        self.type = type
        self.many = many
        self.namespace = namespace

    def get_pascal_case_name(self):
        parts = self.name.split("_")
        pascal_case_name = ""
        for i in range(0, len(parts)):
            pascal_case_name += parts[i].capitalize()
        return pascal_case_name

    def get_camel_case_name(self):
        parts = self.name.split("_")
        camel_case_name = ""
        # first to lower
        camel_case_name += parts[0].lower()
        for i in range(1, len(parts)):
            camel_case_name += parts[i].capitalize()
        return camel_case_name

    def get_full_type(self, default_types):
        type = self.type
        if (type in default_types.values()):
            full_type = type
        else:
            full_type = "\\" + self.namespace + "\\" + type

        return full_type

    def get_var_type(self, default_types):
        full_type = self.get_full_type(default_types)
        var_type = full_type
        if (self.many):
            var_type += "[]"

        var_type += "|null"

        return var_type

    def get_serialized_type(self, default_types):
        full_type = self.get_full_type(default_types)
        # remove first backslash
        if(full_type[0] == "\\"):
            full_type = full_type[1:]
        serialized_type = full_type if not self.many else "array<" + full_type + ">"
        return serialized_type

    def get_setter_type(self, default_types):
        full_type = self.get_full_type(default_types)
        if (self.many):
            full_type = "array"
        return "?" + full_type