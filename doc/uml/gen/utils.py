import inspect
import os
import re

FILTER_CLASSES = ["Enum", "object", "Representation", "Base"]

STYLE = """
<style>
    classDiagram{
        FontColor Black
        BackgroundColor White
        LineThickness 2
        LineColor Black
        RoundCorner 10
    }
</style>
"""


def is_class_variable(var, value):
    return (
        type(value) != "function"
        and not inspect.isclass(value)
        and not var.startswith("__")
        and not var.endswith("__")
    )


def find_class_variables(clas):
    return clas.__annotations__


def find_class_table_name(clas):
    if "__table__" in clas.__dict__:
        return '"' + clas.__name__ + " - " + clas.__dict__["__table__"].name + '"'
    return clas.__name__


def is_enum(clas):
    for base in clas.__bases__:
        if base.__name__ == "Enum":
            return True

    return False


def write_class(f, clas, classes):
    name = find_class_table_name(clas)
    class_names = [find_class_table_name(c) for c in classes]
    f.write(f"class {name} {{\n")
    edges = []
    for varname, vartype in find_class_variables(clas).items():
        print(repr(vartype))
        reg = re.findall(
            r"<class '(?:\w+\.)*(\w+)'>|"
            + r"(?:typing\.)?(List|list)(\[)(?:\w+\.)*(\w+)(\])|"
            + r"(?:\w+\.)*(\w+)( \| )(?:\w+\.)*(\w+)",
            repr(vartype),
        )[0]
        f.write(f"{varname}: {''.join(reg)}\n")
        for reference in reg:
            if reference in class_names:
                edges.append(reference)
    f.write(f"}}\n")

    if inspect.isabstract(clas) or clas.__name__.startswith("Abstract"):
        f.write(f"abstract class {name}\n")
    for base in clas.__bases__:
        if base not in classes:
            continue
        f.write(f"{base.__name__} <|-- {name}\n")
    for dest in edges:
        f.write(f"{dest} <-- {name}\n")


def is_table(clas):
    return "__table__" in clas.__dict__ or "__abstract__" in clas.__dict__


def is_valid_class(clas):
    return inspect.isclass(clas) and not (
        is_enum(clas) or clas.__name__ in FILTER_CLASSES
    )


def write_uml_file(filename, classes):
    with open(filename, "w") as f:
        f.write(f"@startuml\n")
        f.write("skinparam useBetaStyle true\n")
        f.write("skinparam linetype ortho\n")
        f.write(STYLE)

        for clas in classes:
            write_class(f, clas, classes)

        f.write(f"@enduml")
    os.system(f"java -jar doc/uml/gen/plantuml.jar {filename}")


if __name__ == "__main__":
    from mace import domain

    classes = []
    for attr, value in domain.__dict__.items():
        if not is_valid_class(value):
            continue
        classes.append(value)
    write_uml_file("doc/uml/test.puml", classes)
