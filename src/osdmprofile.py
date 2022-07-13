# calendars -> availabilityConditions
import datetime
from typing import List

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDate, XmlDateTime

from netex import AvailabilityCondition, OperatingDaysRelStructure, OperatingDay, FareFrame, \
    ValidityConditionsRelStructure, TypeOfSalesOfferPackage, AlternativeText, MultilingualString, Cell, \
    FarePriceVersionedChildStructure, FareSection, PointOnSection, CompanionProfile, LimitingRule, UserProfile, \
    CompanionProfilesRelStructure, DiscountBasisEnumeration, UsageParametersInFrameRelStructure, PublicationDelivery, \
    DataObjectsRelStructure, CompositeFrame, FramesRelStructure, UserProfileRef, FareTablesInFrameRelStructure, \
    FareTable, CellsRelStructure, SalesOfferPackage, PriceGroup, FarePricesRelStructure, SalesOfferPackagePrice, \
    FarePricesInFrameRelStructure, PreassignedFareProduct, PriceGroupsRelStructure, PriceGroupRef, \
    FareProductsInFrameRelStructure, GenericParameterAssignment, GenericParameterAssignmentsRelStructure, \
    BooleanOperatorEnumeration, ValidityParametersRelStructure, OperatorRef, UsageParametersRelStructure, \
    FareStructureElementsInFrameRelStructure, FareStructureElement, ClassOfUse, FareClassEnumeration
from osdm import Calendars, ServiceClassDefinitions, Texts, Prices, Price, RegionalConstraints, RegionalValidity, \
    ServiceConstraints, CarrierConstraints, PassengerConstraints, CombinationConstraint, IncludedFreePassenger, \
    FareDelivery
from osdm.osdm import OSDM, Fares
import itertools


def mapDates(dates: List[XmlDate]):
    if not dates:
        return None

    return OperatingDaysRelStructure(operating_day_ref_or_operating_day=[OperatingDay(calendar_date=x) for x in dates])

def mapCalendar(calendar: Calendars):
    # TODO: UTC offset (model as Locale?)
    return  AvailabilityCondition(id=calendar.id, from_date=calendar.from_date, to_date=calendar.until_date, operating_days=mapDates(calendar.dates))

def mapCalendars(calendars: List[Calendars]):
    if not calendars:
        return None

    return ValidityConditionsRelStructure(choice=[mapCalendar(x) for x in calendars])

def mapServiceClassDefinition(serviceClassDefinition: ServiceClassDefinitions):
    fare_class = None
    if serviceClassDefinition.comfortClass == 'FIRST':
        fare_class = FareClassEnumeration.FIRST_CLASS
    elif serviceClassDefinition.comfortClass == 'SECOND':
        fare_class = FareClassEnumeration.SECOND_CLASS
    elif serviceClassDefinition.comfortClass == 'THIRD':
        fare_class = FareClassEnumeration.THIRD_CLASS

    return ClassOfUse(serviceClassDefinition.id, name=MultilingualString(serviceClassDefinition.text_ref), fare_class=fare_class)

def mapServiceClassDefinitions(serviceClassDefinitions: List[ServiceClassDefinitions]):
    return [mapServiceClassDefinition(x) for x in serviceClassDefinitions]

def mapTranslations(translations):
    if not translations:
        return None

    # TODO: shortText, does not have a matching AlternativeText
    return [AlternativeText(text=MultilingualString(value=x.textUtf8, lang=x.language)) for x in translations]

def mapText(text: Texts):
    # AlternativeText()

    return TypeOfSalesOfferPackage(id=text.id, name=text.text_utf8, short_name=text.text_utf8, alternative_texts=mapTranslations(text.translations))

def mapPricePrice(price: Price):
    # TODO: not in NeTEx vatDetails
    return FarePriceVersionedChildStructure(amount=price.amount / (10 ** price.scale), currency=price.currency)

