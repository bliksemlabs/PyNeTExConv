import datetime
from typing import Optional

from xsdata.models.datatype import XmlDateTime

from netex import Codespace, Version, DataSource, ResponsibilitySet, VersionFrameDefaultsStructure, LocaleStructure, \
    SystemOfUnits, MultilingualString, Operator, ContactStructure, CompositeFrame, PublicationDelivery, \
    DataObjectsRelStructure, VersionTypeEnumeration, TypeOfFrameRef, VersionsRelStructure, FramesRelStructure, \
    ResourceFrame, DataSourcesInFrameRelStructure, ResponsibilitySetsInFrameRelStructure, ZonesInFrameRelStructure, \
    OrganisationsInFrameRelStructure, OperationalContextsInFrameRelStructure, VehicleTypesInFrameRelStructure
from refs import getRef, setIdVersion


class DutchNeTExProfile:
    def getDataSource(self, id: str, name: str, short_name: str, description: str) -> DataSource:
        data_source = DataSource(name=MultilingualString(name), short_name=MultilingualString(short_name), description=MultilingualString(description))
        setIdVersion(data_source, self.codespace, id, None)
        return data_source

    def getOperator(self, id: str, name: str, short_name: str, customer_service_contact_details: Optional[ContactStructure]):

        operator = Operator(name=MultilingualString(name), short_name=MultilingualString(short_name), customer_service_contact_details=customer_service_contact_details)
        setIdVersion(operator, self.codespace, id, None)
        return operator

    def getFrameDefaults(self, codespace: Codespace,
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

    def getResourceFrame(self) -> ResourceFrame:
        resource_frame = ResourceFrame()
        setIdVersion(resource_frame, self.codespace, "ResourceFrame", self.version)
        resource_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_RESOURCE", version="9.2.3")
        resource_frame.data_sources = DataSourcesInFrameRelStructure(data_source=[self.data_source])
        resource_frame.responsibility_sets = ResponsibilitySetsInFrameRelStructure(
            responsibility_set=[self.responsibility_set_partitie, self.responsibility_set_concessie, self.responsibility_set_financier])
        resource_frame.zones = ZonesInFrameRelStructure(transport_administrative_zone=[self.transport_administrative_zone])
        resource_frame.organisations = OrganisationsInFrameRelStructure(operator=[self.operator])
        resource_frame.operational_contexts = OperationalContextsInFrameRelStructure(
            operational_context=[self.operational_contexts])
        resource_frame.vehicle_types = VehicleTypesInFrameRelStructure(compound_train_or_train_or_vehicle_type=self.vehicle_types)
        # resource_frame.vehicles = VehiclesInFrameRelStructure(train_element_or_vehicle=getVehicles(codespace))

        return resource_frame

    def getCompositeFrame(self) -> CompositeFrame:
        composite_frame = CompositeFrame()
        setIdVersion(composite_frame, self.codespace, "WTR", self.version)
        composite_frame.frame_defaults = self.getFrameDefaults(self.codespace, self.data_source, self.responsibility_set_partitie)
        composite_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_BASELINE", version="9.2.3")
        composite_frame.versions = VersionsRelStructure(version_ref_or_version=[self.version])
        composite_frame.frames = FramesRelStructure(resource_frame=[self.getResourceFrame()])

        # service_frame, service_journey_patterns, time_demand_types = getServiceFrame(codespace, version,
        #                                                                              operational_contexts,
        #                                                                              responsibility_set_concessie)

        """
        composite_frame.type_of_frame_ref = TypeOfFrameRef(ref="BISON:TypeOfFrame:NL_TT_BASELINE", version="9.2.3")
        composite_frame.versions = VersionsRelStructure(version_ref_or_version=[version])
        composite_frame.codespaces = CodespacesRelStructure(codespace_ref_or_codespace=[codespace])
        composite_frame.frames = FramesRelStructure(resource_frame=[
            getResourceFrame(codespace, version, operational_contexts, data_source,
                             [responsibility_set_partitie, responsibility_set_concessie, responsibility_set_financier],
                             transport_administrative_zone, operator)],
                                                    service_frame=[service_frame],
                                                    timetable_frame=[getTimetableFrame(codespace, version, operator,
                                                                                       service_journey_patterns,
                                                                                       time_demand_types)])
        """
        return composite_frame

    def getVersion(self, version_version: datetime.date, start_date: datetime.date,
                   end_date: datetime.time) -> Version:
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time())

        version = Version(start_date=XmlDateTime.from_datetime(start_date),
                          end_date=XmlDateTime.from_datetime(end_date),
                          version_type=VersionTypeEnumeration.BASELINE)
        version.version = version_version.strftime("%Y%m%d")
        setIdVersion(version, self.codespace, version.version, version)
        return version

    def getPublicationDelivery(self) -> PublicationDelivery:
        composite_frame = self.getCompositeFrame()

        publication_delivery = PublicationDelivery(publication_timestamp=XmlDateTime.from_datetime(datetime.datetime.now()))
        publication_delivery.version = "ntx:1.1"
        publication_delivery.participant_ref = "NDOV"
        publication_delivery.description = "NeTEx export"
        publication_delivery.data_objects = DataObjectsRelStructure(choice=[composite_frame])

        return publication_delivery