from csv import reader
import os
import json
import Consent.ADuo as ADuo
import random


def createBasicSet(data_root, diabetes, healthy, outpath):
    patientList = []
    dirsDiabetes = os.listdir(data_root + diabetes)
    patientList = createPatientList(data_root, patientList, diabetes, dirsDiabetes)
    dirsHealthy = os.listdir(data_root + healthy)
    patientList = createPatientList(data_root, patientList, healthy, dirsHealthy)

    with open(outpath, 'w') as outfile:
        json.dump({"patient": patientList}, outfile)


def randomConsent():
    keys = ADuo.duo_prim.keys()
    rc = random.choice(list(keys))
    print(ADuo.duo_prim[rc])

    sec_keys = ADuo.duo_sec
    sec_keys.remove('NPU')
    num_choices = random.randint(0,3)

    r_sec_keys = random.choices(list(sec_keys), k=num_choices)
    chance = random.random()
    if chance < 0.3:
        r_sec_keys.append('PU')
    else:
        r_sec_keys.append('NPU')

    ADuo.duo_sec.add('NPU')

    return list(ADuo.duo_prim[rc]), r_sec_keys


def randomAge(minAge=1, maxAge=100):
    return random.randint(minAge, maxAge)


def createPatientDict(id, hasDiabetes, annotations, glucose, insulin, food, consent):
    pd = {
        "id": id,
        "glucose": glucose,
        "food": food,
        "hasDiabetes": hasDiabetes,
        "consent": consent,
        "age": randomAge()
    }

    if hasDiabetes:
        pd['insulin'] = insulin
    else:
        pd['annotations'] = annotations

    return pd

def createConsent(id, name):
    consent = {}

    main, sec = randomConsent()

    consent['id'] = id+name
    consent['datatype'] = name
    consent['main'] = main
    consent['secondary'] = sec
    return consent

def createDataList(path, baseid, listid):
    gl = []
    with open(path) as file:
        csv_reader = reader(file)
        headLine = None
        counter = 0
        for rowIdx, row in enumerate(csv_reader):
            if rowIdx > 100:
                break

            if rowIdx == 0:
                headLine = row
            else:
                gluc = {}
                for colIdx, col in enumerate(row):
                    gluc[headLine[colIdx]] = col
                    gluc['id'] = baseid + listid + str(counter)

                gl.append(gluc)
                counter += 1

    return gl


def createPatientList(data_root, patientList, subPath, dirs):
    maxPatientNum = 8

    for patient_folder in dirs:

        annoPath = data_root + subPath + patient_folder + "/annotations.csv"
        insulinPath = data_root + subPath + patient_folder + "/insulin.csv"
        hasDiabetes = True if os.path.exists(insulinPath) else False


        if hasDiabetes:
            id = "D" + patient_folder
            insulin = createDataList(insulinPath, id, "insu")
            anno = None
        else:
            id = "H" + patient_folder
            insulin = None
            anno = createDataList(annoPath, id, "anno")

        gluc = createDataList(data_root + subPath + patient_folder + "/glucose.csv", id, "gluc")
        food = createDataList(data_root + subPath + patient_folder + "/food.csv", id, "food")
        consent = createConsent(id, "patient")

        patientList.append(createPatientDict(id, hasDiabetes, anno, gluc, insulin, food, consent))
        maxPatientNum += -1
        if maxPatientNum < 0:
            return patientList


def adam2duo(adam):
    duo_main = ADuo.adam_main_mapped_to_duo[adam["main"]]
    duo_sec = []
    for aEntry in adam["second"]:
        duo_sec.append(ADuo.adam_sec_mapped_to_duo[aEntry])

    return {"main":duo_main, "secondary":duo_sec}

