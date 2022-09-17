import datetime
from dataclasses import dataclass
from typing import Tuple, Union

from utils import transformations


def xstr(s: Union[str, float]) -> str:
    return "" if s is None else str(s)


def long_date(date: datetime.datetime, return_placeholder=True) -> str:
    if return_placeholder:
        return "CCYY-MM-DDThh:mmZ" if date is None else date.strftime("%Y-%m-%dT%H:%MZ")
    else:
        return "" if date is None else date.strftime("%Y-%m-%dT%H:%MZ")


def short_date(date: datetime.datetime, return_placeholder=True) -> str:
    if return_placeholder:
        return "CCYY-MM-DD" if date is None else date.strftime("%Y-%m-%d")
    else:
        return "" if date is None else date.strftime("%Y-%m-%d")


def crux_date(date: datetime.datetime, minus_one_sec=False) -> str:
    date = date - datetime.timedelta(seconds=1) if minus_one_sec and date else date
    return date.strftime("%Y%m%d:%H%M%S") if date else "00000000:000000"


def add_unit(s: float, u: str) -> str:
    return "" if s is None else str(s) + " " + u


def format_multiple_lines2(s: str) -> str:
    return "" if s is None else s.replace("\n", "\n" + 30 * " " + ": ")


def format_multiple_lines(s: str) -> str:
    if s is None:
        return ""
    else:
        nl = "\n                              : "
        substrings = s.split("\n")

        new_string = ""
        for substring in substrings:
            words = substring.split(" ")
            new_substring = ""
            new_line = ""
            for word in words:
                if len(new_line + word) < 49:
                    new_line += word + " "
                else:
                    new_substring += new_line[:-1] + nl
                    new_line = word + " "
            new_substring += new_line[:-1] + nl
            new_string += new_substring

        return new_string.rstrip(nl)


def merge_fw_versions(rec_fw_ver: str, me_fw_ver: str) -> str:
    return rec_fw_ver if me_fw_ver is None else rec_fw_ver + " / " + me_fw_ver


def format_satellite_systems(sat_sys: dict) -> str:
    sat_sys_str = ""
    for k, v in sat_sys.items():
        sat_sys_str += str(k) + "+" if v is True else ""

    return sat_sys_str[:-1]


def get_title(n):
    titles = {
        0: "0.   Form",
        1: "1.   Site Identification of the GNSS Monument",
        2: "2.   Site Location Information",
        3: "3.   GNSS Receiver Information",
        4: "4.   GNSS Antenna Information",
        5: "5.   Surveyed Local Ties",
        6: "6.   Frequency Standard",
        7: "7.   Collocation Information",
        8: "8.   Meteorological Instrumentation",
        9: "9.  Local Ongoing Conditions Possibly Affecting Computed Position",
        10: "10.  Local Episodic Effects Possibly Affecting Data Quality",
        11: "11.  On-Site, Point of Contact Agency Information",
        12: "12.  Responsible Agency (if different from 11.)",
        13: "13.  More Information",
    }

    return titles[n] + "\n\n"


@dataclass
class Header:
    site_name: str

    def to_txt(self):
        return (
            f"     {self.site_name} Site Information Form (site log)\n"
            f"     International GNSS Service\n"
            f"     See Instructions at:\n"
            f"       ftp://igs.org/pub/station/general/sitelog_instr.txt\n\n"
        )


@dataclass
class Form:
    prepared_by: str
    date_prepared: datetime.datetime
    report_type: str
    previous_site_log: str
    modified_added_sections: str

    def to_txt(self):
        return (
            f"{get_title(0)}"
            f"     Prepared by (full name)  : {self.prepared_by}\n"
            f"     Date Prepared            : {short_date(self.date_prepared)}\n"
            f"     Report Type              : {self.report_type}\n"
            f"     If Update:\n"
            f"      Previous Site Log       : {self.previous_site_log}\n"
            f"      Modified/Added Sections : {self.modified_added_sections}\n"
            f"\n\n"
        )


