from typing import Optional
import datetime
import xsdata
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime, XmlDuration, XmlTime

from refs import getRef

from netex import VersionFrameDefaultsStructure, CodespaceRefStructure, ResponsibilitySetRefStructure, \
    DataSourceRefStructure, LocaleStructure, SystemOfUnits, Version, DataManagedObject, Codespace, CompositeFrame, \
    TypeOfFrameRef, VersionTypeEnumeration, VersionFrameVersionStructure, VersionsRelStructure, CodespacesRelStructure, \
    PublicationDelivery, DataObjectsRelStructure, FramesRelStructure, ResourceFrame, DataSourcesInFrameRelStructure, \
    DataSource, MultilingualString, ResponsibilitySet, ResponsibilityRoleAssignmentsRelStructure, \
    ResponsibilityRoleAssignment, VersionOfObjectRefStructure, TransportAdministrativeZone, \
    ResponsibilitySetsInFrameRelStructure, ZonesInFrameRelStructure, Operator, ContactStructure, \
    OrganisationsInFrameRelStructure, OperationalContext, AllModesEnumeration, OperationalContextsInFrameRelStructure, \
    VehicleType, VehicleModeEnumeration, TypeOfFuelEnumeration, ServiceFacilitySetsRelStructure, ServiceFacilitySet, \
    MobilityFacilityEnumeration, PassengerCommsFacilityEnumeration, VehicleTypesInFrameRelStructure, Vehicle, \
    VehicleTypeRef, VehiclesInFrameRelStructure, PassengerCapacityStructure, ServiceFrame, \
    RoutePointsInFrameRelStructure, RouteLinksInFrameRelStructure, RouteLink, LineString, PosList, \
    RoutePointRefStructure, OperationalContextRef, Route1, Line1, AllVehicleModesOfTransportEnumeration, \
    TypeOfServiceRef, AccessibilityAssessment, LinesInFrameRelStructure, LineRef, DestinationDisplay, \
    DestinationDisplaysInFrameRelStructure, ViasRelStructure, ViaVersionedChildStructure, RoutesInFrameRelStructure, \
    ScheduledStopPointsInFrameRelStructure, ScheduledStopPoint, LocationStructure2, Pos, ProjectionsRelStructure, \
    PointProjection, PointRefStructure, RoutePoint, ServiceJourneyPattern, DestinationDisplayRef, RouteRef, \
    PointsInJourneyPatternRelStructure, ScheduledStopPointRef, StopPointInJourneyPattern, \
    JourneyPatternsInFrameRelStructure, TimingLink, TimingPointRefStructure, TimingLinksInFrameRelStructure, \
    PointsOnRouteRelStructure, PointOnRoute, RoutePointRef, RouteLinkRef, RouteLinkRefStructure, TimeDemandType, \
    JourneyRunTimesRelStructure, JourneyRunTime, TimingLinkRef, JourneyWaitTimesRelStructure, JourneyWaitTime, \
    TimeDemandTypesInFrameRelStructure, TimetableFrame, OperatorView, OperatorRef, ServiceJourney1, \
    JourneysInFrameRelStructure, ServiceJourneyPatternRef, TimeDemandTypeRef, TimeDemandTypeRefStructure, \
    LimitationStatusEnumeration, AvailabilityCondition, ValidityConditionsRelStructure, AvailabilityConditionRef

import datetime

def getBitString(available: list):
    l = sorted(available)
    y,m,d = min(l).split('-')
    f = datetime.date(int(y),int(m),int(d))
    f_orig = f
    y,m,d = max(l).split('-')
    t = datetime.date(int(y),int(m),int(d))

    out = ''
    while f <= t:
        out += str(int(f.isoformat() in l))
        f += datetime.timedelta(days=1)

    return (f_orig, t, out)

def setIdVersion(obj: object, codespace: Codespace, id: str, version: Optional[Version]):
    name = type(obj).__name__
    if hasattr(obj.Meta, 'name'):
        name = obj.Meta.name
    obj.id = "{}:{}:{}".format(codespace.xmlns, name, id)
    if version:
        obj.version = version.version
    else:
        obj.version = "any"

def getVersionOfObjectRef(obj: object):
    return VersionOfObjectRefStructure(name_of_ref_class=type(obj).__name__, ref=obj.id)

def getFrameDefaults(codespace: Codespace,
                     data_source: DataSource,
                     responsibility_set: ResponsibilitySet
                     ) -> VersionFrameDefaultsStructure:
    frame_defaults = VersionFrameDefaultsStructure(default_codespace_ref=getRef(codespace),
                                                   default_data_source_ref=getRef(data_source),
                                                   default_responsibility_set_ref=getRef(responsibility_set),
                                                   default_locale=LocaleStructure(time_zone="Europe/Amsterdam", default_language="nl"),
                                                   default_location_system="EPSG:28992",
                                                   default_system_of_units=SystemOfUnits.SI_METRES,
                                                   default_currency="EUR"
                                                   )
    return frame_defaults

def getDataSource(codespace: Codespace) -> DataSource:
    data_source = DataSource(name=MultilingualString("openOV"), short_name=MultilingualString("OPENOV"), description=MultilingualString("openOV"))
    setIdVersion(data_source, codespace, "OPENOV", None)
    return data_source

