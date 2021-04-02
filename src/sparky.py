from SPARQLWrapper import SPARQLWrapper, JSON


class Sparky:

    def __init__(self, duo_consent, consent_required_info, base_url):
        self.duo_consent = duo_consent
        self.consent_required_info: set = consent_required_info

        self.sparql = SPARQLWrapper(base_url)
        self.sparql.setReturnFormat(JSON)

        self.prefix_to_uri = {
            "http://schema.org/": "schema",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "https://www.wikidata.org/wiki/": "wd",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://purl.obolibrary.org/obo/": "purl",
            "file:/uploaded/generated/": "ug"
        }
        self.uri_to_prefix = {
            "schema": "http://schema.org/",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "wd": "https://www.wikidata.org/wiki/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "purl": "http://purl.obolibrary.org/obo/",
            "ug": "file:/uploaded/generated/"
        }

        self.select = {"name": {"name": "pred", "var": "?pred", "modifier": "DISTINCT", "encasing": False}}

        self.where = []
        self.where.append({"s": "?s0", "p": "rdf:type", "o": "wd:Q181600"})
        self.where.append({"s": "?s0", "p": "?pred", "o": "?o0"})

        self.filter = []
        self.filter_idx = {}

        self.results = []

    def construct_query(self, select=None, add_duo=True, verbose=False):
        select = select if select else self.get_select()
        query = f"""{self.get_prefixes()}\nSELECT {select}\nWHERE {{{self.get_where(add_duo=add_duo)}\n{self.get_filter()}}}"""
        if verbose:
            print(query)

        return query

    def execute_query(self, select=None, add_duo=True):
        self.sparql.setQuery(self.construct_query(select, add_duo=add_duo))
        results = self.sparql.query().convert()
        # result_vars = results['head']['vars']
        result_values = results["results"]["bindings"]

        return result_values

    def transform_results(self, result_values):

        self.results = []

        for result_value in result_values:

            uri_unres = result_value['pred']['value']
            uri_dict = self.resolve_kg_id(uri_unres)

            if not uri_dict:
                continue

            aType = self.get_type(uri_dict['prefix'] + ":" + uri_dict['value'])

            dp, ioc = self.get_summary(uri_dict['prefix'] + ":" + uri_dict['value'])

            self.results.append(
                {"name": uri_dict['name'], "prefix": uri_dict['prefix'], "value": uri_dict['value'],
                 "dp": dp, "ioc": ioc, "type": aType})

        return self.results

    def get_summary(self, name):

        last_w = self.where.pop(-1)
        self.where.append({"s": last_w['s'], "p": name, "o": last_w['o']})

        select = f"(COUNT({last_w['o']}) AS ?datapoints)  (COUNT(DISTINCT {last_w['s']}) AS ?inobj)"

        results = self.execute_query(select, add_duo=True)

        self.where.pop(-1)
        self.where.append(last_w)

        data_points = results[0]['datapoints']['value']
        in_obj_count = results[0]['inobj']['value']

        return data_points, in_obj_count

    def display_results(self):
        results = self.execute_query()
        results = self.transform_results(results)
        print("")
        counter = 0
        for result in results:
            tipe = "Object" if result['type'] == 'object' else ("Attribute: " + result['type'])
            line = f"""{counter}| {tipe:<20}| {result['name']:<15}| Number of datapoints: {result['dp']:<5}| In Parent Objects: {result['ioc']:<2}"""
            print(line)
            counter +=1
        print("")
        return results

    def get_filter(self):
        if len(self.filter) == 0:
            return ""
        filter_str = f"""\tFILTER("""
        for filte in self.filter:
            filter_str += f"xsd:{filte['type']}({filte['attr']}) {filte['condition']} {filte['value']} and "

        return filter_str[:-4] + f").\n"

    def get_select(self):
        select_str = f""
        for name in self.select.keys():
            modif = self.select[name]['modifier']
            vari = self.select[name]['var']
            if self.select[name]['encasing']:
                select_str += f"{modif}({vari}) "
            else:
                select_str += f"{modif} {vari} "
        return select_str[:-1]

    def get_prefixes(self):
        prefix_str = f""
        for key in self.uri_to_prefix.keys():
            prefix_str += f"PREFIX {key}: <{self.uri_to_prefix[key]}>\n"
        return prefix_str

    def get_where(self, add_duo=True):
        where_str = f"""\n"""
        count = 0
        for line in self.where:
            where_str += f"""\t{line['s']} {line['p']} {line['o']}.\n"""
            # For example if ?patient ?rdf:type wd:patienttype // need type call to find patients!
            if line['o'] in self.consent_required_info and add_duo:
                where_str += f"\t{line['s']} purl:DUO_0000001 ?duo{count}.\n"
                where_str += f"\t?duo{count} purl:IAO_0000618 '{self.duo_consent['main']}'.\n"

                for sec_cond in self.duo_consent['secondary']:
                    where_str += f"\t?duo{count} purl:IAO_0000641 '{sec_cond}'. \n"

                count += 1
                continue

            # for example if ?patient wd:GLucose ?data // could work well with bridge idea for specific data
            if line['p'] in self.consent_required_info and line['o'].startswith("?") and add_duo:
                # insert_consent_check = f'\t{o} purl:DUO_0000001 "{statement}". \n'
                where_str += f"\t{line['o']} purl:DUO_0000001 ?duo{count}.\n"
                where_str += f"\t?duo{count} purl:IAO_0000618 '{self.duo_consent['main']}'.\n"

                for sec_cond in self.duo_consent['secondary']:
                    where_str += f'\t?duo{count} purl:IAO_0000641 "{sec_cond}". \n'

                count += 1
                continue

        return where_str[:-1]

    def resolve_kg_id(self, uri):
        exclude = {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "type",
            "https://www.wikidata.org/wiki/Q853614": "identifier",
            "http://purl.obolibrary.org/obo/DUO_0000001": "Data use permission",
            "http://www.w3.org/2000/01/rdf-schema#type": "type",
        }

        if uri in exclude:
            return None

        resolved = {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "type",
            "https://www.wikidata.org/wiki/Q853614": "identifier",
            "https://www.wikidata.org/wiki/Q37525": "glucose",
            "https://www.wikidata.org/wiki/Q895262": "hasDiabetes",
            "https://www.wikidata.org/wiki/Q7240673": "insulin",
            "https://www.wikidata.org/wiki/Q2095": "food",
            "http://purl.obolibrary.org/obo/DUO_0000001": "Data use permission",
            "https://www.wikidata.org/wiki/Q185836": "age",
            "https://www.wikidata.org/wiki/Q857525": "annotation",
            "https://www.wikidata.org/wiki/Q12453": "measurement",
            "https://www.wikidata.org/wiki/Q57481290": "comments",
            "https://www.wikidata.org/wiki/Q205892": "Calendar date",
            "https://www.wikidata.org/wiki/Q11471": "time",
            "https://www.wikidata.org/wiki/Q47574": "unit of measurement",
            "file:/uploaded/generated/fast_insulin": "fast insuling",
            "file:/uploaded/generated/slow_insulin": "slow insuling",
            "file:/uploaded/generated/balance": "balance",
            "https://www.wikidata.org/wiki/Q1200750": "description",
            "https://www.wikidata.org/wiki/Q93873471": "calories",
            "https://www.wikidata.org/wiki/Q478798": "image",
            "https://www.wikidata.org/wiki/Q2498665": "food quality",
            "https://www.wikidata.org/wiki/Q56241591": "type description",
            "https://www.wikidata.org/wiki/Q6045928": "end date",
            "https://www.wikidata.org/wiki/P582": "end time",
            "https://www.wikidata.org/wiki/Q10855024": "start dadte",
            "https://www.wikidata.org/wiki/Q24575110": "start time"
        }

        if uri not in resolved:
            print("NOT FOUND: " + uri)

        prefix, value = self.uri_format_rdf(uri)

        return {"name": resolved[uri], "prefix": prefix, "value": value}

    def uri_format_rdf(self, uri):
        uri_split = str(uri).rsplit("/", 1)

        prefix_uri = uri_split[0]
        value = uri_split[1]

        if prefix_uri in self.prefix_to_uri:
            prefix = self.prefix_to_uri[prefix_uri]
        elif prefix_uri + "/" in self.prefix_to_uri:
            prefix = self.prefix_to_uri[prefix_uri + "/"]
        else:
            print(f"NOT FOUND URI PREFIX: {uri}")
            return "not found", "not found"
        # print(f"prefix: {prefix}, value: {value}")
        return prefix, value

    def get_type(self, name):

        last_w = self.where.pop(-1)
        self.where.append({"s": last_w['s'], "p": name, "o": last_w['o']})
        self.where.append({"s": last_w['o'], "p": "?asdf", "o": "?qwert"})
        is_obj_result = self.execute_query(f"DISTINCT (datatype({last_w['o']}) as ?dt)", add_duo=False)

        self.where.pop(-1)

        if len(is_obj_result) > 0:
            self.where.pop(-1)
            self.where.append(last_w)
            return "object"

        is_obj_result = self.execute_query(f"DISTINCT(datatype({last_w['o']}) as ?dt)", add_duo=False)

        value = is_obj_result[0]['dt']['value']
        val_str = value.split('#')[1]

        self.where.pop(-1)
        self.where.append(last_w)

        return val_str

    def advance(self, result):
        last_w = self.where.pop(-1)
        last_w['p'] = f"{result['prefix']}:{result['value']}"
        self.where.append(last_w)
        new_w = {'s': last_w['o'], 'p': '?pred', 'o': '?o' + str(len(self.where))}
        self.where.append(new_w)

    def previous(self):
        self.where.pop(-1)
        self.where[-1]['p'] = '?pred'
        for idc in self.filter_idx.keys():
            if self.filter_idx[idc] < len(self.where)-1:
                self.where.pop(-1)
                self.where[-1]['p'] = '?pred'
                self.filter.pop(idc)


    def add_filter(self, result, condition, value):
        last_w = self.where.pop(-1)

        idc = 0
        while idc < 100:
            if idc in self.filter_idx:
                idc += 1
            else:
                break

        self.filter_idx[idc] = len(self.where)

        new_w = {'s': last_w['s'], 'p': f"{result['prefix']}:{result['value']}", 'o': '?o' + str(len(self.where))}

        self.where.append(new_w)
        self.where.append(last_w)

        fil = {'type': result['type'], 'attr': f"{self.where[-2]['o']}", 'condition': condition, 'value': value,
               'id': idc}

        self.filter.append(fil)

    def return_results(self):
        ret = []
        results = self.execute_query(select=f"  DISTINCT ?s0")
        for res in results:
           ret.append(res['s0']['value'])
        return ret