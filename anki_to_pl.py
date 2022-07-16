# coding: utf-8

from AnkiTools.tools.read import readApkg
# https://pypi.org/project/AnkiTools/0.1.9/
# https://github.com/patarapolw/AnkiTools
import json
import os
import re
import sys
from config import Config


class ANKI_PL_Convertor:

	config_names = ['dir_path', 'anki_filepath', 'parts_settings', 'set_type_name', 'set_title', 'max_elements_in_set']

	def __init__(self, config):
		for config_name in self.config_names:
			setattr(self, config_name, getattr(config, config_name))
		self.anki = readApkg(self.anki_filepath)

	def show_sets(self):
		for set_id, item in self.anki.models.items():
			print("------------")
			print("Set:", set_id)
			for field_index in range(len(item['fields'])):
				print(field_index, "-", item['fields'][field_index])
			print("############")

	def show_field_names(self, set_id=None):
		if not set_id:
			element_id = sorted(list(self.anki.cards.keys()))[0]
			element = self.anki.cards[element_id]
			set_is_found = True
		else:
			set_is_found = False
			elements_ids = sorted(list(self.anki.cards.keys()))
			for element_id in elements_ids:
				element = self.anki.cards[element_id]
				if set_id == element["note"]['mid']:
					set_is_found = True
					break

		if set_is_found:
			print("Element from set {}".format(element["note"]['mid']))
			print("ID", element_id)
			print("Parts:")
			for field_index in range(len(element["note"]["model"]["fields"])):
				print(field_index, '-', element["note"]["model"]["fields"][field_index], '-', element["note"]["content"][field_index])				
				if self.parts_settings[field_index].get("handle_func"):
					print("\tHandeled content:", self.parts_settings[field_index]["handle_func"](element["note"]["content"][field_index]))
		else:
			print("Set \"{}\" hasn't been found".format(set_id))

	def create_file(self):
		parts_settings = self.parts_settings
		set_type_name = self.set_type_name
		set_title = self.set_title
		max_elements_in_set = self.max_elements_in_set

		sets = {}
		for set_id, item in self.anki.models.items():
			set_id = str(set_id)
			sets[set_id] = {"version": 0,
							"set": {"set_properties": {"type": {"language": {"code": parts_settings[0]["lang"]},
																"name": set_type_name,
																"abstract": ""},
														"title": item['name']},
														"parts_types": []},
							"parts_indexes": [],
							"elements": []}

			for part_number in range(len(parts_settings)):
				part_setting = parts_settings[part_number]
				sets[set_id]["set"]["parts_types"].append({"type": {"format": {"name": "text"},
																			"language": {"code": part_setting["lang"]},
																			"name": part_setting["part_name"]},
																			"position": part_number + 1})
				sets[set_id]["parts_indexes"].append(item['fields'].index(part_setting["field_name"]))

		elements_ids = sorted(list(self.anki.cards.keys()))

		elements_unique = []

		element_position = 0
		for element_id in elements_ids:

			element = self.anki.cards[element_id]

			set_id = element["note"]['mid']

			if not sets.get(set_id):
				sets[set_id] = []

			set_parts_indexes = sets[set_id]["parts_indexes"]
			
			parts = []
			concat_content = ''
			for index in range(len(set_parts_indexes)):

				part_index = set_parts_indexes[index]
				part_content = element["note"]["content"][part_index]

				if parts_settings[index].get("handle_func"):
					part_content = parts_settings[index]["handle_func"](part_content)

				parts.append({"part": {"content": part_content,
										"style": None,
										"comment": None},
								"position": index + 1})
				concat_content += part_content

			if concat_content not in elements_unique:
				elements_unique.append(concat_content)
				element_position += 1
				sets[set_id]["elements"].append({"parts": parts,
												"element": {"abstract": None},
												"position": element_position})

		for set_id, set_data in sets.items():

			if not os.path.exists(self.dir_path):
				os.mkdir(self.dir_path)

			if not set_title:
				set_title = set_data["set"]["set_properties"]["title"]

			filename_base = re.sub("[/\\:*«»<>[]?\"\n\r\t]", " ", set_title)


			def chunks(lst, n):
				for i in range(0, len(lst), n):
					yield lst[i:i + n]

			elements_in_chunks = chunks(set_data["elements"], max_elements_in_set)

			chunk_number = 0
			for elements_in_chunk in elements_in_chunks:
				chunk_number += 1
				set_data["set"]["set_properties"]["title"] = "{} {}".format(set_title, chunk_number)
				set_data["elements"] = elements_in_chunk
				filename = "{} {}.json".format(filename_base, chunk_number)
				filepath = os.path.join(self.dir_path, filename)

				with open(filepath, 'w', encoding='utf-8') as file:
					json.dump(set_data, file, ensure_ascii=False)

if __name__ == "__main__":
	conv = ANKI_PL_Convertor(Config)
	print(sys.argv)
	if len(sys.argv) == 1 or sys.argv[1] in ['show_field_names', 'sfn']:
		if len(sys.argv) < 3:
			conv.show_field_names()
		else:
			conv.show_field_names(sys.argv[2])
	elif sys.argv[1] in ['create_file', 'cf']:
		conv.create_file()