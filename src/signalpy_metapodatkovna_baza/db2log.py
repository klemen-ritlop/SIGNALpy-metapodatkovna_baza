import argparse
import configparser
import datetime
import os
import string
import sys
import urllib.request

try:
    import psycopg2
    import psycopg2.extensions
    from psycopg2.extras import NamedTupleCursor
except ModuleNotFoundError:
    print("Module psycopg2 not installed. pip install psycopg2")
    sys.exit(-1)

from signalpy_metapodatkovna_baza import queries, templates


def execute_query(db_connection: psycopg2.extensions.connection, q: str, v: tuple):
    cur = db_connection.cursor(
        cursor_factory=NamedTupleCursor
    )  # type: psycopg2.extensions.cursor
    cur.execute(q, v)
    results = cur.fetchall()
    cur.close()

    return results


def download_antenna_gra() -> None:
    directory = os.path.dirname(os.path.realpath(__file__))
    # TODO: kam se zapise gra file (mora se v data folder)
    #  https://stackoverflow.com/questions/4519127/setuptools-package-data-folder-location

    try:
        urllib.request.urlretrieve(
            url="https://files.igs.org/pub/station/general/antenna.gra",
            filename=os.path.join(directory, "antenna.gra"),
        )
    except Exception:
        pass


def get_antenna_graphic(antenna_igs_name: str, gra_file: str) -> str:
    graphic = ""
    header = ""

    antenna_not_found = False

    line = ""
    with open(gra_file, "r", encoding="utf-8") as f:
        while antenna_igs_name not in line:
            line = f.readline()
            if "Machine-readable quick reference section begins here." in line:
                antenna_not_found = True
                break
        else:
            header = line

            while line[0] in string.ascii_uppercase or line == "\n":
                line = f.readline()

            graphic += line

            line = f.readline()
            while line[0] not in string.ascii_uppercase:
                graphic += line
                line = f.readline()

    if not antenna_not_found:
        return (header + "\n" + graphic).rstrip() + "\n"

    return antenna_igs_name + "\n" + "Antenna not found in antennas.gra.\n\n"


def get_antenna_graphic_abbreviation_list(antennas_graphic: str) -> str:
    all_abbreviations = {
        "BAM": "BAM: bottom of antenna mount",
        "BCR": "BCR: bottom of chokering",
        "BDG": "BDG: bottom of dome ground plane",
        "BGP": "BGP: bottom of ground plane",
        "BPA": "BPA: bottom of preamplifier",
        "TCR": "TCR: top of chokering",
        "TDG": "TDG: top of dome ground plane",
        "TGP": "TGP: top of ground plane",
        "TOP": "TOP: top of pole",
        "TPA": "TPA: top of preamplifier",
        "MMI": "MMI: man-machine interface",
        "NOM": "NOM: north orientation mark (placed on antenna by manufacturer)",
        "RXC": "RXC: receiver connector (connect antenna to external receiver)",
        "UNK": "UNK: unknown",
        "BAT": "BAT: battery compartment door release",
        "BTD": "BTD: bottom of tear drop shape (wide end)",
        "CMP": "CMP: mounted compass",
        "DIS": "DIS: display/digital readout (DIS is a specific type of MMI)",
        "DRY": "DRY: cap or cover for drying agent",
        "PCS": "PCS: PC card slot",
        "TMT": "TMT: tape measure tab or notch for slant height pole",
        "CAC": "CAC: nonspecific cable connector (only allowed for legacy calibrations)",
        "CTC": "CTC: external controller connector",
        "DAC": "DAC: data cable connector (for data collectors besides external receivers)",
        "PWC": "PWC: power port; external power connector",
        "RTC": "RTC: RTK connector; UHF connector for RTK broadcasting antenna",
    }

    abbreviations = ""
    for abb, des in all_abbreviations.items():
        if abb in antennas_graphic:
            abbreviations += des + "\n"

    return abbreviations


