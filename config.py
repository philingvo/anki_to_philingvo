class Config:
	
	dir_path = "converted_files"
	anki_filepath = r"F:\ANKI\French_idioms_FR-EN.apkg" # path to anki file

	parts_settings = [
					{'field_name': 'eng',
					'lang': 'en',
					'part_name': 'term',
					'handle_func': lambda text: text.split(" ")[0]},
					{'field_name': 'rus',
					'lang': 'ru',
					'part_name': 'definition'}
					]

	set_type_name = "French-English dictionary"
	set_title = "French Idioms"
	max_elements_in_set = 60