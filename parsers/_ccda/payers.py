#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:13:02 2018

@author: mansooralam, yanjingwang
"""

from ... import core
from ...core import wrappers
from ... import documents

def payers(ccda):
    parse_date = documents.parse_date
    parse_name = documents.parse_name
    parse_address = documents.parse_address
    parse_phones = documents.parse_phones_and_email
    
    data = []

    payers = ccda.section('payers')
    print("Payers")
    for entry in payers.els_by_tag("entry"):
        policy = entry.tag("act").tag("entryRelationship").tag("act").tag("id").attr("extension")
        policyOrg = entry.tag("act").tag("entryRelationship").tag("act").tag("performer").tag("assignedEntity").tag("representedOrganization")
        po_name = policyOrg.tag("name").val()
        po_phone, po_email = parse_phones(policyOrg.els_by_tag("telecom"))
        po_address = parse_address(policyOrg.tag("addr"))
        po_payid = entry.tag("act").tag("entryRelationship").tag("act").tag("performer").tag("assignedEntity").tag("id").attr("extension")
            
        data.append({"code":entry.tag("code").attr("code"),
                     "name":entry.tag("code").attr("displayName"),
                     "code_system":entry.tag("code").attr("codeSystem"),
                     "code_system_name":entry.tag("code").attr("codeSystemName"),
                     "policy_number":policy,
                     "organization":po_name,
                     "phone":po_phone,
                     "email":po_email,
                     "address":po_address,
                     "pay_id":po_payid,
                    })
                    
    return wrappers.ListWrapper(data)
    
    
