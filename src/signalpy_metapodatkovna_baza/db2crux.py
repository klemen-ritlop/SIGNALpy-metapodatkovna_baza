import argparse
import configparser
import datetime
import os
import sys

try:
    import psycopg2
    import psycopg2.extensions
    from psycopg2.extras import NamedTupleCursor
except ModuleNotFoundError:
    print("Module psycopg2 not installed. pip install psycopg2")
    exit(-1)

from signalpy_metapodatkovna_baza import queries, templates


def execute_query(db_connection: psycopg2.extensions.connection, q: str, v: tuple):
    cur = db_connection.cursor(
        cursor_factory=NamedTupleCursor
    )  # type: psycopg2.extensions.cursor
    cur.execute(q, v)
    results = cur.fetchall()
    cur.close()
    return results


def get_station_data(db_connection: psycopg2.extensions.connection, station_id: int):
    # get station info
    station_qr = execute_query(db_connection, queries.station_data, (station_id,))

    # get station coordinates
    coordinates_qr = execute_query(
        db_connection, queries.station_coordinates, (station_id,)
    )

    if not coordinates_qr:
        return None

    station = templates.Site.from_query(station_qr, coordinates_qr)

    # get station receiver history
    receivers_qr = execute_query(db_connection, queries.receiver_history, (station_id,))

    receivers = []
    for receiver_qr in receivers_qr:
        receivers.append(templates.Receiver.from_query(receiver_qr))

    # get station antenna history
    antennas_qr = execute_query(db_connection, queries.antenna_history, (station_id,))

    antennas = []
    for antenna_qr in antennas_qr:
        antennas.append(templates.Antenna.from_query(antenna_qr))

    # get agency
    agency_qr = execute_query(db_connection, queries.agency, (station_id,))
    agency = templates.Agency.from_query(agency_qr, [], [])

    return {
        "station": station,
        "receivers": receivers,
        "antennas": antennas,
        "agency": agency,
    }


def get_crux_file(save_dir=""):
    # --- CONNECT TO DATABASE ---
    database_config = configparser.ConfigParser()
    database_config.read("database.ini")
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

    # get list of all stations in database
    query = "SELECT station_id FROM station_information ORDER BY country_iso3_code,four_char_id"
    stations_qr = execute_query(db_connection, query, ())

    # crux_file_name = f'SI-CORS_{datetime.datetime.now().strftime("%Y-%m-%d")}.crux'
    crux_file_name = "SI-CORS.crux"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_path = os.path.join(save_dir, crux_file_name)

    if os.path.exists(file_path):
        overwrite = input("File already exists. Overwrite? Y = yes, N = no\n")
        if overwrite.lower() == "n":
            print(f"Crux file {crux_file_name} was not saved.")

    crux = open(os.path.join(file_path), "w", encoding="UTF-8")
    crux.write(f"# file created: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
    crux.write("update_insert:\n\n")

    for station_qr in stations_qr:
        station_id = station_qr.station_id
        data = get_station_data(db_connection, station_id)

        if not data:
            continue

        crux.write("#*B\n")
        crux.write(f"    O - {data['station'].four_char_id}:\n")
        crux.write(data["station"].print_to_crux())
        crux.write(data["agency"].print_to_crux())

        crux.write("\n")

        for r in data["receivers"]:
            crux.write(r.print_to_crux())

        crux.write("\n")

        for a in data["antennas"]:
            crux.write(a.print_to_crux())

        crux.write("\n")

        for a in data["antennas"]:
            crux.write(a.print_eccentricities_to_crux())

        crux.write("#*E\n")

    crux.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        "-o",
        "--out_dir",
        help="Saving directory. If not set, log file is saved in the script directory.",
        type=str,
        default=".",
    )

    input_arguments = arg_parser.parse_args()

    get_crux_file(save_dir=input_arguments.out_dir)