class Site(object):
    def __init__(
        self,
        site_name: str,
        four_char_id: str,
        monument_inscription: str,
        domes_number: str,
        cdp_number: str,
        monument_description: str,
        monument_height: float,
        monument_foundation: str,
        foundation_depth: float,
        marker_description: str,
        date_installed: datetime.datetime,
        geologic_characteristic: str,
        bedrock_type: str,
        bedrock_condition: str,
        fracture_spacing: str,
        fault_zones_nearby: str,
        distance_activity: str,
        additional_information_1: str,
        city: str,
        state: str,
        country: str,
        tectonic_plate: str,
        position_xyz: dict,
        position_llh: dict,
        additional_information_2: str,
    ):
        self.site_name = site_name
        self.four_char_id = four_char_id
        self.monument_inscription = monument_inscription
        self.domes_number = domes_number
        self.cdp_number = cdp_number
        self.monument_description = monument_description
        self.monument_height = monument_height
        self.monument_foundation = monument_foundation
        self.foundation_depth = foundation_depth
        self.marker_description = marker_description
        self.date_installed = date_installed
        self.geologic_characteristic = geologic_characteristic
        self.bedrock_type = bedrock_type
        self.bedrock_condition = bedrock_condition
        self.fracture_spacing = fracture_spacing
        self.fault_zones_nearby = fault_zones_nearby
        self.distance_activity = distance_activity
        self.additional_information_1 = additional_information_1

        self.city = city
        self.state = state
        self.country = country
        self.tectonic_plate = tectonic_plate
        self.position_XYZ = position_xyz
        self.position_llh = position_llh
        self.additional_information_2 = additional_information_2

    @classmethod
    def from_query(cls, station_info_qr, coordinates_qr):
        return cls(
            station_info_qr[0].site_name,
            station_info_qr[0].four_char_id,
            station_info_qr[0].monument_inscription,
            station_info_qr[0].domes_number,
            station_info_qr[0].cdp_number,
            station_info_qr[0].monument_description,
            station_info_qr[0].monument_height,
            station_info_qr[0].monument_foundation,
            station_info_qr[0].foundation_depth,
            station_info_qr[0].marker_description,
            station_info_qr[0].date_installed,
            station_info_qr[0].geologic_characteristic,
            station_info_qr[0].bedrock_type,
            station_info_qr[0].bedrock_condition,
            station_info_qr[0].fracture_spacing,
            station_info_qr[0].fault_zones_nearby,
            station_info_qr[0].fault_zones_distance_activity,
            station_info_qr[0].additional_info_1,
            station_info_qr[0].city,
            station_info_qr[0].state_province,
            station_info_qr[0].country_name,
            station_info_qr[0].tectonic_plate,
            {
                "X": float(coordinates_qr[0].X),
                "Y": float(coordinates_qr[0].Y),
                "Z": float(coordinates_qr[0].Z),
                "reference_frame": coordinates_qr[0].reference_frame,
            },
            transformations.ecef2geodetic(
                float(coordinates_qr[0].X),
                float(coordinates_qr[0].Y),
                float(coordinates_qr[0].Z),
                unit="dms",
                ellipsoid_name="GRS80",
            ),
            station_info_qr[0].additional_info_2,
        )

    def print_to_log(self):
        return (
            "{get_title(1)}"
            "     Site Name                : {xstr(self.site_name)}\n"
            "     Four Character ID        : {xstr(self.four_char_id)}\n"
            "     Monument Inscription     : {xstr(self.monument_inscription)}\n"
            "     IERS DOMES Number        : {xstr(self.domes_number)}\n"
            "     CDP Number               : {xstr(self.cdp_number)}\n"
            "     Monument Description     : {xstr(self.monument_description).upper()}\n"
            "       Height of the Monument : {xstr(add_unit(self.monument_height, 'm'))}\n"
            "       Monument Foundation    : {xstr(self.monument_foundation).upper()}\n"
            "       Foundation Depth       : {xstr(add_unit(self.foundation_depth, 'm'))}\n"
            "     Marker Description       : {xstr(self.marker_description).upper()}\n"
            "     Date Installed           : {long_date(self.date_installed)}\n"
            "     Geologic Characteristic  : {xstr(self.geologic_characteristic).upper()}\n"
            "       Bedrock Type           : {xstr(self.bedrock_type).upper()}\n"
            "       Bedrock Condition      : {xstr(self.bedrock_condition).upper()}\n"
            "       Fracture Spacing       : {xstr(self.fracture_spacing)}\n"
            "       Fault zones nearby     : {xstr(self.fault_zones_nearby).upper()}\n"
            "         Distance/activity    : {format_multiple_lines(self.distance_activity)}\n"
            "     Additional Information   : {format_multiple_lines(self.additional_information_1)}\n"
            "\n\n"
            "{get_title(2)}"
            "     City or Town             : {xstr(self.city)}\n"
            "     State or Province        : {xstr(self.state)}\n"
            "     Country                  : {xstr(self.country)}\n"
            "     Tectonic Plate           : {xstr(self.tectonic_plate).upper()}\n"
            "     Approximate Position ({self.position_XYZ['reference_frame']})\n"
            "       X coordinate (m)       : {self.position_XYZ['X']:.4f}\n"
            "       Y coordinate (m)       : {self.position_XYZ['Y']:.4f}\n"
            "       Z coordinate (m)       : {self.position_XYZ['Z']:.4f}\n"
            "       Latitude (N is +)      : {self.position_llh['lat'][0]:+03d}{self.position_llh['lat'][1]:02d}{self.position_llh['lat'][2]:09.6f}\n"
            "       Longitude (E is +)     : {self.position_llh['lon'][0]:+04d}{self.position_llh['lon'][1]:02d}{self.position_llh['lon'][2]:09.6f}\n"
            "       Elevation (m,ellips.)  : {self.position_llh['h']:10.4f}\n"
            "     Additional Information   : {format_multiple_lines(self.additional_information_2)}\n"
            "\n\n"
        )

    def print_to_crux(self):
        return (
            f"        \"APPROX POSITION XYZ\" : {{0:\"{self.position_XYZ['X']:.4f}\", 1:\"{self.position_XYZ['Y']:.4f}\", 2:\"{self.position_XYZ['Z']:.4f}\"}}\n"
            f'        "MARKER NAME"         : {{0:"{self.four_char_id}"}}\n'
            f'        "MARKER NUMBER"       : {{0:"{self.domes_number if self.domes_number else self.four_char_id}"}}\n'
        )


