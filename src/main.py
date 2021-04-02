import utils
from sparky import Sparky

data_root = "C:/src/Datasets/D1NAMO/"
diabetes = "diabetes_subset/"
healthy = "healthy_subset/"
outpath = './output/patientList.json'
base_url = 'http://192.168.0.101:7200/repositories/patient'

# utils.createBasicSet(data_root, diabetes, healthy, outpath)


consent_required_info = {
    "wd:Q181600",
    # "wd:Q37525"
}

adam_main = "HMB"
adam_additional = []

adam_consent = {"main": adam_main, "second": adam_additional}


def define_filter(selected_pred):
    print(f"Filter for: {selected_pred['name']}")
    print(f"Type operator, [=,<,>]")
    opp = input()
    print(f"Type Value you want to compare too")
    val = input()

    return opp, val


def explore_dadtaset(duo_consent, consent_required_info):
    inp = 0


    sparky = Sparky(duo_consent, consent_required_info, base_url)

    print("To exit type: -2 and then press enter")
    print("To to get one step back type: -1 and then press enter")
    print("X is an attribute and can not be explored further")
    print("To investigate the dataset further, type the corresponding number and press enter")
    print("")

    while inp != -2:

        results = sparky.display_results()

        inp = int(input())

        if inp == -1:
            sparky.previous()
        if inp == -2:
            return sparky.return_results()
        else:
            selected_results = results[inp]

            if selected_results['type'] == 'object':
                sparky.advance(selected_results)
            else:
                print("ATTRIBUTE!")
                condition, value = define_filter(selected_results)

                sparky.add_filter(selected_results, condition, value)


duo_consent = utils.adam2duo(adam_consent)
selected_patient_ids = explore_dadtaset(duo_consent, consent_required_info)
print(f"Returned Patient IDs:\n{selected_patient_ids}")