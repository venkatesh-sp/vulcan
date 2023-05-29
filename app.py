from hl7apy import parser
from hl7apy.core import Group, Segment

file1 = open("ADT/ADT_A01 - 1.txt", "r").read()
file2 = open("ADT/ADT_A01 - 2.txt", "r").read()
file3 = open("ADT/ADT_A01 - 3.txt", "r").read()
file4 = open("VXU/VXU_V04 - 3.txt", "r").read()


indent = ""
indent_seg = "    "
indent_fld = "        "


def subgroup(group, indent):
    indent = indent + "    "
    print(indent, "Subroup:", group.name)
    for group_segment in group.children:
        if isinstance(group_segment, Group):
            subgroup(group_segment)
        else:
            print(indent_seg, indent, group_segment.name)
            for attribute in group_segment.children:
                print(indent_fld, indent, attribute.long_name, "===>", attribute.value)


def showmsg(hl7):
    msg = parser.parse_message(
        hl7.replace("\n", "\r"), find_groups=False, validation_level=2
    )
    for segment in msg.children:
        if isinstance(segment, Segment):
            print(indent, "Segment:", segment.name)
            for attribute in segment.children:
                print(
                    indent_fld,
                    indent,
                    "Attribute:",
                    attribute.long_name,
                    "===>",
                    "Value:",
                    attribute.value,
                )
        if isinstance(segment, Group):
            for group in segment.children:
                print(indent, "Group:", group.name)
                for group_segment in group.children:
                    if isinstance(group_segment, Group):
                        subgroup(group_segment.long_name, indent)
                    else:
                        print(indent_seg, indent, group_segment.name)
                        for attribute in group_segment.children:
                            print(
                                indent_fld,
                                indent,
                                attribute.long_name,
                                "===>",
                                attribute.value,
                            )


# showmsg(file1)
# print("\n\n\n=====\n\n\n")
# showmsg(file2)
# print("\n\n\n=====\n\n\n")
# showmsg(file4)
# print("\n\n\n=====\n\n\n")
showmsg(file4)