class Receiver(object):
    def __init__(
        self,
        i: int,
        receiver_type: str,
        satellite_system: dict,
        serial_number: str,
        receiver_fw_version: str,
        me_fw_version: str,
        elevation_cutoff: int,
        date_installed: datetime.datetime,
        date_removed: datetime.datetime,
        temperature_stabilization: str,
        additional_information: str,
    ):
        self.i = i
        self.receiver_type = receiver_type
        self.satellite_system = satellite_system
        self.serial_number = serial_number
        self.receiver_fw_version = receiver_fw_version
        self.me_fw_version = me_fw_version
        self.elevation_cutoff = elevation_cutoff
        self.date_installed = date_installed
        self.date_removed = date_removed
        self.temperature_stabilization = temperature_stabilization
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, receiver_qr, i=1):
        return cls(
            i,
            receiver_qr.receiver_igs_name,
            {
                "GPS": receiver_qr.gps,
                "GLO": receiver_qr.glo,
                "GAL": receiver_qr.gal,
                "BDS": receiver_qr.bds,
                "QZSS": receiver_qr.qzss,
                "IRNSS": receiver_qr.irnss,
                "SBAS": receiver_qr.sbas,
            },
            receiver_qr.serial_number
            if "unknown" not in receiver_qr.serial_number
            else "",
            receiver_qr.receiver_fw_version
            if "unknown" not in receiver_qr.receiver_fw_version
            else "",
            receiver_qr.me_fw_version,
            receiver_qr.elevation_cutoff,
            receiver_qr.date_installed,
            receiver_qr.date_removed,
            receiver_qr.temperature_stabilization,
            receiver_qr.additional_info,
        )

    def print_to_log(self):
        return (
            f"3.{self.i:<3d}Receiver Type            : {self.receiver_type.rstrip()}\n"
            f"     Satellite System         : {format_satellite_systems(self.satellite_system)}\n"
            f"     Serial Number            : {self.serial_number}\n"
            f"     Firmware Version         : {merge_fw_versions(self.receiver_fw_version, self.me_fw_version)}\n"
            f"     Elevation Cutoff Setting : {add_unit(self.elevation_cutoff, 'deg')}\n"
            f"     Date Installed           : {long_date(self.date_installed)}\n"
            f"     Date Removed             : {long_date(self.date_removed)}\n"
            f"     Temperature Stabiliz.    : {xstr(self.temperature_stabilization) if xstr(self.temperature_stabilization) else 'none'}\n"
            f"     Additional Information   : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "3.x  Receiver Type            : (A20, from rcvr_ant.tab; see instructions)\n"
            "     Satellite System         : (GPS+GLO+GAL+BDS+QZSS+SBAS)\n"
            "     Serial Number            : (A20, but note the first A5 is used in SINEX)\n"
            "     Firmware Version         : (A11)\n"
            "     Elevation Cutoff Setting : (deg)\n"
            "     Date Installed           : (CCYY-MM-DDThh:mmZ)\n"
            "     Date Removed             : (CCYY-MM-DDThh:mmZ)\n"
            "     Temperature Stabiliz.    : (none or tolerance in degrees C)\n"
            "     Additional Information   : (multiple lines)\n"
            "\n\n"
        )

    def print_to_crux(self):
        installed = crux_date(self.date_installed)
        removed = crux_date(self.date_removed, minus_one_sec=True)
        sn = self.serial_number
        rec_name = self.receiver_type
        fw = (
            f"{self.receiver_fw_version} / {self.me_fw_version}"
            if self.me_fw_version
            else f"{self.receiver_fw_version}"
        )
        return f'        "REC # / TYPE / VERS"  + {installed} {removed} : {{0:"{sn}", 1:"{rec_name.rstrip()}", 2:"{fw}"}}\n'


