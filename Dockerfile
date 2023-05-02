FROM python:3.9.16

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/lab_student_manager/
CMD [ "python", "main.py" ]