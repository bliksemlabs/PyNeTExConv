# PyNeTExConv

NeTExConv and its successor NeTExConv2 are Java based implementations to convert public transport data exchange standards into other standards.
The key difference with many other conversion software is the use of [NeTEx](https://netex-cen.eu/) as an intermediate presentation.
To achieve a conversion an existing standard is projected as NeTEx structures matching the original semantic presentation of that standard.
Each converted source becomes a NeTEx file in that standards "NeTEx-profile".
The conversion between profiles is based on transitivity of concepts.
Concepts may be normalised, denormalised, projected or inferred into equivalent concepts, matching the target profile.
The conversion aims to provide an audit trail in the lifecycle of new objects.

## Motivation for a Python implementation

NeTExConv2 is based on Java and its JAXB backend to transform an XSD into a Java Object representation.
Since the original [NeTEx XSD](https://github.com/NeTEx-CEN/NeTEx) based schema's can be considered extremely complex the number of vendors and languages that support the conversion is limited.
While Java allows the creation of cross platform (web) applications, the current state of affairs is less than ideal. Until recently there was no automatic way in Python to parse a NeTEx XML file without manually using [ElementTree](https://lxml.de/) or equivalents. 
[xsData](https://xsdata.readthedocs.io/en/latest/) is a very recent development, which allows to automatically convert XML Schema into Python Data Classes.
Using the same architecture partial parsing, a hybrid method using XPath and specific object deserialisation, allows to handle (very) large document in a structured fashion. 
The experience of the conversion allows us to build a [PySide](https://www.qt.io/qt-for-python) based GUI for viewing NeTEx files.

## License

In order to stimulate the adoption of NeTEx in the open source community (and beyond) we have currently licensed this work as virally as possible under the [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.nl.html).
There must not be any ambiguity that this is an open source work and its source code and modifications must be shared with clients and end users.
In order to relicense this work in the future we make use of the [Harmony Agreement](http://harmonyagreements.org/).
The result of the conversion is obviously the same as the license of the data as you have put into it.

## Acknowledgements
We would like to thank Christodoulos Tsoulloftas for his work on xsData.
[SBB CFF FFS](https://www.sbb.ch/) for their commitments in the direction of open data, and open source transit developments.
The [Dutch Ministry of Infrastructure and Water Management](https://www.government.nl/ministries/ministry-of-infrastructure-and-water-management) for their current and historic efforts in public transport standardisation and data reuse.
