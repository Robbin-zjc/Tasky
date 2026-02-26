"""
    Tasky is a task deadline tracker application
    Copyright (C) 2022-2025  Abhineet Kelley (AbhiK002)
"""

import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import Qt, QTimer, QSize

from files.gui_ops import TaskyStyle
from files.tasky_ops import Functions

PRIORITY_ITEMS = ["Low", "Medium", "High", "Critical"]
CATEGORY_ITEMS = ["General", "Work", "Study", "Health", "Personal", "Research"]

I18N = {
    "en": {
        "window_title": "Tasky - Deadline Accelerator",
        "heading": "DEADLINE ACCELERATOR",
        "view": "View",
        "category": "Category",
        "new_task": " New Task",
        "import_csv": " Import CSV",
        "theme": " Theme",
        "about": "About Tasky",
        "language_btn": " 中文",
        "by_time": "By Time",
        "by_category": "By Category",
        "by_priority": "By Priority",
        "all": "All",
        "focus": "Focus",
        "high_risk": "High Risk",
        "clear_all": "CLEAR ALL TASKS",
        "select_csv": "Select CSV File",
        "import_done": "Import Complete",
        "import_done_msg": "Imported {count} tasks from CSV.",
        "delete_task": "Delete Task",
        "delete_confirm": "Delete Confirmation",
        "delete_confirm_msg": "Are you sure you want to delete Task {num}?\n\nTask Name: {name}\n",
        "clear_confirm": "Clear All Confirmation",
        "clear_confirm_msg": "Do you want to DELETE ALL tasks?\n\n(You cannot undo this)",
    },
    "zh": {
        "window_title": "Tasky - 截止加速器",
        "heading": "截止加速器",
        "view": "视图",
        "category": "分类",
        "new_task": " 新建任务",
        "import_csv": " 导入 CSV",
        "theme": " 主题",
        "about": "关于 Tasky",
        "language_btn": " English",
        "by_time": "按时间",
        "by_category": "按分类",
        "by_priority": "按优先级",
        "all": "全部",
        "focus": "专注分",
        "high_risk": "高风险",
        "clear_all": "清空全部任务",
        "select_csv": "选择 CSV 文件",
        "import_done": "导入完成",
        "import_done_msg": "已从 CSV 导入 {count} 个任务。",
        "delete_task": "删除任务",
        "delete_confirm": "删除确认",
        "delete_confirm_msg": "确认删除任务 {num} 吗？\n\n任务名：{name}\n",
        "clear_confirm": "清空确认",
        "clear_confirm_msg": "是否删除全部任务？\n\n（此操作不可撤销）",
    }
}

TStyle = TaskyStyle()
TBackEnd = Functions()