def getTransportAdministrativeZone(codespace: Codespace) -> TransportAdministrativeZone:
    transport_administrative_zone = TransportAdministrativeZone()
    setIdVersion(transport_administrative_zone, codespace, "DOEKSEN", None)
    transport_administrative_zone.name = MultilingualString("Doeksen")
    transport_administrative_zone.short_name = MultilingualString("DOEK")
    transport_administrative_zone.description = MultilingualString("Waddenveren Vlieland en Terschelling")
    return transport_administrative_zone

def getResponsibilitySet(codespace: Codespace, transport_administrative_zone: TransportAdministrativeZone) -> ResponsibilitySet:
    responsibility_set = ResponsibilitySet()
    setIdVersion(responsibility_set, codespace, "DOEKSEN", None)
    responsibility_set.name = MultilingualString(value="Doeksen")

    responsibility_role_assignment = ResponsibilityRoleAssignment()
    setIdVersion(responsibility_role_assignment, codespace, "DOEKSEN", None)
    responsibility_role_assignment.responsible_area_ref = getVersionOfObjectRef(transport_administrative_zone)
    responsibility_set.roles = ResponsibilityRoleAssignmentsRelStructure(responsibility_role_assignment=[responsibility_role_assignment])

    return responsibility_set

def getOperator(codespace: Codespace) -> Operator:
    operator = Operator()
    setIdVersion(operator, codespace, "DOEKSEN", None)
    operator.name = MultilingualString("B.V. Rederij G. Doeksen en Zonen")
    operator.short_name = MultilingualString("Doeksen")
    operator.customer_service_contact_details = ContactStructure(email="info@rederij-doeksen.nl", phone="+31889000888", url="https://rederij-doeksen.nl/")
    return operator

def getVehicleTypes(codespace: Codespace) -> list[VehicleType]:
    vehicle_types = []
    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "LNG", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.NATURAL_GAS
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=692)
    vehicle_type.length = 70
    vehicle_type.width = 17.3
    vehicle_type.name = "Schepen op LNG"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "LNG", None)
    service_facility_set.mobility_facility_list = [MobilityFacilityEnumeration.BOARDING_ASSISTANCE, MobilityFacilityEnumeration.ONBOARD_ASSISTANCE, MobilityFacilityEnumeration.SUITABLE_FOR_PUSHCHAIRS, MobilityFacilityEnumeration.SUITABLE_FOR_WHEELCHAIRS]
    service_facility_set.passenger_comms_facility_list = [PassengerCommsFacilityEnumeration.FREE_WIFI]
    vehicle_type.facilities = ServiceFacilitySetsRelStructure(service_facility_set_ref_or_service_facility_set=[service_facility_set])
    vehicle_types.append(vehicle_type)

    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "Friesland", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.DIESEL
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=1100)
    vehicle_type.length = 69
    vehicle_type.width = 16
    vehicle_type.name = "Ms Friesland"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "Friesland", None)
    service_facility_set.mobility_facility_list = [MobilityFacilityEnumeration.BOARDING_ASSISTANCE, MobilityFacilityEnumeration.ONBOARD_ASSISTANCE, MobilityFacilityEnumeration.SUITABLE_FOR_PUSHCHAIRS, MobilityFacilityEnumeration.SUITABLE_FOR_WHEELCHAIRS]
    service_facility_set.passenger_comms_facility_list = [PassengerCommsFacilityEnumeration.FREE_WIFI]
    vehicle_type.facilities = ServiceFacilitySetsRelStructure(service_facility_set_ref_or_service_facility_set=[service_facility_set])
    vehicle_types.append(vehicle_type)

    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "Vlieland", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.DIESEL
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=950)
    vehicle_type.length = 68
    vehicle_type.width = 17
    vehicle_type.name = "Ms Vlieland"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "Vlieland", None)
    service_facility_set.mobility_facility_list = [MobilityFacilityEnumeration.BOARDING_ASSISTANCE, MobilityFacilityEnumeration.ONBOARD_ASSISTANCE, MobilityFacilityEnumeration.SUITABLE_FOR_PUSHCHAIRS, MobilityFacilityEnumeration.SUITABLE_FOR_WHEELCHAIRS]
    service_facility_set.passenger_comms_facility_list = [PassengerCommsFacilityEnumeration.FREE_WIFI]
    vehicle_type.facilities = ServiceFacilitySetsRelStructure(
        service_facility_set_ref_or_service_facility_set=[service_facility_set])
    vehicle_types.append(vehicle_type)

    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "Koegelwieck", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.DIESEL
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=312)
    vehicle_type.length = 35.5
    vehicle_type.width = 10
    vehicle_type.name = "Ms Koegelwieck"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "Koegelwieck", None)
    service_facility_set.mobility_facility_list = [MobilityFacilityEnumeration.BOARDING_ASSISTANCE, MobilityFacilityEnumeration.ONBOARD_ASSISTANCE, MobilityFacilityEnumeration.SUITABLE_FOR_PUSHCHAIRS, MobilityFacilityEnumeration.SUITABLE_FOR_WHEELCHAIRS]
    service_facility_set.passenger_comms_facility_list = [PassengerCommsFacilityEnumeration.FREE_WIFI]
    vehicle_type.facilities = ServiceFacilitySetsRelStructure(
        service_facility_set_ref_or_service_facility_set=[service_facility_set])
    vehicle_types.append(vehicle_type)

    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "Tiger", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.DIESEL
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=414)
    vehicle_type.length = 52
    vehicle_type.width = 12
    vehicle_type.name = "Ms Tiger"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "Tiger", None)
    service_facility_set.mobility_facility_list = [MobilityFacilityEnumeration.BOARDING_ASSISTANCE, MobilityFacilityEnumeration.ONBOARD_ASSISTANCE, MobilityFacilityEnumeration.SUITABLE_FOR_PUSHCHAIRS, MobilityFacilityEnumeration.SUITABLE_FOR_WHEELCHAIRS]
    service_facility_set.passenger_comms_facility_list = [PassengerCommsFacilityEnumeration.FREE_WIFI]
    vehicle_type.facilities = ServiceFacilitySetsRelStructure(
        service_facility_set_ref_or_service_facility_set=[service_facility_set])
    vehicle_types.append(vehicle_type)

    vehicle_type = VehicleType()
    vehicle_type.vehicle_mode = VehicleModeEnumeration.WATER
    setIdVersion(vehicle_type, codespace, "Waddentaxi", None)
    vehicle_type.type_of_fuel = TypeOfFuelEnumeration.DIESEL
    vehicle_type.passenger_capacity = PassengerCapacityStructure(total_capacity=12)
    vehicle_type.name = "Waddentaxi"
    service_facility_set = ServiceFacilitySet()
    setIdVersion(service_facility_set, codespace, "Waddentaxi", None)
    vehicle_types.append(vehicle_type)

    return vehicle_types