def mapPrice(price: Prices):
    # TODO: Are the multiple "Price" elements for multiple currencies, Yes!
    # SAlesOfferPackage instead?
    return [Cell(id=prices.id + ":" + prices_x.currency, cell_price=mapPricePrice(prices_x)) for prices_x in prices.price]

def mapPrices(prices: List[Prices]):
    cell_list = [mapPrice(x) for x in prices]
    cells = list(itertools.chain(*cell_list))
    fare_table = FareTable(cells=CellsRelStructure(choice=cells))
    return [fare_table]

def mapPrices2(prices: List[Prices]):
    return [PriceGroup(id=price.id,
                       members=FarePricesRelStructure(choice=[SalesOfferPackagePrice(id=price.id + ":" + pp.currency, amount=pp.amount / (10 ** pp.scale), currency=pp.currency) for pp in price.price])) for price in prices]

def mapRegionalValidity(regional_validity: List[RegionalValidity]):
    # TODO, very complex need to know how this works
    # [PointOnSection(order=x.seq_nb, ) for x in regional_validity]
    pass

def mapRegionalConstraints(regional_constraint: RegionalConstraints):
    # entryConnectionPointId, exitConnectionPointId (borders between fare regions
    # We the
    # StationSet = virtual stop for station between two (international) borders

    return FareSection(id=regional_constraint.id, points_on_section=mapRegionalValidity(regional_constraint.regional_validity))

def mapServiceConstraints(service_constraints: ServiceConstraints):
    pass

def mapCarrierConstraint(carrier_constraints: CarrierConstraints):
    gpa = []
    if carrier_constraints.included_carrier:
        gpa += [GenericParameterAssignment(id=carrier_constraints.id + ":I", validity_parameters=ValidityParametersRelStructure(all_operators_ref_or_operator_ref=[OperatorRef(ref=x) for x in carrier_constraints.included_carrier]))]

    if carrier_constraints.excluded_carrier:
        gpa += [GenericParameterAssignment(id=carrier_constraints.id + ":E", limitation_grouping_type=BooleanOperatorEnumeration.NOT, validity_parameters=ValidityParametersRelStructure(all_operators_ref_or_operator_ref=[OperatorRef(ref=x) for x in carrier_constraints.excluded_carrier]))]

    return GenericParameterAssignment(
        id=carrier_constraints.id,
        includes_grouping_type=BooleanOperatorEnumeration.AND,
        includes=GenericParameterAssignmentsRelStructure(generic_parameter_assignment_or_generic_parameter_assignment_in_context=gpa))

def mapCarrierConstraints(carrier_constraints: List[CarrierConstraints]):
    return FareStructureElement(id="CarrierConstraints",
                                validity_parameter_assignments=GenericParameterAssignmentsRelStructure(generic_parameter_assignment_or_generic_parameter_assignment_in_context=[mapCarrierConstraint(carrier_constraint) for carrier_constraint in carrier_constraints]))

def mapCombinationConstraint(combination_constraint: List[CombinationConstraint]):
    # TODO: PassengerTypeRef
    return [CompanionProfile(minimum_number_of_persons=x.max_number, maximum_number_of_persons=x.min_number, user_profile_ref=UserProfileRef(ref=x.passenger_type_ref)) for x in combination_constraint]

def mapIncludedFreePassengers(included_free_passenger: List[IncludedFreePassenger]):
    return [CompanionProfile(discount_basis=DiscountBasisEnumeration.FREE, maximum_number_of_persons=x.number, user_profile_ref=UserProfileRef(ref=x.passenger_type_ref)) for x in included_free_passenger]


