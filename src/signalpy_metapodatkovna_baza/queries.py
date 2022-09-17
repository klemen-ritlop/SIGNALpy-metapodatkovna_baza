station_data = (
    "SELECT si.*, c.country_name "
    "FROM station_information AS si, country AS c "
    "WHERE si.country_iso3_code = c.country_iso3_code AND si.nine_char_id = %s"
)

station_coordinates = (
    "SELECT * " "FROM coordinates " "WHERE station_id = %s AND valid_to is null"
)

receiver_history = (
    "SELECT rl.*,  r.receiver_igs_name, r.serial_number "
    "FROM receiver_log AS rl, receiver AS r "
    "WHERE rl.receiver_id = r.receiver_id AND rl.station_id = %s "
    "ORDER BY date_installed ASC"
)

antenna_history = (
    "SELECT al.*, a.antenna_igs_name, a.serial_number, a.radome_igs_code, a.radome_serial_number, at.arp_code "
    "FROM antenna_log AS al, antenna AS a, antenna_type AS at "
    "WHERE al.antenna_id = a.antenna_id AND a.antenna_igs_name = at.antenna_igs_name AND station_id = %s "
    "ORDER BY date_installed ASC"
)

surveyed_local_ties = (
    "SELECT slt.*, slt2si.station_id "
    "FROM surveyed_local_ties AS slt, surveyed_local_ties_to_station_information AS slt2si "
    "WHERE slt.local_tie_id = slt2si.local_tie_id AND station_id = %s "
    "ORDER BY local_tie_id asc"
)

frequency_standard_history = (
    "SELECT * FROM frequency_standard_log "
    "WHERE station_id= %s "
    "ORDER BY effective_date_start ASC"
)

collocation_information = (
    "SELECT ci.*, cisi.station_id "
    "FROM collocation_information AS ci, collocation_information_to_station_information AS cisi "
    "WHERE ci.collocation_id = cisi.collocation_id AND station_id = %s"
)

humidity_sensor = (
    "SELECT hsl.*, hs.serial_number, hst.* "
    "FROM humidity_sensor_log AS hsl, humidity_sensor AS hs, humidity_sensor_type AS hst "
    "WHERE hsl.humidity_sensor_id = hs.humidity_sensor_id AND hs.model = hst.humidity_sensor_model AND "
    "hs.manufacturer = hst.manufacturer AND station_id = %s "
    "ORDER BY effective_date_start ASC"
)

pressure_sensor = (
    "SELECT psl.*, ps.serial_number, pst.* "
    "FROM pressure_sensor_log AS psl, pressure_sensor AS ps, pressure_sensor_type AS pst "
    "WHERE psl.pressure_sensor_id = ps.pressure_sensor_id AND ps.model = pst.pressure_sensor_model AND "
    "ps.manufacturer = pst.manufacturer AND station_id = %s "
    "ORDER BY effective_date_start ASC"
)

temperature_sensor = (
    "SELECT tsl.*, ts.serial_number, tst.* "
    "FROM temperature_sensor_log AS tsl, temperature_sensor AS ts, temperature_sensor_type AS tst "
    "WHERE tsl.temperature_sensor_id = ts.temperature_sensor_id AND "
    "ts.model = tst.temperature_sensor_model AND ts.manufacturer = tst.manufacturer AND station_id = %s "
    "ORDER BY effective_date_start ASC"
)

water_vapor_radiometer = (
    "SELECT wvrl.*, wvr.serial_number, wvrt.* "
    "FROM water_vapor_radiometer_log AS wvrl, water_vapor_radiometer AS wvr, water_vapor_radiometer_type AS wvrt "
    "WHERE wvrl.water_vapor_radiometer_id = wvr.water_vapor_radiometer_id AND "
    "wvr.model = wvrt.water_vapor_radiometer_model AND wvr.manufacturer = wvrt.manufacturer AND station_id = %s "
    "ORDER BY effective_date_start ASC"
)

other_meteorological_instrumentation = (
    "SELECT omil.* "
    "FROM other_meteorological_instrumentation_log AS omil "
    "WHERE station_id = %s "
    "ORDER BY instrument_id ASC"
)

radio_interference = (
    "SELECT * "
    "FROM radio_interference_log "
    "WHERE station_id = %s "
    "ORDER BY effective_date_start ASC"
)

multipath_source = (
    "SELECT * "
    "FROM multipath_source_log "
    "WHERE station_id = %s "
    "ORDER BY effective_date_start ASC"
)

signal_obstruction = (
    "SELECT * "
    "FROM signal_obstruction_log "
    "WHERE station_id = %s "
    "ORDER BY effective_date_start ASC"
)

local_episodic_effect = (
    "SELECT * "
    "FROM local_episodic_effect_log "
    "WHERE station_id = %s "
    "ORDER BY date_start ASC, event ASC"
)

point_of_contact_agency = (
    "SELECT * "
    "FROM point_of_contact_agency_log AS poc, agency AS a "
    "WHERE poc.station_id = %s AND poc.point_of_contact_agency_id=a.agency_id"
)

contact = "SELECT * " "FROM contact " "WHERE contact_id = %s"

agency = (
    "SELECT * "
    "FROM point_of_contact_agency_log AS poc, agency AS a "
    "WHERE poc.station_id = %s AND poc.point_of_contact_agency_id=a.agency_id"
)

more_information = "SELECT * " "FROM more_information_log " "WHERE station_id = %s"
