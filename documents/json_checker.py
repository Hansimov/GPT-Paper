import io
import json
from utils.logger import logger
from pathlib import Path


class JsonChecker:
    def __init__(self):
        pass

    def check(self, input_json=None, fix=True, quiet=True):
        logger.enter_quiet(quiet)

        if type(input_json) == str:
            lines = io.StringIO(input_json).readlines()
        elif isinstance(input_json, Path):
            with open(json_path, "r") as rf:
                lines = rf.readlines()
        else:
            raise Exception("Invalid input json type.")

        # for line in lines:
        #     print(line)

        is_valid = False
        line_num = 0
        while not is_valid or line_num < len(lines):
            try:
                text = "".join(lines)
                data = json.loads(text)
                is_valid = True
            except json.decoder.JSONDecodeError as e:
                line_num = e.lineno
                col_num = e.colno
                logger.err(f"Error at line {line_num}: {e.msg}")
                logger.note(f"{lines[line_num-1]}")
                logger.err("^", indent=col_num)
                if fix:
                    lines = self.fix_by_remove_line(lines, line_num)
                else:
                    raise e

        logger.exit_quiet(quiet)
        res = None
        if is_valid:
            logger.success("Json fixed!")
            # logger.mesg(data)
            res = data
        else:
            logger.note("Invalid json cannot be fixed by removing lines.")
        return res

    def fix_by_remove_line(self, lines, line_number):
        logger.mesg(f"Removing line {line_number}:")
        logger.success(f"{lines[line_number-1]}")
        lines.pop(line_number - 1)
        return lines


if __name__ == "__main__":
    json_path = (
        Path(__file__).parents[1] / "notebook" / "review_outline_details_invalid.txt"
    )
    json_chekcer = JsonChecker()
    json_chekcer.check(json_path, quiet=False)