def make_log_file(nine_char_id, save_dir="", prepared_by="", is_new=False):

    header = templates.Header(site_name=nine_char_id)

    form = templates.Form(
        prepared_by=prepared_by,
        date_prepared=datetime.datetime.now(),
        report_type="UPDATE" if not is_new else "NEW",
        previous_site_log="vnesi rocno" if not is_new else "",
        modified_added_sections="vnesi rocno" if not is_new else "",
    )

    # --- CONNECT TO DATABASE ---
    database_config = configparser.ConfigParser()
    database_config.read("database.ini")
    # TODO database.ini kot vhodni parameter skripte
    connection_settings = {
        "host": database_config.get("connection_settings", "host"),
        "port": database_config.get("connection_settings", "port"),
        "database": database_config.get("connection_settings", "database_name"),
        "user": database_config.get("connection_settings", "username"),
        "password": database_config.get("connection_settings", "password"),
    }
    try:
        db_connection = psycopg2.connect(
            **connection_settings
        )  # type: psycopg2.extensions.connection
    except psycopg2.OperationalError as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(-1)

    # --- EXECUTE ALL QUERIES ---
    # station info query
    var = (nine_char_id,)
    # var = ("GSR100SVN",)
    station_info_qr = execute_query(db_connection, queries.station_data, var)

    # station coordinates query
    try:
        var = (station_info_qr[0].station_id,)
    except IndexError:
        print(f"Station {nine_char_id} does not exist.")
        sys.exit(-1)

    coordinates_qr = execute_query(db_connection, queries.station_coordinates, var)

    # station receiver history query
    var = (station_info_qr[0].station_id,)
    receiver_log_qr = execute_query(db_connection, queries.receiver_history, var)

    # station antenna history query
    var = (station_info_qr[0].station_id,)
    antenna_log_qr = execute_query(db_connection, queries.antenna_history, var)

    # station surveyed local ties
    var = (station_info_qr[0].station_id,)
    local_ties_qr = execute_query(db_connection, queries.surveyed_local_ties, var)

    # frequency standard history query
    var = (station_info_qr[0].station_id,)
    frequency_standard_log_qr = execute_query(
        db_connection, queries.frequency_standard_history, var
    )

    # collocation information query
    var = (station_info_qr[0].station_id,)
    collocation_information_log_qr = execute_query(
        db_connection, queries.collocation_information, var
    )

    # humidity sensor query
    var = (station_info_qr[0].station_id,)
    humidity_sensor_log_qr = execute_query(db_connection, queries.humidity_sensor, var)

    # pressure sensor query
    var = (station_info_qr[0].station_id,)
    pressure_sensor_log_qr = execute_query(db_connection, queries.pressure_sensor, var)

    # temperature sensor query
    var = (station_info_qr[0].station_id,)
    temperature_sensor_log_qr = execute_query(
        db_connection, queries.temperature_sensor, var
    )

    # water vapor radiometer query
    var = (station_info_qr[0].station_id,)
    water_vapor_radiometer_log_qr = execute_query(
        db_connection, queries.water_vapor_radiometer, var
    )

    # other meteorological instrumentation query
    var = (station_info_qr[0].station_id,)
    other_meteorological_instrumentation_log_qr = execute_query(
        db_connection, queries.other_meteorological_instrumentation, var
    )

    # radio interference query
    var = (station_info_qr[0].station_id,)
    radio_interference_log_qr = execute_query(
        db_connection, queries.radio_interference, var
    )

    # multipath_source query
    var = (station_info_qr[0].station_id,)
    multipath_source_log_qr = execute_query(
        db_connection, queries.multipath_source, var
    )

    # signal_obstruction query
    var = (station_info_qr[0].station_id,)
    signal_obstruction_log_qr = execute_query(
        db_connection, queries.signal_obstruction, var
    )

    # local_episodic_effect query
    var = (station_info_qr[0].station_id,)
    local_episodic_effect_log_qr = execute_query(
        db_connection, queries.local_episodic_effect, var
    )

    # point_of_contact_agency query
    var = (station_info_qr[0].station_id,)
    point_of_contact_agency_log_qr = execute_query(
        db_connection, queries.point_of_contact_agency, var
    )

    try:
        primary_contact_id = point_of_contact_agency_log_qr[0].primary_contact_id
        var = (primary_contact_id,)
        point_of_contact_agency_primary_contact_qr = execute_query(
            db_connection, queries.contact, var
        )
    except IndexError:
        point_of_contact_agency_primary_contact_qr = None

    try:
        secondary_contact_id = point_of_contact_agency_log_qr[0].secondary_contact_id
        var = (secondary_contact_id,)
        point_of_contact_agency_secondary_contact_qr = execute_query(
            db_connection, queries.contact, var
        )
    except IndexError:
        point_of_contact_agency_secondary_contact_qr = None

    # responsible_agency query
    var = (station_info_qr[0].station_id,)
    responsible_agency_log_qr = execute_query(db_connection, queries.agency, var)

    try:
        primary_contact_id = responsible_agency_log_qr[0].primary_contact_id
        var = (primary_contact_id,)
        responsible_agency_primary_contact_qr = execute_query(
            db_connection, queries.contact, var
        )
    except IndexError:
        responsible_agency_primary_contact_qr = None

    try:
        secondary_contact_id = responsible_agency_log_qr[0].secondary_contact_id
        var = (secondary_contact_id,)
        responsible_agency_secondary_contact_qr = execute_query(
            db_connection, queries.contact, var
        )
    except IndexError:
        responsible_agency_secondary_contact_qr = None

    # more_information query
    var = (station_info_qr[0].station_id,)
    more_information_log_qr = execute_query(
        db_connection, queries.more_information, var
    )

    db_connection.close()

    # --- QUERIES TO TEMPLATES ---
    station_info = templates.Site.from_query(station_info_qr, coordinates_qr)

    receivers = []
    i = 1
    for rl in receiver_log_qr:
        receivers.append(templates.Receiver.from_query(rl, i))
        i += 1

    antennas = []
    i = 1
    for al in antenna_log_qr:
        antennas.append(templates.Antenna.from_query(al, i))
        i += 1

    local_ties = []
    i = 1
    for tie in local_ties_qr:
        local_ties.append(templates.LocalTie.from_query(tie, i))
        i += 1

    frequency_standards = []
    i = 1
    if not frequency_standard_log_qr:
        fs = templates.FrequencyStandard(
            i=1,
            standard_type="internal",
            input_frequency="",
            effective_dates=(receivers[0].date_installed, None),
            notes="",
        )
        frequency_standards.append(fs)
    else:
        for fsl in frequency_standard_log_qr:
            frequency_standards.append(templates.FrequencyStandard.from_query(fsl, i))
            i += 1

    collocations = []
    i = 1
    for cil in collocation_information_log_qr:
        collocations.append(templates.CollocationInformation.from_query(cil, i))
        i += 1

    humidity_sensors = []
    i = 1
    for hsl in humidity_sensor_log_qr:
        humidity_sensors.append(templates.HumiditySensor.from_query(hsl, i))
        i += 1

    pressure_sensors = []
    i = 1
    for psl in pressure_sensor_log_qr:
        pressure_sensors.append(templates.PressureSensor.from_query(psl, i))
        i += 1

    temperature_sensors = []
    i = 1
    for tsl in temperature_sensor_log_qr:
        temperature_sensors.append(templates.TemperatureSensor.from_query(tsl, i))
        i += 1

    water_vapor_radiometers = []
    i = 1
    for wvrl in water_vapor_radiometer_log_qr:
        water_vapor_radiometers.append(
            templates.WaterVaporRadiometer.from_query(wvrl, i)
        )
        i += 1

    other_meteorological_instrumentation = []
    i = 1
    for omil in other_meteorological_instrumentation_log_qr:
        other_meteorological_instrumentation.append(
            templates.OtherMeteorologicalInstrumentation.from_query(omil, i)
        )
        i += 1

    radio_interferences = []
    i = 1
    for ril in radio_interference_log_qr:
        radio_interferences.append(templates.RadioInterference.from_query(ril, i))
        i += 1

    multipath_sources = []
    i = 1
    for msl in multipath_source_log_qr:
        multipath_sources.append(templates.MultipathSource.from_query(msl, i))
        i += 1

    signal_obstructions = []
    i = 1
    for sol in signal_obstruction_log_qr:
        signal_obstructions.append(templates.SignalObstruction.from_query(sol, i))
        i += 1

    local_episodic_effects = []
    i = 1
    for leel in local_episodic_effect_log_qr:
        lee = templates.LocalEpisodicEffect(
            i=i,
            dates=(leel.date_start, leel.date_end),
            event=leel.event,
        )
        local_episodic_effects.append(lee)
        i += 1

    point_of_contact_agency = templates.Agency.from_query(
        point_of_contact_agency_log_qr,
        point_of_contact_agency_primary_contact_qr,
        point_of_contact_agency_secondary_contact_qr,
    )

    responsible_agency = templates.Agency.from_query(
        responsible_agency_log_qr,
        responsible_agency_primary_contact_qr,
        responsible_agency_secondary_contact_qr,
    )

    more_information = templates.MoreInformation.from_query(more_information_log_qr)

    antennas_graphic = ""
    for antenna in antennas:
        antennas_graphic += (
            get_antenna_graphic(antenna.antenna_type.rstrip(), "antenna.gra") + "\n\n"
        )

    abbreviations = get_antenna_graphic_abbreviation_list(antennas_graphic)

    # --- WRITE LOG FILE ---
    log_file_name = f"{nine_char_id}_{form.date_prepared.year}{form.date_prepared.month:02d}{form.date_prepared.day:02d}.log"

    while not os.path.exists(save_dir):
        save_dir = input(
            "Save directory does not exist. Enter existing directory or press X to exit.\n"
        )
        if save_dir.lower() == "x":
            print(f"Log file {log_file_name} was not saved.")
            sys.exit(-1)

    file_path = os.path.join(save_dir, log_file_name)

    if os.path.exists(file_path):
        overwrite = input("File already exists. Overwrite? Y = yes, N = no\n")
        if overwrite.lower() == "n":
            print(f"Log file {log_file_name} was not saved.")

    with open(file_path, "w", encoding="UTF-8") as o:
        # write header
        o.writelines(header.to_txt())

        # write 0. Form
        o.writelines(form.to_txt())

        # write 1.   Site Identification of the GNSS Monument and 2.   Site Location Information
        o.writelines(station_info.print_to_log())

        # write 3.   GNSS Receiver Information
        o.writelines(templates.get_title(3))
        for r in receivers:
            o.writelines(r.print_to_log())
        o.writelines(templates.Receiver.print_blank_to_log())

        # write 4.   GNSS Antenna Information
        o.writelines(templates.get_title(4))
        for a in antennas:
            o.writelines(a.print_to_log())
        o.writelines(templates.Antenna.print_blank_to_log())

        # write 5.   Surveyed Local Ties
        o.writelines(templates.get_title(5))
        for lt in local_ties:
            o.writelines(lt.print_to_log())
        o.writelines(templates.LocalTie.print_blank_to_log())

        # write 6.   Frequency Standard
        o.writelines(templates.get_title(6))
        for fs in frequency_standards:
            o.writelines(fs.print_to_log())
        o.writelines(templates.FrequencyStandard.print_blank_to_log())

        # write 7.   Collocation Information
        o.writelines(templates.get_title(7))
        for c in collocations:
            o.writelines(c.print_to_log())
        o.writelines(templates.CollocationInformation.print_blank_to_log())

        # write 8.   Meteorological Instrumentation
        # write 8.1 Humidity Sensor Model
        o.writelines(templates.get_title(8))
        for hs in humidity_sensors:
            o.writelines(hs.print_to_log())
        o.writelines(templates.HumiditySensor.print_blank_to_log())

        # write 8.2 Pressure Sensor Model
        for ps in pressure_sensors:
            o.writelines(ps.print_to_log())
        o.writelines(templates.PressureSensor.print_blank_to_log())

        # write 8.3 Temp. Sensor Model
        for ts in temperature_sensors:
            o.writelines(ts.print_to_log())
        o.writelines(templates.TemperatureSensor.print_blank_to_log())

        # write 8.4 Water Vapor Radiometer
        for wvr in water_vapor_radiometers:
            o.writelines(wvr.print_to_log())
        o.writelines(templates.WaterVaporRadiometer.print_blank_to_log())

        # write 8.5 Other Instrumentation
        o.writelines(templates.OtherMeteorologicalInstrumentation.print_blank_to_log())

        # write 9.  Local Ongoing Conditions Possibly Affecting Computed Position
        # write 9.1 Radio Interferences
        o.writelines(templates.get_title(9))
        for ri in radio_interferences:
            o.writelines(ri.to_txt())
        o.writelines(templates.RadioInterference.blank_entry())

        # write 9.2 Multipath Sources
        for ms in multipath_sources:
            o.writelines(ms.print_to_log())
        o.writelines(templates.MultipathSource.print_blank_to_log())

        # write 9.3 Signal Obstructions
        for so in signal_obstructions:
            o.writelines(so.to_txt())
        o.writelines(templates.SignalObstruction.blank_entry())

        # write 10.  Local Episodic Effects Possibly Affecting Data Quality
        o.writelines(templates.get_title(10))
        for lee in local_episodic_effects:
            o.writelines(lee.print_to_log())
        o.writelines(templates.LocalEpisodicEffect.print_blank_to_log())

        # write 11.   On-Site, Point of Contact Agency Information
        o.writelines(templates.get_title(11))
        o.writelines(point_of_contact_agency.print_to_log())

        # write 12.  Responsible Agency
        o.writelines(templates.get_title(12))
        o.writelines(responsible_agency.print_to_log())

        # write 13.  More Information
        o.writelines(templates.get_title(13))
        o.writelines(more_information.print_to_log())
        o.write(antennas_graphic)
        o.write(abbreviations)

    print(f"Log file {log_file_name} successfully saved.")


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "station_name", help="Long station name (e.g. GSR100SVN).", type=str
    )

    arg_parser.add_argument(
        "-a",
        "--author",
        help="Value for " "Prepared by" " field in log file.",
        type=str,
        default="",
    )

    arg_parser.add_argument(
        "-o",
        "--out_dir",
        help="Saving directory. If not set, log file is saved in the script directory.",
        type=str,
        default=".",
    )

    arg_parser.add_argument(
        "-n",
        "--new",
        help="If this flag is set, "
        "Report Type"
        " field in log file is set to NEW (default: UPDATE).",
        action="store_true",
    )

    input_arguments = arg_parser.parse_args()

    # posodobi antenna.gra file
    download_antenna_gra()

    # naredi log-datoteko
    make_log_file(
        input_arguments.station_name,
        save_dir=input_arguments.out_dir,
        prepared_by=input_arguments.author,
        is_new=input_arguments.new,
    )
