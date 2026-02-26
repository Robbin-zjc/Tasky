"""
    Tasky is a task deadline tracker application
    Copyright (C) 2022-2025  Abhineet Kelley (AbhiK002)

    This file is part of Tasky.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
import os
import sys
import subprocess
import datetime
import csv
from .taskylog import TaskyLog


class AboutTasky:
    # ------------------  About Tasky -------------------- #
    version = 'v2.1'
    creator = 'Abhineet Kelley'
    release = '20th September 2025'
    github = 'https://github.com/AbhiK002/Tasky'
    license = 'https://github.com/AbhiK002/Tasky/blob/main/LICENSE'
    startup_message = "Tasky - Copyright (C) 2022-2025  Abhineet Kelley  -  This program comes with ABSOLUTELY NO WARRANTY. This is a free software, and you are welcome to redistribute it under certain conditions; type `about' to view the license."
    # ---------------------------------------------------- #


class OSFunctions:
    @staticmethod
    def is_windows_system():
        return sys.platform.startswith("win")

    @staticmethod
    def is_system_mac():
        return sys.platform.startswith("darwin")

    @staticmethod
    def is_linux_system():
        return sys.platform.startswith("linux")

    @staticmethod
    def open_file(path):
        if OSFunctions.is_windows_system():
            os.startfile(path)
        elif OSFunctions.is_system_mac():
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    @staticmethod
    def clear_terminal():
        if OSFunctions.is_windows_system():
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    @staticmethod
    def exit_program():
        sys.exit(0)

    @staticmethod
    def set_terminal_title(title: str):
        if OSFunctions.is_windows_system():
            os.system(f"title {title}")
        else:
            sys.stdout.write(f"\33]0;{title}\a")
            sys.stdout.flush()


class Functions:
    PRIORITY_SCORES = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
    }

    def __init__(self):
        self.TL = TaskyLog()
        self.TL.info("Tasky's functions accessed")

        self.taskymain_path = Path.home() / "Tasky"
        self.tasks_path = self.taskymain_path / "newtasks.txt"
        self.old_tasks_path = self.taskymain_path / 'tasks.txt'
        self.meta_tasks_path = self.taskymain_path / 'tasks_meta.txt'
        self.check_tasks_txt()

        self.old_tasks = []

        self.months = {
            "01": 31, "02": 29, "03": 31, "04": 30,
            "05": 31, "06": 30, "07": 31, "08": 31,
            "09": 30, "10": 31, "11": 30, "12": 31,
        }

        self.month_names = {
            1: "january", 2: "february", 3: "march", 4: "april",
            5: "may", 6: "june", 7: "july", 8: "august",
            9: "september", 10: "october", 11: "november", 12: "december",
        }

        self.month_name_to_num = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }

        self.current_year = int(datetime.datetime.today().strftime("%Y"))
        self.str_to_date_obj = datetime.datetime.strptime

        self.spl = [":)", ":(", ":D", ":>", ":<", ":|", ":/", ":\\", ":O", ":P", "XD",
                    ">:(", ">:)", "._.", ".-.", "O_O", "LOL", "LMAO", "-_-",
                    ">_<", "(:", "):", "D:", ":^*", ";-;", ":'D", ":')", ":'("]

        self.TL.info("defined datasets for months, month names and special inputs")

    def tasky_version(self, left_width=23, link=False):
        t_width = 60
        l_width = left_width
        github = AboutTasky.github
        licc = AboutTasky.license
        if link:
            github = f"<a href='{github}'> AbhiK002/Tasky </a>"
            licc = f"<a href='{licc}'> View License </a>"

        about = '\n'.join((
            '-' * t_width + "<br>" * link,
            '  About Tasky  '.center(t_width, '-') + "<br>" * link,
            f'\n{"VERSION".ljust(l_width)} = {AboutTasky.version}{"<br>" * link}',
            f'{"RELEASE DATE".ljust(l_width)} = {AboutTasky.release}{"<br>" * link}',
            f'{"CREATOR".ljust(l_width)} = {AboutTasky.creator}{"<br>" * link}',
            f'{"SOURCE CODE".ljust(l_width)} = {github}{"<br>" * link}',
            f'{"LICENSE".ljust(l_width)} = {licc}{"<br>" * link}',
            '-' * t_width
        ))
        return about

    @staticmethod
    def return_datetime_now_parts():
        return datetime.datetime.now().strftime("%y %m %d %H %M").split()

    def check_tasks_txt(self):
        self.taskymain_path.mkdir(parents=True, exist_ok=True)
        open(self.tasks_path, "a", encoding="utf-8").close()
        open(self.old_tasks_path, "a", encoding="utf-8").close()
        open(self.meta_tasks_path, "a", encoding="utf-8").close()

    def _read_text_compatible(self, path):
        for enc in ("utf-8", "utf-8-sig", "gbk", "cp1252", "latin-1"):
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def read_tasks_file(self):
        self.check_tasks_txt()
        return self._read_text_compatible(self.tasks_path)

    def read_meta_tasks_file(self):
        self.check_tasks_txt()
        return self._read_text_compatible(self.meta_tasks_path)

    @staticmethod
    def is_leap(year):
        return int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0)

    def timediff(self, tt, diff_of: list = False, tasky_output=True):
        self.TL.function(f"timediff({tt})")

        if not diff_of:
            tny, tnm, tnd, tnh, tnmin = self.return_datetime_now_parts()
        else:
            tny, tnm, tnd, tnh, tnmin = diff_of

        tty, ttm, ttd, tth, ttmin = tt.split(":")

        diffy = int(tty) - int(tny)
        diffm = int(ttm) - int(tnm)
        diffd = int(ttd) - int(tnd)
        diffh = int(tth) - int(tnh)
        diffmin = int(ttmin) - int(tnmin)

        if diffmin < 0:
            diffmin += 60
            diffh -= 1

        if diffh < 0:
            diffh += 24
            diffd -= 1

        if diffd < 0:
            diffd += self.months.get(tnm)
            if int(tnm) == 2 and not self.is_leap(tny):
                diffd -= 1
            diffm -= 1

        if diffm < 0:
            diffm += 12
            diffy -= 1

        if not tasky_output:
            return [diffy, diffm, diffd, diffh, diffmin]

        if diffy < 0:
            output = "Task Expired".rjust(19)
        else:
            output = (
                f"{(f'{diffy}y' * any((diffy,))).rjust(3)} "
                f"{(f'{diffm}M' * any((diffy, diffm))).rjust(3)} "
                f"{(f'{diffd}d' * any((diffy, diffm, diffd))).rjust(3)} "
                f"{(f'{diffh}h' * any((diffy, diffm, diffd, diffh))).rjust(3)} "
                f"{(f'{diffmin}m' * any((diffy, diffm, diffd, diffh, diffmin))).rjust(3)}"
            )

            if diffmin <= 30 and sum((diffy, diffm, diffd, diffh)) == 0:
                output = f"LESS THAN {diffmin} MIN".rjust(19)

        self.TL.info(output)
        return output

    def clear_tasks(self):
        open(self.tasks_path, 'w', encoding="utf-8").close()
        open(self.meta_tasks_path, 'w', encoding="utf-8").close()
        self.TL.function("all current tasks cleared")

    def is_valid_task(self, task):
        self.TL.function(f"CHECKING IF '{task}' IS VALID TASK STRING")
        try:
            ttime, tname, tdesc = task.split("\t", 2)
        except ValueError:
            self.TL.error("GIVEN TASK STRING IS INVALID (unpack error)")
            return False

        try:
            s1_conditions = (
                not all((ttime, tname.strip())),
                not 1 <= len(tname.strip()) <= 30,
                len(tdesc.strip()) > 168,
                len(ttime) != 14,
                not str(self.current_year)[-2:] <= ttime[:2] <= '99',
            )
        except IndexError:
            self.TL.error("GIVEN TASK STRING IS INVALID (index error)")
            return False

        if any(s1_conditions):
            self.TL.error("GIVEN TASK STRING IS INVALID (any cond1)")
            return False

        try:
            datetime.datetime.strptime(ttime, "%y:%m:%d:%H:%M")
        except ValueError:
            self.TL.error("GIVEN TASK STRING IS INVALID (date conversion)")
            return False

        return True

    @staticmethod
    def task_identity(task):
        ttime, tname, _ = task.split("\t", 2)
        return f"{ttime}\t{tname.strip()}"

    def parse_deadline_to_datetime(self, tt):
        return datetime.datetime.strptime(tt, "%y:%m:%d:%H:%M")

    def read_meta_map(self):
        self.check_tasks_txt()
        meta_map = {}
        for raw in self._read_text_compatible(self.meta_tasks_path).splitlines():
            try:
                key, category, priority, source, status = raw.split("\t", 4)
            except ValueError:
                continue
            meta_map[key] = {
                "category": category or "General",
                "priority": (priority or "Medium").title(),
                "source": source or "manual",
                "status": status or "todo",
            }
        return meta_map

    def write_meta_map(self, meta_map):
        rows = []
        for key, meta in sorted(meta_map.items()):
            rows.append(
                f"{key}\t{meta.get('category', 'General')}\t{meta.get('priority', 'Medium')}\t"
                f"{meta.get('source', 'manual')}\t{meta.get('status', 'todo')}"
            )
        with open(self.meta_tasks_path, "w", encoding="utf-8") as meta_file:
            meta_file.write("\n".join(rows))

    def sync_meta_with_tasks(self, tasks):
        meta_map = self.read_meta_map()
        valid_keys = set()
        for task in tasks:
            key = self.task_identity(task)
            valid_keys.add(key)
            if key not in meta_map:
                meta_map[key] = {
                    "category": "General",
                    "priority": "Medium",
                    "source": "manual",
                    "status": "todo",
                }

        for key in list(meta_map.keys()):
            if key not in valid_keys:
                del meta_map[key]

        self.write_meta_map(meta_map)
        return meta_map

    def update_task_meta(self, task, category=None, priority=None, source=None, status=None):
        meta_map = self.read_meta_map()
        key = self.task_identity(task)
        existing = meta_map.get(key, {
            "category": "General",
            "priority": "Medium",
            "source": "manual",
            "status": "todo",
        })
        if category is not None:
            existing["category"] = category
        if priority is not None:
            existing["priority"] = priority.title()
        if source is not None:
            existing["source"] = source
        if status is not None:
            existing["status"] = status
        meta_map[key] = existing
        self.write_meta_map(meta_map)

    def import_tasks_from_csv(self, csv_path):
        tasks = self.read_and_sort_tasks_file()
        imported = 0
        with open(csv_path, newline='', encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                name = (row.get("name") or row.get("task") or "").strip()
                deadline = (row.get("deadline") or row.get("due") or "").strip()
                desc = (row.get("description") or "").strip()
                category = (row.get("category") or "General").strip() or "General"
                priority = (row.get("priority") or "Medium").strip().title() or "Medium"

                if not name or not deadline:
                    continue

                parsed = None
                for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
                    try:
                        parsed = datetime.datetime.strptime(deadline, fmt)
                        if " %H:%M" not in fmt:
                            parsed = parsed.replace(hour=23, minute=59)
                        break
                    except ValueError:
                        continue
                if parsed is None:
                    continue

                tt = parsed.strftime("%y:%m:%d:%H:%M")
                task_string = f"{tt}\t{name[:30]}\t{desc[:168]}"
                if self.is_valid_task(task_string):
                    tasks.append(task_string)
                    imported += 1

        tasks = self.remove_duplicates(self.strip_tasks(tasks))[:100]
        self.write_tasks(tasks)
        meta_map = self.sync_meta_with_tasks(tasks)
        for task in tasks:
            key = self.task_identity(task)
            if meta_map[key].get("source") == "manual":
                meta_map[key]["source"] = "import"
                if meta_map[key].get("category") == "General":
                    meta_map[key]["category"] = category if 'category' in locals() else "General"
                if meta_map[key].get("priority") == "Medium":
                    meta_map[key]["priority"] = priority if 'priority' in locals() else "Medium"
        self.write_meta_map(meta_map)
        return imported

    def strip_tasks(self, tlist):
        for i, task in enumerate(tlist):
            ttime, tname, tdesc = task.split("\t", 2)
            tlist[i] = f"{ttime}\t{tname.strip()}\t{tdesc.strip()}"
        return tlist

    def write_tasks(self, last):
        with open(self.tasks_path, "w", encoding="utf-8") as taskfile:
            taskfile.write('\n'.join(last))

    def read_and_sort_tasks_file(self):
        self.check_tasks_txt()
        read_data = self._read_text_compatible(self.tasks_path).split('\n')
        taskslist = sorted(filter(self.is_valid_task, read_data))

        if not self.converted():
            self.get_old_tasks()
            taskslist = sorted(set(taskslist) | set(self.old_tasks))
            check_path = self.taskymain_path / 'old_checked'
            check_path.mkdir(parents=True, exist_ok=True)

        taskslist = self.remove_duplicates(self.strip_tasks(taskslist))

        if len(taskslist) > 100:
            taskslist = taskslist[:100]

        self.write_tasks(taskslist)
        self.sync_meta_with_tasks(taskslist)
        return taskslist

    def converted(self):
        check_path = self.taskymain_path / 'old_checked'
        return check_path.exists()

    def get_old_tasks(self):
        self.check_tasks_txt()
        read_data = self._read_text_compatible(self.old_tasks_path).split('\n')
        if not read_data:
            self.old_tasks = []
            return
        converted_data = list(map(lambda task: '\t'.join(task.split("=", 2) + ['']), read_data))
        self.old_tasks = sorted(filter(self.is_valid_task, converted_data))

    def remove_duplicates(self, tlist):
        final = []
        descriptions = {}
        for task in tlist:
            ttime, tname, tdesc = task.split('\t', 2)
            key = f"{ttime}\t{tname}\t"
            if tdesc != '':
                descriptions[key] = tdesc
            if key not in final:
                final.append(key)

        for i, key in enumerate(final):
            final[i] = key + descriptions.get(key, '')

        return final

    def remove(self, num, last_copy):
        last = last_copy
        try:
            target = last[int(num) - 1]
            key = self.task_identity(target)
            last.pop(int(num) - 1)
        except IndexError:
            return

        self.write_tasks(last)
        meta_map = self.read_meta_map()
        if key in meta_map:
            del meta_map[key]
            self.write_meta_map(meta_map)

    def calculate_risk_score(self, task_time, priority="Medium"):
        try:
            deadline = self.parse_deadline_to_datetime(task_time)
        except ValueError:
            return 0

        now = datetime.datetime.now()
        remaining_hours = (deadline - now).total_seconds() / 3600
        priority_weight = self.PRIORITY_SCORES.get(priority.lower(), 2)

        if remaining_hours <= 0:
            return 100
        if remaining_hours <= 24:
            base = 85
        elif remaining_hours <= 72:
            base = 65
        elif remaining_hours <= 168:
            base = 45
        else:
            base = 25

        return min(100, int(base + priority_weight * 4))

    def return_deadlines_with_meta(self, given_tasks_list=False):
        tasks = given_tasks_list if given_tasks_list else self.read_and_sort_tasks_file()
        meta_map = self.sync_meta_with_tasks(tasks)
        deadlines = []

        for i, task in enumerate(tasks):
            ttime, tname, tdesc = task.split("\t", 2)
            key = self.task_identity(task)
            meta = meta_map.get(key, {
                "category": "General",
                "priority": "Medium",
                "source": "manual",
                "status": "todo",
            })
            deadline = self.timediff(ttime)
            risk = self.calculate_risk_score(ttime, meta.get("priority", "Medium"))

            deadlines.append({
                "num": str(i + 1),
                "deadline_text": deadline,
                "name": tname,
                "desc": tdesc,
                "ttime": ttime,
                "category": meta.get("category", "General"),
                "priority": meta.get("priority", "Medium"),
                "source": meta.get("source", "manual"),
                "status": meta.get("status", "todo"),
                "risk": risk,
            })

        return deadlines

    def return_deadlines(self, given_tasks_list=False):
        data = self.return_deadlines_with_meta(given_tasks_list)
        return [(d["num"], d["deadline_text"], d["name"], d["desc"]) for d in data]

    def analyze_user_state(self):
        tasks = self.return_deadlines_with_meta()
        if not tasks:
            return {
                "focus_score": 100,
                "overdue_ratio": 0.0,
                "high_risk_count": 0,
                "nudge": "今天没有待办，保持节奏即可。",
            }

        overdue = [t for t in tasks if t["deadline_text"].strip() == "Task Expired"]
        high_risk = [t for t in tasks if t["risk"] >= 75]

        overdue_ratio = len(overdue) / len(tasks)
        risk_ratio = len(high_risk) / len(tasks)
        focus_score = max(0, int(100 - overdue_ratio * 50 - risk_ratio * 35))

        if overdue_ratio > 0.35:
            nudge = "你有较多已过期任务，先清理 1 个最小任务建立动量。"
        elif risk_ratio > 0.40:
            nudge = "高风险任务偏多：建议先做 25 分钟冲刺，优先 High/Critical。"
        else:
            nudge = "状态可控：继续按优先级推进，先完成再完美。"

        return {
            "focus_score": focus_score,
            "overdue_ratio": round(overdue_ratio, 2),
            "high_risk_count": len(high_risk),
            "nudge": nudge,
        }
