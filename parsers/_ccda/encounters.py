#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 21:17:08 2018

@author: mansooralam, yanjingwang
"""

"""
Parser for the CCDA encounters section
"""

from ...core import wrappers
from ...documents import parse_address, parse_date, parse_name
from ... import documents


def encounters(ccda):

    parse_phones = documents.parse_phones_and_email

    data = []

    encounters = ccda.section('encounters')

    for entry in encounters.entries():
        start_date = parse_date(entry.tag('effectiveTime').attr('value'))
        end_date = start_date
        if start_date is None:
#           Allscripts - PRofession EHR\datapoint_ambulatory sample XML does not contain all encounter data
            start_date = parse_date(entry.tag("effectiveTime").tag("low").attr("value"))
            end_date = parse_date(entry.tag("effectiveTime").tag("high").attr("value"))
            if end_date is None:
                end_date = entry.tag("effectiveTime").tag("high").attr("nullFlavor")
                
#            sys.exit()

        el = entry.tag('code')
        name = el.attr('displayName')
        code = el.attr('code')
        code_system = el.attr('codeSystem')
        code_system_name = el.attr('codeSystemName')
        code_system_version = el.attr('codeSystemVersion')

        # translation
        el = entry.tag('translation')
        translation_name = el.attr('displayName')
        translation_code = el.attr('code')
        translation_code_system = el.attr('codeSystem')
        translation_code_system_name = el.attr('codeSystemName')

        # performer
        el = entry.tag("performer").tag("assignedEntity")
        performer_name = parse_name(el.tag("assignedPerson").tag("name"))
        performer_suffix = el.tag("assignedPerson").tag("name").tag("suffix").val()

        el = el.tag("representedOrganization")
        performer_org = el.tag("name").val()
        performer_addr = parse_address(el.tag("addr"))
        performer_phone = parse_phones(el.els_by_tag("telecom"))
        
        
        #performer_phone = []
        #for pnumber in phones:
        #    performer_phone.append(pnumber.attr("value"))
        #performer_phone = el.tag("telecom").attr("value")


        #el = entry.tag('performer').tag('code')
        #performer_name = el.attr('displayName')
        #performer_code = el.attr('code')
        #performer_code_system = el.attr('codeSystem')
        #performer_code_system_name = el.attr('codeSystemName')

        # participant => location
        el = entry.tag('participant')
        organization = el.tag('code').attr('displayName')

        location_dict = parse_address(el)
        location_dict.organization = organization

        # findings
        findings = []
        findings_els = entry.els_by_tag('entryRelationship')
        for current in findings_els:
            erel = current.tag("act").tag("entryRelationship")
            if erel.tag("statusCode").attr("code") not in ["", None, "None"]:
                findings.append ({"Status":erel.tag("statusCode").attr("code"),
                                  "Action":erel.tag("code").attr("displayName"),
                                  "Diagnosis":erel.tag("value").tag("translation").attr("displayName"),
                                  "Dx":erel.tag("value").tag("translation").attr("code"),
                                  "CodeSystemName":erel.tag("value").tag("translation").attr("codeSystemName"),
                                 })
        # findings = []
        # findings_els = entry.els_by_tag('entryRelationship')
        # for current in findings_els:
            # el = current.tag('value')
            # findings.append(wrappers.ObjectWrapper(
                # name=el.attr('displayName'),
                # code=el.attr('code'),
                # code_system=el.attr('codeSystem'),
            # ))

        data.append(wrappers.ObjectWrapper(
            start_date=start_date,
            end_date=end_date,
            name=name,
            code=code,
            code_system=code_system,
            code_system_name=code_system_name,
            code_system_version=code_system_version,
            findings=findings,
            translation=wrappers.ObjectWrapper(
                name=translation_name,
                code=translation_code,
                code_system=translation_code_system,
                code_system_name=translation_code_system_name
            ),
            performer=wrappers.ObjectWrapper(
                name=performer_name,
                suffix=performer_suffix,
                org=performer_org,
                address=performer_addr,
                phone=performer_phone
            ),
            location=location_dict
        ))

    return wrappers.ListWrapper(data)