def getVehicles(codespace: Codespace) -> list[Vehicle]:
    vehicles = []

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Vlamingh", None)
    vehicle.name = "Ms Willem de Vlamingh"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:LNG", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Barentsz", None)
    vehicle.name = "Ms Willem Barentsz"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:LNG", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Friesland", None)
    vehicle.name = "Ms Friesland"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Friesland", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Vlieland", None)
    vehicle.name = "Ms Vlieland"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Vlieland", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Koegelwieck", None)
    vehicle.name = "Ms Koegelwieck"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Koegelwieck", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Tiger", None)
    vehicle.name = "Ms Tiger"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Tiger", version="any")
    vehicles.append(vehicle)

    vehicle = Vehicle()
    setIdVersion(vehicle, codespace, "Zeehond", None)
    vehicle.name = "Ms Zeehond"
    vehicle.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Waddentaxi", version="any")
    vehicles.append(vehicle)
    return vehicles

def getResourceFrame(codespace: Codespace, version: Version,
                     operational_context: OperationalContext,
                     data_source: DataSource,
                     responsibility_set: ResponsibilitySet,
                     transport_administrative_zone: TransportAdministrativeZone,
                     operator: Operator) -> ResourceFrame:
    resource_frame = ResourceFrame()
    setIdVersion(resource_frame, codespace, "ResourceFrame", version)
    resource_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_RESOURCE", version="9.2.3")
    resource_frame.data_sources = DataSourcesInFrameRelStructure(data_source=[data_source])
    resource_frame.responsibility_sets = ResponsibilitySetsInFrameRelStructure(responsibility_set=[responsibility_set])
    resource_frame.zones = ZonesInFrameRelStructure(transport_administrative_zone=[transport_administrative_zone])
    resource_frame.organisations = OrganisationsInFrameRelStructure(operator=[operator])
    resource_frame.operational_contexts = OperationalContextsInFrameRelStructure(operational_context=[operational_context])
    resource_frame.vehicle_types = VehicleTypesInFrameRelStructure(compound_train_or_train_or_vehicle_type=getVehicleTypes(codespace))
    resource_frame.vehicles = VehiclesInFrameRelStructure(train_element_or_vehicle=getVehicles(codespace))

    return resource_frame

def getOperationalContext(codespace: Codespace) -> OperationalContext:
    operational_context = OperationalContext()
    setIdVersion(operational_context, codespace, "WATER", None)
    operational_context.vehicle_mode = AllModesEnumeration.WATER
    return operational_context

def getLine(codespace: Codespace, version: Version) -> Line1:
    accessibility_assessment = AccessibilityAssessment(mobility_impaired_access=LimitationStatusEnumeration.TRUE)
    setIdVersion(accessibility_assessment, codespace, "DOEKSEN", version)

    line = Line1(name=MultilingualString("Harlingen - Terschelling - Vlieland"),
                 transport_mode=AllVehicleModesOfTransportEnumeration.WATER,
                 type_of_service_ref=TypeOfServiceRef(ref="BISON:TypeOfService:Standaard"),
                 monitored=False,
                 accessibility_assessment=accessibility_assessment
                 )
    setIdVersion(line, codespace, "DOEKSEN", version)
    return line

def getIndex(l):
    return {x.id:x for x in l }

