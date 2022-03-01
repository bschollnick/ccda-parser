import xmltodict
import os.path
from pprint import pprint
import sys
from nameparser import HumanName
from datetime import datetime

try:
    from pyccda import CCDA
except ModuleNotFoundError:
    # #
    sys.path.append("..")
    from pyccda import CCDA


def build_address(address_data, start_data=None):
    if start_data:
        out_addr = start_data
    else:
        out_addr = {}

    if hasattr(address_data,"city"):
        out_addr["City"] = address_data.city
    if hasattr(address_data,"country"):
        out_addr["Country"] = address_data.country
    if hasattr(address_data,"state"):
        out_addr["State"] = address_data.state
    if hasattr(address_data,"street"):
        out_addr["Street"] = address_data.street
    if hasattr(address_data,"zip"):
        out_addr["Zip"] = address_data.zip
    return out_addr

def is_empty(data):
    return data in ["", None, "None", []]

    
def build_name(name_data):
    if type(name_data) is str:
        return name_data
    elif name_data in [None]:
        return ""

    name = ""
    if hasattr(name_data, "prefix"):
        if not is_empty(name_data.prefix):
            name += "%s " % name_data.prefix

    if not is_empty(name_data.given):
        name += " ".join(name_data.given)
        
    if not is_empty(name_data.family):
        name += " %s" % name_data.family
    
    if hasattr(name_data, "suffix"):
        if not is_empty(name_data.suffix):
            name += " %s" % name_data.suffix

    if is_empty(name):
        return None

    return HumanName(name)

def build_phone(phone_data):
    out_phone = []
    if phone_data in ["", None, {}]:
        return None
        
    if type(phone_data) is str:
        #print("Phone String")
        return phone_data.strip()
    elif type(phone_data) is list:
        #print("Phone List")
        for entry in phone_data:
            out_phone.append(classify(entry, out_phone))
        return out_phone
    
    outphone = []
    for ptype in phone_data:
        out_phone.append ({ptype.title():phone_data[ptype]})
        
    return out_phone

def build_author(author_data):
    output = {}
    if hasattr(author_data, "name"):
        output["Name"] = build_name(author_data.name)

    if hasattr(author_data, "phone"):
        output["Phone"] = build_phone(author_data.phone)

    if hasattr(author_data, "address"):
        output["Address"] = build_address(author_data.address)
    return output

def build_qty(qty_date):
    return {"Unit":qty_date.unit,
            "Value":qty_date.value}

def build_location(location_data):
    output = {}
    output["Address"] = build_address(location_data)
#    output["Name"] = build_name(location_data.name)
    if hasattr(location_data, "organization"):
        output["Organization"] = location_data.organization
    return output

def build_date_range(daterange):
    output = {}
    if hasattr(daterange, "start"):
        output["Start"] = daterange.start
    if hasattr(daterange, "end"):
        output["End"] = daterange.end
    if hasattr(daterange, "date"):
        output["Date"] = daterange
    return output

