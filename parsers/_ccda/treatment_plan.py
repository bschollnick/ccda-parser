#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:13:02 2018

@author: mansooralam, yanjingwang
"""

from ... import core
from ...core import wrappers
from ... import documents


def treatment_plan(ccda):
    
    parse_date = documents.parse_date
    parse_address = documents.parse_address
    parse_name = documents.parse_name
    
    data = []

    treatment_plans = ccda.section('treatment_plan')
    title = treatment_plans.tag("code").attr("displayName")
    entries = treatment_plans.entries()

    return data