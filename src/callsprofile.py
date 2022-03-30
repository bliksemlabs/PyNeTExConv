from xsdata.models.datatype import XmlDuration

from netex import StopPointInJourneyPattern, ServiceJourneyPattern, PointsInJourneyPatternRelStructure, \
    ServiceJourneyPatternRef, TimingLink, TimingPointRefStructure, TimingLinkRefStructure, TimingLinkRef, \
    DepartureStructure, ArrivalStructure, JourneyRunTime, JourneyWaitTime, \
    PointInJourneyPatternRefStructure, OnwardTimingLinkView, TimeDemandType, JourneyRunTimesRelStructure, \
    JourneyWaitTimesRelStructure, TimeDemandTypeRefStructure, RouteView, ServiceJourney, Codespace, Line, Route, \
    ScheduledStopPoint, Version

from refs import setIdVersion, getRef, getIndex

class CallsProfile:
    codespace: Codespace
    lines: list[Line]
    routes: list[Route]
    scheduled_stop_points: list[ScheduledStopPoint]
    service_journeys: list[ServiceJourney]
    version: Version

    @staticmethod
    def getRunTime(departure: DepartureStructure, arrival: ArrivalStructure) -> int:
        return ((arrival.day_offset or 0) * 86400 + arrival.time.hour * 3600 + arrival.time.minute * 60 + arrival.time.second) - ((departure.day_offset or 0) * 86400 + departure.time.hour * 3600 +  departure.time.minute * 60 + departure.time.second)

    @staticmethod
    def getWaitTime(arrival: ArrivalStructure, departure: DepartureStructure) -> int:
        return ((departure.day_offset or 0) * 86400 + departure.time.hour * 3600 +  departure.time.minute * 60 + departure.time.second) - ((arrival.day_offset or 0) * 86400 + arrival.time.hour * 3600 + arrival.time.minute * 60 + arrival.time.second)

    def getTimeDemandTypes(self):
        tdts = {}

        for sj in self.service_journeys:
            parts = []
            parts2 = []
            calls = sj.calls.call
            for call_i in range(0, len(calls) - 1):
                run_time = self.getRunTime(calls[call_i].departure, calls[call_i + 1].arrival)
                wait_time = self.getWaitTime(calls[call_i].arrival, calls[call_i].departure)
                tl = calls[call_i].onward_timing_link_view.timing_link_ref
                ssp = calls[call_i].scheduled_stop_point_ref

                parts.append(tuple([run_time, wait_time, tl, ssp]))
                parts2.append(tuple([run_time, wait_time, tl.ref, ssp.ref]))

            tdt_hash = hash(tuple(parts2))
            if tdt_hash not in tdts:
                run_times = []
                part = 0
                for x in parts:
                    jrt = JourneyRunTime(run_time=XmlDuration("PT{}S".format(x[0])), timing_link_ref=getRef(x[2], TimingLinkRef))
                    setIdVersion(jrt, self.codespace, "{}-{}".format(tdt_hash % 65449, part), self.version)
                    run_times.append(jrt)
                    part += 1

                if len(run_times) == 0:
                    run_times = None
                else:
                    run_times = JourneyRunTimesRelStructure(journey_run_time=run_times)

                wait_times = []
                part = 0
                for x in parts:
                    if x[1] > 0:
                        jwt = JourneyWaitTime(wait_time=XmlDuration("PT{}S".format(x[1])), scheduled_stop_point_ref=x[3])
                        wait_times.append(jwt)
                        part += 1

                if len(wait_times) == 0:
                    wait_times = None
                else:
                    wait_times = JourneyWaitTimesRelStructure(journey_wait_time=wait_times)

                tdt = TimeDemandType(run_times=run_times, wait_times=wait_times)
                setIdVersion(tdt, self.codespace, str(tdt_hash % 65449), self.version)
                tdts[tdt_hash] = tdt

            tdt = tdts[tdt_hash]
            sj.time_demand_type_ref = getRef(tdt, TimeDemandTypeRefStructure)
            sj.departure_time = calls[0].departure.time
            sj.departure_day_offset =  calls[0].departure.day_offset

        return list(tdts.values())

    def getServiceJourneyPatterns(self) -> (list[ServiceJourneyPattern], list[TimingLink]):
        lines = getIndex(self.lines)
        routes = getIndex(self.routes)
        ssp = getIndex(self.scheduled_stop_points)

        sjps = {}
        tls = {}
        tlsh = {}

        sj: ServiceJourney
        for sj in self.service_journeys:
            spijps = []
            for call in sj.calls.call:
                spijp = StopPointInJourneyPattern(scheduled_stop_point_ref=call.scheduled_stop_point_ref,
                                                  order=call.order,
                                                  for_alighting=call.arrival.for_alighting,
                                                  for_boarding=call.departure.for_boarding,
                                                  destination_display_view=call.destination_display_view,
                                                  derived_from_object_ref=call.id)
                spijps.append(spijp)

            spijp_hash = hash(tuple([(spijp.scheduled_stop_point_ref.ref, spijp.for_alighting, spijp.for_boarding, spijp.destination_display_view) for spijp in spijps]))
            if spijp_hash not in sjps:
                sjp = ServiceJourneyPattern()

                if sj.journey_pattern_view:
                    mine = vars(sjp).keys()
                    for attr, value in vars(sj.journey_pattern_view).items():
                        if attr in mine:
                            setattr(sjp, attr, value)

                sjp.derived_from_object_ref = sj.id
                sjp.route_ref = sj.route_ref
                # TODO: remove this one, because it can be fully resolved
                # sjp.route_view = RouteView(line_ref=routes[sj.route_ref.ref].line_ref)
                sjp.points_in_sequence = PointsInJourneyPatternRelStructure(point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern=spijps)
                setIdVersion(sjp, self.codespace, str(spijp_hash % 65449), self.version)
                for spijp in spijps:
                    setIdVersion(spijp, self.codespace, '{}-{}'.format(str(spijp_hash % 65449), spijp.order), self.version)

                sjps[spijp_hash] = sjp

                line = lines[sj.line_ref.ref]

                # TODO: This assumes a TimingPointInJourneyPattern or StopPointInJourneyPattern
                piss = sjp.points_in_sequence.point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern
                for pis_i in range(0, len(piss) - 1):
                    tl_hash = hash(tuple([line.operational_context_ref, piss[pis_i].scheduled_stop_point_ref.ref, piss[pis_i+1].scheduled_stop_point_ref.ref]))
                    if tl_hash not in tlsh:
                        timing_link = TimingLink(derived_from_object_ref=piss[pis_i].id,
                                                 operational_context_ref=line.operational_context_ref,
                                                 from_point_ref=getRef(ssp[piss[pis_i].scheduled_stop_point_ref.ref], TimingPointRefStructure),
                                                 to_point_ref=getRef(ssp[piss[pis_i+1].scheduled_stop_point_ref.ref], TimingPointRefStructure))
                        setIdVersion(timing_link, self.codespace, str(tl_hash % 65449), self.version)
                        tls[timing_link.id] = timing_link
                        tlsh[tl_hash] = timing_link
                    else:
                        timing_link = tlsh[tl_hash]

                    piss[pis_i].onward_timing_link_ref = getRef(timing_link, TimingLinkRefStructure)

            sjp = sjps[spijp_hash]
            sj.service_journey_pattern_ref = getRef(sjp, ServiceJourneyPatternRef)
            piss = sjp.points_in_sequence.point_in_journey_pattern_or_stop_point_in_journey_pattern_or_timing_point_in_journey_pattern
            for pis_i in range(0, len(piss)):
                if piss[pis_i].onward_timing_link_ref:
                    tl = tls[piss[pis_i].onward_timing_link_ref.ref]
                    if sj.calls.call[pis_i].onward_service_link_view and sj.calls.call[pis_i].onward_service_link_view.distance:
                        tl.distance = sj.calls.call[pis_i].onward_service_link_view.distance

                    # TODO: eventually OnwardTimingLinkView would get a Distance
                    sj.calls.call[pis_i].onward_timing_link_view = OnwardTimingLinkView(timing_link_ref=getRef(piss[pis_i].onward_timing_link_ref, TimingLinkRef))
                sj.calls.call[pis_i].point_in_journey_pattern_ref = getRef(piss[pis_i], PointInJourneyPatternRefStructure)

        return (list(sjps.values()), list(tls.values()))

if __name__ == '__main__':
    cp = CallsProfile()
    cp.getTimeDemandTypes()