def getJourneyPatterns(codespace: Codespace, version: Version, routes: list[Route1],
                       destination_displays: list[DestinationDisplay],
                       scheduled_stop_points: list[ScheduledStopPoint],
                       timing_links: list[TimingLink]) -> list[ServiceJourneyPattern]:

    routes = getIndex(routes)
    destination_displays = getIndex(destination_displays)
    scheduled_stop_points = getIndex(scheduled_stop_points)
    timing_links = getIndex(timing_links)

    journey_patterns = []
    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:HT'], RouteRef),
                          destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Terschelling'], DestinationDisplayRef),
                          points_in_sequence=PointsInJourneyPatternRelStructure(point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'], ScheduledStopPointRef),
                                                        onward_timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HT']),
                                                        order=1),
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                  ScheduledStopPointRef),
                                  order=2)
                          ]))
    setIdVersion(service_journey_pattern, codespace, "HT", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:VT'], RouteRef),
                          destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Terschelling'], DestinationDisplayRef),
                          points_in_sequence=PointsInJourneyPatternRelStructure(point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'], ScheduledStopPointRef),
                                                        onward_timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VT']),
                                                        order=1),
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                  ScheduledStopPointRef),
                                  order=2)
                          ]))
    setIdVersion(service_journey_pattern, codespace, "VT", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:TV'], RouteRef),
                          destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Vlieland'], DestinationDisplayRef),
                          points_in_sequence=PointsInJourneyPatternRelStructure(point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], ScheduledStopPointRef),
                                                        onward_timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:TV']),
                                                        order=1),
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                  ScheduledStopPointRef),
                                  order=2)
                          ]))
    setIdVersion(service_journey_pattern, codespace, "TV", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:HV'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Vlieland'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:HV']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))
    setIdVersion(service_journey_pattern, codespace, "HV", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:TH'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Harlingen'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:TH']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "TH", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:VH'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Harlingen'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:VH']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "VH", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:HTV'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:VlielandTerschelling'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:HT']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points[
                                                                    'DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                ScheduledStopPointRef),
                                                                is_wait_point=True,
                                                                onward_timing_link_ref=getRef(
                                                                    timing_links['DOEKSEN:TimingLink:TV']),
                                                                order=2),

                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                    ScheduledStopPointRef),
                                                                order=3)
                                                        ]))
    setIdVersion(service_journey_pattern, codespace, "HTV", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:VHT'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays[
                                                                                       'DOEKSEN:DestinationDisplay:TerschellingHarlingen'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points[
                                                                    'DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                ScheduledStopPointRef),
                                                                onward_timing_link_ref=getRef(
                                                                    timing_links['DOEKSEN:TimingLink:VT']),
                                                                order=1),
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points[
                                                                    'DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                ScheduledStopPointRef),
                                                                is_wait_point=True,
                                                                onward_timing_link_ref=getRef(
                                                                    timing_links['DOEKSEN:TimingLink:HT']),
                                                                order=2),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points[
                                                                        'DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                    ScheduledStopPointRef),
                                                                order=3)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "VTH", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:TVH'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays[
                                                                                       'DOEKSEN:DestinationDisplay:HarlingenVlieland'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points[
                                                                    'DOEKSEN:ScheduledStopPoint:Terschelling'],
                                                                ScheduledStopPointRef),
                                                                onward_timing_link_ref=getRef(
                                                                    timing_links['DOEKSEN:TimingLink:TV']),
                                                                order=1),
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points[
                                                                    'DOEKSEN:ScheduledStopPoint:Vlieland'],
                                                                ScheduledStopPointRef),
                                                                is_wait_point=True,
                                                                onward_timing_link_ref=getRef(
                                                                    timing_links['DOEKSEN:TimingLink:VH']),
                                                                order=2),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points[
                                                                        'DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                                    ScheduledStopPointRef),
                                                                order=3)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "TVH", version)
    journey_patterns.append(service_journey_pattern)


    # Waddentaxi

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:HTX'], RouteRef),
                          destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Terschelling'], DestinationDisplayRef),
                          points_in_sequence=PointsInJourneyPatternRelStructure(point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                              StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'], ScheduledStopPointRef),
                                                        onward_timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HTX']),
                                                        order=1),
                              StopPointInJourneyPattern(
                                  scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'],
                                                                  ScheduledStopPointRef),
                                  order=2)
                          ]))

    setIdVersion(service_journey_pattern, codespace, "HTX", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:HVX'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Vlieland'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:HVX']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "HVX", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:THX'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Harlingen'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:THX']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "THX", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:VHX'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Harlingen'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:VHX']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "VHX", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:TVX'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Vlieland'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:TVX']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "TVX", version)
    journey_patterns.append(service_journey_pattern)

    service_journey_pattern = ServiceJourneyPattern(route_ref=getRef(routes['DOEKSEN:Route:VTX'], RouteRef),
                                                    destination_display_ref=getRef(destination_displays['DOEKSEN:DestinationDisplay:Terschelling'],
                                                                                   DestinationDisplayRef),
                                                    points_in_sequence=PointsInJourneyPatternRelStructure(
                                                        point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=[
                                                            StopPointInJourneyPattern(scheduled_stop_point_ref=getRef(
                                                                scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'],
                                                                ScheduledStopPointRef),
                                                                                      onward_timing_link_ref=getRef(
                                                                                          timing_links['DOEKSEN:TimingLink:VTX']),
                                                                                      order=1),
                                                            StopPointInJourneyPattern(
                                                                scheduled_stop_point_ref=getRef(
                                                                    scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'],
                                                                    ScheduledStopPointRef),
                                                                order=2)
                                                        ]))

    setIdVersion(service_journey_pattern, codespace, "VTX", version)
    journey_patterns.append(service_journey_pattern)

    idx = 1
    for jp in journey_patterns:
        for spinjp in jp.points_in_sequence.point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern:
            setIdVersion(spinjp, codespace, str(idx), version)
            idx += 1

    return journey_patterns

