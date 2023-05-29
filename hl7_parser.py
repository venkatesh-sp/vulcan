from hl7apy import parser
from hl7apy.core import Group, Segment

from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.humanname import HumanName

file1 = open("input_messages/ADT/ADT_A01 - 1.txt", "r").read()
file2 = open("input_messages/ADT/ADT_A01 - 2.txt", "r").read()
file3 = open("input_messages/ADT/ADT_A01 - 3.txt", "r").read()
file4 = open("input_messages/VXU/VXU_V04 - 3.txt", "r").read()


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
    # Extract relevant data from HL7 v2 message
    patient_id = msg.PID.PID_3.CX_1.value
    patient_name = msg.PID.PID_5.XPN_1.value
    birth_date = msg.PID.PID_7.value

    # Create FHIR resources
    patient = Patient()
    patient.id = patient_id
    patient.name = [HumanName(text=patient_name)]
    patient.birthDate = birth_date

    identifier = Identifier()
    identifier.system = "http://example.com/mrn"
    identifier.value = patient_id
    patient.identifier = [identifier]

    # Convert FHIR resources to JSON
    fhir_json = patient.json(indent=2)

    # Print the FHIR JSON
    print(fhir_json)
    # for segment in msg.children:
    #     if isinstance(segment, Segment):
    #         print(indent, "Segment:", segment.name)
    #         for attribute in segment.children:
    #             print(
    #                 indent_fld,
    #                 indent,
    #                 "Attribute:",
    #                 attribute.long_name,
    #                 "===>",
    #                 "Value:",
    #                 attribute.value,
    #             )
    #     if isinstance(segment, Group):
    #         for group in segment.children:
    #             print(indent, "Group:", group.name)
    #             for group_segment in group.children:
    #                 if isinstance(group_segment, Group):
    #                     subgroup(group_segment.long_name, indent)
    #                 else:
    #                     print(indent_seg, indent, group_segment.name)
    #                     for attribute in group_segment.children:
    #                         print(
    #                             indent_fld,
    #                             indent,
    #                             attribute.long_name,
    #                             "===>",
    #                             attribute.value,
    #                         )


# showmsg(file1)
# print("\n\n\n=====\n\n\n")
# showmsg(file2)
# print("\n\n\n=====\n\n\n")
# showmsg(file4)
# print("\n\n\n=====\n\n\n")
showmsg(file4)
