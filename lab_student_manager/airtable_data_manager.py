import time
import logging
from airtable import airtable
from custom_exceptions import NoAvailableStudentSlots


def get_air_table_conn_obj(at_token, at_base_id):
    logging.debug("GETTING THE AIRTABLE CONN OBJ...")
    at = airtable.Airtable(base_id=at_base_id, api_key=at_token)
    logging.debug("THE AIRTABLE CONN OBJ IS READY!")
    return at


def get_free_student_slots(at_token, at_base_id, at_table_db):
    logging.debug("ENTERING IN THE get_free_student_slots method")
    result = {"records": []}
    at = get_air_table_conn_obj(at_token, at_base_id)
    for r in at.iterate(table_name=at_table_db, filter_by_formula="is_taken=0"):
        result["records"].append(r)
    return result


def mark_student_as_taken(student_id, at_table_db, at_token, at_base_id):
    at = get_air_table_conn_obj(at_token, at_base_id)
    # getting the epoch to use it in the slot_time_taken field
    epoch_time = int(time.time())
    # prepare the new fields dict
    new_fields = {"is_taken": 1, "slot_time_taken": epoch_time}

    at.update(at_table_db, student_id, new_fields)


def mark_student_as_free(student_id, at_table_db, at_token, at_base_id):
    # at.get(table_name, table_name, record_id=None, limit=0, offset=None,
    #        filter_by_formula=None, view=None, max_records=0, fields=[])
    at = get_air_table_conn_obj(at_token, at_base_id)
    results = at.get(table_name=at_table_db, filter_by_formula='FIND("{std_id}", email)'.format(std_id=student_id), limit=1)
    target_student_id = results['records'][0]['id']

    # getting the epoch to use it in the slot_time_taken field
    epoch_time = int(time.time())
    # prepare the new fields dict
    new_fields = {"is_taken": 0, "slot_time_taken": epoch_time}

    at.update(at_table_db, target_student_id, new_fields)


def get_and_reserve_one_slot(at_token, at_base_id, at_table_db):
    all_free_slots_list = []
    logging.debug("### GETTING THE SLOT")
    try:
        # Filter the students that are free
        all_free_slots_list = get_free_student_slots(at_token, at_base_id, at_table_db)['records']
        all_free_slots_list = sorted(all_free_slots_list, key=lambda d: d['fields']['email'])

        if not bool(all_free_slots_list):
            raise NoAvailableStudentSlots
        else:
            print("Found available student slots!")
            for slot in all_free_slots_list:
                print("Student {} is available!".format(slot['fields']['email']))
    except NoAvailableStudentSlots:
        print("Exception occurred: No student slots are available!")
        raise

    # We have some available slots. Let me take one for you.
    final_student_slot = all_free_slots_list[0]
    # and then we mark is as taken
    mark_student_as_taken(student_id=final_student_slot['id'], at_table_db=at_table_db, at_token=at_token,
                          at_base_id=at_base_id)

    return final_student_slot


def main():
    print("Nothing to see here...")
    #mark_student_as_free(student_id="c100", at_table_db="available-student-slots", at_token="patOcIsd8jwYA1FVG.16d4c7182ca439820399d332ddd363ca5fdc9906467906dd985ec01c2810ccae", at_base_id="appTyAirnMcRNH4kR")


if __name__ == '__main__':
    main()
