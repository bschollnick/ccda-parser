#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 21:30:56 2018

@author: mansooralam, yanjingwang
"""

"""
Parser for the CCDA procedures section
"""

from ...core import wrappers
from ... import core
from ... import documents


def procedures(ccda):

    parse_date = documents.parse_date
    parse_address = documents.parse_address
    data = wrappers.ListWrapper()
    parse_name = documents.parse_name

    procedures = ccda.section('procedures')

    for entry in procedures.entries():

        el = entry.tag('effectiveTime')
        #date = parse_date(el.attr('value'))
        effective_times = entry.els_by_tag('effectiveTime')

        # the first effectiveTime is the med start date
        try:
            el = effective_times[0]
        except IndexError:
            el = None
        start_date = None
        end_date = None
        if el:
            start_date = parse_date(el.tag('low').attr('value'))
            end_date = parse_date(el.tag('high').attr('value'))

        el = entry.tag('code')
        name = el.attr('displayName')
        code = el.attr('code')
        code_system = el.attr('codeSystem')

        #status = entry.tag("statusCode").val()
        #print(dir(status), "Val:",status)
      #  status = status.attr("completed")
        #print(dir(status))
        #sys.exit()
        if not name:
            name = core.strip_whitespace(entry.tag('originalText').val())

        # 'specimen' tag not always present
        specimen_name = None
        specimen_code = None
        specimen_code_system = None

        #el = entry.tag('performer').tag('addr')
        addresses = entry.els_by_tag("addr")
        ##for ex in el:
         #   print(dir(ex), ex.empty(), ex.is_empty(), ex)
         #   if el is None:
         #       print("None")
         #       print(entry.tag("procedure").attr("classCode"))

#        sys.exit()
#        if el is None:
#            el = entry.tag("performer").tag("assignedEntity").tag("addr")
        organization = entry.tag("representedOrganization").tag('name').val()
        phone = entry.tag("representedOrganization").tag('telecom').attr('value')

        for addr in addresses:
            performer_dict = parse_address(addr)
            print(dir(performer_dict))
            print(performer_dict.street)
        #performer_dict = parse_address(entry.tag("representedOrganization").tag("addr"))
        performer_dict.organization = organization
        performer_dict.phone = phone
        performer_dict.name =  parse_name(entry.tag("name"))

        # participant => device
        el = entry.template('2.16.840.1.113883.10.20.22.4.37').tag('code')
        device_name = el.attr('displayName')
        device_code = el.attr('code')
        device_code_system = el.attr('codeSystem')

        status = entry.tag("statusCode").attr("code")
        data.append(wrappers.ObjectWrapper(
            start_date=start_date,
            end_date=end_date,
            name=name,
            status=status,
            code=code,
            code_system=code_system,
            specimen=wrappers.ObjectWrapper(
                name=specimen_name,
                code=specimen_code,
                code_system=specimen_code_system
            ),
            performer=performer_dict,
            device=wrappers.ObjectWrapper(
                name=device_name,
                code=device_code,
                code_system=device_code_system
            )
        ))

    return data