class Antenna(object):
    def __init__(
        self,
        i: int,
        antenna_type: str,
        serial_number: str,
        arp: str,
        delta_h: float,
        delta_n: float,
        delta_e: float,
        alignment: int,
        radome_type: str,
        radome_serial_number: str,
        cable_type: str,
        cable_length: int,
        date_installed: datetime.datetime,
        date_removed: datetime.datetime,
        additional_information: str,
    ):
        self.i = i
        self.antenna_type = antenna_type
        self.serial_number = serial_number
        self.arp = arp
        self.delta_h = delta_h
        self.delta_n = delta_n
        self.delta_e = delta_e
        self.alignment = alignment
        self.radome_type = radome_type
        self.radome_serial_number = radome_serial_number
        self.cable_type = cable_type
        self.cable_length = cable_length
        self.date_installed = date_installed
        self.date_removed = date_removed
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, antenna_qr, i=1):
        return cls(
            i,
            antenna_qr.antenna_igs_name,
            antenna_qr.serial_number
            if "unknown" not in antenna_qr.serial_number
            else "",
            antenna_qr.arp_code,
            antenna_qr.delta_h,
            antenna_qr.delta_n,
            antenna_qr.delta_e,
            antenna_qr.alignment_from_north,
            antenna_qr.radome_igs_code,
            antenna_qr.radome_serial_number,
            antenna_qr.cable_type,
            antenna_qr.cable_length,
            antenna_qr.date_installed,
            antenna_qr.date_removed,
            antenna_qr.additional_info,
        )

    def print_to_log(self):
        return (
            f"4.{self.i:<3d}Antenna Type             : {self.antenna_type} {self.radome_type}\n"
            f"     Serial Number            : {self.serial_number}\n"
            f"     Antenna Reference Point  : {self.arp}\n"
            f"     Marker->ARP Up Ecc. (m)  : {self.delta_h:8.4f}\n"
            f"     Marker->ARP North Ecc(m) : {self.delta_n:8.4f}\n"
            f"     Marker->ARP East Ecc(m)  : {self.delta_e:8.4f}\n"
            f"     Alignment from True N    : {add_unit('{:+d}'.format(self.alignment) if type(self.alignment) == int else self.alignment, 'deg')}\n"
            f"     Antenna Radome Type      : {self.radome_type}\n"
            f"     Radome Serial Number     : {xstr(self.radome_serial_number)}\n"
            f"     Antenna Cable Type       : {xstr(self.cable_type)}\n"
            f"     Antenna Cable Length     : {add_unit(self.cable_length, 'm')}\n"
            f"     Date Installed           : {long_date(self.date_installed)}\n"
            f"     Date Removed             : {long_date(self.date_removed)}\n"
            f"     Additional Information   : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "4.x  Antenna Type             : (A20, from rcvr_ant.tab; see instructions)\n"
            "     Serial Number            : (A*, but note the first A5 is used in SINEX)\n"
            '     Antenna Reference Point  : (BPA/BCR/XXX from "antenna.gra"; see instr.)\n'
            "     Marker->ARP Up Ecc. (m)  : (F8.4)\n"
            "     Marker->ARP North Ecc(m) : (F8.4)\n"
            "     Marker->ARP East Ecc(m)  : (F8.4)\n"
            "     Alignment from True N    : (deg; + is clockwise/east)\n"
            "     Antenna Radome Type      : (A4 from rcvr_ant.tab; see instructions)\n"
            "     Radome Serial Number     : \n"
            "     Antenna Cable Type       : (vendor & type number)\n"
            "     Antenna Cable Length     : (m)\n"
            "     Date Installed           : (CCYY-MM-DDThh:mmZ)\n"
            "     Date Removed             : (CCYY-MM-DDThh:mmZ)\n"
            "     Additional Information   : (multiple lines)\n"
            "\n\n"
        )

    def print_to_crux(self):
        installed = crux_date(self.date_installed)
        removed = crux_date(self.date_removed, minus_one_sec=True)
        sn = xstr(self.serial_number)
        ant_name = self.antenna_type
        radome = self.radome_type
        return f'        "ANT # / TYPE"         + {installed} {removed} : {{0:"{sn}", 1:"{ant_name.rstrip()}", 2:"{radome}"}}\n'

    def print_eccentricities_to_crux(self):
        installed = crux_date(self.date_installed)
        removed = crux_date(self.date_removed, minus_one_sec=True)
        return f'        "ANTENNA: DELTA H/E/N" + {installed} {removed} : {{0:"{self.delta_h:.4f}", 1:"{self.delta_e:.4f}", 2:"{self.delta_n:.4f}"}}\n'


class LocalTie(object):
    def __init__(
        self,
        i: int,
        tied_marker_name: str,
        tied_marker_usage: str,
        tied_marker_cdp_number: str,
        tied_marker_domes_number: str,
        dx: float,
        dy: float,
        dz: float,
        accuracy: float,
        survey_method: str,
        date_measured: datetime.datetime,
        additional_information: str,
    ):
        self.i = i
        self.tied_marker_name = tied_marker_name
        self.tied_marker_usage = tied_marker_usage
        self.tied_marker_cdp_number = tied_marker_cdp_number
        self.tied_marker_domes_number = tied_marker_domes_number
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.accuracy = accuracy
        self.survey_method = survey_method
        self.date_measured = date_measured
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, local_ties_qr, i=1):
        return cls(
            i,
            local_ties_qr.marker_name,
            local_ties_qr.marker_usage,
            local_ties_qr.marker_cdp_number,
            local_ties_qr.marker_domes_number,
            local_ties_qr.dx,
            local_ties_qr.dy,
            local_ties_qr.dz,
            local_ties_qr.accuracy,
            local_ties_qr.survey_method,
            local_ties_qr.date_measured,
            local_ties_qr.additional_info,
        )

    def print_to_log(self):
        return (
            f"5.{self.i:<3d}Tied Marker Name         : {self.tied_marker_name}\n"
            f"     Tied Marker Usage        : {xstr(self.tied_marker_usage).upper()}\n"
            f"     Tied Marker CDP Number   : {xstr(self.tied_marker_cdp_number)}\n"
            f"     Tied Marker DOMES Number : {xstr(self.tied_marker_domes_number)}\n"
            f"     Differential Components from GNSS Marker to the tied monument (ITRS)\n"
            f"       dx (m)                 : {add_unit(self.dx, 'm')}\n"
            f"       dy (m)                 : {add_unit(self.dy, 'm')}\n"
            f"       dz (m)                 : {add_unit(self.dz, 'm')}\n"
            f"     Accuracy (mm)            : {add_unit(self.accuracy, 'mm')}\n"
            f"     Survey method            : {xstr(self.survey_method).upper()}\n"
            f"     Date Measured            : {short_date(self.date_measured, return_placeholder=False)}\n"
            f"     Additional Information   : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "5.x  Tied Marker Name         : \n"
            "     Tied Marker Usage        : (SLR/VLBI/LOCAL CONTROL/FOOTPRINT/etc)\n"
            "     Tied Marker CDP Number   : (A4)\n"
            "     Tied Marker DOMES Number : (A9)\n"
            "     Differential Components from GNSS Marker to the tied monument (ITRS)\n"
            "       dx (m)                 : (m)\n"
            "       dy (m)                 : (m)\n"
            "       dz (m)                 : (m)\n"
            "     Accuracy (mm)            : (mm)\n"
            "     Survey method            : (GPS CAMPAIGN/TRILATERATION/TRIANGULATION/etc)\n"
            "     Date Measured            : (CCYY-MM-DDThh:mmZ)\n"
            "     Additional Information   : (multiple lines)\n"
            "\n\n"
        )


