#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:48:03 2018

@author: mansooralam, yanjingwang
"""

from ...core import codes
from ... import documents
from ...core import wrappers
import langcodes
from pprint import pprint



def demographics(ccda):
    
    parse_date = documents.parse_date
    parse_name = documents.parse_name
    parse_address = documents.parse_address
    parse_phones = documents.parse_phones_and_email
    
    demographics = ccda.section('demographics')

    patient = demographics.tag('patientRole')
    el = patient.tag('patient').tag('name')
    patient_name_dict = parse_name(el)

    el = patient.tag('patient')
    dob = parse_date(el.tag('birthTime').attr('value'))
    gender = codes.gender(el.tag('administrativeGenderCode').attr('code'))
    marital_status = codes.marital_status(el.tag('maritalStatusCode').attr('code'))

    el = patient.tag('addr')
    patient_address_dict = parse_address(el)

    phones = {}
    
    mrns = []
    raw_mrns = patient.els_by_tag("id")
    for id_entry in raw_mrns:
        mrns.append(id_entry.attr("extension").strip())
        
    phones, email = parse_phones(patient.els_by_tag("telecom"))
#    print("Phones:", phones)
    
    languageCode = patient.tag('languageCommunication').tag('languageCode').attr('code')
#    language = langcodes.Language.make(languageCode).display_name()
    language = langcodes.Language.get(languageCode).display_name()

    race = patient.tag('raceCode').attr('displayName')
    ethnicity = patient.tag('ethnicGroupCode').attr('displayName')
    religion = patient.tag('religiousAffiliationCode').attr('displayName')

    el = patient.tag('birthplace')
    birthplace_dict = parse_address(el)

    el = patient.tag('guardian')
    guardian_relationship = el.tag('code').attr('displayName')
    guardian_relationship_code = el.tag('code').attr('code')
    #guardian_home = el.tag('telecom').attr('value')
    guardian_phone, guardian_email = parse_phones(el.els_by_tag("telecom"))


    el = el.tag('guardianPerson').tag('name')
    guardian_name_dict = parse_name(el)

    el = patient.tag('guardian').tag('addr')
    guardian_address_dict = parse_address(el)

    participant = demographics.tag("participant")
    assoc_entity = participant.tag("associatedEntity")
    associated_name_dict = parse_name(assoc_entity.tag("associatedPerson").tag("name"))

    el = assoc_entity.tag('addr')
    associated_address_dict = parse_address(el)

    #associated_phone = assoc_entity.tag('telecom').attr("value")
    associated_phone, associated_email = parse_phones(assoc_entity.els_by_tag("telecom"))
    #phones, email = parse_phones(patient.els_by_tag("telecom"))

    associated_relation = assoc_entity.tag("code").attr("displayName")

    el = patient.tag('providerOrganization')
    provider_organization = el.tag('name').val()
    #provider_phone = el.tag('telecom').attr('value')
    provider_phone, provider_email = parse_phones(el.els_by_tag("telecom"))

    providers = []
#    pcp_start_date = parse_date(demographics.tag("documentationOf").tag("serviceEvent").tag("effectiveTime").tag('low').attr('value'))
#    pcp_end_date = parse_date(demographics.tag("documentationOf").tag("serviceEvent").tag("effectiveTime").tag('high').attr('value'))
    for provider in demographics.tag("documentationOf").tag("serviceEvent").els_by_tag("performer"):
        pcp = provider
        pcp_name = parse_name(pcp.tag("assignedEntity").tag("assignedPerson").tag("name"))
        pcp_suffix = pcp.tag("assignedEntity").tag("assignedPerson").tag("suffix").val()
        pcp_label = pcp.tag("functionCode").attr("displayName")
        if pcp_label in ["", None, "None"]:
            pcp_label = "Performer"
        else:
            pcp_label = "Performer (%s)" % pcp_label
        
        pcp_start_date = parse_date(pcp.tag("time").tag('low').attr('value'))
        pcp_end_date = parse_date(pcp.tag("time").tag('high').attr('value'))
        pcp_addr = parse_address(pcp.tag("assignedEntity").tag("addr"))
        pcp_phone, pcp_email = parse_phones(pcp.tag("assignedEntity").els_by_tag("telecom"))
        providers.append({"start_date":pcp_start_date,
                          "end_date":pcp_end_date,
                          "name":pcp_name,
                          "label":pcp_label,
                          "address":pcp_addr,
                          "phone":pcp_phone,
                          "email":pcp_email,
                          })
                          
    legal_auth = {}
    lauth = demographics.tag("legalAuthenticator")
    legal_auth["time"] = lauth.tag("time").attr("value")
    legal_auth["address"] = parse_address(lauth.tag("assignedEntity").tag("addr"))
    legal_auth["phone"], legal_auth["email"] = parse_phones(lauth.tag("assignedEntity").els_by_tag("telecom"))
    legal_auth["name"] = parse_name(lauth.tag("assignedEntity").tag("name"))
    # pcp = demographics.tag("documentationOf").tag("serviceEvent")
    # pcp_start_date = parse_date(pcp.tag("effectiveTime").tag('low').attr('value'))
    # pcp_end_date = parse_date(pcp.tag("effectiveTime").tag('high').attr('value'))
    # pcp = pcp.tag("performer")
    # pname = pcp.tag("assignedEntity").tag("assignedPerson").tag("name")
    # #pcp_start = 
    # #pcp_end = 
    # pcp_name = parse_name(pname)
    # pcp_suffix = pname.tag("suffix").val()
    # pcp_label = pcp.tag("functionCode").attr("displayName")
    # pcp_addr = parse_address(pcp.tag("assignedEntity").tag("addr"))
    # #pcp_phone = pcp.tag("assignedEntity").tag('telecom').attr("value")
    # pcp_phone, pcp_email = parse_phones(pcp.tag("assignedEntity").els_by_tag("telecom"))
        
        
    # el = patient.tag('providerOrganization')
    # provider_organization = el.tag('name').val()
    # #provider_phone = el.tag('telecom').attr('value')
    # provider_phone, provider_email = parse_phones(el.els_by_tag("telecom"))
    
    # provider_address_dict = parse_address(el.tag('addr'))


    return wrappers.ObjectWrapper(
        mrns=mrns,
        name=patient_name_dict,
        dob=dob,
        gender=gender,
        marital_status=marital_status,
        address=patient_address_dict,
        phone = phones,
        # phone=wrappers.ObjectWrapper(
            # home=home,
            # work=work,
            # mobile=mobile
        # ),
        email=email,
        languageCode=languageCode,
        language=language,
        race=race,
        ethnicity=ethnicity,
        religion=religion,
        birthplace=wrappers.ObjectWrapper(
            state=birthplace_dict.state,
            zip=birthplace_dict.zip,
            country=birthplace_dict.country
        ),
        associated=wrappers.ObjectWrapper(
            name=wrappers.ObjectWrapper(
                given=associated_name_dict.given,
                family=associated_name_dict.family
            ),
            relationship=associated_relation,
            relationship_code="",
            address=associated_address_dict,
            phone= associated_phone,
            email=associated_email,
            #phone=wrappers.ObjectWrapper(
            #    home=associated_phone
            #)
        ),
        guardian=wrappers.ObjectWrapper(
            name=wrappers.ObjectWrapper(
                given=guardian_name_dict.given,
                family=guardian_name_dict.family
            ),
            relationship=guardian_relationship,
            relationship_code=guardian_relationship_code,
            address=guardian_address_dict,
            phone = guardian_phone,
            email = guardian_email
            #phone=wrappers.ObjectWrapper(
            #    home=guardian_home
            #)
        ),
        pcp=wrappers.ObjectWrapper(
            name=pcp_name,
            suffix=pcp_suffix,
            phone=pcp_phone,
            email=pcp_email,
            address=pcp_addr,
            label=pcp_label,
            start_date=pcp_start_date,
            end_date=pcp_end_date
            ),

        providers=providers,
        legal_authenticator=legal_auth,
        #provider=wrappers.ObjectWrapper(
        #    organization=provider_organization,
        #    phone=provider_phone,
        #    address=provider_address_dict
        #)
    )
