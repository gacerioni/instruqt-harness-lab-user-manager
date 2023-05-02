class Student:
    def __init__(self, email, harness_project, password="default", is_taken=0, slot_time_taken="0"):
        self.email = email
        self.password = password
        self.harness_project = harness_project
        self.is_taken = is_taken

    def __str__(self):
        obj_dict = {"email": self.email, "password": self.password, "harness_project": self.harness_project}
        return str(obj_dict)
