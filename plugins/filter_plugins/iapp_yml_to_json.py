#!/usr/bin/env python

from pprint import pprint

class FilterModule(object):
    '''This class is used to convert yml object to json object'''

    def filters(self):
        return {
             'iapp_yml_to_json': iapp_yml_to_json
        }


def iapp_yml_to_json(collection):
    return YmlToJsonConverter(collection).parse_json_dict()



class YmlToJsonConverter:
    '''This class is used to convert yml object to json object'''

    def __init__(self, yml_input):
        self.yml_input = yml_input
        self.variables = []
        self.tables = []
        self.json_output = {}

    def parse_json_variables(self, key, value):
        dict_object = {}
        dict_object["encrypted"] = "no"
        dict_object["name"] =  key
        if value is None:
            value = ""
        if value is True:
            value = "Yes"
        if value is False:
            value = "No"
        dict_object["value"] = value
        self.variables.append(dict_object)
    
    def parse_json_tables(self, key, list_of_dict):
        dict_object = {}
        dict_object["name"] = key
        dict_object["columnNames"] =  self.parse_json_col_names(list_of_dict[0])
        dict_object["rows"] = self.parse_json_rows(list_of_dict)
 
        self.tables.append(dict_object)
    
    def parse_json_col_names(self, dict_obj):
        col_names = dict_obj.keys()
        col_names.sort()
        return col_names

    def parse_json_rows(self, list_of_dict):
        rows = []
        for dict_obj in list_of_dict:
            row = self.parse_json_row(dict_obj)
            rows.append(row)

        return rows
        
    def parse_json_row(self, dict_obj):
        row = {}
        row_values = []
        
        keys = dict_obj.keys()
        keys.sort()
    
        for key in keys:
            value = dict_obj[key]
 
            if value is True:
                value = "yes"
            if value is False:
                value = "no"
           
            if value == "":
                value = ''

            if value is None:
                value = ''
            
            row_values.append(value)
            row["row"] = row_values
    
        return row
        
    def parse_json_dict(self):
        for key in self.yml_input.keys():
            value = self.yml_input[key]
            if (isinstance(value, list) == True):
                self.parse_json_tables(key, value)
            else:
                self.parse_json_variables(key, value)
        
        self.json_output["tables"] = self.tables
        self.json_output["variables"] = self.variables
        return self.json_output
