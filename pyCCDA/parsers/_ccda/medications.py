#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 21:28:27 2018

@author: mansooralam, yanjingwang
"""

"""
Parser for the CCDA medications section
"""

from ...core import wrappers
from ... import core
from ... import documents


def medications(ccda):

    parse_date = documents.parse_date
    parse_address = documents.parse_address
    parse_name = documents.parse_name
    data = wrappers.ListWrapper()
    medications = ccda.section('medications')

    for entry in medications.entries():

        el = entry.tag('text')
        sig = core.strip_whitespace(el.val())

        effective_times = entry.els_by_tag('effectiveTime')
        status = entry.tag("statusCode").attr("code")
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

        # the second effectiveTime might the schedule period or it might just
        # be a random effectiveTime from further in the entry... xsi:type should
        # tell us
        try:
            el = effective_times[1]
        except IndexError:
            el = None
        schedule_type = None
        schedule_period_value = None
        schedule_period_unit = None
        if el and el.attr('xsi:type') == 'PIVL_TS':
            institution_specified = el.attr('institutionSpecified')
            if institution_specified == 'true':
                schedule_type = 'frequency'
            elif institution_specified == 'false':
                schedule_type = 'interval'

            el = el.tag('period')
            schedule_period_value = el.attr('value')
            schedule_period_unit = el.attr('unit')

        el = entry.tag('manufacturedProduct').tag('code')
        product_name = el.attr('displayName').strip()
        product_code = el.attr('code')
        product_code_system = el.attr('codeSystem')

        product_original_text = None
        el = entry.tag('manufacturedProduct').tag('originalText')
        if not el.is_empty():
            product_original_text = core.strip_whitespace(el.val())
        # if we don't have a product name yet, try the originalText version
        if not product_name and product_original_text:
            product_name = product_original_text

        el = entry.tag('manufacturedProduct').els_by_tag('translation')
        manu_data = {}
        for item in el:
            csname = item.attr("codeSystemName").title()
            manu_data[csname] = {}
            manu_data[csname]["Name"] = item.attr("displayName")
            manu_data[csname]["code"] = item.attr("code")
            manu_data[csname]["codeSystem"] = item.attr("codeSystem")
            manu_data[csname]["codeSystemName"] = item.attr("codeSystemName")

        if "National Drug Codes" in manu_data:
            translation_name = manu_data["National Drug Codes"]["Name"]
            translation_code = manu_data["National Drug Codes"]["code"]
            translation_code_system = manu_data["National Drug Codes"]["codeSystem"]
            translation_code_system_name = manu_data["National Drug Codes"]["codeSystemName"]
        else:
            translation_name = manu_Data[manu_data.keys()[0]]["Name"]
            translation_code = manu_data[manu_data.keys()[0]]["code"]
            translation_code_system = manu_data[manu_data.keys()[0]]["codeSystem"]
            translation_code_system_name = manu_data[manu_data.keys()[0]]["codeSystemName"]

            #el = entry.tag('manufacturedProduct').tag('translation')
            #translation_name = el.attr('displayName')
            #if translation_name not in ["", None]:
                #translation_name = translation_name.strip()
            #translation_code = el.attr('code')
            #translation_code_system = el.attr('codeSystem')
            #translation_code_system_name = el.attr('codeSystemName')

        el = entry.tag('doseQuantity')
        dose_value = el.attr('value')
        dose_unit = el.attr('unit')

        el = entry.tag('rateQuantity')
        rate_quantity_value = el.attr('value')
        rate_quantity_unit = el.attr('unit')

        el = entry.tag('precondition').tag('value')
        precondition_name = el.attr('displayName')
        precondition_code = el.attr('code')
        precondition_code_system = el.attr('codeSystem')

        el = entry.template('2.16.840.1.113883.10.20.22.4.19').tag('value')
        reason_name = el.attr('displayName')
        reason_code = el.attr('code')
        reason_code_system = el.attr('codeSystem')

        el = entry.tag('routeCode')
        route_name = el.attr('displayName')
        route_code = el.attr('code')
        route_code_system = el.attr('codeSystem')
        route_code_system_name = el.attr('codeSystemName')

        # participant/playingEntity => vehicle
        el = entry.tag('participant').tag('playingEntity')
        vehicle_name = el.tag('name').val()

        el = el.tag('code')
        # prefer the code vehicle_name but fall back to the non-coded one
        vehicle_name = el.attr('displayName') or vehicle_name
        vehicle_code = el.attr('code')
        vehicle_code_system = el.attr('codeSystem')
        vehicle_code_system_name = el.attr('codeSystemName')

        el = entry.tag('administrationUnitCode')
        administration_name = el.attr('displayName')
        administration_code = el.attr('code')
        administration_code_system = el.attr('codeSystem')
        administration_code_system_name = el.attr('codeSystemName')

        # performer => prescriber
        #el = entry.tag('performer')
        author = entry.tag("author")
        provider_name = parse_name(author.tag("assignedAuthor").tag("assignedPerson").tag("name"))
#        provider_phone = author.tag("assignedAuthor").tag("telecom")
#        provider_addr = parse_address(author.tag("assignedAuthor").tag("addr"))
        prescriber_organization = el.tag('name').val()
        prescriber_person = None

        data.append(wrappers.ObjectWrapper(
            date_range=wrappers.ObjectWrapper(
                start=start_date,
                end=end_date
            ),
            text=sig,
            status=status,
            product=wrappers.ObjectWrapper(
                name=product_name,
                code=product_code,
                code_system=product_code_system,
                text=product_original_text,
                translation=wrappers.ObjectWrapper(
                    name=translation_name,
                    code=translation_code,
                    code_system=translation_code_system,
                    code_system_name=translation_code_system_name
                )
            ),
            dose_quantity=wrappers.ObjectWrapper(
                value=dose_value,
                unit=dose_unit
            ),
            rate_quantity=wrappers.ObjectWrapper(
                value=rate_quantity_value,
                unit=rate_quantity_unit
            ),
            precondition=wrappers.ObjectWrapper(
                name=precondition_name,
                code=precondition_code,
                code_system=precondition_code_system
            ),
            reason=wrappers.ObjectWrapper(
                name=reason_name,
                code=reason_code,
                code_system=reason_code_system
            ),
            route=wrappers.ObjectWrapper(
                name=route_name,
                code=route_code,
                code_system=route_code_system,
                code_system_name=route_code_system_name
            ),
            schedule=wrappers.ObjectWrapper(
                type=schedule_type,
                period_value=schedule_period_value,
                period_unit=schedule_period_unit
            ),
            vehicle=wrappers.ObjectWrapper(
                name=vehicle_name,
                code=vehicle_code,
                code_system=vehicle_code_system,
                code_system_name=vehicle_code_system_name
            ),
            administration=wrappers.ObjectWrapper(
                name=administration_name,
                code=administration_code,
                code_system=administration_code_system,
                code_system_name=administration_code_system_name
            ),
            prescriber=wrappers.ObjectWrapper(
                organization=prescriber_organization,
                person=prescriber_person,
                provider=provider_name,
            )
        ))

    return data