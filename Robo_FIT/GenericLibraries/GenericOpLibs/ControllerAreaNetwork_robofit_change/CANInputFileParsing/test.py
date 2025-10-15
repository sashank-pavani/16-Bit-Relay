import cantools


def load_arxml(arxml_file_path):
    try:
        # Load the ARXML file
        db = cantools.database.load_file(arxml_file_path)
        return db
    except Exception as e:
        print(f"Error loading ARXML file: {e}")
        return None


# Example usage:
arxml_file_path = "C:/robofit/CRE/Libraries/ExternalFiles/DBFiles/E3_1_2_Premium_BMC_HV.arxml"
database = load_arxml(arxml_file_path)
if database:
    print("ARXML file loaded successfully!")
    # You can now access messages, signals, etc. from the loaded database object
    print(f"Number of messages: {len(database.messages)}")
else:
    print("Failed to load ARXML file.")
