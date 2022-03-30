import datetime
import math

import psycopg2, psycopg2.extras
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime, XmlTime

from callsprofile import CallsProfile
from netex import Codespace, DataSource, MultilingualString, Version, VersionFrameDefaultsStructure, \
    VersionTypeEnumeration, LocaleStructure, SystemOfUnits, Operator, ContactStructure, Locale, LanguageUsageStructure, \
    LanguageUseEnumeration, Line, PresentationStructure, AllVehicleModesOfTransportEnumeration, PrivateCode, \
    PublicationDelivery, DataObjectsRelStructure, OperationalContext, ResourceFrame, TypeOfFrameRef, \
    DataSourcesInFrameRelStructure, OrganisationsInFrameRelStructure, OperationalContextsInFrameRelStructure, \
    CompositeFrame, VersionsRelStructure, FramesRelStructure, ServiceFrame, LinesInFrameRelStructure, \
    OperatorRefStructure, OperatorRef, StopArea, LocationStructure2, SimplePointVersionStructure, PrivateCodeStructure, \
    ScheduledStopPoint, StopTypeEnumeration, StopAreaRefsRelStructure, StopAreaRefStructure, \
    StopAreasInFrameRelStructure, ScheduledStopPointsInFrameRelStructure, AvailabilityCondition, ServiceJourneyPattern, \
    StopPointInJourneyPattern, DestinationDisplayView, ScheduledStopPointRef, Call, ArrivalStructure, \
    DepartureStructure, CallsRelStructure, ValidityConditionsRelStructure, AvailabilityConditionRef, BlockRef, \
    DirectionTypeEnumeration, AccessibilityAssessment, LimitationStatusEnumeration, TimetableFrame, \
    JourneysInFrameRelStructure, LineRef, JourneyPatternView, CodespacesRelStructure, \
    JourneyPatternsInFrameRelStructure, ServiceJourney, TimingLinksInFrameRelStructure, \
    TimeDemandTypesInFrameRelStructure, OnwardTimingLinkView, OnwardServiceLinkView, PathLink, RouteRef, Route, \
    RoutePoint, PointsOnRouteRelStructure, RoutePointRef, PointOnRoute, RoutePointsInFrameRelStructure, \
    RoutesInFrameRelStructure, RouteLink, RouteLinksInFrameRelStructure
from refs import setIdVersion, getRef, getIndex, getIdByRef, getBitString2, getFakeRef, getOptionalString