class FrequencyStandard(object):
    def __init__(
        self,
        i: int,
        standard_type: str,
        input_frequency: str,
        effective_dates: Tuple[datetime.datetime, Union[datetime.datetime, None]],
        notes: str,
    ):
        self.i = i
        self.standard_type = standard_type
        self.input_frequency = input_frequency
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, frequency_standard_qr, i=1):
        return cls(
            i,
            frequency_standard_qr.type,
            frequency_standard_qr.input_frequency,
            (
                frequency_standard_qr.effective_date_start,
                frequency_standard_qr.effective_date_end,
            ),
            frequency_standard_qr.notes,
        )

    def print_to_log(self):
        return (
            f"6.{self.i:<3d}Standard Type            : {self.standard_type.upper()}\n"
            f"       Input Frequency        : {xstr(self.input_frequency)}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "6.x  Standard Type            : (INTERNAL or EXTERNAL H-MASER/CESIUM/etc)\n"
            "       Input Frequency        : (if external)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n\n"
        )


class CollocationInformation(object):
    def __init__(
        self,
        i: int,
        instrumentation_type: str,
        status: str,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        notes: str,
    ):
        self.i = i
        self.instrumentation_type = instrumentation_type
        self.status = status
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, collocation_information_qr, i=1):
        return cls(
            i,
            collocation_information_qr.instrumentation_type,
            collocation_information_qr.status,
            (
                collocation_information_qr.effective_date_start,
                collocation_information_qr.effective_date_end,
            ),
            collocation_information_qr.notes,
        )

    def print_to_log(self):
        return (
            f"7.{self.i:<3d}Instrumentation Type     : {self.instrumentation_type}\n"
            f"       Status                 : {self.status.upper()}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "7.x  Instrumentation Type     : (GPS/GLONASS/DORIS/PRARE/SLR/VLBI/TIME/etc)\n"
            "       Status                 : (PERMANENT/MOBILE)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n\n"
        )


class HumiditySensor:
    def __init__(
        self,
        i: int,
        sensor_model: str,
        manufacturer: str,
        serial_number: str,
        data_sampling_interval: float,
        accuracy: float,
        aspiration: str,
        delta_h: float,
        calibration_date: datetime.datetime,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        notes: str,
    ):
        self.i = i
        self.sensor_model = sensor_model
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.data_sampling_interval = data_sampling_interval
        self.accuracy = accuracy
        self.aspiration = aspiration
        self.delta_h = delta_h
        self.calibration_date = calibration_date
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, humidity_sensor_qr, i=1):
        return cls(
            i,
            humidity_sensor_qr.humidity_sensor_model,
            humidity_sensor_qr.manufacturer,
            humidity_sensor_qr.serial_number,
            humidity_sensor_qr.data_sampling_interval,
            humidity_sensor_qr.accuracy,
            humidity_sensor_qr.aspiration,
            humidity_sensor_qr.delta_h,
            humidity_sensor_qr.calibration_date,
            (
                humidity_sensor_qr.effective_date_start,
                humidity_sensor_qr.effective_date_end,
            ),
            humidity_sensor_qr.notes,
        )

    def print_to_log(self):
        return (
            f"8.1.{self.i:<2d}Humidity Sensor Model   : {self.sensor_model}\n"
            f"       Manufacturer           : {self.manufacturer}\n"
            f"       Serial Number          : {xstr(self.serial_number)}\n"
            f"       Data Sampling Interval : {add_unit(self.data_sampling_interval, 'sec')}\n"
            f"       Accuracy (% rel h)     : {xstr(self.accuracy)}\n"
            f"       Aspiration             : {xstr(self.aspiration.upper())}\n"
            f"       Height Diff to Ant     : {add_unit(self.delta_h, 'm')}\n"
            f"       Calibration date       : {short_date(self.calibration_date)}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "8.1.x Humidity Sensor Model   : \n"
            "       Manufacturer           : \n"
            "       Serial Number          : \n"
            "       Data Sampling Interval : (sec)\n"
            "       Accuracy (% rel h)     : (% rel h)\n"
            "       Aspiration             : (UNASPIRATED/NATURAL/FAN/etc)\n"
            "       Height Diff to Ant     : (m)\n"
            "       Calibration date       : (CCYY-MM-DD)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n"
        )