class ccda_document():
    def __init__(self):
        self.ccda_filename = None
        self.ccda = None

    def read_ccda(self,filename):
        self.ccda_filename = filename
        with open(self.ccda_filename) as f:
            self.ccda = CCDA(f.read())

    def return_allergies(self):
        def return_allergy_element(datum):
            return {"Date":build_date_range(datum.date_range),
                    #"Start":datum.date_range.start,
                    #"End":datum.date_range.end,
                    "Allergen":datum.allergen.name,
                    #"Name":datum.name,
                    "Reaction":datum.reaction.name,
                    "Reaction_Type":datum.reaction_type.name,
                    "Severity":datum.severity,
                    "Status":datum.status
                    }
        output = []
        data = self.ccda.data.allergies
        for x in data:
           output.append(return_allergy_element(x))
        return output

    def return_careplan(self):
        def return_careplan_element(datum):
            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Code_System_Name":datum.code_system_name,
                    "Name":datum.name,
                    "Text":datum.text
                    }
        output = []
        data = self.ccda.data.care_plan
        for x in data:
            output.append(return_careplan_element(x))
        return output

    def return_documents(self):
        # def return_document_element(datum):
            # return {"Code":datum.code,
                    # "Code_System":datum.code_system,
                    # "Code_System_Name":datum.code_system_name,
                    # "Name":datum.name,
                    # "Text":datum.text
                    # }
        data = self.ccda.data.document
        output = {"Author":build_author(data.author),
                  "Date":data.date,
                  "Documentation_Of":[],
                  "Title":data.title,
                  "Location":build_location(data.location)
                  }
        for x in data.documentation_of:
            output["Documentation_Of"].append({
                "Address":build_address(x.address),
                "Name":build_name(x.name),
                "phone":build_phone(x.phone)
            })
        return output

    def return_demographics(self):
        def return_provider(datum):
            return {    "Start_Date":datum["start_date"],
                        "End_Date":datum["end_date"],
                        "Name":build_name(datum["name"]),
                        "Address":build_address(datum["address"]),
                        #"Organization":data.organization,
                        "Phone":build_phone(datum["phone"]),
                        "Email":datum["email"],
                        "Label":datum["label"],
                        #"Start_Date":
                        }
            
        data = self.ccda.data.demographics
        pcp = {"Name":build_name(data.pcp.name),
               #"Suffix":data.pcp.suffix,
               "Address":build_address(data.pcp.address),
               "Phone":build_phone(data.pcp.phone),
               "Label":data.pcp.label,
               "Start":data.pcp.start_date,
               "End":data.pcp.end_date,
               "Email":data.pcp.email}
        associated = {"Address":build_address(data.associated.address),
                      "Name":build_name(data.associated.name),
                      "Phone":build_phone(data.associated.phone),
                      "Email":data.associated.email,
                      "Relationship":data.associated.relationship,
                      "Relationship_Code":data.associated.relationship_code}

        guardian = {"Address":build_address(data.guardian.address),
                    "Name":build_name(data.guardian.name),
                    "Phone":build_phone(data.guardian.phone),
                    "Email":data.guardian.email,
                    "Relationship":data.guardian.relationship,
                    "Relationship_Code":data.guardian.relationship_code}
        lauth = {"Address":build_address(data.legal_authenticator["address"]),
                 "Name":build_name(data.legal_authenticator["name"]),
                 "Phone":build_phone(data.legal_authenticator["phone"]),
                 "Email":data.legal_authenticator["email"],
                 "Time":data.legal_authenticator["time"]}

        providers = []
        for prov in data.providers:
            providers.append(return_provider(prov))
            
        return {"Mrns":data.mrns,
                "Address":build_address(data.address),
                "Birthplace":build_address(data.birthplace),#data.birthplace,
                "Dob":data.dob,
                "Email":data.email,
                "Ethnicity":data.ethnicity,
                "Gender":data.gender,
                "Associated":associated,
                "Guardian":guardian,
                "LanguageCode":data.languageCode,
                "Language":data.language,
                "Marital_Status":data.marital_status,
                "Name":build_name(data.name),
                "Phone":build_phone(data.phone),
                "Providers":providers,
                "Pcp":pcp,
                "Race":data.race,
                "Religion":data.religion,
                "Legal_Authenticator":lauth,
                }

    def return_encounters(self):
        def return_encounter_element(datum):
            #findings = []
            #for entry in findings:
            #    findings.append(entry)
            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Code_System_Name":datum.code_system_name,
                    "Start Date":datum.start_date,
                    "End Date":datum.end_date,
                    "Findings":datum.findings,
                    "Location":build_location(datum.location),
                    "Name":datum.name,
                    "Performer":{"Name":build_name(datum.performer.name),
                                 "Suffix":datum.performer.suffix,
                                 "Organization":datum.performer.org,
                                 "Address":build_address(datum.performer.address),
                                 "Phone":datum.performer.phone,
                                 },
                    "Translation":datum.translation.name,
                    "Translation Code":datum.translation.code
                    }
        output = []
        data = self.ccda.data.encounters
        for x in data:
            output.append(return_encounter_element(x))
        return output

    def return_functional_statuses(self):
        """
        untested
        """
        output = []
        data = self.ccda.data.functional_statuses
        for x in data:
            output.append({"Date":build_date_range(x.date),
                           "Name":x.name})
        return output

    def return_immunizations(self):
        """
        """
        def build_route(datum):
            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Code_System_Name":datum.code_system_name,
                    "Name":build_name(datum.name)}
            
        def build_translation(trans):
            return {"Code":trans.code,
                    "Code_System":trans.code_system,
                    "Code_System_Name":trans.code_system_name,
                    "Name":build_name(trans.name)}
                    
        def build_product(datum):
            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Code_System_Name":datum.code_system_name,
                    "Lot_Number":datum.lot_number,
                    "Manufacturer_Name":datum.manufacturer_name,
                    "Name":build_name(datum.name),
                    "Translation":build_translation(datum.translation)}
            
        def build_education(datum):

            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Name":build_name(datum.name)}
            
        output = []
        data = self.ccda.data.immunizations
        for entry in data:
            immunization = {"Date":build_date_range(entry.date),
                            "Dose_Quantity":build_qty(entry.dose_quantity),
                            "Education_Type":build_education(entry.education_type),
                            "Instructions":entry.instructions,
                            "product":build_product(entry.product),
                            "route":build_route(entry.route)}
                            
            output.append(immunization)
        return output

    def return_instructions(self):
        """
        untested
        """
        def build_instruction(datum):
            return {"Code":datum.code,
                    "Code_System":datum.code_system,
                    "Name":build_name(datum.name),
                    "Text":datum.text}
            
        output = []
        data = self.ccda.data.instructions
        for entry in data:
            output.append(build_instruction(entry))
        return output

    def return_medications(self):
        """
        untested
        """
        def return_prescriber(datum):
            return {"Organization":datum.organization,
                    "Person":datum.person,
                    "Provider":build_name(datum.provider),
                    #"Address":build_address(datum.address),
                    #"Phone":build_phone(datum.phone)
                    }

        def return_product(datum):
            return {"Name":datum.name,
                    "Text":datum.text,
                    "Translation":datum.translation.name}

        def return_schedule(datum):
            return {"Period_Unit":datum.period_unit,
                    "Period_Value":datum.period_value,
                    "Type":datum.type}
        def return_medication_element(datum):
            #print("QTY:",datum.dose_quantity.unit, datum.dose_quantity.value)
            return {
                    "Administration":datum.administration.name,
                    "Status":datum.status,
                    "Date":build_date_range(datum.date_range),
                    "Dose_Quantity":build_qty(datum.dose_quantity),
                    "Precondition":datum.precondition.name,
                    "Prescriber":return_prescriber(datum.prescriber),
                    "Product":return_product(datum.product),
                    "Rate_Quantity":build_qty(datum.rate_quantity),
                    "Refills":datum.refills,
                    "Fill_Quantity":datum.fill_quantity,
                    "Fill_Unit":datum.fill_unit,
                    "Reason":datum.reason.name,
                    "Route":datum.route.name,
                    "Schedule":return_schedule(datum.schedule),
                    "Text":datum.text,
                    "Vehicle":build_name(datum.vehicle.name),
                    }
        output = []
        data = self.ccda.data.medications
        for entry in data:
            output.append(return_medication_element(entry))
        return output

    def return_problems(self):
        output = []
        data = self.ccda.data.problems
        for entry in data:
            output.append({"Age":entry.age,
                           "Code":entry.code,
                           "Code_System":entry.code_system,
                           "Code_System_Name":entry.code_system_name,
                           "Comment":entry.comment,
                           "Date":build_date_range(entry.date_range),
                           "Name":entry.name,
                           "Status":entry.status,
                           "Translation":entry.translation.name,
                           "Translation Code":entry.translation.code,
                           "Translation Code Name":entry.translation.code_system_name})
        return output

    def return_procedures(self):
        """
        Please note speciman is *ALWAYS* None.

        This in the library pyccda\parsers\_ccda\procedures.py

        """
        def build_procedure(datum):
            #print(datum.name, dir(datum.name))
            performer = {"Name":build_name(datum.performer.name),
                         "Address":build_address(datum.performer),
                         "Organization":datum.performer.organization,
                         "Phone":build_phone(datum.performer.phone)}
            return {"Code":datum.code,
                    "Start_Date":datum.start_date,
                    "End_Date":datum.end_date,#build_date_range(datum.date),
                    "Status":datum.status,
                    "Device":datum.device.name,
                    "Name":datum.name,
                    "Performer":performer,
                    "Specimen":datum.specimen.name}
        output = []
        data = self.ccda.data.procedures
        for entry in data:
            output.append(build_procedure(entry))
        return output

    def return_results(self):
        def build_reference_range(ref_datum):
            return {"High_Unit":ref_datum.high_unit,
                    "High_Value":ref_datum.high_value,
                    "Low_Unit":ref_datum.low_unit,
                    "Low_Value":ref_datum.low_value,
                    "Text":ref_datum.text,
                    }

        def build_test(test_datum):
            #
            # Split name into the components?
            #
            #print(dir(test_datum.reference_range))
            return {"Date":build_date_range(test_datum.date),
                    "Name":test_datum.name,
                    "Status":test_datum.status,
                    "Provider":build_name(test_datum.provider),
                    "Reference_Range":build_reference_range(test_datum.reference_range),
                    "Translation":test_datum.translation.name,
                    "Unit":test_datum.unit,
                    "Value":str(test_datum.value).strip()}

        def build_results(datum):
            datum_out = []
            for x in datum.tests:
                #print(dir(x))
                datum_out.append(build_test(x))
            return {"Name":datum.name,
                    "Tests":datum_out}

        output = []
        data = self.ccda.data.results
        for entry in data:
            output.append(build_results(entry))
        return output

    def return_smoking(self):
        data = self.ccda.data.smoking_status
        print(data)
        return data.name

    def return_vitals(self):
        output = {}
        data = self.ccda.data.vitals
        for entry in data:
            for result in entry.results:
                if result.name == None and result.unit == None and result.value in [0, None, ""]:
                    continue
                if result.date not in output:
                    output[result.date] = {}
                if len(result.date) == 14:
                    date = datetime.strptime(result.date, "%Y%m%d%H%M%S")
                else:
                    date = datetime.strptime(result.date, "%Y%m%d")
                output[result.date][result.name] = {"Name:":result.name,
                                          "Unit":result.unit,
                                          "Value":result.value,
                                          "Date":date
                                          }
        return output

    def return_social_history(self):
        shistory = self.ccda.data.social_history
        return shistory
        
def convert_demographics(ddata):
    #
    #   Need to flatten the data
    #
    pass
    

document = ccda_document()
test_path = None
filenames = None
for fname in filenames:

if len(sys.argv) > 1:
    test_path = ""
    filenames = sys.argv[1:]
    
for fname in filenames:
    test_file = os.path.join(test_path, fname)
    document.read_ccda(test_file)
    demographics = document.return_demographics()
    print()
    print(demographics["Name"])
    #pprint(document.return_demographics())
#    pprint(document.return_social_history())
#    pprint(document.return_documents())        # CCD Title
#   pprint(document.return_encounters()[0:5])
#    pprint(document.return_functional_statuses())
    #pprint(document.return_immunizations()) # untested
    #print(document.return_instructions()) # untested
#    pprint(document.return_medications()[0:5])
#    pprint(document.return_problems())
    pprint(document.return_procedures()[0:3])
    #pprint(document.return_allergies())
    #print (document.return_careplan()) # Patricia Bunk only
 #   pprint(document.return_results()[0:5])  #???
    #pprint(document.return_smoking())
    #pprint(document.return_vitals())
#    pprint(document.return_social_history())
#pprint(output)
    print("-"*30)

    
