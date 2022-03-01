#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:13:02 2018

@author: mansooralam, yanjingwang
"""

from ... import core
from ...core import wrappers
from ... import documents

def social_history(ccda):
    parse_date = documents.parse_date
    parse_name = documents.parse_name
    parse_address = documents.parse_address
    parse_phones = documents.parse_phones_and_email
    
    data = []

    social_history = ccda.section('social_history')

    for entry in social_history.entries():
        value = ""
        value = entry.tag("value").attr("displayName")
        value_code = entry.tag("value").attr("code")
        if value in ["", None]:
            value = entry.tag("value").attr("value")
            if value in ["", None]:
                value = entry.tag("code").tag("originalText").val()
                if value in ["", None]:
                    value = entry.tag("value").attr("nullFlavor")
            
        data.append({"code":entry.tag("code").attr("code"),
                    "name":entry.tag("code").attr("displayName"),
                    "code_system":entry.tag("code").attr("codeSystem"),
                    "code_system_name":entry.tag("code").attr("codeSystemName"),
                    "value":value,
                    "value_code":value_code,
                    "Date":parse_date(entry.tag("effectiveTime").attr("value"))
                    })
                    
    return wrappers.ListWrapper(data)
    
    