class PressureSensor:
    def __init__(
        self,
        i: int,
        sensor_model: str,
        manufacturer: str,
        serial_number: str,
        data_sampling_interval: float,
        accuracy: float,
        delta_h: float,
        calibration_date: datetime.datetime,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        notes: str,
    ):
        self.i = i
        self.sensor_model = sensor_model
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.data_sampling_interval = data_sampling_interval
        self.accuracy = accuracy
        self.delta_h = delta_h
        self.calibration_date = calibration_date
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, pressure_sensor_qr, i=1):
        return cls(
            i,
            pressure_sensor_qr.pressure_sensor_model,
            pressure_sensor_qr.manufacturer,
            pressure_sensor_qr.serial_number,
            pressure_sensor_qr.data_sampling_interval,
            pressure_sensor_qr.accuracy,
            pressure_sensor_qr.delta_h,
            pressure_sensor_qr.calibration_date,
            (
                pressure_sensor_qr.effective_date_start,
                pressure_sensor_qr.effective_date_end,
            ),
            pressure_sensor_qr.notes,
        )

    def print_to_log(self):
        return (
            f"8.2.{self.i:<2d}Pressure Sensor Model   : {self.sensor_model}\n"
            f"       Manufacturer           : {self.manufacturer}\n"
            f"       Serial Number          : {xstr(self.serial_number)}\n"
            f"       Data Sampling Interval : {add_unit(self.data_sampling_interval, 'sec')}\n"
            f"       Accuracy               : {xstr(self.accuracy)}\n"
            f"       Height Diff to Ant     : {add_unit(self.delta_h, 'm')}\n"
            f"       Calibration date       : {short_date(self.calibration_date)}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "8.2.x Pressure Sensor Model   : \n"
            "       Manufacturer           : \n"
            "       Serial Number          : \n"
            "       Data Sampling Interval : (sec)\n"
            "       Accuracy               : (hPa)\n"
            "       Height Diff to Ant     : (m)\n"
            "       Calibration date       : (CCYY-MM-DD)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n"
        )


class TemperatureSensor:
    def __init__(
        self,
        i: int,
        sensor_model: str,
        manufacturer: str,
        serial_number: str,
        data_sampling_interval: float,
        accuracy: float,
        aspiration: str,
        delta_h: float,
        calibration_date: datetime.datetime,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        notes: str,
    ):
        self.i = i
        self.sensor_model = sensor_model
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.data_sampling_interval = data_sampling_interval
        self.accuracy = accuracy
        self.aspiration = aspiration
        self.delta_h = delta_h
        self.calibration_date = calibration_date
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, temperature_sensor_qr, i=1):
        return cls(
            i,
            temperature_sensor_qr.temperature_sensor_model,
            temperature_sensor_qr.manufacturer,
            temperature_sensor_qr.serial_number,
            temperature_sensor_qr.data_sampling_interval,
            temperature_sensor_qr.accuracy,
            temperature_sensor_qr.aspiration,
            temperature_sensor_qr.delta_h,
            temperature_sensor_qr.calibration_date,
            (
                temperature_sensor_qr.effective_date_start,
                temperature_sensor_qr.effective_date_end,
            ),
            temperature_sensor_qr.notes,
        )

    def print_to_log(self):
        return (
            f"8.3.{self.i:<2d}Temp. Sensor Model      : {self.sensor_model}\n"
            f"       Manufacturer           : {self.manufacturer}\n"
            f"       Serial Number          : {xstr(self.serial_number)}\n"
            f"       Data Sampling Interval : {add_unit(self.data_sampling_interval, 'sec')}\n"
            f"       Accuracy               : {xstr(self.accuracy)}\n"
            f"       Aspiration             : {xstr(self.aspiration.upper())}\n"
            f"       Height Diff to Ant     : {add_unit(self.delta_h, 'm')}\n"
            f"       Calibration date       : {short_date(self.calibration_date)}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "8.3.x Temp. Sensor Model      : \n"
            "       Manufacturer           : \n"
            "       Serial Number          : \n"
            "       Data Sampling Interval : (sec)\n"
            "       Accuracy               : (deg C)\n"
            "       Aspiration             : (UNASPIRATED/NATURAL/FAN/etc)\n"
            "       Height Diff to Ant     : (m)\n"
            "       Calibration date       : (CCYY-MM-DD)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n"
        )


class WaterVaporRadiometer(object):
    def __init__(
        self,
        i: int,
        sensor_model: str,
        manufacturer: str,
        serial_number: str,
        distance_to_antenna: float,
        delta_h: float,
        calibration_date: datetime.datetime,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        notes: str,
    ):
        self.i = i
        self.sensor_model = sensor_model
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.distance_to_antenna = distance_to_antenna
        self.delta_h = delta_h
        self.calibration_date = calibration_date
        self.effective_dates = effective_dates
        self.notes = notes

    @classmethod
    def from_query(cls, water_vapor_radiometer_qr, i=1):
        return cls(
            i,
            water_vapor_radiometer_qr.water_vapor_radiometer_model,
            water_vapor_radiometer_qr.manufacturer,
            water_vapor_radiometer_qr.serial_number,
            water_vapor_radiometer_qr.distance_to_antenna,
            water_vapor_radiometer_qr.delta_h,
            water_vapor_radiometer_qr.calibration_date,
            (
                water_vapor_radiometer_qr.effective_date_start,
                water_vapor_radiometer_qr.effective_date_end,
            ),
            water_vapor_radiometer_qr.notes,
        )

    def print_to_log(self):
        return (
            f"8.4.{self.i:<2d}Water Vapor Radiometer  : {self.sensor_model}\n"
            f"       Manufacturer           : {self.manufacturer}\n"
            f"       Serial Number          : {self.serial_number}\n"
            f"       Distance to Antenna    : {self.distance_to_antenna}\n"
            f"       Height Diff to Ant     : {self.delta_h}\n"
            f"       Calibration date       : {self.calibration_date}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Notes                  : {format_multiple_lines(self.notes)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "8.4.x Water Vapor Radiometer  : \n"
            "       Manufacturer           : \n"
            "       Serial Number          : \n"
            "       Distance to Antenna    : (m)\n"
            "       Height Diff to Ant     : (m)\n"
            "       Calibration date       : (CCYY-MM-DD)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Notes                  : (multiple lines)\n"
            "\n"
        )


