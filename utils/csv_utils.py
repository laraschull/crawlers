import csv


def writeheader():
    with open('test.csv', 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["First Name", "Last Name", "Inmate ID", "DOB", "Age", "Sex", "Race", "Facility", "Date of Sentence"
                        , "Estimated Release Date", "Description of Offense", "Headshot URI"])


def write(inmate, record, facility):
    with open('test.csv', 'a', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([inmate.firstNames, inmate.lastName, inmate.id, inmate.DOB, inmate.age, inmate.sex, inmate.race,
                        facility.name, record.sentenceDate, record.estReleaseDate, record.offense, inmate.headshot])