def getRouteLinks(codespace: Codespace, version: Version, route_points: list[RoutePoint], operational_context_ref: OperationalContextRef) -> list[RouteLink]:
    route_points = getIndex(route_points)

    route_links = []
    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "HT", version)
    route_links.append(route_link)

    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "HV", version)
    route_links.append(route_link)

    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "TV", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "TH", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "VH", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "VT", version)
    route_links.append(route_link)

    # Waddentaxi

    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "HTX", version)
    route_links.append(route_link)

    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "HVX", version)
    route_links.append(route_link)

    route_link = RouteLink(from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRefStructure),
                             to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "TVX", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "THX", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "VHX", version)
    route_links.append(route_link)

    route_link = RouteLink(to_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRefStructure),
                             from_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRefStructure),
                           operational_context_ref=operational_context_ref)
    setIdVersion(route_link, codespace, "VTX", version)
    route_links.append(route_link)

    return route_links


def getTimingLinks(codespace: Codespace, version: Version, scheduled_stop_points: list[ScheduledStopPoint]) -> list[TimingLink]:
    scheduled_stop_points = getIndex(scheduled_stop_points)

    timing_links = []
    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "HT", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "HV", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "TV", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "TH", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "VH", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "VT", version)
    timing_links.append(timing_link)

    # Waddentaxi

    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "HTX", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "HVX", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'], TimingPointRefStructure),
                             to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "TVX", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "THX", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:HarlingenTaxi'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "VHX", version)
    timing_links.append(timing_link)

    timing_link = TimingLink(to_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:TerschellingTaxi'], TimingPointRefStructure),
                             from_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:VlielandTaxi'], TimingPointRefStructure))
    setIdVersion(timing_link, codespace, "VTX", version)
    timing_links.append(timing_link)

    return timing_links

def getRoutes(codespace: Codespace, version: Version, line: Line1,
              route_points: list[RoutePoint],
              route_links: list[RouteLink]) -> list[Route1]:
    routes = []
    route_points = getIndex(route_points)
    route_links = getIndex(route_links)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HT-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HT'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HT-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "HT", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VT-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VT'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VT-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "VT", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TV-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VT'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TV-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "TV", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HV-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HV'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HV-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "HV", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TH-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:TH'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TH-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "TH", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VH-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VH'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VH-1", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "VH", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HTV-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HT'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HTV-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:TV'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HTV-3", version=version.version,
                                    order=3, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "HTV", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VHT-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VH'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VHT-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HT'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VHT-3", version=version.version,
                                    order=3, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "VHT", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TVH-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Terschelling'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:TV'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TVH-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Vlieland'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VH'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TVH-3", version=version.version,
                                    order=3, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:Harlingen'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "TVH", version)
    routes.append(route)


    # Waddentaxi

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HTX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HTX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HTX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "HTX", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HVX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:HVX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:HVX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "HVX", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:THX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:THX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:THX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "THX", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VHX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VHX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VHX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:HarlingenTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "VHX", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TVX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:TVX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:TVX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "TVX", version)
    routes.append(route)

    route = Route1(line_ref=getRef(line, LineRef),
                   points_in_sequence=PointsOnRouteRelStructure(point_on_route=[
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VTX-1", version=version.version,
                                    order=1, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:VlielandTaxi'], RoutePointRef),
                                    onward_route_link_ref=getRef(route_links['DOEKSEN:RouteLink:VTX'], RouteLinkRefStructure)),
                       PointOnRoute(id="DOEKSEN:PointOnRoute:VTX-2", version=version.version,
                                    order=2, route_point_ref=getRef(route_points['DOEKSEN:RoutePoint:TerschellingTaxi'], RoutePointRef))
                   ]))
    setIdVersion(route, codespace, "VTX", version)
    routes.append(route)

    return routes

def getDestinationDisplay(codespace: Codespace, version: Version) -> list[DestinationDisplay]:
    destination_displays = []

    text = MultilingualString("Harlingen")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text)
    setIdVersion(destination_display, codespace, "Harlingen", version)
    destination_displays.append(destination_display)

    text = MultilingualString("Harlingen")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text, vias=ViasRelStructure(none_or_via=[ViaVersionedChildStructure(name=MultilingualString("Vlieland"))]))
    setIdVersion(destination_display, codespace, "HarlingenVlieland", version)
    destination_displays.append(destination_display)


    text = MultilingualString("Terschelling")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text)
    setIdVersion(destination_display, codespace, "Terschelling", version)
    destination_displays.append(destination_display)

    text = MultilingualString("Terschelling")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text, vias=ViasRelStructure(none_or_via=[ViaVersionedChildStructure(name=MultilingualString("Harlingen"))]))
    setIdVersion(destination_display, codespace, "TerschellingHarlingen", version)
    destination_displays.append(destination_display)


    text = MultilingualString("Vlieland")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text)
    setIdVersion(destination_display, codespace, "Vlieland", version)
    destination_displays.append(destination_display)

    text = MultilingualString("Vlieland")
    destination_display = DestinationDisplay(name=text, front_text=text, side_text=text, vias=ViasRelStructure(none_or_via=[ViaVersionedChildStructure(name=MultilingualString("Terschelling"))]))
    setIdVersion(destination_display, codespace, "VlielandTerschelling", version)
    destination_displays.append(destination_display)

    return destination_displays