def mapPassengerConstraint(passenger_constraints: PassengerConstraints):
    # passengerConstraint -> UserProfile
    # includedFreePassenger -> CompanionProfile?
    # LimitingRule() (is about MinimumMaximum Price
    # TODO: PassengerWeight?
    # TODO: isAncillaryItem? Might be WiFi
    # NameRef, NeTEx does not support normalisation of Names
    # TODO: Age to Travel Alone
    # TODO: AgeToReserve

    return UserProfile(
        id=passenger_constraints.id,
        minimum_age=passenger_constraints.lower_age_limit, maximum_age=passenger_constraints.upper_age_limit,
                companion_profiles=CompanionProfilesRelStructure(companion_profile_ref_or_companion_profile=\
                                                                 mapCombinationConstraint(passenger_constraints.combination_constraint) +\
                                                                 mapIncludedFreePassengers(passenger_constraints.included_free_passenger)))

def mapPassengerConstraints(passenger_constraints: List[PassengerConstraints]):
    return UsageParametersInFrameRelStructure(user_profile=[mapPassengerConstraint(x) for x in passenger_constraints])

def mapFare(fare: Fares):
    generic_parameter_assignment = GenericParameterAssignment(includes_grouping_type=BooleanOperatorEnumeration.AND,
                                                              includes=GenericParameterAssignmentsRelStructure(generic_parameter_assignment_or_generic_parameter_assignment_in_context=[

                                                              ]))
    return PreassignedFareProduct(id=fare.id,
                                  name=MultilingualString(value=fare.name_ref),
                                  generic_parameter_assignment=generic_parameter_assignment,
                                  price_groups=PriceGroupsRelStructure(price_group_ref_or_price_group=[PriceGroupRef(ref=fare.price_ref)]))

def mapFares(fares: list[Fares]):
    # TODO: How is it possible that the IDs of multiple fares are equal?
    # TODO: fare_type/product_type in NeTEx would be single, return, etc. but NOT reservation
    preassigned_fare_product = [mapFare(fare) for fare in fares if fare.fare_type == 'ADMISSION']

    return FareProductsInFrameRelStructure(preassigned_fare_product=preassigned_fare_product)


from pathlib import Path
from xsdata.formats.dataclass.parsers import JsonParser
json_string = Path("/mnt/storage/home/skinkie/Sources/PyNeTExConv/examples/OSDM-Offline-1185_2.json").read_text()
parser = JsonParser()
osdm = parser.from_string(json_string, OSDM)

serializer_config = SerializerConfig(ignore_default_attributes=True)
serializer_config.pretty_print = True
serializer = XmlSerializer(serializer_config)

ns_map = {'': 'http://www.netex.org.uk/netex', 'gml': 'http://www.opengis.net/gml/3.2'}

with open('/tmp/out.xml', 'w') as out:
    fare_frame = FareFrame(
        fare_structure_elements=FareStructureElementsInFrameRelStructure(fare_structure_element=[mapCarrierConstraints(osdm.fare_delivery.fare_structure.carrier_constraints)]),
        price_groups=FarePricesInFrameRelStructure(price_group=mapPrices2(osdm.fare_delivery.fare_structure.prices)),
        # fare_tables=FareTablesInFrameRelStructure(fare_table=mapPrices(osdm.fare_delivery.fare_structure.prices)),
        content_validity_conditions=mapCalendars(osdm.fare_delivery.fare_structure.calendars),
        usage_parameters=mapPassengerConstraints(osdm.fare_delivery.fare_structure.passenger_constraints),
        fare_products=mapFares(osdm.fare_delivery.fare_structure.fares)
    )

    composite_frame = CompositeFrame(frames=FramesRelStructure(fare_frame=[fare_frame]))

    publication_delivery = PublicationDelivery(
        publication_timestamp=XmlDateTime.from_datetime(datetime.datetime.now()))
    publication_delivery.version = "ntx:1.1"
    publication_delivery.participant_ref = "NDOV"
    publication_delivery.description = "NeTEx export"
    publication_delivery.data_objects = DataObjectsRelStructure(choice=[composite_frame])

    serializer.write(out, publication_delivery, ns_map)