class App(QWidget):
    def tr(self, key, **kwargs):
        return I18N[self.language][key].format(**kwargs)

    def __init__(self):
        app = QApplication(sys.argv)
        super(App, self).__init__()

        self.language = "zh"
        self.t_style = TStyle.stylesheet()
        scr_width = int(app.primaryScreen().size().width())
        scr_height = int(app.primaryScreen().size().height())

        self.setWindowTitle(self.tr("window_title"))
        self.setObjectName("MainWindow")
        self.setGeometry(int((scr_width - 900) / 2), int((scr_height - 760) / 2), 900, 760)
        self.setMinimumSize(820, 420)
        self.setWindowIcon(QIcon(TStyle.tlogo_path))
        self.setStyleSheet(self.t_style)

        self.mainlayout = QtWidgets.QVBoxLayout(self)
        self.mainlayout.setSpacing(0)
        self.mainlayout.setContentsMargins(10, 10, 10, 0)

        self.tasks_parted_list = []
        self.tasks_list = []
        self.task_boxes = []
        self.last_read = ''
        self.last_meta_read = ''
        self.current_view_mode = "time"
        self.current_category_filter = "All"
        self.task_window = None

        self.add_top_frame()
        self.add_tasks_container()
        self.add_buttons_frame()

        self.mainlayout.addWidget(self.tasks_frame, 1)
        self.mainlayout.addWidget(self.buttons_frame)

        self.last_datetime = TBackEnd.return_datetime_now_parts()
        self.gui_refresh_timer = QTimer()
        self.gui_refresh_timer.timeout.connect(self.refresh_gui)
        self.gui_refresh_timer.setInterval(600)
        self.gui_refresh_timer.start()

        self.refresh_tasks()

        self.show()
        sys.exit(app.exec_())

    def add_top_frame(self):
        self.tasks_frame = QWidget(self)
        self.tasks_frame.setObjectName("TasksFrame")
        self.tasks_frame_layout = QtWidgets.QVBoxLayout(self.tasks_frame)
        self.tasks_frame_layout.setContentsMargins(8, 0, 8, 0)

        self.heading_label = QtWidgets.QLabel(self.tr("heading"))
        self.heading_label.setObjectName("TasksHeadingLabel")
        self.heading_label.setAlignment(Qt.AlignCenter)

        self.controls_frame = QWidget(self.tasks_frame)
        controls_layout = QtWidgets.QHBoxLayout(self.controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.view_mode_combo = QtWidgets.QComboBox(self.controls_frame)
        self.view_mode_combo.addItems([self.tr("by_time"), self.tr("by_category"), self.tr("by_priority")])
        self.view_mode_combo.currentTextChanged.connect(self.change_view_mode)

        self.category_combo = QtWidgets.QComboBox(self.controls_frame)
        self.category_combo.addItem(self.tr("all"))
        self.category_combo.addItems(CATEGORY_ITEMS)
        self.category_combo.currentTextChanged.connect(self.change_category_filter)

        self.view_label = QtWidgets.QLabel(self.tr("view"))
        self.category_label = QtWidgets.QLabel(self.tr("category"))

        controls_layout.addWidget(self.view_label)
        controls_layout.addWidget(self.view_mode_combo)
        controls_layout.addSpacing(16)
        controls_layout.addWidget(self.category_label)
        controls_layout.addWidget(self.category_combo)
        controls_layout.addStretch()

        self.analysis_label = QtWidgets.QLabel("")
        self.analysis_label.setAlignment(Qt.AlignCenter)
        self.analysis_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #123456;")

        self.tasks_frame_layout.addWidget(self.heading_label)
        self.tasks_frame_layout.addWidget(self.controls_frame)
        self.tasks_frame_layout.addWidget(self.analysis_label)

    def add_tasks_container(self):
        self.tasks_container = QWidget(self.tasks_frame)
        self.tasks_container.setObjectName("TasksContainer")

        self.tasks_layout = QtWidgets.QVBoxLayout(self.tasks_container)
        self.tasks_layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.tasks_layout.setContentsMargins(12, 12, 5, 12)

        self.tasks_scroll_area = QtWidgets.QScrollArea()
        self.tasks_scroll_area.setObjectName("TasksScrollArea")
        self.tasks_scroll_area.setWidgetResizable(True)
        self.tasks_scroll_area.setWidget(self.tasks_container)

        self.tasks_frame_layout.addWidget(self.tasks_scroll_area, 1)

    def add_buttons_frame(self):
        self.buttons_frame = QWidget(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self.buttons_frame)

        self.new_task_button = QtWidgets.QPushButton(self.tr("new_task"))
        self.new_task_button.setIcon(QIcon(TStyle.new_task_icon))
        self.new_task_button.setObjectName("NewTaskButton")
        self.new_task_button.clicked.connect(self.open_task)

        self.import_button = QtWidgets.QPushButton(self.tr("import_csv"))
        self.import_button.setObjectName("NewTaskButton")
        self.import_button.clicked.connect(self.import_csv_tasks)

        self.switch_mode_button = QtWidgets.QPushButton(f" {'Dark' if TStyle.theme == 'light' else 'Light'}{self.tr('theme')}")
        self.switch_mode_button.setIcon(QIcon(TStyle.switch_mode_icon))
        self.switch_mode_button.setObjectName("SwitchModeButton")
        self.switch_mode_button.clicked.connect(self.switch_theme)

        self.language_button = QtWidgets.QPushButton(self.tr("language_btn"))
        self.language_button.setObjectName("SwitchModeButton")
        self.language_button.clicked.connect(self.toggle_language)

        self.about_tasky = QtWidgets.QPushButton()
        self.about_tasky.setIcon(QIcon(TStyle.tlogo_path))
        self.about_tasky.setObjectName("AboutButton")
        self.about_tasky.setToolTip(self.tr("about"))
        self.about_tasky.clicked.connect(self.show_about_tasky)

        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.new_task_button)
        self.buttons_layout.addWidget(self.import_button)
        self.buttons_layout.addWidget(self.switch_mode_button)
        self.buttons_layout.addWidget(self.language_button)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.about_tasky)

    def apply_language(self):
        self.setWindowTitle(self.tr("window_title"))
        self.heading_label.setText(self.tr("heading"))
        self.view_label.setText(self.tr("view"))
        self.category_label.setText(self.tr("category"))
        self.new_task_button.setText(self.tr("new_task"))
        self.import_button.setText(self.tr("import_csv"))
        self.switch_mode_button.setText(f" {TStyle.theme.title()}{self.tr('theme')}")
        self.language_button.setText(self.tr("language_btn"))
        self.about_tasky.setToolTip(self.tr("about"))

        cur_mode = self.current_view_mode
        self.view_mode_combo.blockSignals(True)
        self.view_mode_combo.clear()
        self.view_mode_combo.addItems([self.tr("by_time"), self.tr("by_category"), self.tr("by_priority")])
        self.view_mode_combo.setCurrentIndex({"time": 0, "category": 1, "priority": 2}[cur_mode])
        self.view_mode_combo.blockSignals(False)

        cur_filter = self.current_category_filter
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(self.tr("all"))
        self.category_combo.addItems(CATEGORY_ITEMS)
        self.category_combo.setCurrentText(cur_filter if cur_filter != "All" else self.tr("all"))
        self.category_combo.blockSignals(False)

        self.refresh_tasks()

    def toggle_language(self):
        self.language = "en" if self.language == "zh" else "zh"
        self.apply_language()

    def show_about_tasky(self):
        state = TBackEnd.analyze_user_state()
        text = (
            f"<FONT>{TBackEnd.tasky_version(1, link=True)}"
            f"<br><br><b>Focus Score</b>: {state['focus_score']}/100"
            f"<br><b>Nudge</b>: {state['nudge']}</FONT>"
        )
        QtWidgets.QMessageBox.information(self, 'Tasky', text, QtWidgets.QMessageBox.Ok)

    def change_view_mode(self, text):
        self.current_view_mode = {
            self.tr("by_time"): "time",
            self.tr("by_category"): "category",
            self.tr("by_priority"): "priority",
        }.get(text, "time")
        self.refresh_tasks()

    def change_category_filter(self, text):
        self.current_category_filter = "All" if text == self.tr("all") else text
        self.refresh_tasks()

    def get_sorted_filtered_tasks(self):
        data = TBackEnd.return_deadlines_with_meta()
        if self.current_category_filter != "All":
            data = [d for d in data if d["category"] == self.current_category_filter]

        if self.current_view_mode == "category":
            data.sort(key=lambda d: (d["category"], d["ttime"]))
        elif self.current_view_mode == "priority":
            order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            data.sort(key=lambda d: (order.get(d["priority"], 2), d["ttime"]))
        else:
            data.sort(key=lambda d: d["ttime"])

        return data

    def refresh_tasks(self):
        self.gui_refresh_timer.stop()

        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.task_boxes.clear()

        self.tasks_list = TBackEnd.read_and_sort_tasks_file()
        self.tasks_parted_list = self.get_sorted_filtered_tasks()
        self.last_read = TBackEnd.read_tasks_file()
        self.last_meta_read = TBackEnd.read_meta_tasks_file()

        state = TBackEnd.analyze_user_state()
        self.analysis_label.setText(
            f"{self.tr('focus')} {state['focus_score']}/100 | {self.tr('high_risk')} {state['high_risk_count']} | {state['nudge']}"
        )

        for task in self.tasks_parted_list:
            task_box = TaskBox(task, self)
            task_box.delete_button.pressed.connect(lambda p=int(task["num"]), q=self.tasks_list: [self.direct_delete(p, q)])

            if task["desc"]:
                tooltip_text = f"<FONT color=black>{task['desc']}</FONT>"
                task_box.setToolTip(tooltip_text)

            self.tasks_layout.addWidget(task_box)
            self.task_boxes.append(task_box)

        self.clear_all = QtWidgets.QPushButton(self.tr("clear_all"))
        self.clear_all.setObjectName("ClearAllButton")
        self.clear_all.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_all.clicked.connect(self.clear_all_tasks)
        if not self.tasks_parted_list:
            self.clear_all.setEnabled(False)

        self.tasks_layout.addWidget(self.clear_all, alignment=Qt.AlignCenter)
        self.tasks_layout.addStretch()

        self.gui_refresh_timer.start()

    def refresh_gui(self):
        if TBackEnd.read_tasks_file() != self.last_read or TBackEnd.read_meta_tasks_file() != self.last_meta_read:
            self.refresh_tasks()
            return

        time_now = TBackEnd.return_datetime_now_parts()
        if self.last_datetime == time_now:
            return

        self.last_datetime = time_now
        self.refresh_tasks()

    def import_csv_tasks(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, self.tr("select_csv"), "", "CSV Files (*.csv)")
        if not csv_path:
            return

        imported = TBackEnd.import_tasks_from_csv(csv_path)
        QtWidgets.QMessageBox.information(self, self.tr("import_done"), self.tr("import_done_msg", count=imported))
        self.refresh_tasks()

    def open_task(self, num=False):
        if self.task_window is None:
            self.gui_refresh_timer.stop()
            self.setEnabled(False)
            self.task_window = TaskWindow(num, self)
            win_timer = QTimer(self.task_window)
            win_timer.setSingleShot(True)
            win_timer.timeout.connect(self.task_window.show)
            win_timer.setInterval(200)
            win_timer.start()

    def direct_delete(self, tasknum, tlist):
        if tasknum - 1 in range(len(tlist)):
            tname = tlist[tasknum - 1].split("\t", 2)[1]
            display_text = self.tr("delete_confirm_msg", num=tasknum, name=tname)
            decision = QtWidgets.QMessageBox.question(self, self.tr("delete_confirm"), display_text,
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if decision == QtWidgets.QMessageBox.Yes:
                TBackEnd.remove(tasknum, tlist)
        self.refresh_tasks()

    def clear_all_tasks(self):
        decision = QtWidgets.QMessageBox.warning(
            self, self.tr("clear_confirm"), self.tr("clear_confirm_msg"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if decision == QtWidgets.QMessageBox.Yes:
            TBackEnd.clear_tasks()
        self.refresh_tasks()

    def closeEvent(self, e):
        sys.exit()

    def switch_theme(self):
        self.switch_mode_button.setText(f" {TStyle.theme.title()}{self.tr('theme')}")
        TStyle.switch_mode()
        self.t_style = TStyle.stylesheet()
        self.setStyleSheet(self.t_style)

        if self.task_window is not None:
            self.task_window.setStyleSheet(TStyle.twindow_stylesheet())

        self.new_task_button.setIcon(QIcon(TStyle.new_task_icon))
        self.switch_mode_button.setIcon(QIcon(TStyle.switch_mode_icon))
        self.refresh_tasks()


class TaskBox(QtWidgets.QPushButton):
    def __init__(self, task_data, mainwindow: App):
        super(TaskBox, self).__init__()
        self.setStyleSheet(TStyle.stylesheet())

        task_lay = QtWidgets.QHBoxLayout(self)
        task_lay.setContentsMargins(0, 0, 0, 0)

        t = QtWidgets.QLabel(task_data["num"])
        t.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        t.setObjectName("TaskNum")

        self.td = QtWidgets.QLabel(task_data["deadline_text"].strip())
        self.td.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.td.setObjectName("TaskDead")

        label_text = f"[{task_data['priority']}] {task_data['name']} ({task_data['category']}) | Risk {task_data['risk']}"
        tn = QtWidgets.QLabel(label_text)
        tn.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        tn.setObjectName("TaskName")

        tnlay = QtWidgets.QVBoxLayout(tn)
        tnlay.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tnlay.setContentsMargins(0, 0, 4, 0)

        self.delete_button = QtWidgets.QPushButton(tn)
        self.delete_button.setObjectName("DeleteButton")
        self.delete_button.setToolTip(mainwindow.tr("delete_task"))
        del_icon = QIcon(TStyle.delete_button_icon)
        self.delete_button.setIcon(del_icon)
        iconsize = QSize()
        iconsize.setWidth(25)
        iconsize.setHeight(25)
        self.delete_button.setIconSize(iconsize)
        self.delete_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_button.setVisible(False)

        tnlay.addWidget(self.delete_button)

        task_lay.addWidget(t)
        task_lay.addStretch()
        task_lay.addWidget(self.td, 5)
        task_lay.addWidget(tn, 10)
        task_lay.addStretch()

        self.pressed.connect(lambda p=int(task_data["num"]): [mainwindow.open_task(p)])

        self.setObjectName("TaskItem")
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def enterEvent(self, e):
        self.delete_button.setVisible(True)

    def leaveEvent(self, e):
        self.delete_button.setVisible(False)


class TaskWindow(QWidget):
    def __init__(self, task_num=False, mainWindow: App = None):
        super(TaskWindow, self).__init__()
        self.window_style = TStyle.twindow_stylesheet()
        self.mainWindow = mainWindow

        self.task_number = task_num
        self.tlist = mainWindow.tasks_list.copy()

        if task_num in range(1, len(self.tlist) + 1):
            title = f"Edit Task {task_num}"
        else:
            title = "New Task"
            self.task_number = False

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(TStyle.tlogo_path))
        self.setStyleSheet(self.window_style)
        self.setMinimumSize(650, 660)
        self.setMaximumSize(740, 740)
        self.setObjectName("TaskWindow")

        self.win_layout = QtWidgets.QVBoxLayout(self)

        self.win_title = QtWidgets.QLabel(title, self)
        self.win_title.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.win_title.setObjectName("TaskWindowTitle")

        self.win_items = QWidget(self)
        self.win_items.setObjectName("TaskWindowItems")
        self.items_layout = QtWidgets.QVBoxLayout(self.win_items)

        self.task_name_frame = QWidget(self.win_items)
        self.tnf_layout = QtWidgets.QHBoxLayout(self.task_name_frame)
        self.tnf_label = QtWidgets.QLabel("Task Name", self.task_name_frame)
        self.tnf_entry = QtWidgets.QLineEdit(self.task_name_frame)
        self.tnf_entry.setObjectName("NameEntry")
        self.tnf_entry.setMaxLength(30)
        self.tnf_layout.addWidget(self.tnf_label)
        self.tnf_layout.addWidget(self.tnf_entry, 1)

        self.task_date_frame = QWidget(self.win_items)
        self.tdf_layout = QtWidgets.QHBoxLayout(self.task_date_frame)
        self.tdf_date_entry = QtWidgets.QLineEdit(self.task_date_frame)
        self.tdf_date_entry.setPlaceholderText("DD")
        self.tdf_date_entry.setMaxLength(2)
        self.tdf_month_entry = QtWidgets.QComboBox(self.task_date_frame)
        for month in TBackEnd.month_names.values():
            self.tdf_month_entry.addItem(month.title())
        self.tdf_year_entry = QtWidgets.QLineEdit(self.task_date_frame)
        self.tdf_year_entry.setPlaceholderText("YYYY")
        self.tdf_year_entry.setMaxLength(4)
        self.tdf_layout.addWidget(QtWidgets.QLabel("Date"))
        self.tdf_layout.addWidget(self.tdf_date_entry)
        self.tdf_layout.addWidget(QtWidgets.QLabel("Month"))
        self.tdf_layout.addWidget(self.tdf_month_entry)
        self.tdf_layout.addWidget(QtWidgets.QLabel("Year"))
        self.tdf_layout.addWidget(self.tdf_year_entry)

        self.task_time_frame = QWidget(self.win_items)
        self.ttif_layout = QtWidgets.QHBoxLayout(self.task_time_frame)
        self.ttf_hours_entry = QtWidgets.QLineEdit(self.task_time_frame)
        self.ttf_hours_entry.setPlaceholderText("HH")
        self.ttf_hours_entry.setMaxLength(2)
        self.ttf_mins_entry = QtWidgets.QLineEdit(self.task_time_frame)
        self.ttf_mins_entry.setPlaceholderText("MM")
        self.ttf_mins_entry.setMaxLength(2)
        self.ttif_layout.addWidget(QtWidgets.QLabel("Hours (24h)"))
        self.ttif_layout.addWidget(self.ttf_hours_entry)
        self.ttif_layout.addWidget(QtWidgets.QLabel("Mins"))
        self.ttif_layout.addWidget(self.ttf_mins_entry)

        self.task_meta_frame = QWidget(self.win_items)
        self.meta_layout = QtWidgets.QHBoxLayout(self.task_meta_frame)
        self.category_combo = QtWidgets.QComboBox(self.task_meta_frame)
        self.category_combo.addItems(CATEGORY_ITEMS)
        self.priority_combo = QtWidgets.QComboBox(self.task_meta_frame)
        self.priority_combo.addItems(PRIORITY_ITEMS)
        self.meta_layout.addWidget(QtWidgets.QLabel("Category"))
        self.meta_layout.addWidget(self.category_combo)
        self.meta_layout.addStretch()
        self.meta_layout.addWidget(QtWidgets.QLabel("Priority"))
        self.meta_layout.addWidget(self.priority_combo)

        self.task_desc_frame = QWidget(self.win_items)
        self.task_desc_layout = QtWidgets.QHBoxLayout(self.task_desc_frame)
        self.tdesc_entry = QtWidgets.QTextEdit(self.task_name_frame)
        self.tdesc_entry.setObjectName("DescriptionEntry")
        self.tdesc_entry.setPlaceholderText("Describe the task in max 168 characters")
        self.task_desc_layout.addWidget(QtWidgets.QLabel("Task Description"))
        self.task_desc_layout.addWidget(self.tdesc_entry, 1)

        self.items_layout.addWidget(self.task_name_frame)
        self.items_layout.addWidget(self.task_date_frame)
        self.items_layout.addWidget(self.task_time_frame)
        self.items_layout.addWidget(self.task_meta_frame)
        self.items_layout.addWidget(self.task_desc_frame)

        self.buttons_frame = QWidget(self)
        self.buttons_layout = QtWidgets.QHBoxLayout(self.buttons_frame)

        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setObjectName("DeleteButton")
        self.delete_button.setIcon(QIcon(TStyle.delete_button_icon))
        self.delete_button.setIconSize(QSize(30, 30))
        self.delete_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.delete_button.clicked.connect(self.delete_task)
        self.delete_button.setToolTip("Delete Task")
        if not self.task_number:
            self.delete_button.setEnabled(False)

        self.save_task_button = QtWidgets.QPushButton("Save")
        self.save_task_button.setObjectName("SaveButton")
        self.save_task_button.clicked.connect(self.save_task)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setObjectName("CancelButton")
        self.cancel_button.clicked.connect(self.close)

        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.save_task_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addStretch()

        self.win_layout.addWidget(self.win_title)
        self.win_layout.addWidget(self.win_items, 1)
        self.win_layout.addWidget(self.buttons_frame)

        self.fill_task_details()

    def fill_task_details(self):
        yy, mm, dd, HH, MM = TBackEnd.return_datetime_now_parts()
        self.tnf_entry.setPlaceholderText(f"Task {len(self.tlist) + 1}")

        if self.task_number:
            task = self.tlist[self.task_number - 1]
            ttime, name, desc = task.split("\t", 2)
            yy, mm, dd, HH, MM = ttime.split(":")
            self.tnf_entry.setText(name.strip())
            self.tdesc_entry.setText(desc)

            meta_map = TBackEnd.read_meta_map()
            meta = meta_map.get(TBackEnd.task_identity(task), {})
            self.category_combo.setCurrentText(meta.get("category", "General"))
            self.priority_combo.setCurrentText(meta.get("priority", "Medium"))

        self.tdf_year_entry.setText(str(int(yy) + 2000))
        self.tdf_month_entry.setCurrentText(TBackEnd.month_names[int(mm)].title())
        self.tdf_date_entry.setText(dd)
        self.ttf_hours_entry.setText(HH)
        self.ttf_mins_entry.setText(MM)

    def validate_entries(self):
        tdate = self.tdf_date_entry.text().strip().zfill(2)
        tmonth = self.tdf_month_entry.currentText()
        tmonth_num = str(TBackEnd.month_name_to_num[tmonth.lower()]).zfill(2)
        days_in_month = TBackEnd.months[tmonth_num]
        tyear = self.tdf_year_entry.text().strip()
        thour = self.ttf_hours_entry.text().strip().zfill(2)
        tmins = self.ttf_mins_entry.text().strip().zfill(2)
        tdesc = self.tdesc_entry.toPlainText().strip().replace('\n', ' ')

        if not tdate.isdecimal() or int(tdate) not in range(1, days_in_month + 1):
            return False
        if not tyear.isdecimal() or int(tyear) not in range(TBackEnd.current_year, 2100):
            return False
        if not thour.isdecimal() or int(thour) not in range(0, 24):
            return False
        if not tmins.isdecimal() or int(tmins) not in range(0, 60):
            return False
        if len(tdesc) > 168:
            return False
        return True

    def save_task(self):
        if not self.validate_entries():
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please check date/time/description inputs.")
            return

        tname = self.tnf_entry.text().strip() or (f"Task {self.task_number}" if self.task_number else f"Task {len(self.tlist) + 1}")
        task_date = self.tdf_date_entry.text().strip().zfill(2)
        task_month = str(TBackEnd.month_name_to_num[self.tdf_month_entry.currentText().lower()]).zfill(2)
        task_year = self.tdf_year_entry.text().strip()[-2:]
        task_hours = self.ttf_hours_entry.text().strip().zfill(2)
        task_mins = self.ttf_mins_entry.text().strip().zfill(2)
        task_desc = self.tdesc_entry.toPlainText().strip().replace('\n', ' ')

        task_string = f"{task_year}:{task_month}:{task_date}:{task_hours}:{task_mins}\t{tname}\t{task_desc}"

        if self.task_number:
            self.tlist[self.task_number - 1] = task_string
        else:
            self.tlist.append(task_string)

        TBackEnd.write_tasks(self.tlist)
        TBackEnd.sync_meta_with_tasks(self.tlist)
        TBackEnd.update_task_meta(
            task_string,
            category=self.category_combo.currentText(),
            priority=self.priority_combo.currentText(),
            source="manual",
            status="todo",
        )
        self.close()

    def delete_task(self):
        if not self.task_number:
            return

        task_index = self.task_number - 1
        if task_index in range(len(self.tlist)):
            tname = self.tlist[task_index].split("\t", 2)[1]
            decision = QtWidgets.QMessageBox.question(
                self,
                "Delete Confirmation",
                f"Are you sure you want to delete Task {self.task_number}?\n\nTask name: {tname}\n",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if decision == QtWidgets.QMessageBox.Yes:
                TBackEnd.remove(self.task_number, self.tlist)
                self.close()

    def closeEvent(self, e):
        self.mainWindow.task_window = None
        self.mainWindow.setEnabled(True)
        self.mainWindow.refresh_tasks()


if __name__ == '__main__':
    App()
