"""
This module contains the basic functions 
for testing queries to the main database.
"""
import json
import os
import unittest
from dotenv import load_dotenv
import database.main_db.admin_crud as admin_crud
import database.main_db.common_crud as common_crud
import database.main_db.teacher_crud as teacher_crud
import database.main_db.student_crud as student_crud
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.students_group import StudentsGroup


class TestMainDb(unittest.TestCase):
    """
    This class is designed to test the basic functions of adding, 
    deleting, and changing data in the main database table.
    """
    def test_chat(self):
        """
        Check adding and deleting chat from the main database table.
        """
        chat = -1234567890

        chats_1 = common_crud.get_chats()
        self.assertFalse(chat in chats_1)

        # add_chat
        admin_crud.add_chat(chat)
        chats_2 = common_crud.get_chats()
        self.assertTrue(chat in chats_2)

        # delete_chat
        admin_crud.delete_chat(chat)
        chats_3 = common_crud.get_chats()
        self.assertEqual(chats_3, chats_1)
        self.assertNotEqual(chats_3, chats_2)

    def test_teacher(self):
        """
        Check adding and deleting a teacher in the main database table.
        """
        teacher_full_name = "Учительский Преподаватель Магистрович"
        teacher_telegram_id = 111222333444

        teachers_1 = [teacher.full_name for teacher 
                      in admin_crud.get_teachers()]
        self.assertTrue(teacher_full_name not in teachers_1)

        # add_teacher
        admin_crud.add_teacher(teacher_full_name, teacher_telegram_id)
        teachers_list = admin_crud.get_teachers()
        teachers_2 = [it.full_name for it in teachers_list]
        self.assertTrue(teacher_full_name in teachers_2)
        self.assertNotEqual(teachers_1, teachers_2)
        teacher_tg_id_list_1 = [it.telegram_id for it in teachers_list]
        self.assertTrue(teacher_telegram_id in teacher_tg_id_list_1)
        self.assertTrue(admin_crud.is_teacher(teacher_telegram_id))

        # delete_teacher
        admin_crud.delete_teacher_on_tg_id(teacher_telegram_id)
        teachers_list = admin_crud.get_teachers()
        teachers_3 = [it.full_name for it in teachers_list]
        teacher_tg_id_list_2 = [it.telegram_id for it in teachers_list]
        self.assertEqual(teachers_3, teachers_1)
        self.assertNotEqual(teacher_tg_id_list_2, teacher_tg_id_list_1)
        self.assertTrue(teacher_telegram_id not in teacher_tg_id_list_2)

    def test_admin_modes(self):
        """
        Check the administrator verification functionality with different mods.
        """
        load_dotenv()
        real_admin = int(os.getenv('DEFAULT_ADMIN'))  # Telegram ID
        fake_admin = 987876765  # fake Telegram ID

        # is_admin
        self.assertTrue(admin_crud.is_admin(real_admin))
        self.assertFalse(admin_crud.is_admin(fake_admin))

        # is_admin_and_teacher
        self.assertTrue(admin_crud.is_admin_and_teacher(real_admin))

        # is_admin_with_teacher_mode
        admin_crud.switch_admin_mode_to_teacher(real_admin)
        self.assertTrue(admin_crud.is_admin_with_teacher_mode)

        # is_admin_no_teacher_mode
        teacher_crud.switch_teacher_mode_to_admin(real_admin)
        self.assertTrue(admin_crud.is_admin_no_teacher_mode)

    def test_student(self):
        """
        Check the presence, addition, deletion of a student 
        from the main database table.
        """
        user_student = common_crud.UserEnum.STUDENT
        user_unknown = common_crud.UserEnum.UNKNOWN
        student_tg_id = 1333666991  # fake Telegram ID
        student_full_name = "Студентов Наукогрыз Салагович"

        # user_verification
        self.assertEqual(
            common_crud.user_verification(student_tg_id), user_unknown
        )
        self.assertFalse(
            student_crud.has_student(student_full_name)
        )
        # add_student
        fake_group_id = 1
        admin_crud.add_student(student_full_name, fake_group_id)
        student_crud.set_telegram_id(student_full_name, student_tg_id)
        self.assertEqual(
            common_crud.user_verification(student_tg_id), user_student
        )
        self.assertTrue(student_crud.is_student(student_tg_id))

        # ban_student
        self.assertFalse(common_crud.is_ban(student_tg_id))
        common_crud.ban_student(student_tg_id)
        self.assertTrue(common_crud.is_ban(student_tg_id))

        # unban_student
        common_crud.unban_student(student_tg_id)
        self.assertFalse(common_crud.is_ban(student_tg_id))

        # delete_student
        student_id = student_crud.get_student_by_tg_id(student_tg_id).id
        admin_crud.delete_student(student_id)
        self.assertEqual(
            common_crud.user_verification(student_tg_id), user_unknown
        )
        self.assertFalse(student_crud.is_student(student_tg_id))

    def test_disciplines_and_groups(self):
        """
        Checking the presence, addition, deletion of 
        a discipline and student groups
        from the main database table.
        """
        # create_disciplines_config
        with open("unittests/db_tests/fake_disciplines_config.json", encoding="utf-8") as json_file:
            data = json.load(json_file)
            discipline = DisciplineWorksConfig(**data)

        # add_disciplines
        list_disciplines_1 = [
            it.full_name for it in admin_crud.get_all_disciplines()
            ]
        self.assertFalse(discipline.full_name in list_disciplines_1)
        admin_crud.add_discipline(discipline)
        list_disciplines_2 = [
            it.full_name for it in admin_crud.get_all_disciplines()
            ]
        self.assertTrue(discipline.full_name in list_disciplines_2)

        # create_group_config
        with open("unittests/db_tests/fake_groups_config.json", encoding="utf-8") as json_file:
            data = json.load(json_file)
            groups_list = [StudentsGroup(**it) for it in data]
            group_name_1 = data[0]["group_name"]

        # add_groups
        admin_crud.add_students_group(groups_list)
        groups_from_db = admin_crud.get_all_groups()
        self.assertTrue(group_name_1 in [it.group_name for it in groups_from_db])

        # some_actions_with_groups
        discipline_id = [it for it in admin_crud.get_all_disciplines()
                         if discipline.full_name == it.full_name]

        teacher_name = "Выдуманный Препод Старпёрович"
        teacher_tg_id = 4455667788

        admin_crud.add_teacher(
            teacher_name,
            teacher_tg_id
        )
        fake_teacher = [it for it in admin_crud.get_teachers()
                      if it.telegram_id == teacher_tg_id]
        admin_crud.assign_teacher_to_discipline(fake_teacher[0].id, discipline_id[0].id)
        groups = admin_crud.get_all_groups()
        group_id = [it for it in groups if it.group_name == group_name_1]
        admin_crud.assign_teacher_to_group(fake_teacher[0].id, group_id[0].id)

        # delete_disciplines
        admin_crud.delete_group(group_id[0].id)
        admin_crud.delete_discipline(discipline_id[0].id)
        admin_crud.delete_teacher(fake_teacher[0].id)


if __name__ == "__main__":
    unittest.main()
