def read_file(file_name: str):
    file = open(file_name, 'r')
    data_file = {}

    level_01_id = 1
    level_02_id = 1
    level_03_id = 1

    for line in file:
        text = line.replace('	', '').replace('\n', '')
        if text != '':
            level = check_level(line)

            if level == 1:
                data_file[f"{level_01_id}"] = {
                    'text': text,
                    'sub_level_id': None
                }
                level_01_id += 1
                level_02_id = 1
                level_03_id = 1
            elif level == 2:
                data_file[f"{level_01_id}-{level_02_id}"] = {
                    'text': text,
                    'sub_level_id': level_01_id - 1,
                    'offset': 1
                }
                level_02_id += 1
                level_03_id = 1
            elif level == 3:
                data_file[f"{level_01_id}-{level_02_id}-{level_03_id}"] = {
                    'text': text,
                    'sub_level_id': level_01_id - 1,
                    'offset': 2
                }
                level_03_id += 1

    file.close()
    return data_file


def check_level(line) -> int:
    if '	' in line:
        return 1 + check_level(line.replace('	', '', 1))
    else:
        return 1