class OtherMeteorologicalInstrumentation(object):
    def __init__(self, i: int, description: str):
        self.i = i
        self.description = description

    @classmethod
    def from_query(cls, other_meteorological_instrumentation_qr, i=1):
        return cls(
            i,
            other_meteorological_instrumentation_qr.description,
        )

    def print_to_log(self):
        return (
            f"8.5.{self.i:<2d}Other Instrumentation   : {format_multiple_lines(self.description)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return "8.5.x Other Instrumentation   : (multiple lines)\n\n\n"


class RadioInterference(object):
    def __init__(
        self,
        i: int,
        source: str,
        observed_degradations: str,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        additional_information: str,
    ):
        self.i = i
        self.source = source
        self.observed_degradations = observed_degradations
        self.effective_dates = effective_dates
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, radio_interference_qr, i=1):
        return cls(
            i,
            radio_interference_qr.radio_interference_source,
            radio_interference_qr.observed_degradations,
            (
                radio_interference_qr.effective_date_start,
                radio_interference_qr.effective_date_end,
            ),
            radio_interference_qr.additional_information,
        )

    def to_txt(self):
        return (
            f"9.1.{self.i:<2d}Radio Interferences     : {self.source.upper()}\n"
            f"       Observed Degradations  : {xstr(self.observed_degradations.upper())}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Additional Information : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def blank_entry():
        return (
            "9.1.x Radio Interferences     : (TV/CELL PHONE ANTENNA/RADAR/etc)\n"
            "       Observed Degradations  : (SN RATIO/DATA GAPS/etc)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Additional Information : (multiple lines)\n"
            "\n"
        )


class MultipathSource(object):
    def __init__(
        self,
        i: int,
        source: str,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        additional_information: str,
    ):
        self.i = i
        self.source = source
        self.effective_dates = effective_dates
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, multipath_source_qr, i=1):
        return cls(
            i,
            multipath_source_qr.multipath_source,
            (
                multipath_source_qr.effective_date_start,
                multipath_source_qr.effective_date_end,
            ),
            multipath_source_qr.additional_information,
        )

    def print_to_log(self):
        return (
            f"9.2.{self.i:<2d}Multipath Sources       : {self.source.upper()}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Additional Information : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "9.2.x Multipath Sources       : (METAL ROOF/DOME/VLBI ANTENNA/etc)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Additional Information : (multiple lines)\n"
            "\n"
        )


class SignalObstruction(object):
    def __init__(
        self,
        i: int,
        source: str,
        effective_dates: Tuple[datetime.datetime, datetime.datetime],
        additional_information: str,
    ):
        self.i = i
        self.source = source
        self.effective_dates = effective_dates
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, signal_obstruction_qr, i=1):
        return cls(
            i,
            signal_obstruction_qr.signal_obstruction_source,
            (
                signal_obstruction_qr.effective_date_start,
                signal_obstruction_qr.effective_date_end,
            ),
            signal_obstruction_qr.additional_information,
        )

    def to_txt(self):
        return (
            f"9.3.{self.i:<2d}Signal Obstructions     : {self.source.upper()}\n"
            f"       Effective Dates        : {short_date(self.effective_dates[0])}/{short_date(self.effective_dates[1])}\n"
            f"       Additional Information : {format_multiple_lines(self.additional_information)}\n"
            f"\n"
        )

    @staticmethod
    def blank_entry():
        return (
            "9.3.x Signal Obstructions     : (TREES/BUILDINGS/etc)\n"
            "       Effective Dates        : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "       Additional Information : (multiple lines)\n"
            "\n\n"
        )


class LocalEpisodicEffect(object):
    def __init__(
        self, i: int, dates: Tuple[datetime.datetime, datetime.datetime], event: str
    ):
        self.i = i
        self.dates = dates
        self.event = event

    @classmethod
    def from_query(cls, local_episodic_effect_qr, i=1):
        return cls(
            i,
            (local_episodic_effect_qr.date_start, local_episodic_effect_qr.date_end),
            local_episodic_effect_qr.event,
        )

    def print_to_log(self):
        return (
            f"10.{self.i:<2d}Date                     : {short_date(self.dates[0])}/{short_date(self.dates[1])}\n"
            f"     Event                    : {format_multiple_lines(self.event)}\n"
            f"\n"
        )

    @staticmethod
    def print_blank_to_log():
        return (
            "10.x Date                     : (CCYY-MM-DD/CCYY-MM-DD)\n"
            "     Event                    : (TREE CLEARING/CONSTRUCTION/etc)\n"
            "\n\n"
        )


