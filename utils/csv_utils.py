import csv


def writeheader():
    with open('test.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["First Name", "Last Name", "Inmate ID", "DOB", "Age", "Sex", "Race", "Facility", "Date.py of Sentence"
                        , "Estimated Release Date.py", "Description of Offense", "Headshot URI"])


def write(inmate, record, facility):
    with open('test.csv', 'a', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([inmate.name.first, inmate.name.last, inmate.id, inmate.DOB, inmate.age, inmate.sex, inmate.race,
                        facility.name, record.sentenceDate, record.estReleaseDate, record.offense, inmate.headshot])