def getTimeDemandTypes(codespace: Codespace, version: Version, scheduled_stop_points: list[ScheduledStopPoint], timing_links: list[TimingLink]) -> list[TimeDemandType]:
    timing_links = getIndex(timing_links)
    scheduled_stop_points = getIndex(scheduled_stop_points)
    time_demand_types = []
    time_demand_type = TimeDemandType(run_times=JourneyRunTimesRelStructure(journey_run_time=[
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Veerdienst-TH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:TH'], TimingLinkRef),
                       run_time=XmlDuration("PT115M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Veerdienst-HT", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HT'], TimingLinkRef),
                       run_time=XmlDuration("PT115M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Veerdienst-VH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VH'], TimingLinkRef),
                       run_time=XmlDuration("PT95M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Veerdienst-HV", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HV'], TimingLinkRef),
                       run_time=XmlDuration("PT95M"))
    ]))
    setIdVersion(time_demand_type, codespace, "Veerdienst", version)
    time_demand_types.append(time_demand_type)


    time_demand_type = TimeDemandType(run_times=JourneyRunTimesRelStructure(journey_run_time=[
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-TH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HT'], TimingLinkRef),
                       run_time=XmlDuration("PT50M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-HT", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HT'], TimingLinkRef),
                       run_time=XmlDuration("PT50M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-VH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VH'], TimingLinkRef),
                       run_time=XmlDuration("PT45M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-HV", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HV'], TimingLinkRef),
                       run_time=XmlDuration("PT45M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-VT", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VT'], TimingLinkRef),
                       run_time=XmlDuration("PT30M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Sneldienst-TV", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:TV'], TimingLinkRef),
                       run_time=XmlDuration("PT30M"))
    ]), wait_times=JourneyWaitTimesRelStructure(journey_wait_time=[
        JourneyWaitTime(id="DOEKSEN:JourneyWaitTime:Sneldienst-Terschelling", version=version.version,
                        scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Terschelling'], ScheduledStopPointRef),
                        wait_time=XmlDuration("PT10M")),
        JourneyWaitTime(id="DOEKSEN:JourneyWaitTime:Sneldienst-Vlieland", version=version.version,
                        scheduled_stop_point_ref = getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Vlieland'],
                                          ScheduledStopPointRef),
                                   wait_time = XmlDuration("PT5M")),
        JourneyWaitTime(id="DOEKSEN:JourneyWaitTime:Sneldienst-Harlingen", version=version.version,
                        scheduled_stop_point_ref=getRef(scheduled_stop_points['DOEKSEN:ScheduledStopPoint:Harlingen'],
                                                        ScheduledStopPointRef),
                        wait_time=XmlDuration("PT20M"))

    ]))
    setIdVersion(time_demand_type, codespace, "Sneldienst", version)
    time_demand_types.append(time_demand_type)

    time_demand_type = TimeDemandType(run_times=JourneyRunTimesRelStructure(journey_run_time=[
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-TH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:TH'], TimingLinkRef),
                       run_time=XmlDuration("PT60M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-HT", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HT'], TimingLinkRef),
                       run_time=XmlDuration("PT60M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-VH", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VH'], TimingLinkRef),
                       run_time=XmlDuration("PT60M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-HV", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:HV'], TimingLinkRef),
                       run_time=XmlDuration("PT60M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-VT", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:VT'], TimingLinkRef),
                       run_time=XmlDuration("PT25M")),
        JourneyRunTime(id="DOEKSEN:JourneyRunTime:Waddentaxi-TV", version=version.version,
                       timing_link_ref=getRef(timing_links['DOEKSEN:TimingLink:TV'], TimingLinkRef),
                       run_time=XmlDuration("PT25M"))
    ]))
    setIdVersion(time_demand_type, codespace, "Waddentaxi", version)
    time_demand_types.append(time_demand_type)

    return time_demand_types

# def getStopAssignments(codespace: Codespace, version: Version):

def getScheduledStopPointsAndRoutePoints(codespace: Codespace, version: Version): # -> tuple(list[ScheduledStopPoint], list[RoutePoint]):
    scheduled_stop_points = []
    route_points = []

    location = LocationStructure2(pos=Pos(value=[156806, 576730], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "Harlingen", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Harlingen"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(choice = [PointProjection(
                                 id="DOEKSEN:PointProjection:Harlingen", version=version.version,
                                 project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "Harlingen", version)
    scheduled_stop_points.append(ssp)

    location = LocationStructure2(pos=Pos(value=[134233, 589994], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "Vlieland", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Vlieland"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(
                                 choice=[PointProjection(id="DOEKSEN:PointProjection:Vlieland", version=version.version,
                                                         project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "Vlieland", version)
    scheduled_stop_points.append(ssp)

    location = LocationStructure2(pos=Pos(value=[143673, 596727], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "Terschelling", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Terschelling"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(
                                 choice=[PointProjection(id="DOEKSEN:PointProjection:Terschelling", version=version.version,
                                                         project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "Terschelling", version)
    scheduled_stop_points.append(ssp)


    # Waddentaxi

    location = LocationStructure2(pos=Pos(value=[156617, 576533], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "HarlingenTaxi", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Harlingen (Waddentaxi)"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(choice = [PointProjection(id="DOEKSEN:PointProjection:HarlingenTaxi", version=version.version,
                                                                                           project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "HarlingenTaxi", version)
    scheduled_stop_points.append(ssp)

    location = LocationStructure2(pos=Pos(value=[135246, 590040], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "VlielandTaxi", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Vlieland (Waddentaxi)"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(
                                 choice=[PointProjection(id="DOEKSEN:PointProjection:VlielandTaxi", version=version.version,
                                                         project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "VlielandTaxi", version)
    scheduled_stop_points.append(ssp)

    location = LocationStructure2(pos=Pos(value=[143453, 596687], srs_name="EPGS:28992", srs_dimension=2))
    route_point = RoutePoint(location=location)
    setIdVersion(route_point, codespace, "TerschellingTaxi", version)
    route_points.append(route_point)
    ssp = ScheduledStopPoint(name=MultilingualString("Terschelling (Waddentaxi)"), for_boarding=True, for_alighting=True,
                             projections=ProjectionsRelStructure(
                                 choice=[PointProjection(id="DOEKSEN:PointProjection:TerschellingTaxi", version=version.version,
                                                         project_to_point_ref=getRef(route_point, PointRefStructure))]),
                             location=location)
    setIdVersion(ssp, codespace, "TerschellingTaxi", version)
    scheduled_stop_points.append(ssp)



    return (scheduled_stop_points, route_points)

def getServiceFrame(codespace: Codespace, version: Version, operational_context: OperationalContext) -> ServiceFrame:
    service_frame = ServiceFrame()
    setIdVersion(service_frame, codespace, "ServiceFrame", version)
    service_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_SERVICE", version="9.2.3")

    operational_context_ref = getRef(operational_context, OperationalContextRef)

    # service_frame.route_links = RouteLinksInFrameRelStructure()
    # route_link = RouteLink(distance=1,
    #                       line_string=LineString(pos_or_point_property_or_pos_list=PosList()),
    #                        from_point_ref=RoutePointRefStructure(), to_point_ref=RoutePointRefStructure(),
    #                        operational_context_ref=operational_context_ref)
    # service_frame.route_links.route_link.append(route_link)

    line = getLine(codespace, version)
    service_frame.lines = LinesInFrameRelStructure()
    service_frame.lines.line.append(line)

    scheduled_stop_points, route_points = getScheduledStopPointsAndRoutePoints(codespace, version)
    timing_links = getTimingLinks(codespace, version, scheduled_stop_points)
    route_links = getRouteLinks(codespace, version, route_points, operational_context_ref)
    destination_displays = getDestinationDisplay(codespace, version)
    routes = getRoutes(codespace, version, line, route_points, route_links)

    service_frame.route_points = RoutePointsInFrameRelStructure(route_point=route_points)
    service_frame.scheduled_stop_points = ScheduledStopPointsInFrameRelStructure(scheduled_stop_point=scheduled_stop_points)
    service_frame.timing_links = TimingLinksInFrameRelStructure(timing_link=timing_links)
    service_frame.route_links = RouteLinksInFrameRelStructure(route_link=route_links)
    service_frame.destination_displays = DestinationDisplaysInFrameRelStructure(destination_display=destination_displays)
    service_frame.routes = RoutesInFrameRelStructure(route=routes)

    service_frame.journey_patterns = JourneyPatternsInFrameRelStructure(choice=getJourneyPatterns(codespace, version, routes, destination_displays, scheduled_stop_points, timing_links))
    service_frame.time_demand_types = TimeDemandTypesInFrameRelStructure(time_demand_type=getTimeDemandTypes(codespace, version, scheduled_stop_points, timing_links))

    return service_frame

def getServiceJourneyAndAvailabilityCondition(codespace: Codespace, version: Version) -> tuple:
    import gzip
    import csv

    agg_available = {}
    agg_service_journey = {}

    service_journeys = []

    with gzip.open("/tmp/doeksen-20211125.csv.gz", 'rt', newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            r_date, r_from, r_time, r_to, r_vehicletype, r_duration, r_available, r_price = row
            unique = hash('-'.join([r_from, r_time, r_to, r_vehicletype, r_duration]))
            if unique in agg_available:
                agg_available[unique].add(r_date)
            else:
                agg_available[unique] = {r_date}
                agg_service_journey[unique] = [r_from, r_time, r_to, r_vehicletype, r_duration]

    availability_conditions = []
    for unique, l in agg_available.items():
        from_date, to_date, valid_day_bits = getBitString(l)
        availability_condition = AvailabilityCondition(from_date=XmlDateTime.from_datetime(datetime.datetime.combine(from_date, datetime.datetime.min.time())),
                                                       to_date=XmlDateTime.from_datetime(datetime.datetime.combine(to_date, datetime.datetime.min.time())),
                                                       valid_day_bits=valid_day_bits)
        setIdVersion(availability_condition, codespace, unique, version)
        availability_conditions.append(availability_condition)

    for unique, (r_from, r_time, r_to, r_vehicletype, r_duration) in agg_service_journey.items():
        if '(via ' in r_vehicletype:
            continue
        
        service_journey = ServiceJourney1()
        setIdVersion(service_journey, codespace, unique, version)
        tdt = r_vehicletype
        if r_vehicletype == 'Waddentaxi Ms. Zeehond':
            tdt = 'Waddentaxi'

        service_journey.validity_conditions_or_valid_between = ValidityConditionsRelStructure(choice=AvailabilityConditionRef(ref="DOEKSEN:AvailabilityCondition:{}".format(unique), version=version.version))
        service_journey.departure_time = XmlTime.from_string(r_time + ':00')
        service_journey.time_demand_type_ref = TimeDemandTypeRefStructure(ref="DOEKSEN:TimeDemandType:{}".format(tdt) , version=version.version)

        if r_vehicletype == 'Waddentaxi Ms. Zeehond':
            service_journey.vehicle_type_ref = VehicleTypeRef(ref="DOEKSEN:VehicleType:Waddentaxi", version="any")
            service_journey.accessibility_assessment = AccessibilityAssessment(mobility_impaired_access=LimitationStatusEnumeration.FALSE)
            service_journey.service_journey_pattern_ref = ServiceJourneyPatternRef(ref="DOEKSEN:ServiceJourneyPattern:{}{}X".format(r_from[0], r_to[0]), version=version.version)
        else:
            service_journey.service_journey_pattern_ref = ServiceJourneyPatternRef(ref="DOEKSEN:ServiceJourneyPattern:{}{}".format(r_from[0], r_to[0]), version=version.version)
            service_journey.accessibility_assessment = AccessibilityAssessment(mobility_impaired_access=LimitationStatusEnumeration.TRUE)
        setIdVersion(service_journey.accessibility_assessment, codespace, unique, version)

        service_journeys.append(service_journey)

    service_journeys =  sorted(service_journeys, key=lambda x: x.departure_time)

    return service_journeys, availability_conditions

def getTimetableFrame(codespace: Codespace, version: Version, operator: Operator) -> TimetableFrame:
    timetable_frame = TimetableFrame()
    setIdVersion(timetable_frame, codespace, "Timetable", version)
    timetable_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_TIMETABLE", version="9.2.3")
    timetable_frame.operator_view = OperatorView(operator_ref=getRef(operator, OperatorRef))

    service_journeys, availabilityconditions = getServiceJourneyAndAvailabilityCondition(codespace, version)

    timetable_frame.vehicle_journeys = JourneysInFrameRelStructure(choice=service_journeys)
    timetable_frame.content_validity_conditions = ValidityConditionsRelStructure(choice=availabilityconditions)

    return timetable_frame

def getCompositeFrame(codespace: Codespace, version: Version) -> CompositeFrame:
    operational_context = getOperationalContext(codespace)
    data_source = getDataSource(codespace)
    transport_administrative_zone = getTransportAdministrativeZone(codespace)
    responsibility_set = getResponsibilitySet(codespace, transport_administrative_zone)

    operator = getOperator(codespace)

    composite_frame = CompositeFrame()
    setIdVersion(composite_frame, codespace, "Timetable", version)
    composite_frame.frame_defaults = getFrameDefaults(codespace, data_source, responsibility_set)
    composite_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_BASELINE", version="9.2.3")
    composite_frame.versions = VersionsRelStructure(version_ref_or_version=[version])
    composite_frame.codespaces = CodespacesRelStructure(codespace_ref_or_codespace=[codespace])
    composite_frame.frames = FramesRelStructure(resource_frame=[getResourceFrame(codespace, version, operational_context, data_source, responsibility_set, transport_administrative_zone, operator)],
                                                service_frame=[getServiceFrame(codespace, version, operational_context)],
                                                timetable_frame=[getTimetableFrame(codespace, version, operator)])

    return composite_frame

def getVersion(codespace: Codespace, version_version: datetime.date, start_date: datetime.date, end_date: datetime.time) -> Version:
    version = Version(start_date=XmlDateTime.from_datetime(start_date), end_date=XmlDateTime.from_datetime(end_date), version_type=VersionTypeEnumeration.BASELINE)
    version.version = version_version.strftime("%Y%m%d")
    setIdVersion(version, codespace, version.version, version)
    return version

def getPublicationDelivery(codespace: Codespace, version: Version) -> PublicationDelivery:
    composite_frame = getCompositeFrame(codespace, version)

    publication_delivery = PublicationDelivery(publication_timestamp=XmlDateTime.from_datetime(datetime.datetime.now()))
    publication_delivery.participant_ref = "NDOV"
    publication_delivery.description = "NeTEx export"
    publication_delivery.data_objects = DataObjectsRelStructure(choice=[composite_frame])

    return publication_delivery



start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
end_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
codespace = Codespace(id="BISON:Codespace:DOEKSEN", xmlns="DOEKSEN")
version = getVersion(codespace, datetime.date.today(), start_date, end_date)
publication_delivery = getPublicationDelivery(codespace, version)

serializer_config = SerializerConfig(ignore_default_attributes=True)
serializer_config.pretty_print = True
serializer = XmlSerializer(serializer_config)

ns_map = {'': 'http://www.netex.org.uk/netex', 'gml': 'http://www.opengis.net/gml/3.2'}

with open('/tmp/out.xml', 'w') as out:
    serializer.write(out, publication_delivery, ns_map)