class Agency(object):
    def __init__(
        self,
        agency: str,
        abbreviation: str,
        address: str,
        contact_name_1: str,
        telephone_primary_1: str,
        telephone_secondary_1: str,
        fax_1: str,
        email_1: str,
        contact_name_2: str,
        telephone_primary_2: str,
        telephone_secondary_2: str,
        fax_2: str,
        email_2: str,
        additional_information: str,
    ):
        self.agency = agency
        self.abbreviation = abbreviation
        self.address = address
        self.contact_name_1 = contact_name_1
        self.telephone_primary_1 = telephone_primary_1
        self.telephone_secondary_1 = telephone_secondary_1
        self.fax_1 = fax_1
        self.email_1 = email_1
        self.contact_name_2 = contact_name_2
        self.telephone_primary_2 = telephone_primary_2
        self.telephone_secondary_2 = telephone_secondary_2
        self.fax_2 = fax_2
        self.email_2 = email_2
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, agency_qr, primary_contact_qr, secondary_contact_qr):
        return cls(
            agency_qr[0].name if agency_qr else "",
            agency_qr[0].abbreviation if agency_qr else "",
            agency_qr[0].mailing_address if agency_qr else "",
            primary_contact_qr[0].name if primary_contact_qr else "",
            primary_contact_qr[0].telephone_primary if primary_contact_qr else "",
            primary_contact_qr[0].telephone_secondary if primary_contact_qr else "",
            primary_contact_qr[0].fax if primary_contact_qr else "",
            primary_contact_qr[0].email if primary_contact_qr else "",
            secondary_contact_qr[0].name if secondary_contact_qr else "",
            secondary_contact_qr[0].telephone_primary if secondary_contact_qr else "",
            secondary_contact_qr[0].telephone_secondary if secondary_contact_qr else "",
            secondary_contact_qr[0].fax if secondary_contact_qr else "",
            secondary_contact_qr[0].email if secondary_contact_qr else "",
            agency_qr[0].additional_information if agency_qr else "",
        )

    def print_to_log(self):
        return (
            f"     Agency                   : {xstr(self.agency)}\n"
            f"     Preferred Abbreviation   : {xstr(self.abbreviation)}\n"
            f"     Mailing Address          : {format_multiple_lines(self.address)}\n"
            f"     Primary Contact\n"
            f"       Contact Name           : {xstr(self.contact_name_1)}\n"
            f"       Telephone (primary)    : {xstr(self.telephone_primary_1)}\n"
            f"       Telephone (secondary)  : {xstr(self.telephone_secondary_1)}\n"
            f"       Fax                    : {xstr(self.fax_1)}\n"
            f"       E-mail                 : {xstr(self.email_1)}\n"
            f"     Secondary Contact\n"
            f"       Contact Name           : {xstr(self.contact_name_2)}\n"
            f"       Telephone (primary)    : {xstr(self.telephone_primary_2)}\n"
            f"       Telephone (secondary)  : {xstr(self.telephone_secondary_2)}\n"
            f"       Fax                    : {xstr(self.fax_2)}\n"
            f"       E-mail                 : {xstr(self.email_2)}\n"
            f"     Additional Information   : {format_multiple_lines(self.additional_information)}\n"
            f"\n\n"
        )

    def print_to_crux(self):
        return f'        "OBSERVER / AGENCY"   : {{0:"automatic", 1:"{self.abbreviation}"}}\n'


class MoreInformation(object):
    def __init__(
        self,
        primary_data_center: str,
        secondary_data_center: str,
        url_more_info: str,
        site_map: str,
        site_diagram: str,
        horizon_mask: str,
        monument_description: str,
        site_pictures: str,
        additional_information: str,
    ):
        self.primary_data_center = primary_data_center
        self.secondary_data_center = secondary_data_center
        self.url_more_info = url_more_info
        self.site_map = site_map
        self.site_diagram = site_diagram
        self.horizon_mask = horizon_mask
        self.monument_description = monument_description
        self.site_pictures = site_pictures
        self.additional_information = additional_information

    @classmethod
    def from_query(cls, more_information_qr):
        return cls(
            more_information_qr[0].primary_data_center if more_information_qr else "",
            more_information_qr[0].secondary_data_center if more_information_qr else "",
            more_information_qr[0].url_more_info if more_information_qr else "",
            more_information_qr[0].site_map if more_information_qr else "",
            more_information_qr[0].site_diagram if more_information_qr else "",
            more_information_qr[0].horizon_mask if more_information_qr else "",
            more_information_qr[0].monument_description if more_information_qr else "",
            more_information_qr[0].site_pictures if more_information_qr else "",
            more_information_qr[0].additional_information
            if more_information_qr
            else "",
        )

    def print_to_log(self):
        return (
            f"     Primary Data Center      : {xstr(self.primary_data_center)}\n"
            f"     Secondary Data Center    : {xstr(self.secondary_data_center)}\n"
            f"     URL for More Information : {xstr(self.url_more_info)}\n"
            f"     Hardcopy on File\n"
            f"       Site Map               : {xstr(self.site_map)}\n"
            f"       Site Diagram           : {xstr(self.site_diagram)}\n"
            f"       Horizon Mask           : {xstr(self.horizon_mask)}\n"
            f"       Monument Description   : {xstr(self.monument_description)}\n"
            f"       Site Pictures          : {xstr(self.site_pictures)}\n"
            f"     Additional Information   : {format_multiple_lines(self.additional_information)}\n"
            f"     Antenna Graphics with Dimensions\n\n"
        )