class GtfsNeTexProfile(CallsProfile):
    @staticmethod
    def getShortName(name: str):
        if len(name) > 8:
            return ''.join([x[0].upper() for x in name.split(' ')])
        return name

    def getCodespaceAndDataSource(self) -> (Codespace, DataSource, Version, VersionFrameDefaultsStructure):
        feed_info_sql = """select * from feed_info limit 1;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(feed_info_sql)
            for row in cur.fetchall():
                short_name = self.getShortName(row['feed_publisher_name'])
                codespace = Codespace(id="{}:Codespace:{}".format(short_name, short_name), xmlns=short_name,
                                      xmlns_url=row['feed_publisher_url'], description=row['feed_publisher_name'])
                data_source = DataSource(name=MultilingualString(row['feed_publisher_name']),
                                         short_name=MultilingualString(short_name),
                                         description=MultilingualString(row['feed_publisher_name']))
                setIdVersion(data_source, codespace, short_name, None)

                start_date = datetime.datetime.combine(row['feed_start_date'], datetime.datetime.min.time())
                end_date = datetime.datetime.combine(row['feed_end_date'], datetime.datetime.min.time())

                version = Version(start_date=XmlDateTime.from_datetime(start_date),
                                  end_date=XmlDateTime.from_datetime(end_date),
                                  version_type=VersionTypeEnumeration.BASELINE)
                version.version = row['feed_version']
                setIdVersion(version, codespace, version.version, version)

                frame_defaults = VersionFrameDefaultsStructure(default_codespace_ref=getRef(codespace),
                                                               default_data_source_ref=getRef(data_source),
                                                               default_locale=LocaleStructure(default_language=row['feed_lang']),
                                                               default_location_system="EPSG:4326",
                                                               default_system_of_units=SystemOfUnits.SI_METRES
                                                               )

                return (codespace, data_source, version, frame_defaults)

    def getResourceFrame(self) -> ResourceFrame:
        resource_frame = ResourceFrame()
        setIdVersion(resource_frame, self.codespace, "ResourceFrame", self.version)
        resource_frame.data_sources = DataSourcesInFrameRelStructure(data_source=[self.data_source])
        # TODO: Zone information can be obtained from stops.txt
        # resource_frame.zones = ZonesInFrameRelStructure(transport_administrative_zone=[transport_administrative_zone])
        resource_frame.organisations = OrganisationsInFrameRelStructure(operator=self.operators)
        resource_frame.operational_contexts = OperationalContextsInFrameRelStructure(
            operational_context=self.getOperationalContexts())
        # resource_frame.vehicle_types = VehicleTypesInFrameRelStructure(compound_train_or_train_or_vehicle_type=getVehicleTypes(codespace))
        # resource_frame.vehicles = VehiclesInFrameRelStructure(train_element_or_vehicle=getVehicles(codespace))
        return resource_frame

    def getOperators(self) -> list[Operator]:
        feed_info_sql = """select * from agency;"""
        results = []

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(feed_info_sql)
            for row in cur.fetchall():
                operator = Operator(name=MultilingualString(row['agency_name']),
                                    locale=Locale(time_zone=row['agency_timezone'],
                                                  languages=LocaleStructure.Languages(language_usage=[LanguageUsageStructure(language=row['agency_lang'],
                                                                                                                             language_use=[LanguageUseEnumeration.NORMALLY_USED])])),
                                    customer_service_contact_details=ContactStructure(url=row['agency_url'], phone=row['agency_phone'], email=row['agency_email']))
                setIdVersion(operator, self.codespace, row['agency_id'], None)
                results.append(operator)

        return results

    @staticmethod
    def gtfsToNeTEx(otp_type: str):
        if otp_type == 'SUBWAY':
            otp_type = 'METRO'
        elif otp_type == 'FERRY':
            otp_type = 'WATER'
        elif otp_type == 'CABLE_CAR':
            otp_type = 'FUNICULAR'
        elif otp_type == 'GONDOLA':
            otp_name = 'CABLEWAY'
        return AllVehicleModesOfTransportEnumeration[otp_type]

    def getOperationalContexts(self) -> list[OperationalContext]:
        operational_contexts = []

        operational_contexts_sql = """select distinct route_type, otp_type from routes join route_type using (route_type);"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(operational_contexts_sql)
            for row in cur.fetchall():
                operational_context = OperationalContext()
                setIdVersion(operational_context, self.codespace, row['route_type'], None)
                operational_context.vehicle_mode = self.gtfsToNeTEx(row['otp_type'])
                operational_contexts.append(operational_context)

        return operational_contexts

    def getLines(self) -> list[Line]:
        operators = getIndex(self.operators)

        lines = []

        lines_sql = """select routes.*, otp_type from routes join route_type using (route_type) order by route_sort_order;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(lines_sql)
            for row in cur.fetchall():
                presentation = None
                if row['route_color'] is not None or row['route_color_text'] is not None:
                    presentation = PresentationStructure(colour=row['route_color'], text_colour=row['route_text_color'],
                                                         background_colour=row['route_color'])

                line = Line(name=MultilingualString(row['route_long_name']),
                             short_name=getOptionalString(row['route_short_name']),
                             description=getOptionalString(row['route_desc']),
                             transport_mode=self.gtfsToNeTEx(row['otp_type']),
                             presentation=presentation,
                             url=row['route_url'],
                             operator_ref=getRef(operators[getIdByRef(Operator(), self.codespace, row['agency_id'])], OperatorRef),
                             public_code=row['route_short_name'],
                             private_code=PrivateCode(value=row['route_id'], type="route_id")
                             )
                setIdVersion(line, self.codespace, row['route_id'], self.version)
                lines.append(line)

        return lines

    def getStopAreas(self) -> list[StopArea]:
        stop_areas = []

        stop_area_sql = """select * from stops where location_type = 1 order by stop_id;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(stop_area_sql)
            for row in cur.fetchall():
                location = LocationStructure2(latitude=row['stop_lat'], longitude=row['stop_lon'], srs_name="EPSG:4326")
                stop_area = StopArea(name=MultilingualString(row['stop_name']), public_code=row['stop_code'],
                                     description=getOptionalString(row['stop_desc']),
                                     private_code=PrivateCode(value=row['stop_id'], type="stop_id"),
                                     centroid=SimplePointVersionStructure(location=location),
                                     )
                setIdVersion(stop_area, self.codespace, row['stop_id'], self.version)
                stop_areas.append(stop_area)

        return stop_areas

    def getScheduledStopPoints(self) -> list[ScheduledStopPoint]:
        stop_areas = getIndex(self.stop_areas)

        scheduled_stop_points = []
        passenger_stop_assignments = []

        scheduled_stop_points_sql = """select * from stops where location_type = 0 or location_type is null order by stop_id;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(scheduled_stop_points_sql)
            for row in cur.fetchall():
                short_stop_code = None
                if row['platform_code'] is not None:
                    short_stop_code = PrivateCodeStructure(value=row['platformcode'])

                location = LocationStructure2(longitude=row['stop_lon'], latitude=row['stop_lat'], srs_name="EPSG:4326")

                stop_areas = None
                if row['parent_station'] is not None:
                    stop_area_ref = getIdByRef(StopArea(), self.codespace, row['parent_station'])
                    stop_areas = StopAreaRefsRelStructure(stop_area_ref=[
                        getRef(stop_areas[stop_area_ref], StopAreaRefStructure)])


                scheduled_stop_point = ScheduledStopPoint(name=MultilingualString(row['stop_name']),
                                                          description=getOptionalString(row['stop_desc']),
                                                          private_code=PrivateCode(value=row['stop_id'],
                                                                                   type="stop_id"),
                                                          short_stop_code=short_stop_code,
                                                          public_code=row['stop_code'],
                                                          url=row['stop_url'],
                                                          location=location,
                                                          stop_areas=stop_areas)
                setIdVersion(scheduled_stop_point, self.codespace, row['stop_id'], self.version)
                scheduled_stop_points.append(scheduled_stop_point)

                """
                stop_place_ref = None
                if row['stopplacecoderef'] is not None:
                    stop_place_ref = getFakeRef(row['stopplacecoderef'], StopPlaceRef, "any")

                quay_ref = None
                if row['quaycoderef'] is not None:
                    quay_ref = getFakeRef(row['quaycoderef'], QuayRef, "any")

                if stop_place_ref is not None or quay_ref is not None:
                    passenger_stop_assignment = PassengerStopAssignment(
                        scheduled_stop_point_ref=getRef(scheduled_stop_point, ScheduledStopPointRef),
                        stop_place_ref=stop_place_ref,
                        quay_ref=quay_ref, order=1)
                    setIdVersion(passenger_stop_assignment, codespace, row['id'], version)
                    passenger_stop_assignments.append(passenger_stop_assignment)
                """

        return scheduled_stop_points

    def getPaths(self):
        pl = PathLink()


    def getRoutes(self) -> (list[Route], list[RoutePoint], list[RouteLink]):
        lines = getIndex(self.lines)

        shape_route_mapping = {}

        # Within NeTEx it is not possible to have a route (GTFS-shape) pointing to multiple lines (GTFS-route)
        shape_route_sql = """select distinct shape_id, array_agg(distinct route_id) as route_ids from trips group by shape_id;""";
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(shape_route_sql)
            for row in cur.fetchall():
                if len(row['route_ids']) > 0:
                    shape_route_mapping[row['shape_id']] = [(row['shape_id'] + '-' + x, x) for x in row['route_ids']]
                else:
                    shape_route_mapping[row['shape_id']] = [(row['shape_id'], None)]

        shape_sql = """select shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence, shape_dist_traveled from shapes order by shape_id, shape_pt_sequence, shape_dist_traveled;"""

        routes = {}
        route_points = []
        route_links = []

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(shape_sql)
            prev_order = 1
            prev_route = None
            prev_distance = 0
            prev_route_point = None
            prev_shape_id = None

            for row in cur.fetchall():
                route_point = RoutePoint(location=LocationStructure2(longitude=row['shape_pt_lon'], latitude=row['shape_pt_lat']))
                setIdVersion(route_point, self.codespace, "{}-{}".format(row['shape_id'], row['shape_pt_sequence']), self.version)
                route_points.append(route_point)

                if row['shape_id'] == prev_shape_id:
                    # It is the same route, and still being extended
                    distance = None
                    if row['shape_dist_traveled']:
                        distance = row['shape_dist_traveled'] - prev_distance

                    route_link = RouteLink(from_point_ref=getRef(prev_route_point),
                                           to_point_ref=getRef(route_point),
                                           distance=distance)
                    setIdVersion(route_link, self.codespace,
                                 "{}-{}".format(row['shape_id'], row['shape_pt_sequence']), self.version)
                    route_links.append(route_link)

                    for route in prev_route:
                        route.points_in_sequence.point_on_route[-1].onward_route_link_ref = getRef(route_link)

                else:
                    prew_order = 1
                    prev_route = []
                    prev_distance = 0
                    prev_route_point = None
                    prev_shape_id = None

                    route_ids = shape_route_mapping.get(row['shape_id'], [row['shape_id']])
                    for route_id, line_id in route_ids:
                        route = Route()
                        setIdVersion(route, self.codespace, route_id, self.version)
                        route.private_code = PrivateCode(value = row['shape_id'], type = "shape_id")
                        route.points_in_sequence = PointsOnRouteRelStructure()
                        if line_id:
                            line = lines[getIdByRef(Line(), self.codespace, line_id)]
                            route.line_ref = getRef(line, LineRef)

                        routes[route_id] = route
                        prev_route.append(route)

                for route in prev_route:
                    point_on_route = PointOnRoute(order=prev_order, route_point_ref=getRef(route_point, RoutePointRef)) # shape_pt_sequence is non-negative integer
                    setIdVersion(point_on_route, self.codespace, "{}-{}".format(route_id, row['shape_pt_sequence']), self.version)
                    route.points_in_sequence.point_on_route.append(point_on_route)

                prev_shape_id = row['shape_id']
                prev_route_point = route_point
                prev_distance = row['shape_dist_traveled']
                prev_order += 1

        return (list(routes.values()), route_points, route_links)

    def getServiceFrame(self) -> ServiceFrame:
        service_frame = ServiceFrame()
        # service_frame.prerequisites.resource_frame_ref
        setIdVersion(service_frame, self.codespace, "ServiceFrame", self.version)

        service_frame.lines = LinesInFrameRelStructure(line=self.lines)


        """
        destination_displays = getDestinationDisplays(codespace, version)
        stop_areas = getStopAreas(codespace, version)
        scheduled_stop_points, passenger_stop_assignments = getScheduledStopPoints(codespace, version, route_points,
                                                                                   stop_areas)
        service_journey_patterns, timing_links, service_journey_patterns_transport_mode = getServiceJourneyPatterns(
            codespace, version, routes, lines, scheduled_stop_points, operational_contexts, destination_displays)

        service_journey_patterns = sorted(service_journey_patterns, key=lambda x: x.id)
        timing_links = sorted(timing_links, key=lambda x: x.id)
        """

        self.stop_areas = sorted(self.stop_areas, key=lambda x: x.id)
        self.scheduled_stop_points = sorted(self.scheduled_stop_points, key=lambda x: x.id)

        """
        destination_displays = sorted(destination_displays, key=lambda x: x.id)
        passenger_stop_assignments = sorted(passenger_stop_assignments, key=lambda x: x.id)

        """
        self.route_points = sorted(self.route_points, key=lambda x: x.id)
        service_frame.route_points = RoutePointsInFrameRelStructure(route_point=self.route_points)

        self.route_links = sorted(self.route_links, key=lambda x: x.id)
        service_frame.route_links = RouteLinksInFrameRelStructure(route_link=self.route_links)

        self.routes = sorted(self.routes, key=lambda x: x.id)
        service_frame.routes = RoutesInFrameRelStructure(route=self.routes)

        if self.stop_areas:
            service_frame.stop_areas = StopAreasInFrameRelStructure(stop_area=self.stop_areas)

        service_frame.scheduled_stop_points = ScheduledStopPointsInFrameRelStructure(
            scheduled_stop_point=self.scheduled_stop_points)

        if self.timing_links:
            service_frame.timing_links = TimingLinksInFrameRelStructure(timing_link=self.timing_links)

        if self.time_demand_types:
            self.time_demand_types = sorted(self.time_demand_types, key=lambda x: x.id)
            service_frame.time_demand_types = TimeDemandTypesInFrameRelStructure(time_demand_type=self.time_demand_types)

        """
        service_frame.destination_displays = DestinationDisplaysInFrameRelStructure(
            destination_display=destination_displays)
        service_frame.stop_assignments = StopAssignmentsInFrameRelStructure(
            passenger_stop_assignment=passenger_stop_assignments)
        """

        if self.service_journey_patterns:
            service_frame.journey_patterns = JourneyPatternsInFrameRelStructure(choice=self.service_journey_patterns)


        return service_frame

    def getAvailabilityConditions(self) -> list[AvailabilityCondition]:
        availability_conditions = []
        availability_condition_sql = """select service_id, array_agg(date) as positivedates from universal_calendar group by service_id;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(availability_condition_sql)
            for row in cur.fetchall():
                valid_day_bits = getBitString2(row['positivedates'], self.version.start_date.to_datetime().date(), self.version.end_date.to_datetime().date())
                availability_condition = AvailabilityCondition(from_date=self.version.start_date,
                                                               to_date=self.version.end_date,
                                                               valid_day_bits=valid_day_bits)
                setIdVersion(availability_condition, self.codespace, row['service_id'], self.version)
                availability_conditions.append(availability_condition)

        return availability_conditions

    @staticmethod
    def noonTimeToNeTEx(time: str):
        hour, minute, second = time.split(':')
        hour = int(hour)
        day_offset = int(math.floor(hour / 24))
        return (XmlTime(hour=hour % 24, minute=int(minute), second=int(second), microsecond=0), day_offset)

    @staticmethod
    def directionToNeTEx(direction_id: int):
        if direction_id is None:
            return None

        elif direction_id == 1:
            return DirectionTypeEnumeration.INBOUND

        return DirectionTypeEnumeration.OUTBOUND

    @staticmethod
    def wheelchairToNeTEx(wheelchair_accessible: int):
        if wheelchair_accessible == 0:
            return LimitationStatusEnumeration.UNKNOWN

        return LimitationStatusEnumeration.TRUE


    def getServiceJourneys(self) -> list[ServiceJourney]:
        routes = getIndex(self.routes, 'private_code.value')
        lines = getIndex(self.lines)
        availability_conditions = getIndex(self.availability_conditions)

        service_journeys = {}

        trips_sql = """select * from trips order by trip_id;"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(trips_sql)

            for row in cur.fetchall():
                line = lines[getIdByRef(Line(), self.codespace, row['route_id'])]
                availability_condition = availability_conditions[getIdByRef(AvailabilityCondition(), self.codespace, row['service_id'])]
                destination_display_view = None
                if row['trip_headsign']:
                    destination_display_view = DestinationDisplayView(name=MultilingualString(row['trip_headsign']),
                                                                      front_text=MultilingualString(
                                                                          row['trip_headsign']))

                accessibility_assessment = None
                if row['wheelchair_accessible']:
                    accessibility_assessment = AccessibilityAssessment(mobility_impaired_access=self.wheelchairToNeTEx(row['wheelchair_accessible']))
                    setIdVersion(accessibility_assessment, self.codespace, row['trip_id'], self.version)

                route_ref = None
                if row['shape_id']:
                    route_ref = getRef(routes[row['shape_id']], RouteRef)
                    # route_ref = getFakeRef(row['shape_id'], RouteRef, self.version.version)

                service_journey = ServiceJourney(line_ref=getRef(line, LineRef),
                                                  private_code=PrivateCode(value=row['trip_id'], type="trip_id"),
                                                  short_name=getOptionalString(row['trip_short_name']),
                                                  validity_conditions_or_valid_between=ValidityConditionsRelStructure(choice=[getRef(availability_condition, AvailabilityConditionRef)]),
                                                  route_ref=route_ref, # shape_id
                                                  journey_pattern_view=JourneyPatternView(destination_display_view=destination_display_view),
                                                  direction_type=self.directionToNeTEx(row['direction_id']),
                                                  block_ref=getFakeRef(row['block_id'], BlockRef, "any"),
                                                  accessibility_assessment=accessibility_assessment
                                                  )
                setIdVersion(service_journey, self.codespace, row['trip_id'], self.version)

                service_journeys[row['trip_id']] = service_journey

        scheduled_stop_points = getIndex(self.scheduled_stop_points)

        stop_times_sql = """select * from stop_times order by trip_id, stop_sequence;"""

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(stop_times_sql)
            trip_id = None
            service_journey = None
            prev_call = None
            prev_shape_traveled = 0
            prev_order = 1
            for row in cur.fetchall():
                if row['trip_id'] != trip_id:
                    trip_id = row['trip_id']
                    service_journey = service_journeys[trip_id]
                    service_journey.calls = CallsRelStructure()
                    prev_call = None
                    prev_shape_traveled = 0
                    prev_order = 1

                destination_display_view = None
                if row['stop_headsign']:
                    destination_display_view = DestinationDisplayView(name=MultilingualString(row['stop_headsign']),
                                                                      front_text=MultilingualString(
                                                                          row['stop_headsign']))

                from_point_ref = getIdByRef(ScheduledStopPoint(), self.codespace, row['stop_id'])
                from_ssp = scheduled_stop_points[from_point_ref]
                arrival_time, arrival_dayoffset = self.noonTimeToNeTEx(row['arrival_time'])
                departure_time, departure_dayoffset = self.noonTimeToNeTEx(row['departure_time'])

                if prev_call and row['shape_dist_traveled']:
                    distance = row['shape_dist_traveled'] - prev_shape_traveled
                    prev_call.onward_service_link_view = OnwardServiceLinkView(distance=distance)

                call = Call(scheduled_stop_point_ref=getRef(from_ssp, ScheduledStopPointRef),
                             destination_display_view=destination_display_view,
                             arrival=ArrivalStructure(time=arrival_time, day_offset=arrival_dayoffset,
                                                      for_alighting=(row['drop_off_type'] != 1)),
                             departure=DepartureStructure(time=departure_time, day_offset=departure_dayoffset,
                                                      for_boarding=(row['pickup_type'] != 1)),
                             request_stop=(row['pickup_type'] == 2 or row['pickup_type'] == 3 or row[
                                 'drop_off_type'] == 2 or row['drop_off_type'] == 3),
                             order=prev_order) # stop_sequence is non-negative integer
                setIdVersion(call, self.codespace, "{}:{}".format(row['trip_id'], row['stop_sequence']), self.version)

                service_journey.calls.call.append(call)

                prev_call = call
                prev_shape_traveled = row['shape_dist_traveled']
                prev_order += 1

        return list(service_journeys.values())


    def getTimetableFrame(self) -> TimetableFrame:
        timetable_frame = TimetableFrame()
        setIdVersion(timetable_frame, self.codespace, "Timetable", self.version)


        timetable_frame.vehicle_journeys = JourneysInFrameRelStructure(choice=self.service_journeys)
        timetable_frame.content_validity_conditions = ValidityConditionsRelStructure(choice=self.availability_conditions)

        return timetable_frame

    def getCompositeFrame(self) -> CompositeFrame:
        composite_frame = CompositeFrame()
        setIdVersion(composite_frame, self.codespace, self.data_source.short_name.value, self.version)
        composite_frame.frame_defaults = self.frame_defaults
        composite_frame.codespaces = CodespacesRelStructure(codespace_ref_or_codespace=[self.codespace])
        composite_frame.versions = VersionsRelStructure(version_ref_or_version=[self.version])
        composite_frame.frames = FramesRelStructure(resource_frame=[self.getResourceFrame()], service_frame=[self.getServiceFrame()], timetable_frame=[self.getTimetableFrame()])

        return composite_frame

    def getPublicationDelivery(self) -> PublicationDelivery:
        composite_frame = self.getCompositeFrame()

        publication_delivery = PublicationDelivery(
            publication_timestamp=XmlDateTime.from_datetime(datetime.datetime.now()))
        publication_delivery.version = "ntx:1.1"
        publication_delivery.participant_ref = "NDOV"
        publication_delivery.description = "NeTEx export"
        publication_delivery.data_objects = DataObjectsRelStructure(choice=[composite_frame])

        return publication_delivery

    def __init__(self, conn):
        self.conn = conn
        self.codespace, self.data_source, self.version, self.frame_defaults = self.getCodespaceAndDataSource()
        self.operators = self.getOperators()
        self.lines = self.getLines()
        self.routes, self.route_points, self.route_links = self.getRoutes()
        self.stop_areas = self.getStopAreas()
        self.scheduled_stop_points = self.getScheduledStopPoints()
        self.availability_conditions = self.getAvailabilityConditions()
        self.service_journeys = self.getServiceJourneys()
        self.service_journey_patterns, self.timing_links = self.getServiceJourneyPatterns()
        self.time_demand_types = self.getTimeDemandTypes()

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Convert a GTFS DB into a NeTEx file')
    parser.add_argument('--dbname', help='PostgreSQL database name', nargs="?")
    parser.add_argument('--user', help='PostgreSQL username', nargs="?")
    parser.add_argument('--password', help='PostgreSQL password', nargs="?")
    parser.add_argument('--host', help='PostgreSQL hostname', nargs="?")
    parser.add_argument('--output', help='NeTEx output filename', nargs="?")

    args = parser.parse_args()

    if not args.output:
        parser.print_help(sys.stderr)

    connection_string = ''
    if args.dbname:
        connection_string += f"dbname={args.dbname}"
    if args.user:
        connection_string += f" user={args.user}"
    if args.password:
        connection_string += f" password={args.password}"
    if args.host:
        connection_string += f" host={args.host}"

    serializer_config = SerializerConfig(ignore_default_attributes=True)
    serializer_config.pretty_print = True
    serializer = XmlSerializer(serializer_config)

    ns_map = {'': 'http://www.netex.org.uk/netex', 'gml': 'http://www.opengis.net/gml/3.2'}

    with open(args.output, 'w') as out:
        gtfs_netex = GtfsNeTexProfile(conn=psycopg2.connect(connection_string))
        serializer.write(out, gtfs_netex.getPublicationDelivery(), ns_map)
